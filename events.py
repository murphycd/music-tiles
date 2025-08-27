# events.py
"""
Defines event data classes for the publish/subscribe system.
"""
from dataclasses import dataclass
from typing import Tuple, Set


@dataclass
class ModelEvent:
    """Base class for all model events."""


@dataclass
class TileSelectedEvent(ModelEvent):
    """Fired when a tile is selected."""

    coord: Tuple[int, int]


@dataclass
class TileDeselectedEvent(ModelEvent):
    """Fired when a tile is deselected."""

    coord: Tuple[int, int]


@dataclass
class SelectionClearedEvent(ModelEvent):
    """Fired when the entire selection is cleared."""

    # A copy of the coordinates that were cleared.
    cleared_coords: Set[Tuple[int, int]]
