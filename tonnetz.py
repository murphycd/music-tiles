# tonnetz.py
"""
Manages the application's data model, including tile selection and music theory.
"""
from typing import Tuple, Dict, Optional, List, Any
from config import MusicConfig, OctaveConfig
import utils
from events import (
    TileSelectedEvent,
    TileDeselectedEvent,
    TileOctaveChangedEvent,
    SelectionClearedEvent,
    ModelEvent,
)


class TonnetzModel:
    """
    Holds the state of the musical grid and notifies listeners of changes.
    """

    def __init__(self):
        # Maps selected (q, r) coordinates to their octave
        self.selected_tiles: Dict[Tuple[int, int], int] = {}
        self.pitch_class_cache: dict[Tuple[int, int], str] = {}
        self.base_midi_for_naming = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)
        self.use_sharps: bool = MusicConfig.DEFAULT_USE_SHARPS
        self.listeners: List[Any] = []

    def add_listener(self, listener: Any):
        """Adds a listener to be notified of model changes."""
        if listener not in self.listeners:
            self.listeners.append(listener)

    def _notify(self, event: ModelEvent):
        """Notifies all registered listeners of an event."""
        for listener in self.listeners:
            # Assumes listeners have a 'handle_event' method.
            if hasattr(listener, "handle_event"):
                listener.handle_event(event)

    def set_enharmonic_preference(self, use_sharps: bool):
        """Sets the global preference for displaying sharp or flat notes."""
        if self.use_sharps != use_sharps:
            self.use_sharps = use_sharps
            self.pitch_class_cache.clear()

    def is_selected(self, coord: Tuple[int, int]) -> bool:
        """Checks if a tile at a given coordinate is selected."""
        return coord in self.selected_tiles

    def get_octave(self, coord: Tuple[int, int]) -> Optional[int]:
        """Returns the octave for a selected coordinate."""
        return self.selected_tiles.get(coord)

    def toggle_selection(self, coord: Tuple[int, int], initial_octave: int):
        """Toggles the selection state of a coordinate and notifies listeners."""
        if self.is_selected(coord):
            old_octave = self.selected_tiles.pop(coord)
            self._notify(TileDeselectedEvent(coord=coord, octave=old_octave))
        else:
            self.selected_tiles[coord] = initial_octave
            self._notify(TileSelectedEvent(coord=coord, octave=initial_octave))

    def clear_selection(self):
        """Clears the entire selection and notifies listeners."""
        if not self.selected_tiles:
            return
        cleared_tiles_copy = self.selected_tiles.copy()
        self.selected_tiles.clear()
        self._notify(SelectionClearedEvent(cleared_tiles=cleared_tiles_copy))

    def increment_octave(self, coord: Tuple[int, int]) -> Optional[int]:
        """
        Increments a selected tile's octave and notifies listeners.
        Returns the new octave, or None if the tile was not selected.
        """
        if not self.is_selected(coord):
            return None

        current_octave = self.selected_tiles[coord]
        min_o, max_o = OctaveConfig.MIN_OCTAVE, OctaveConfig.MAX_OCTAVE
        span = max_o - min_o + 1
        new_octave = (current_octave - min_o + 1) % span + min_o
        self.selected_tiles[coord] = new_octave
        self._notify(
            TileOctaveChangedEvent(
                coord=coord, old_octave=current_octave, new_octave=new_octave
            )
        )
        return new_octave

    def get_display_note_for_coord(self, coord: Tuple[int, int]) -> str:
        """
        Gets the note name for display. Includes octave only if selected.
        """
        pitch_class = self._get_pitch_class(coord)
        if self.is_selected(coord):
            octave = self.get_octave(coord)
            return f"{pitch_class}{octave}"
        return pitch_class

    def _get_pitch_class(self, coord: Tuple[int, int]) -> str:
        """Calculates and caches the pitch class name for a coordinate."""
        if coord in self.pitch_class_cache:
            return self.pitch_class_cache[coord]

        midi = utils.coord_to_midi(coord, self.base_midi_for_naming)
        pitch_class = utils.midi_to_pitch_class_name(midi, self.use_sharps)

        self.pitch_class_cache[coord] = pitch_class
        return pitch_class

    def set_selection(self, new_selection: Dict[Tuple[int, int], int]):
        """
        Efficiently updates the selection to a new state, firing events only
        for the tiles that changed.

        Args:
            new_selection: A dictionary of {coord: octave} for the new state.
        """
        current_coords = set(self.selected_tiles.keys())
        new_coords = set(new_selection.keys())

        coords_to_deselect = current_coords - new_coords
        coords_to_select = new_coords - current_coords

        # Fire deselection events first
        for coord in coords_to_deselect:
            octave = self.selected_tiles.pop(coord)
            self._notify(TileDeselectedEvent(coord=coord, octave=octave))

        # Fire selection events
        for coord in coords_to_select:
            octave = new_selection[coord]
            self.selected_tiles[coord] = octave
            self._notify(TileSelectedEvent(coord=coord, octave=octave))