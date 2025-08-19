# note_mapper.py
"""
Handles the mapping from grid coordinates to musical notes (e.g., MIDI).
"""
from typing import Tuple
from config import MusicConfig
import utils
from tuning import JUST_INTONATION


class NoteMapper:
    """
    Translates grid coordinates and octaves into absolute MIDI note numbers.
    """

    def __init__(self):
        self.base_midi = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)
        self.tuning_system = JUST_INTONATION

    def set_tuning_system(self, tuning: dict):
        self.tuning_system = tuning

    def _cents_to_pitch_bend(self, cents: float) -> int:
        """Converts a cent value to a 14-bit MIDI pitch bend value."""
        # A pitch bend range of +/- 2 semitones corresponds to 200 cents.
        # The MIDI value range is 0-16383, with 8192 as the center (no bend).
        bend_range_cents = 200
        # Calculate the bend amount relative to the max range (8191)
        bend = (cents / bend_range_cents) * 8191
        # Add to the center value and ensure it's an integer
        return int(8192 + bend)

    def coord_to_midi(self, coord: Tuple[int, int], octave: int) -> Tuple[int, int]:
        """
        Calculates the MIDI note and pitch bend value for a coordinate.
        """
        base_pitch_midi = utils.coord_to_midi(coord, self.base_midi)
        pitch_class = base_pitch_midi % 12
        midi_note = 12 * (octave + 1) + pitch_class

        # Get the cents deviation from the current tuning system
        cents_deviation = self.tuning_system.get(pitch_class, 0)
        pitch_bend_value = self._cents_to_pitch_bend(cents_deviation)

        return midi_note, pitch_bend_value