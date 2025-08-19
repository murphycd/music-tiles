# tonnetz.py
"""
Manages the application's data model, including tile selection and music theory.
"""
from typing import Tuple, Dict, Optional
from config import MusicConfig, OctaveConfig
import utils


class TonnetzModel:
    """Holds the state and logic of the musical grid, independent of the UI."""

    def __init__(self):
        # Maps selected (row, col) coordinates to their octave
        self.selected_tiles: Dict[Tuple[int, int], int] = {}
        self.pitch_class_cache: dict[Tuple[int, int], str] = {}
        self.base_midi = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)
        self.use_sharps: bool = MusicConfig.DEFAULT_USE_SHARPS

    def set_enharmonic_preference(self, use_sharps: bool):
        """Sets the global preference for displaying sharp or flat notes."""
        if self.use_sharps != use_sharps:
            self.use_sharps = use_sharps
            # Invalidate the cache since note names will change
            self.pitch_class_cache.clear()

    def is_selected(self, coord: Tuple[int, int]) -> bool:
        """Checks if a tile at a given coordinate is selected."""
        return coord in self.selected_tiles

    def get_octave(self, coord: Tuple[int, int]) -> Optional[int]:
        """Returns the octave for a selected coordinate."""
        return self.selected_tiles.get(coord)

    def toggle_selection(self, coord: Tuple[int, int], initial_octave: int):
        """Toggles the selection state of a coordinate."""
        if self.is_selected(coord):
            self.selected_tiles.pop(coord)
        else:
            self.selected_tiles[coord] = initial_octave

    def clear_selection(self):
        """Clears the entire selection."""
        self.selected_tiles.clear()

    def increment_octave(self, coord: Tuple[int, int]) -> Optional[int]:
        """
        Increments a selected tile's octave, cycling between min and max.
        Returns the new octave, or None if the tile was not selected.
        """
        if not self.is_selected(coord):
            return None

        current_octave = self.selected_tiles[coord]
        min_o, max_o = OctaveConfig.MIN_OCTAVE, OctaveConfig.MAX_OCTAVE
        span = max_o - min_o + 1
        new_octave = (current_octave - min_o + 1) % span + min_o
        self.selected_tiles[coord] = new_octave
        return new_octave

    def get_midi_note_for_coord(self, coord: Tuple[int, int], octave: int) -> int:
        """
        Calculates the absolute MIDI note number for a coordinate at a specific octave.
        """
        # Get the MIDI note number for the pitch class, relative to the grid's origin.
        base_pitch_midi = utils.coord_to_midi(coord, self.base_midi)

        # Extract the pitch class (0-11) from that base note.
        pitch_class = base_pitch_midi % 12

        # Calculate the final MIDI note using the desired octave.
        # MIDI formula: 12 * (octave + 1) + pitch_class
        return 12 * (octave + 1) + pitch_class

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

        midi = utils.coord_to_midi(coord, self.base_midi)
        pitch_class = utils.midi_to_pitch_class_name(midi, self.use_sharps)

        self.pitch_class_cache[coord] = pitch_class
        return pitch_class
