# events.py
"""
Defines event data classes for the publish/subscribe system.
"""
from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass
class ModelEvent:
    """Base class for all model events."""


@dataclass
class TileSelectedEvent(ModelEvent):
    """Fired when a tile is selected."""

    coord: Tuple[int, int]
    octave: int


@dataclass
class TileDeselectedEvent(ModelEvent):
    """Fired when a tile is deselected."""

    coord: Tuple[int, int]
    octave: int


@dataclass
class TileOctaveChangedEvent(ModelEvent):
    """Fired when a selected tile's octave is changed."""

    coord: Tuple[int, int]
    old_octave: int
    new_octave: int


@dataclass
class SelectionClearedEvent(ModelEvent):
    """Fired when the entire selection is cleared."""

    # A copy of the tiles that were cleared, mapping coord to octave.
    cleared_tiles: Dict[Tuple[int, int], int]
