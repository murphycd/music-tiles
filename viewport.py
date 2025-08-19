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
        """Dispatches to the correct coordinate conversion based on render mode."""
        if self.render_mode == RenderMode.RECTANGLE:
            return self._canvas_to_rect_grid(cx, cy)
        return self._canvas_to_hex_grid(cx, cy)

    def _canvas_to_rect_grid(self, cx: int, cy: int) -> Tuple[int, int]:
        """Converts canvas pixel coordinates to integer world tile coordinates."""
        world_y, world_x = self.canvas_to_world_float(cx, cy)
        return math.floor(world_y), math.floor(world_x)

    def _canvas_to_hex_grid(self, cx: int, cy: int) -> Tuple[int, int]:
        """Converts canvas coordinates to a staggered hex grid coordinate."""
        hex_height = self.zoom
        if hex_height <= 0:
            return 0, 0
        hex_width = (math.sqrt(3) / 2) * hex_height
        if hex_width <= 0:
            return 0, 0

        # Convert canvas coordinates to "world pixel" coordinates, which is the
        # space in which tile centers are calculated before the viewport offset.
        world_px_x = cx + self.offset_x
        world_px_y = cy + self.offset_y

        # Roughly estimate the grid coordinates (r, c) by inverting the
        # rendering formulas.
        r_est = world_px_y / (hex_height * 0.75)
        r_round = int(round(r_est))

        x_destagger = world_px_x - ((r_round & 1) * (hex_width / 2))
        c_est = x_destagger / hex_width
        c_round = int(round(c_est))

        # The initial estimate can be inaccurate near tile borders. To find the
        # true closest tile, check the estimate and its six neighbors.
        min_dist_sq = float("inf")
        best_coord = (r_round, c_round)

        # Define neighbor offsets for the "odd-q" vertical layout.
        if r_round & 1:  # Odd row
            neighbor_offsets = [(0, 1), (0, -1), (-1, -1), (-1, 0), (1, -1), (1, 0)]
        else:  # Even row
            neighbor_offsets = [(0, 1), (0, -1), (-1, 0), (-1, 1), (1, 0), (1, 1)]

        # The list of candidates includes the initial estimate and all its neighbors.
        candidate_coords = [(r_round, c_round)]
        for dr, dc in neighbor_offsets:
            candidate_coords.append((r_round + dr, c_round + dc))

        for r_cand, c_cand in candidate_coords:
            # Calculate the center of the candidate hex in world pixel coordinates.
            center_y = r_cand * hex_height * 0.75
            center_x = c_cand * hex_width + ((r_cand & 1) * (hex_width / 2))

            # Find the squared distance between the click point and the candidate's center.
            # All coordinates are now in the same "world pixel" system.
            dist_sq = (world_px_x - center_x) ** 2 + (world_px_y - center_y) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_coord = (r_cand, c_cand)

        return best_coord

    def canvas_to_world_float(self, cx: int, cy: int) -> Tuple[float, float]:
        """Converts canvas pixel coordinates to precise world coordinates."""
        if self.zoom == 0:
            return 0.0, 0.0
        return (cy + self.offset_y) / self.zoom, (cx + self.offset_x) / self.zoom

    def get_visible_grid_rect(
        self, canvas_width: int, canvas_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Calculates the integer bounding box of visible tiles in world coordinates.
        Returns (min_row, max_row, min_col, max_col).
        """
        # For hex grids, this bounding box will be slightly larger than necessary,
        # but it correctly covers all potentially visible tiles.
        if self.render_mode == RenderMode.RECTANGLE:
            start_row, start_col = self.canvas_to_world_int(0, 0)
            end_row, end_col = self.canvas_to_world_int(canvas_width, canvas_height)
            return start_row, end_row + 1, start_col, end_col + 1

        # For hex grid, we need a slightly larger buffer for the staggered shape
        start_row, start_col = self._canvas_to_rect_grid(0, 0)
        end_row, end_col = self._canvas_to_rect_grid(canvas_width, canvas_height)
        return start_row - 1, end_row + 2, start_col - 1, end_col + 2
