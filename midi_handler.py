# midi_handler.py
"""
Handles MIDI output using the pyfluidsynth library, adhering to its
high-level object-oriented API.
"""
import sys
import os
from typing import TYPE_CHECKING

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
        self.synth: fluidsynth_for_typing.Synth | None = None
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

    def program_select(self, program_num: int, channel: int = 0):
        """Changes the instrument for a given channel."""
        if self.is_active and self.synth and self.sfid is not None:
            self.synth.program_select(channel, self.sfid, 0, program_num)

    def note_on(self, pitch: int, velocity: int = 100, channel: int = 0):
        """Sends a Note On message."""
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteon(channel, pitch, velocity)

    def note_off(self, pitch: int, channel: int = 0):
        """Sends a Note Off message."""
        if self.is_active and self.synth and 0 <= pitch <= 127:
            self.synth.noteoff(channel, pitch)

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
