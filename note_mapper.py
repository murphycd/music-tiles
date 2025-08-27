# note_mapper.py
"""
Handles the mapping from grid coordinates to musical notes (e.g., MIDI).
"""
from typing import Tuple
from config import MusicConfig, TuningConfig
import utils


class NoteMapper:
    """
    Translates grid coordinates and octaves into absolute MIDI note numbers.
    """

    def __init__(self):
        self.base_midi = utils.note_to_midi(MusicConfig.ORIGIN_NOTE)
        self.tuning_system = TuningConfig.get_tuning_systems()[
            TuningConfig.DEFAULT_SELECTION_INDEX
        ]

    def set_tuning_system(self, tuning: TuningConfig.TuningSystem):
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

    def coord_to_midi(self, coord: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calculates the MIDI note and pitch bend for a coordinate.
        The octave is determined by the note's position on the grid and
        wrapped within the configured octave bounds.
        """
        absolute_midi = utils.coord_to_midi(coord, self.base_midi)
        final_midi, _octave = utils.get_wrapped_midi_and_octave(absolute_midi)

        # Pitch bend is based on the pitch class of the *unwrapped* note
        pitch_class_for_tuning = absolute_midi % 12
        cents_deviation = self.tuning_system.definition.get(pitch_class_for_tuning, 0)
        pitch_bend_value = self._cents_to_pitch_bend(cents_deviation)

        return final_midi, pitch_bend_value
