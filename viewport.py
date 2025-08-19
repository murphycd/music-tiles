# viewport.py
"""
Manages the state of the view (pan, zoom) and coordinate transformations.
"""
import math
from typing import Tuple

from config import RenderMode


class Viewport:
    """Handles the mapping between world coordinates and canvas coordinates."""

    def __init__(
        self,
        canvas_width: int,
        canvas_height: int,
        initial_tiles: int,
        render_mode: RenderMode,
    ):
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.zoom: float = 1.0
        self.min_zoom: float = 1.0
        self.max_zoom: float = 100.0
        self.render_mode = render_mode
        self._set_initial_zoom(canvas_width, canvas_height, initial_tiles)

    def set_render_mode(self, mode: RenderMode):
        """Sets the current rendering mode."""
        self.render_mode = mode

    def _set_initial_zoom(self, width: int, height: int, tiles: int):
        """Sets the initial zoom level based on the canvas size."""
        if width <= 1 or height <= 1:
            return
        short_dim = min(width, height)
        self.zoom = short_dim / tiles
        self.offset_x = -width / 2
        self.offset_y = -height / 2

    def reset(self, canvas_width: int, canvas_height: int, initial_tiles: int):
        """Resets the viewport to its initial pan and zoom state."""
        self._set_initial_zoom(canvas_width, canvas_height, initial_tiles)

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
        world_q_float, world_r_float = self.canvas_to_world_float(canvas_x, canvas_y)

        new_zoom = self.zoom * scale
        self.zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if self.zoom == old_zoom:
            return False

        # Re-calculate offset to keep the point under the cursor stationary
        if self.render_mode == RenderMode.RECTANGLE:
            self.offset_x = world_q_float * self.zoom - canvas_x
            self.offset_y = -world_r_float * self.zoom - canvas_y
        else:  # HEXAGON
            # This logic is more complex and depends on the hex geometry
            wx, wy = self._axial_to_world_pixel(world_q_float, world_r_float)
            self.offset_x = wx - canvas_x
            self.offset_y = wy - canvas_y

        return True

    def canvas_to_world_int(self, cx: int, cy: int) -> Tuple[int, int]:
        """Dispatches to the correct coordinate conversion based on render mode."""
        if self.render_mode == RenderMode.RECTANGLE:
            return self._canvas_to_rect_projection(cx, cy)
        return self._canvas_to_hex_grid(cx, cy)

    def _canvas_to_rect_projection(self, cx: int, cy: int) -> Tuple[int, int]:
        """Converts canvas pixels to (q, r) for a rectangular projection."""
        if self.zoom == 0:
            return 0, 0
        # The renderer maps the q-axis to screen-x and the -r-axis to screen-y.
        # This function must be the mathematical inverse of that projection.
        q = math.floor((cx + self.offset_x) / self.zoom)
        r = -math.floor((cy + self.offset_y) / self.zoom)
        return q, r

    def _hex_round(self, q_f: float, r_f: float) -> Tuple[int, int]:
        """Rounds fractional axial coordinates to the nearest hex integer coordinate."""
        s_f = -q_f - r_f
        q = round(q_f)
        r = round(r_f)
        s = round(s_f)

        q_diff = abs(q - q_f)
        r_diff = abs(r - r_f)
        s_diff = abs(s - s_f)

        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        # No 'else' needed as 's' is derived, we only need to return q and r.

        return int(q), int(r)

    def _canvas_to_hex_grid(self, cx: int, cy: int) -> Tuple[int, int]:
        """Converts canvas coordinates to axial hex grid coordinates."""
        if self.zoom <= 0:
            return 0, 0

        # Pointy-top hex orientation
        size = self.zoom / 2.0
        world_px_x = cx + self.offset_x
        world_px_y = cy + self.offset_y

        # Convert world pixel coordinates to fractional axial coordinates
        q_f = (math.sqrt(3) / 3 * world_px_x - 1 / 3 * world_px_y) / size
        r_f = (2 / 3 * world_px_y) / size

        return self._hex_round(q_f, r_f)

    def canvas_to_world_float(self, cx: int, cy: int) -> Tuple[float, float]:
        """Converts canvas pixel coordinates to precise world (q, r) coords."""
        if self.zoom == 0:
            return 0.0, 0.0

        if self.render_mode == RenderMode.RECTANGLE:
            q = (cx + self.offset_x) / self.zoom
            r = -(cy + self.offset_y) / self.zoom
            return q, r

        # HEXAGON mode
        size = self.zoom / 2.0
        world_px_x = cx + self.offset_x
        world_px_y = cy + self.offset_y
        q_f = (math.sqrt(3) / 3 * world_px_x - 1 / 3 * world_px_y) / size
        r_f = (2 / 3 * world_px_y) / size
        return q_f, r_f

    def _axial_to_world_pixel(self, q: float, r: float) -> Tuple[float, float]:
        """Converts axial coordinates to world pixel coordinates (for hex)."""
        size = self.zoom / 2.0
        world_px_x = size * (math.sqrt(3) * q + math.sqrt(3) / 2 * r)
        world_px_y = size * (3.0 / 2.0 * r)
        return world_px_x, world_px_y

    def get_visible_grid_rect(
        self, canvas_width: int, canvas_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Calculates the integer bounding box of visible tiles in (q, r) world coordinates.
        """
        # This generic approach works for any projection (rect or hex)
        corners = [
            self.canvas_to_world_int(0, 0),
            self.canvas_to_world_int(canvas_width, 0),
            self.canvas_to_world_int(0, canvas_height),
            self.canvas_to_world_int(canvas_width, canvas_height),
        ]
        min_q = min(c[0] for c in corners)
        max_q = max(c[0] for c in corners)
        min_r = min(c[1] for c in corners)
        max_r = max(c[1] for c in corners)
        # Add a buffer for safety, especially for hex tiles that bleed over edges
        return min_q - 1, max_q + 2, min_r - 1, max_r + 2
