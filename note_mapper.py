# note_mapper.py
"""
Handles the mapping from grid coordinates to musical notes (e.g., MIDI).
"""
from typing import Tuple
from config import MusicConfig
import utils
from tuning import JUST_INTONATION
#from tuning import EQUAL_TEMPERAMENT
#from tuning import MEANTONE_TUNING
#from tuning import PYTHAGOREAN_TUNING


class NoteMapper:
    """
    Translates grid coordinates and octaves into absolute MIDI note numbers.
    This class decouples the musical theory logic from the grid data model.
    """

    def __init__(self):
        """Initializes the mapper with a base MIDI note from the configuration."""
        self.base_midi = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)
        self.tuning_system = JUST_INTONATION

    def set_tuning_system(self, tuning: dict):
        """Sets the active tuning system."""
        self.tuning_system = tuning

    def _cents_to_pitch_bend(self, cents: float) -> int:
        """Converts a cent value to a 14-bit MIDI pitch bend value."""
        # Assuming a pitch bend range of +/- 2 semitones (400 cents total)
        # The range of the pitch bend value is -8191 to 8191
        bend_range_cents = 200
        bend = (cents / bend_range_cents) * 8191
        return int(8192 + bend)    

    def coord_to_midi(self, coord: Tuple[int, int], octave: int) -> Tuple[int, int]:
        """
        Calculates the absolute MIDI note number for a coordinate at a specific octave.

        Args:
            coord: The (q, r) coordinate on the grid.
            octave: The target octave for the note.

        Returns:
            a tuple containing the MIDI note number and the pitch bend value - or deviation from 12-TET
        """
        # Get the MIDI note number for the pitch class, relative to the grid's origin.
        base_pitch_midi = utils.coord_to_midi(coord, self.base_midi)

        # Extract the pitch class (0-11) from that base note.
        pitch_class = base_pitch_midi % 12

        # Calculate the final MIDI note using the desired octave.
        # MIDI formula: 12 * (octave + 1) + pitch_class
        midi_note = 12 * (octave + 1) + pitch_class

        # Get the cents deviation from the tuning system
        cents_deviation = self.tuning_system.get(pitch_class, 0)
        pitch_bend_value = self._cents_to_pitch_bend(cents_deviation)

        return midi_note, pitch_bend_value
