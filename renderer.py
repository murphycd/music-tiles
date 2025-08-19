# renderer.py
"""
Handles all drawing operations on the Tkinter Canvas.
"""
import tkinter as tk
import tkinter.font as tkFont
import math
from typing import Tuple, Dict, Any

from viewport import Viewport
from tonnetz import TonnetzModel
from config import StyleConfig, ViewConfig, RenderMode
from events import (
    ModelEvent,
    TileSelectedEvent,
    TileDeselectedEvent,
    TileOctaveChangedEvent,
    SelectionClearedEvent,
)


class GridRenderer:
    """Renders the grid state onto the canvas based on the viewport."""

    def __init__(
        self,
        canvas: tk.Canvas,
        viewport: Viewport,
        model: TonnetzModel,
        render_mode: RenderMode,
    ):
        self.canvas = canvas
        self.viewport = viewport
        self.model = model
        self.render_mode = render_mode
        self.visible_items: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self._ref_font_size = 10
        self._min_font_size = 6
        ref_font = tkFont.Font(
            family=StyleConfig.FONT_FAMILY, size=self._ref_font_size, weight="bold"
        )
        self._ref_text_width = ref_font.measure("G#6")

    def handle_event(self, event: ModelEvent):
        """Handles model events to update visuals."""
        if isinstance(
            event, (TileSelectedEvent, TileDeselectedEvent, TileOctaveChangedEvent)
        ):
            self._update_tile_style(event.coord)
        elif isinstance(event, SelectionClearedEvent):
            # A full clear can be handled efficiently by redrawing.
            self.redraw_full()

    def set_render_mode(self, mode: RenderMode):
        """Sets the current render mode and clears visible items."""
        if self.render_mode != mode:
            self.render_mode = mode
            for coord in list(self.visible_items.keys()):
                self._delete_tile(coord)
            self.visible_items.clear()

    def _calculate_font_size(self) -> int:
        """Calculates the optimal font size to fit text within a tile."""
        if self._ref_text_width == 0:
            return self._min_font_size
        scale_factor = 0.85 if self.render_mode == RenderMode.HEXAGON else 0.9
        tile_width = self.viewport.zoom
        estimated_size = (tile_width / self._ref_text_width) * self._ref_font_size
        padded_size = int(estimated_size * scale_factor)
        return max(self._min_font_size, padded_size)

    def redraw_full(self):
        """
        Performs an efficient redraw of the entire visible grid.
        """
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            return

        min_q, max_q, min_r, max_r = self.viewport.get_visible_grid_rect(width, height)
        num_tiles = (max_q - min_q) * (max_r - min_r)
        if num_tiles > ((ViewConfig.MAX_TILES_ON_SCREEN + 10) ** 2):
            print(f"Render aborted: Too many tiles requested ({num_tiles}).")
            return

        required_coords = set(
            (q, r) for q in range(min_q, max_q) for r in range(min_r, max_r)
        )
        current_coords = set(self.visible_items.keys())

        coords_to_remove = current_coords - required_coords
        coords_to_add = required_coords - current_coords
        coords_to_update = current_coords.intersection(required_coords)

        for coord in coords_to_remove:
            self._delete_tile(coord)
        for coord in coords_to_add:
            self._create_tile(coord)
        for coord in coords_to_update:
            self._update_tile_position(coord)

        # Update style for all visible tiles after creation/positioning
        for coord in required_coords:
            self._update_tile_style(coord)

    def _delete_tile(self, coord: Tuple[int, int]):
        """Deletes the canvas items associated with a coordinate."""
        if coord in self.visible_items:
            items = self.visible_items.pop(coord)
            self.canvas.delete(items["shape"])
            if items["text"] is not None:
                self.canvas.delete(items["text"])

    def _get_hexagon_vertices(
        self, center_x: float, center_y: float, size: float
    ) -> list[float]:
        """Calculates the 6 vertices for a pointy-topped hexagon."""
        vertices = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            vertices.append(center_x + size * math.cos(angle))
            vertices.append(center_y + size * math.sin(angle))
        return vertices

    def _create_tile(self, coord: Tuple[int, int]):
        """Dispatches to the correct tile creation method based on render mode."""
        if self.render_mode == RenderMode.RECTANGLE:
            self._create_rect_tile(coord)
        else:
            self._create_hex_tile(coord)

    def _update_tile_position(self, coord: Tuple[int, int]):
        """Dispatches to the correct tile update method based on render mode."""
        if self.render_mode == RenderMode.RECTANGLE:
            self._update_rect_position(coord)
        else:
            self._update_hex_position(coord)

    def _create_rect_tile(self, coord: Tuple[int, int]):
        """Creates new canvas items for a rectangular tile from (q,r) coords."""
        q, r = coord
        zoom = self.viewport.zoom
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y
        x0 = q * zoom - offset_x
        y0 = -r * zoom - offset_y
        x1, y1 = x0 + zoom, y0 + zoom

        rect_id = self.canvas.create_rectangle(x0, y0, x1, y1, tags="tile")
        text_id = None
        if zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD:
            note_name = self.model.get_display_note_for_coord(coord)
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            text_id = self.canvas.create_text(
                x0 + zoom / 2, y0 + zoom / 2, text=note_name, font=font, tags="text"
            )
        self.visible_items[coord] = {"shape": rect_id, "text": text_id}

    def _create_hex_tile(self, coord: Tuple[int, int]):
        """Creates new canvas items for a hexagonal tile."""
        q, r = coord
        size = self.viewport.zoom / 2.0
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y
        center_x_world = size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
        center_y_world = size * (3.0 / 2.0 * r)
        center_x = center_x_world - offset_x
        center_y = center_y_world - offset_y

        vertices = self._get_hexagon_vertices(center_x, center_y, size)
        poly_id = self.canvas.create_polygon(vertices, tags="tile")
        text_id = None

        if self.viewport.zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD:
            note_name = self.model.get_display_note_for_coord(coord)
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            text_id = self.canvas.create_text(
                center_x, center_y, text=note_name, font=font, tags="text"
            )
        self.visible_items[coord] = {"shape": poly_id, "text": text_id}

    def _update_rect_position(self, coord: Tuple[int, int]):
        """Updates the coordinates of an existing rectangular tile from (q,r)."""
        q, r = coord
        zoom = self.viewport.zoom
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y
        x0 = q * zoom - offset_x
        y0 = -r * zoom - offset_y
        x1, y1 = x0 + zoom, y0 + zoom

        items = self.visible_items[coord]
        self.canvas.coords(items["shape"], x0, y0, x1, y1)

        text_visible = zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD
        text_exists = items["text"] is not None
        if text_visible and not text_exists:
            self._delete_tile(coord)
            self._create_rect_tile(coord)
        elif not text_visible and text_exists:
            self.canvas.delete(items["text"])
            items["text"] = None
        elif text_visible and text_exists:
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            self.canvas.coords(items["text"], x0 + zoom / 2, y0 + zoom / 2)
            self.canvas.itemconfigure(items["text"], font=font)

    def _update_hex_position(self, coord: Tuple[int, int]):
        """Updates the coordinates of an existing hexagonal tile."""
        q, r = coord
        size = self.viewport.zoom / 2.0
        offset_x, offset_y = self.viewport.offset_x, self.viewport.offset_y
        center_x_world = size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
        center_y_world = size * (3.0 / 2.0 * r)
        center_x = center_x_world - offset_x
        center_y = center_y_world - offset_y

        vertices = self._get_hexagon_vertices(center_x, center_y, size)
        items = self.visible_items[coord]
        self.canvas.coords(items["shape"], *vertices)

        text_visible = self.viewport.zoom > ViewConfig.NOTE_VISIBILITY_ZOOM_THRESHOLD
        text_exists = items["text"] is not None
        if text_visible and not text_exists:
            self._delete_tile(coord)
            self._create_hex_tile(coord)
        elif not text_visible and text_exists:
            self.canvas.delete(items["text"])
            items["text"] = None
        elif text_visible and text_exists:
            font_size = self._calculate_font_size()
            font = (StyleConfig.FONT_FAMILY, font_size, "bold")
            self.canvas.coords(items["text"], center_x, center_y)
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
            items["shape"], fill=fill, outline=StyleConfig.COLOR_TILE_OUTLINE
        )
        if items["text"] is not None:
            note_name = self.model.get_display_note_for_coord(coord)
            self.canvas.itemconfigure(items["text"], fill=text_fill, text=note_name)
