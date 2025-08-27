# tonnetz.py
"""
Manages the application's data model, including tile selection and music theory.
"""
from typing import Tuple, Set, List, Any
from config import MusicConfig
import utils
from events import (
    TileSelectedEvent,
    TileDeselectedEvent,
    SelectionClearedEvent,
    ModelEvent,
)


class TonnetzModel:
    """
    Holds the state of the musical grid and notifies listeners of changes.
    """

    def __init__(self):
        # A set of selected (q, r) coordinates
        self.selected_tiles: Set[Tuple[int, int]] = set()
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

    def get_octave(self, coord: Tuple[int, int]) -> int:
        """Calculates and returns the octave for a given coordinate."""
        absolute_midi = utils.coord_to_midi(coord, self.base_midi_for_naming)
        _final_midi, final_octave = utils.get_wrapped_midi_and_octave(absolute_midi)
        return final_octave

    def toggle_selection(self, coord: Tuple[int, int]):
        """Toggles the selection state of a coordinate and notifies listeners."""
        if self.is_selected(coord):
            self.selected_tiles.remove(coord)
            self._notify(TileDeselectedEvent(coord=coord))
        else:
            self.selected_tiles.add(coord)
            self._notify(TileSelectedEvent(coord=coord))

    def clear_selection(self):
        """Clears the entire selection and notifies listeners."""
        if not self.selected_tiles:
            return
        cleared_coords_copy = self.selected_tiles.copy()
        self.selected_tiles.clear()
        self._notify(SelectionClearedEvent(cleared_coords=cleared_coords_copy))

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

    def set_selection(self, new_selection: Set[Tuple[int, int]]):
        """
        Efficiently updates the selection to a new state, firing events only
        for the tiles that changed.

        Args:
            new_selection: A set of {coord} for the new state.
        """
        old_selection = self.selected_tiles
        if new_selection == old_selection:
            return

        to_remove = old_selection - new_selection
        to_add = new_selection - old_selection

        # The model state must be updated before notifications are sent,
        # so listeners can query the new state if needed.
        self.selected_tiles = new_selection

        for coord in to_remove:
            self._notify(TileDeselectedEvent(coord=coord))
        for coord in to_add:
            self._notify(TileSelectedEvent(coord=coord))
