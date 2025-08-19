# main.py
"""
The main application entry point.

Initializes the UI, creates the model, viewport, and renderer,
and connects them all via event handlers.
"""
import tkinter as tk
from typing import Optional, Tuple, Set, Dict

from config import (
    DragMode,
    RenderMode,
    StyleConfig,
    ViewConfig,
    InteractionConfig,
    OctaveConfig,
    MidiConfig,
)
from viewport import Viewport
from tonnetz import TonnetzModel
from renderer import GridRenderer
from midi_handler import MidiHandler
from note_mapper import NoteMapper
from midi_controller import MidiController
import utils


class App:
    """The main application controller."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Musical Tile Grid")
        self.root.geometry("1100x700")

        self.octave_label: Optional[tk.Label] = None
        self.enharmonic_button_text: Optional[tk.StringVar] = None
        self.instrument_var: Optional[tk.StringVar] = None
        self.instrument_list: Dict[str, int] = {}

        # --- Component Initialization ---
        self.model = TonnetzModel()
        self.midi_handler = MidiHandler(MidiConfig.SOUNDFONT_PATH, audio_driver='dsound')
        self.note_mapper = NoteMapper()
        self.midi_controller = MidiController(self.midi_handler, self.note_mapper)
        self.model.add_listener(self.midi_controller)

        if self.midi_handler.is_active:
            self.instrument_list = self.midi_handler.get_instruments()
            self.midi_handler.program_select(MidiConfig.DEFAULT_INSTRUMENT)

        self._setup_ui()
        self.viewport: Optional[Viewport] = None
        self.renderer: Optional[GridRenderer] = None

        # --- Interaction State ---
        self.render_mode = ViewConfig.DEFAULT_RENDER_MODE
        self.drag_mode = DragMode.NONE
        self.drag_start_pos: Tuple[int, int] = (0, 0)
        self.drag_last_coord: Optional[Tuple[int, int]] = None
        self.drag_affected_coords: Set[Tuple[int, int]] = set()
        self.drag_button: int = 0
        self.global_octave = OctaveConfig.INITIAL_OCTAVE
        self._update_octave_label()

        self._bind_events()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Handles window close events to clean up resources."""
        self.model.clear_selection()
        self.midi_handler.close()
        self.root.destroy()

    def _initialize_components(self):
        """Creates the viewport and renderer once the canvas is ready."""
        self.viewport = Viewport(
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            ViewConfig.INITIAL_TILES_ON_SCREEN,
            self.render_mode,
        )
        self.renderer = GridRenderer(
            self.canvas, self.viewport, self.model, self.render_mode
        )
        # The renderer is now also a listener for model changes.
        self.model.add_listener(self.renderer)

    def _on_first_configure(self, event):
        """
        Initializes components on the first <Configure> event, which guarantees
        the canvas has a valid size. Then, rebinds to the standard resize handler.
        """
        if self.viewport is None:
            self._initialize_components()
            self._on_resize()
            self.canvas.bind("<Configure>", lambda e: self._on_resize())

    def _setup_ui(self):
        """Creates the main UI frames, canvas, and widgets."""
        top_frame = tk.Frame(self.root, bg=StyleConfig.COLOR_UI_BACKGROUND)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        instructions = (
            "Left-Click/Drag: Toggle Select | Right-Click: Change Octave | "
            "Middle-Click Drag: Pan | Scroll: Zoom"
        )
        tk.Label(
            top_frame, text=instructions, anchor="w", bg=StyleConfig.COLOR_UI_BACKGROUND
        ).pack(side=tk.LEFT, padx=10, pady=5)

        right_frame = tk.Frame(top_frame, bg=StyleConfig.COLOR_UI_BACKGROUND)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.octave_label = tk.Label(
            right_frame, text="", width=15, bg=StyleConfig.COLOR_UI_BACKGROUND
        )
        self.octave_label.pack(side=tk.RIGHT)

        self.enharmonic_button_text = tk.StringVar()
        tk.Button(
            right_frame,
            textvariable=self.enharmonic_button_text,
            command=self._toggle_enharmonics,
        ).pack(side=tk.RIGHT, padx=5)
        self._update_enharmonic_button_text()

        tk.Button(
            right_frame, text="Toggle Layout", command=self._toggle_render_mode
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            right_frame, text="Clear & Reset View", command=self._clear_and_reset
        ).pack(side=tk.RIGHT, padx=5)

        instrument_frame = tk.Frame(right_frame, bg=StyleConfig.COLOR_UI_BACKGROUND)
        instrument_frame.pack(side=tk.RIGHT, padx=5)
        tk.Label(
            instrument_frame, text="Instrument:", bg=StyleConfig.COLOR_UI_BACKGROUND
        ).pack(side=tk.LEFT)

        self.instrument_var = tk.StringVar(self.root)
        instrument_names = (
            list(self.instrument_list.keys())
            if self.instrument_list
            else ["MIDI Disabled"]
        )

        if self.midi_handler.is_active and self.instrument_list:
            default_name = next(
                (
                    name
                    for name, num in self.instrument_list.items()
                    if num == MidiConfig.DEFAULT_INSTRUMENT
                ),
                instrument_names[0],
            )
            self.instrument_var.set(default_name)
        else:
            self.instrument_var.set("MIDI Disabled")

        instrument_menu = tk.OptionMenu(
            instrument_frame,
            self.instrument_var,
            *instrument_names,
        )
        if self.instrument_var:
            self.instrument_var.trace_add("write", self._on_instrument_var_change)

        instrument_menu.config(width=25)
        instrument_menu.pack(side=tk.LEFT)
        if not self.midi_handler.is_active or not self.instrument_list:
            instrument_menu.config(state=tk.DISABLED)

        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _on_instrument_var_change(self, *args):
        """Callback for when the instrument StringVar changes."""
        if self.instrument_var:
            instrument_name = self.instrument_var.get()
            if instrument_name:
                self._change_instrument(instrument_name)

    def _change_instrument(self, instrument_name: str):
        """Changes the current MIDI instrument based on UI selection."""
        if self.midi_handler.is_active and self.instrument_list:
            program_num = self.instrument_list.get(instrument_name)
            if program_num is not None:
                self.midi_handler.program_select(program_num)

    def _update_octave_label(self):
        """Updates the global octave display in the UI."""
        if self.octave_label:
            self.octave_label.config(text=f"Global Octave: {self.global_octave}")

    def _update_enharmonic_button_text(self):
        """Updates the text on the sharps/flats toggle button."""
        if self.enharmonic_button_text and self.model:
            text = "Show Flats (♭)" if self.model.use_sharps else "Show Sharps (♯)"
            self.enharmonic_button_text.set(text)

    def _toggle_enharmonics(self):
        """Toggles the display between sharp and flat enharmonics."""
        if not self.renderer:
            return
        self.model.set_enharmonic_preference(not self.model.use_sharps)
        self._update_enharmonic_button_text()
        self.renderer.redraw_full()

    def _toggle_render_mode(self):
        """Switches between rectangular and hexagonal rendering."""
        if not self.renderer or not self.viewport:
            return
        self.render_mode = (
            RenderMode.HEXAGON
            if self.render_mode == RenderMode.RECTANGLE
            else RenderMode.RECTANGLE
        )
        self.viewport.set_render_mode(self.render_mode)
        self.renderer.set_render_mode(self.render_mode)
        self.renderer.redraw_full()

    def _bind_events(self):
        """Binds all mouse and window events."""
        self.canvas.bind("<Configure>", self._on_first_configure)
        self.canvas.bind("<ButtonPress>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<B2-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Button-4>", self._on_zoom)
        self.canvas.bind("<Button-5>", self._on_zoom)

    def _clear_and_reset(self):
        """Clears the selection and resets the viewport to its initial state."""
        if not self.renderer or not self.viewport:
            return
        self.model.clear_selection()
        self.viewport.reset(
            self.canvas.winfo_width(),
            self.canvas.winfo_height(),
            ViewConfig.INITIAL_TILES_ON_SCREEN,
        )
        self.renderer.redraw_full()

    def _on_resize(self):
        """Handles window resize events."""
        if not self.renderer or not self.viewport:
            return
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.viewport.update_zoom_limits(
            width,
            height,
            ViewConfig.MIN_TILES_ON_SCREEN,
            ViewConfig.MAX_TILES_ON_SCREEN,
        )
        self.renderer.redraw_full()

    def _on_press(self, event):
        """Handles the start of any mouse action."""
        if not self.viewport:
            return

        self.drag_start_pos = (event.x, event.y)
        self.drag_button = event.num
        self.drag_affected_coords.clear()

        if event.num == 1:
            self.drag_mode = DragMode.SELECT
            self.drag_last_coord = self.viewport.canvas_to_world_int(event.x, event.y)
        elif event.num == 2:
            self.drag_mode = DragMode.PAN
            self.canvas.config(cursor="fleur")

    def _on_drag(self, event):
        """Handles mouse drag events for panning or selecting."""
        if not self.renderer or not self.viewport:
            return

        if self.drag_mode == DragMode.PAN:
            dx = event.x - self.drag_start_pos[0]
            dy = event.y - self.drag_start_pos[1]
            self.drag_start_pos = (event.x, event.y)
            self.viewport.pan(dx, dy)
            self.renderer.redraw_full()

        elif self.drag_mode == DragMode.SELECT:
            if self.drag_last_coord is None:
                return

            current_coord = self.viewport.canvas_to_world_int(event.x, event.y)
            if current_coord == self.drag_last_coord:
                return

            for coord in utils.bresenham_line(
                self.drag_last_coord[0],
                self.drag_last_coord[1],
                current_coord[0],
                current_coord[1],
            ):
                if coord not in self.drag_affected_coords:
                    self.model.toggle_selection(coord, self.global_octave)
                    self.drag_affected_coords.add(coord)
            self.drag_last_coord = current_coord

    def _on_release(self, event):
        """Handles the end of a mouse action, processing clicks."""
        if not self.viewport:
            return

        dist_sq = (self.drag_start_pos[0] - event.x) ** 2 + (
            self.drag_start_pos[1] - event.y
        ) ** 2
        is_click = dist_sq < InteractionConfig.CLICK_VS_DRAG_THRESHOLD_SQ

        if self.drag_button == 1 and is_click:
            coord = self.viewport.canvas_to_world_int(event.x, event.y)
            self.model.toggle_selection(coord, self.global_octave)

        elif self.drag_button == 3 and is_click:
            coord = self.viewport.canvas_to_world_int(event.x, event.y)
            if self.model.is_selected(coord):
                new_octave = self.model.increment_octave(coord)
                if new_octave is not None:
                    self.global_octave = new_octave
                    self._update_octave_label()
            else:
                min_o, max_o = OctaveConfig.MIN_OCTAVE, OctaveConfig.MAX_OCTAVE
                span = max_o - min_o + 1
                self.global_octave = (self.global_octave - min_o + 1) % span + min_o
                self._update_octave_label()

        self.drag_mode = DragMode.NONE
        self.drag_last_coord = None
        self.canvas.config(cursor="")

    def _on_zoom(self, event):
        """Handles zooming with the mouse wheel."""
        if not self.renderer or not self.viewport:
            return

        if event.num == 4 or event.delta > 0:
            scale = InteractionConfig.ZOOM_FACTOR
        elif event.num == 5 or event.delta < 0:
            scale = 1 / InteractionConfig.ZOOM_FACTOR
        else:
            return

        if self.viewport.zoom_at(scale, event.x, event.y):
            self.renderer.redraw_full()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
