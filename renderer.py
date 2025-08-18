# renderer.py
"""
Handles all drawing operations on the Tkinter Canvas.
"""
import tkinter as tk
import tkinter.font as tkFont
from typing import Tuple, Dict, Any, Set

from viewport import Viewport
from tonnetz import TonnetzModel
from config import StyleConfig, ViewConfig


class GridRenderer:
    """Renders the grid state onto the canvas based on the viewport."""

    def __init__(self, canvas: tk.Canvas, viewport: Viewport, model: TonnetzModel):
        self.canvas = canvas
        self.viewport = viewport
        self.model = model

        # Maps (row, col) -> {'rect': id, 'text': id}
        self.visible_items: Dict[Tuple[int, int], Dict[str, Any]] = {}

        # Pre-calculate font metrics for dynamic sizing
        self._ref_font_size = 10
        self._min_font_size = 6
        ref_font = tkFont.Font(
            family=StyleConfig.FONT_FAMILY, size=self._ref_font_size, weight="bold"
        )
        self._ref_text_width = ref_font.measure("G#6")

    def _calculate_font_size(self) -> int:
        """Calculates the optimal font size to fit text within a tile."""
        if self._ref_text_width == 0:
            return self._min_font_size

        tile_width = self.viewport.zoom
        estimated_size = (tile_width / self._ref_text_width) * self._ref_font_size
        padded_size = int(estimated_size * 0.9)
        return max(self._min_font_size, padded_size)

    def redraw_full(self):
        """
        Performs an efficient redraw of the entire visible grid.
        It adds, removes, and updates items as needed, avoiding a full clear.
        """
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        min_r, max_r, min_c, max_c = self.viewport.get_visible_grid_rect(width, height)

        # Performance safety check: Abort if trying to render too many tiles.
        num_tiles = (max_r - min_r) * (max_c - min_c)
        if num_tiles > ((ViewConfig.MAX_TILES_ON_SCREEN + 5) ** 2):
            print(f"Render aborted: Too many tiles requested ({num_tiles}).")
            return

        # 1. Determine the set of required tiles
        required_coords = set(
            (r, c) for r in range(min_r, max_r) for c in range(min_c, max_c)
        )
        current_coords = set(self.visible_items.keys())

        # 2. Find which items to remove, add, or update
        coords_to_remove = current_coords - required_coords
        coords_to_add = required_coords - current_coords
        coords_to_update = current_coords.intersection(required_coords)

        # 3. Perform canvas operations
        for coord in coords_to_remove:
            self._delete_tile(coord)

        for coord in coords_to_add:
            self._create_tile(coord)

        for coord in coords_to_update:
            self._update_tile_position(coord)

        self.update_visuals(required_coords)

    def update_visuals(self, coords: Set[Tuple[int, int]]):
        """Updates the style (color, text) of the given set of coordinates."""
        for coord in coords:
            if coord in self.visible_items:
                self._update_tile_style(coord)

    def _delete_tile(self, coord: Tuple[int, int]):
        """Deletes the canvas items associated with a coordinate."""
        if coord in self.visible_items:
            items = self.visible_items.pop(coord)
            self.canvas.delete(items["rect"])
            if items["text"] is not None:
                self.canvas.delete(items["text"])

    def _create_tile(self, coord: Tuple[int, int]):
        """Creates new canvas items for a coordinate."""
        r, c = coord
        zoom = self.viewport.zoom
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y

        x0 = c * zoom - offset_x
        y0 = r * zoom - offset_y
        x1, y1 = x0 + zoom, y0 + zoom

        rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, tags="tile")

        text_id = None
        if zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD:
            note_name = self.model.get_display_note_for_coord(coord)
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            text_id = self.canvas.create_text(
                x0 + zoom / 2,
                y0 + zoom / 2,
                text=note_name,
                font=font,
                tags="tile_text",
            )

        self.visible_items[coord] = {"rect": rect_id, "text": text_id}
        self._update_tile_style(coord)

    def _update_tile_position(self, coord: Tuple[int, int]):
        """Updates the coordinates of existing canvas items."""
        r, c = coord
        zoom = self.viewport.zoom
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y

        x0 = c * zoom - offset_x
        y0 = r * zoom - offset_y
        x1, y1 = x0 + zoom, y0 + zoom

        items = self.visible_items[coord]
        self.canvas.coords(items["rect"], x0, y0, x1, y1)

        # Handle text creation/deletion/update based on zoom
        text_visible = zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD
        text_exists = items["text"] is not None

        if text_visible and not text_exists:
            self._delete_tile(coord)
            self._create_tile(coord)
        elif not text_visible and text_exists:
            self.canvas.delete(items["text"])
            items["text"] = None
        elif text_visible and text_exists:
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            self.canvas.coords(items["text"], x0 + zoom / 2, y0 + zoom / 2)
            self.canvas.itemconfigure(items["text"], font=font)

    def _update_tile_style(self, coord: Tuple[int, int]):
        """Updates the fill and text color of a tile based on selection state."""
        items = self.visible_items.get(coord)
        if not items:
            return

        is_selected = self.model.is_selected(coord)
        fill = (
            StyleConfig.COLOR_TILE_SELECTED
            if is_selected
            else StyleConfig.COLOR_TILE_DEFAULT
        )
        text_fill = (
            StyleConfig.COLOR_TEXT_SELECTED
            if is_selected
            else StyleConfig.COLOR_TEXT_DEFAULT
        )

        self.canvas.itemconfigure(
            items["rect"], fill=fill, outline=StyleConfig.COLOR_TILE_OUTLINE
        )
        if items["text"] is not None:
            note_name = self.model.get_display_note_for_coord(coord)
            self.canvas.itemconfigure(items["text"], fill=text_fill, text=note_name)
