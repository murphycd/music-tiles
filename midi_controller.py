# midi_controller.py
"""
A subscriber that listens to model events and controls MIDI output.
"""
from midi_handler import MidiHandler
from note_mapper import NoteMapper
from config import MidiConfig
from events import (
    ModelEvent,
    TileSelectedEvent,
    TileDeselectedEvent,
    TileOctaveChangedEvent,
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
        self.active_notes = {} # To store which note is on which channel
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
        elif isinstance(event, TileOctaveChangedEvent):
            self._on_tile_octave_changed(event)
        elif isinstance(event, SelectionClearedEvent):
            self._on_selection_cleared(event)

    def _on_tile_selected(self, event: TileSelectedEvent):
        """Handles tile selection by sending a MIDI Note On message."""
        midi_note, pitch_bend = self.note_mapper.coord_to_midi(event.coord, event.octave)
        channel = self._get_next_channel()
        self.midi_handler.pitch_bend(pitch_bend, channel)
        self.midi_handler.note_on(midi_note, MidiConfig.DEFAULT_VELOCITY, channel)
        self.active_notes[(event.coord, event.octave)] = channel

    def _on_tile_deselected(self, event: TileDeselectedEvent):
        """Handles tile deselection by sending a MIDI Note Off message."""
        if (event.coord, event.octave) in self.active_notes:
            channel = self.active_notes.pop((event.coord, event.octave))
            midi_note, _ = self.note_mapper.coord_to_midi(event.coord, event.octave)
            self.midi_handler.note_off(midi_note, channel)

    def _on_tile_octave_changed(self, event: TileOctaveChangedEvent):
        """Handles octave changes by stopping the old note and starting the new one."""
        # Turn off the old note
        if (event.coord, event.old_octave) in self.active_notes:
            channel = self.active_notes.pop((event.coord, event.old_octave))
            old_midi, _ = self.note_mapper.coord_to_midi(event.coord, event.old_octave)
            self.midi_handler.note_off(old_midi, channel)

        # Turn on the new note
        new_midi, pitch_bend = self.note_mapper.coord_to_midi(event.coord, event.new_octave)
        new_channel = self._get_next_channel()
        self.midi_handler.pitch_bend(pitch_bend, new_channel)
        self.midi_handler.note_on(new_midi, MidiConfig.DEFAULT_VELOCITY, new_channel)
        self.active_notes[(event.coord, event.new_octave)] = new_channel

    def _on_selection_cleared(self, event: SelectionClearedEvent):
        """Handles clearing the grid by stopping all previously playing notes."""
        for (coord, octave), channel in self.active_notes.items():
            midi_note, _ = self.note_mapper.coord_to_midi(coord, octave)
            self.midi_handler.note_off(midi_note, channel)
        self.active_notes.clear()
