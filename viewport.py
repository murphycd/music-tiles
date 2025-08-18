# viewport.py
"""
Manages the state of the view (pan, zoom) and coordinate transformations.
"""
import math
from typing import Tuple


class Viewport:
    """Handles the mapping between world coordinates and canvas coordinates."""

    def __init__(self, canvas_width: int, canvas_height: int, initial_tiles: int):
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.zoom: float = 1.0
        self.min_zoom: float = 1.0
        self.max_zoom: float = 100.0
        self._set_initial_zoom(canvas_width, canvas_height, initial_tiles)

    def _set_initial_zoom(self, width: int, height: int, tiles: int):
        """Sets the initial zoom level based on the canvas size."""
        if width <= 1 or height <= 1:
            return
        short_dim = min(width, height)
        self.zoom = short_dim / tiles
        self.offset_x = -width / 2
        self.offset_y = -height / 2

    def update_zoom_limits(
        self, width: int, height: int, min_tiles: int, max_tiles: int
    ):
        """Updates the min/max zoom levels based on canvas size."""
        if width <= 1 or height <= 1:
            return
        short_dim = min(width, height)
        self.min_zoom = short_dim / max_tiles
        self.max_zoom = short_dim / min_tiles

    def pan(self, dx: int, dy: int):
        """Pans the view by a delta in canvas pixels."""
        self.offset_x -= dx
        self.offset_y -= dy

    def zoom_at(self, scale: float, canvas_x: int, canvas_y: int) -> bool:
        """
        Zooms the view by a given scale, keeping the point under the
        cursor stationary.

        Returns:
            True if the zoom level changed, False otherwise.
        """
        old_zoom = self.zoom
        world_y_float, world_x_float = self.canvas_to_world_float(canvas_x, canvas_y)

        new_zoom = self.zoom * scale
        self.zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        self.offset_x = world_x_float * self.zoom - canvas_x
        self.offset_y = world_y_float * self.zoom - canvas_y

        return self.zoom != old_zoom

    def canvas_to_world_int(self, cx: int, cy: int) -> Tuple[int, int]:
        """Converts canvas pixel coordinates to integer world tile coordinates."""
        world_y, world_x = self.canvas_to_world_float(cx, cy)
        return math.floor(world_y), math.floor(world_x)

    def canvas_to_world_float(self, cx: int, cy: int) -> Tuple[float, float]:
        """Converts canvas pixel coordinates to precise world coordinates."""
        return (cy + self.offset_y) / self.zoom, (cx + self.offset_x) / self.zoom

    def get_visible_grid_rect(
        self, canvas_width: int, canvas_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Calculates the integer bounding box of visible tiles in world coordinates.
        Returns (min_row, max_row, min_col, max_col).
        """
        start_row, start_col = self.canvas_to_world_int(0, 0)
        end_row, end_col = self.canvas_to_world_int(canvas_width, canvas_height)
        return start_row, end_row + 1, start_col, end_col + 1
