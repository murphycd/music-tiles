# midi_handler.py
"""
Handles MIDI output using the pyfluidsynth library, adhering to its
high-level object-oriented API.
"""
import sys
import os
from typing import TYPE_CHECKING, Dict, List, Tuple, Optional
from config import TuningConfig

# This block is only processed by type checkers.
# We import 'fluidsynth' with an alias to create a name that will not
# be overwritten at runtime, resolving type checker confusion.
if TYPE_CHECKING:
    import fluidsynth as fluidsynth_for_typing

try:
    import fluidsynth
except ImportError:
    print(
        "pyfluidsynth is not installed. MIDI output will be disabled.", file=sys.stderr
    )
    print("Install it with: pip install pyfluidsynth", file=sys.stderr)
    fluidsynth = None


class MidiHandler:
    """A wrapper for the pyfluidsynth.Synth object."""

    def __init__(self, soundfont_path: str):
        """
        Initializes the FluidSynth synthesizer using the high-level Synth API.
        """
        # The type hint uses the aliased name inside a string literal.
        # This is unambiguous and works for both runtime and type checking.
        self.synth: "fluidsynth_for_typing.Synth | None" = None
        self.sfid: int | None = None
        self.is_active = False
        # self.midi.out = None
        self.instrument_list: Dict[str, int] = {}
        self.available_channels:List[int] = [ch for ch in range(16) if ch != 9] #uses channels 0-8, and 10-15 avoiding 9 for "percussion"
        self.active_note: Dict[Tuple, Tuple[int, int]] = {} #tacks which note_id is playing on which channel and it's pitch
        
        if fluidsynth is None:
            return

        if not os.path.exists(soundfont_path):
            print(
                f"SoundFont file not found at '{soundfont_path}'. "
                "MIDI output will be disabled.",
                file=sys.stderr,
            )
            return

        try:
            # Use local variables for initialization; only assign to self on success.
            # 1. Create the Synth object.
            synth = fluidsynth.Synth()

            # 2. Start the audio driver.
            synth.start()

            # 3. Load the SoundFont.
            sfid = synth.sfload(soundfont_path)

            # 4. Assign to instance attributes now that setup is complete.
            self.synth = synth
            self.sfid = sfid
            self.is_active = True
            print(f"FluidSynth initialized with SoundFont: {soundfont_path}")

        except Exception as e:
            print(f"Failed to initialize FluidSynth: {e}", file=sys.stderr)
            # self.synth remains None and self.is_active remains False.

    def get_instruments(self, bank: int = 0) -> dict[str, int]:
        """
        Retrieves instruments by iterating through possible preset numbers
        and querying for their names, using the public sfpreset_name() method.

        Args:
            bank: The instrument bank to scan (0 is standard for GM).

        Returns:
            A dictionary mapping formatted instrument names to their program numbers.
        """
        if not self.is_active or self.sfid is None or self.synth is None:
            return {}

        instruments = {}
        # General MIDI standard has 128 presets (0-127). We can probe each one.
        for preset_num in range(128):
            preset_name = self.synth.sfpreset_name(self.sfid, bank, preset_num)

            # A non-None return value indicates a valid instrument preset.
            if preset_name:
                formatted_name = f"{preset_num:03d}: {preset_name}"
                instruments[formatted_name] = preset_num

        return instruments

    def program_select(self, program_num: int):
        """Changes the instrument for a given channel."""
        if self.is_active and self.synth and self.sfid is not None:
            for ch in range(16):
                self.synth.program_select(ch, self.sfid, 0, program_num)

    def _cents_to_pitch_bend(self, cents: float) -> int:
        bend_fraction = cents / (TuningConfig.PITCH_BEND_RANGE_SEMITONES * 100)
        bend_value = round(8192 + bend_fraction * 8191)
        return max(0, min(16383, bend_value))
    
      # NEW: The primary method for playing a tuned note.
    def play_tuned_note(self, note_id: Tuple, midi_note: int, cents: float, velocity: int):
        """Plays a note with a specific tuning on an available channel."""
        if not self.is_active or not self.synth or not self.available_channels:
            print("Warning: No available MIDI channels to play note.", file=sys.stderr)
            return

        if note_id in self.active_notes:
            return  # Note is already playing

        channel = self.available_channels.pop(0)
        self.active_notes[note_id] = (channel, midi_note)

        # 1. Send Pitch Bend message for the channel.
        # The pyfluidsynth library exposes this as synth.pitch_bend().
        pitch_bend_val = self._cents_to_pitch_bend(cents)
        self.synth.pitch_bend(channel, pitch_bend_val)
        
        # 2. Send Note On message on the same channel.
        self.synth.noteon(channel, midi_note, velocity)

    def note_off(self, note_id: Tuple):
        """Stops a note based on its unique ID and frees its channel."""
        if not self.is_active or not self.synth or note_id not in self.active_notes:
            return
            
        channel, pitch = self.active_notes.pop(note_id)

        # 1. Send Note Off message.
        self.synth.noteoff(channel, pitch)
        
        # 2. Reset pitch bend on the channel (good practice).
        self.synth.pitch_bend(channel, 8192)
        
        # 3. Return the channel to the pool.
        self.available_channels.append(channel)
        self.available_channels.sort()

    def close(self):
        """
        Stops all sounding notes and closes the synthesizer.
        """
        if self.is_active and self.synth:
            # Turn off all currently playing notes before shutting down.
            for note_id in list(self.active_notes.keys()):
                self.note_off(note_id)
            
            self.synth.delete()
            self.synth = None
            self.is_active = False
            print("FluidSynth terminated.")
