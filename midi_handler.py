# midi_handler.py
"""
Handles MIDI output using the pyfluidsynth library, adhering to its
high-level object-oriented API.
"""
import sys
import os
from typing import TYPE_CHECKING, Optional

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

    def __init__(self, soundfont_path: str, audio_driver: Optional[str] = None):
        """
        Initializes the FluidSynth synthesizer using the high-level Synth API.

         Args:
            soundfont_path: Path to the .sf2 or .sf3 SoundFont file.
            audio_driver: The audio driver for FluidSynth to use (e.g., 'dsound')
        """
        # The type hint uses the aliased name inside a string literal.
        # This is unambiguous and works for both runtime and type checking.
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
            
            # 1. Create the Synth object.
            synth = fluidsynth.Synth()

            # 2. Start the audio driver.
            synth.start(driver=audio_driver)

            # 3. Load the SoundFont.
            sfid = synth.sfload(soundfont_path)

            # 4. Assign to instance attributes now that setup is complete.
            self.synth = synth
            self.sfid = sfid
            self.is_active = True
            self._set_pitch_bend_range()
            print(f"FluidSynth initialized with SoundFont: {soundfont_path}") 

        except Exception as e:
            print(f"Failed to initialize FluidSynth: {e}", file=sys.stderr)
            # self.synth remains None and self.is_active remains False.

    def _set_pitch_bend_range(self, semitones: int = 2):
        """
        Sets the pitch bend range for all channels using RPN messages.
        This is crucial for ensuring the synthesizer interprets pitch bend
        values correctly.

        Args:
            semitones: The desired pitch bend range in semitones (+/-).
        """
        if not self.is_active or not self.synth:
            return
            
        # RPN messages are sent via cc (control change) messages.
        # RPN for Pitch Bend Sensitivity is (0, 0).
        for channel in range(16):
            # Select the Pitch Bend Sensitivity RPN
            self.synth.cc(channel, 101, 0)  # RPN MSB
            self.synth.cc(channel, 100, 0)  # RPN LSB
            
            # Set the new value (semitones)
            self.synth.cc(channel, 6, semitones) # Data Entry MSB
            
            # Optional: for finer control (cents)
            self.synth.cc(channel, 38, 0) # Data Entry LSB
            
            # Deselect the RPN so subsequent cc messages are not misinterpreted
            self.synth.cc(channel, 101, 127)
            self.synth.cc(channel, 100, 127)
            
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
        """Changes the instrument for all 16 channels."""
        if self.is_active and self.synth and self.sfid is not None:
            for channel in range(16):
                self.synth.program_select(channel, self.sfid, 0, program_num)

    def note_on(self, pitch: int, velocity: int = 127, channel: int = 0):
        """Sends a Note On message."""
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteon(channel, pitch, velocity)

    def note_off(self, pitch: int, channel: int = 0):
        """Sends a Note Off message."""
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteoff(channel, pitch)
    
    def pitch_bend(self, value: int, channel: int = 0):
        """sends a pitch bend message"""
        if self.is_active and self.synth:
            self.synth.pitch_bend(channel, value)
    
    def close(self):
        """
        Closes the synthesizer and cleans up resources by calling the
        Synth object's delete() method as shown in the documentation.
        """
        if self.is_active and self.synth:
            self.synth.delete()
            self.synth = None
            self.is_active = False
            print("FluidSynth terminated.")
    
    