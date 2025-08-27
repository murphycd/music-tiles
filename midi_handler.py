# midi_handler.py
"""
Handles MIDI output using the pyfluidsynth library, adhering to its
high-level object-oriented API.
"""
import sys
import os
from typing import TYPE_CHECKING, Optional

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

    def __init__(self, soundfont_path: str, audio_driver: Optional[str] = None):
        self.synth: "fluidsynth_for_typing.Synth | None" = None
        self.sfid: int | None = None
        self.is_active = False

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
            synth = fluidsynth.Synth()
            synth.start(driver=audio_driver)
            sfid = synth.sfload(soundfont_path)

            self.synth = synth
            self.sfid = sfid
            self.is_active = True
            
            self._set_pitch_bend_range(semitones=2)

            print(f"FluidSynth initialized with SoundFont: {soundfont_path}")

        except Exception as e:
            print(f"Failed to initialize FluidSynth: {e}", file=sys.stderr)

    def _set_pitch_bend_range(self, semitones: int):
        """Sets the pitch bend sensitivity for all channels using RPN messages."""
        if not self.is_active or not self.synth:
            return
        
        for channel in range(16):
            # Select the Pitch Bend Sensitivity RPN
            self.synth.cc(channel, 101, 0)  # RPN MSB
            self.synth.cc(channel, 100, 0)  # RPN LSB
            # Set the new value (semitones)
            self.synth.cc(channel, 6, semitones)
            # Deselect the RPN
            self.synth.cc(channel, 101, 127)
            self.synth.cc(channel, 100, 127)
        print(f"Pitch bend range set to +/- {semitones} semitones for all channels.")

    def get_instruments(self, bank: int = 0) -> dict[str, int]:
        if not self.is_active or self.sfid is None or self.synth is None:
            return {}
        instruments = {}
        for preset_num in range(128):
            preset_name = self.synth.sfpreset_name(self.sfid, bank, preset_num)
            if preset_name:
                formatted_name = f"{preset_num:03d}: {preset_name}"
                instruments[formatted_name] = preset_num
        return instruments

    def program_select(self, program_num: int):
        if self.is_active and self.synth and self.sfid is not None:
            for channel in range(16):
                self.synth.program_select(channel, self.sfid, 0, program_num)

    def note_on(self, pitch: int, velocity: int = 127, channel: int = 0):
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteon(channel, pitch, velocity)

    def note_off(self, pitch: int, channel: int = 0):
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteoff(channel, pitch)
    
    def pitch_bend(self, value: int, channel: int = 0):
        """Sends a pitch bend message."""
        if self.is_active and self.synth:
            self.synth.pitch_bend(channel, value)
    
    def close(self):
        if self.is_active and self.synth:
            self.synth.delete()
            self.synth = None
            self.is_active = False
            print("FluidSynth terminated.")