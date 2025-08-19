# midi_handler.py
"""
Handles MIDI output using pygame.midi.
"""
import sys

try:
    import pygame.midi
except ImportError:
    print("Pygame is not installed. MIDI output will be disabled.", file=sys.stderr)
    print("Install it with: pip install pygame", file=sys.stderr)
    pygame = None


class MidiHandler:
    """A wrapper for pygame.midi to handle note on/off messages."""

    def __init__(self):
        """Initializes pygame.midi and opens a connection to an output device."""
        self.midi_out = None
        if pygame is None:
            return

        try:
            pygame.midi.init()
            device_id = pygame.midi.get_default_output_id()

            if device_id == -1:
                print("No default MIDI output device found.", file=sys.stderr)
                # On some systems, we might need to search for the first output device.
                for i in range(pygame.midi.get_count()):
                    info = pygame.midi.get_device_info(i)
                    if info and info[3] == 1:  # type: ignore
                        device_id = i
                        break

            if device_id != -1:
                self.midi_out = pygame.midi.Output(device_id)
                print(f"MIDI output enabled on device ID {device_id}.")
            else:
                print(
                    "MIDI output disabled: No output device available.", file=sys.stderr
                )

        except Exception as e:
            print(f"Failed to initialize MIDI: {e}", file=sys.stderr)
            self.midi_out = None

    def note_on(self, pitch: int, velocity: int = 100):
        """Sends a MIDI Note On message."""
        if self.midi_out and 0 <= pitch <= 127:
            self.midi_out.note_on(pitch, velocity)

    def note_off(self, pitch: int, velocity: int = 0):
        """Sends a MIDI Note Off message."""
        if self.midi_out and 0 <= pitch <= 127:
            self.midi_out.note_off(pitch, velocity)

    def close(self):
        """Closes the MIDI connection and cleans up resources."""
        if self.midi_out:
            del self.midi_out
        if pygame and pygame.midi.get_init():
            pygame.midi.quit()
