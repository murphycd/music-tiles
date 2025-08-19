# note_mapper.py
"""
Handles the mapping from grid coordinates to musical notes (e.g., MIDI).
"""
from typing import Tuple
from config import MusicConfig
import utils


class NoteMapper:
    """
    Translates grid coordinates and octaves into absolute MIDI note numbers.
    This class decouples the musical theory logic from the grid data model.
    """

    def __init__(self):
        """Initializes the mapper with a base MIDI note from the configuration."""
        self.base_midi = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)

    def coord_to_midi(self, coord: Tuple[int, int], octave: int) -> int:
        """
        Calculates the absolute MIDI note number for a coordinate at a specific octave.

        Args:
            coord: The (q, r) coordinate on the grid.
            octave: The target octave for the note.

        Returns:
            The absolute MIDI note number.
        """
        # Get the MIDI note number for the pitch class, relative to the grid's origin.
        base_pitch_midi = utils.coord_to_midi(coord, self.base_midi)

        # Extract the pitch class (0-11) from that base note.
        pitch_class = base_pitch_midi % 12

        # Calculate the final MIDI note using the desired octave.
        # MIDI formula: 12 * (octave + 1) + pitch_class
        return 12 * (octave + 1) + pitch_class
