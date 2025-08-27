# midi_controller.py
"""
A subscriber that listens to model events and controls MIDI output.
"""
import time
from typing import Tuple
from midi_handler import MidiHandler
from note_mapper import NoteMapper
from config import MidiConfig
from events import (
    ModelEvent,
    TileSelectedEvent,
    TileDeselectedEvent,
    SelectionClearedEvent,
)


class MidiController:
    """
    Listens for events from the TonnetzModel and sends corresponding
    messages to the MidiHandler.
    """

    def __init__(self, midi_handler: MidiHandler, note_mapper: NoteMapper):
        """
        Initializes the controller with its dependencies.

        Args:
            midi_handler: The object responsible for MIDI output.
            note_mapper: The object for converting coordinates to MIDI notes.
        """
        self.midi_handler = midi_handler
        self.note_mapper = note_mapper
        self.active_notes: dict[Tuple[int, int], int] = {}  # coord -> channel
        self.next_channel = 0

    def _get_next_channel(self):
        """Gets the next available MIDI channel, rotating through 0-15."""
        channel = self.next_channel
        self.next_channel = (self.next_channel + 1) % 16
        return channel

    def handle_event(self, event: ModelEvent):
        """Dispatches an event to the appropriate handler method."""
        if isinstance(event, TileSelectedEvent):
            self._on_tile_selected(event)
        elif isinstance(event, TileDeselectedEvent):
            self._on_tile_deselected(event)
        elif isinstance(event, SelectionClearedEvent):
            self._on_selection_cleared(event)

    def _on_tile_selected(self, event: TileSelectedEvent):
        """Handles tile selection by sending a MIDI Note On message."""
        midi_note, pitch_bend = self.note_mapper.coord_to_midi(event.coord)
        print(f"Playing Note: {midi_note}, Pitch Bend: {pitch_bend}")

        channel = self._get_next_channel()
        # Send pitch bend BEFORE note on
        self.midi_handler.pitch_bend(pitch_bend, channel)
        # Optional small delay to ensure messages are processed in order
        time.sleep(0.005)
        self.midi_handler.note_on(midi_note, MidiConfig.DEFAULT_VELOCITY, channel)
        self.active_notes[event.coord] = channel

    def _on_tile_deselected(self, event: TileDeselectedEvent):
        """Handles tile deselection by sending a MIDI Note Off message."""
        if event.coord in self.active_notes:
            channel = self.active_notes.pop(event.coord)
            # We only need the note number to turn it off
            midi_note, _ = self.note_mapper.coord_to_midi(event.coord)
            self.midi_handler.note_off(midi_note, channel)

    def _on_selection_cleared(self, event: SelectionClearedEvent):
        """Handles clearing the grid by stopping all previously playing notes."""
        for coord, channel in self.active_notes.items():
            midi_note, _ = self.note_mapper.coord_to_midi(coord)
            self.midi_handler.note_off(midi_note, channel)
        self.active_notes.clear()
