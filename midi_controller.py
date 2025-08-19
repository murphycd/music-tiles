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
        midi_note = self.note_mapper.coord_to_midi(event.coord, event.octave)
        self.midi_handler.note_on(midi_note, MidiConfig.DEFAULT_VELOCITY)

    def _on_tile_deselected(self, event: TileDeselectedEvent):
        """Handles tile deselection by sending a MIDI Note Off message."""
        midi_note = self.note_mapper.coord_to_midi(event.coord, event.octave)
        self.midi_handler.note_off(midi_note)

    def _on_tile_octave_changed(self, event: TileOctaveChangedEvent):
        """Handles octave changes by stopping the old note and starting the new one."""
        old_midi = self.note_mapper.coord_to_midi(event.coord, event.old_octave)
        new_midi = self.note_mapper.coord_to_midi(event.coord, event.new_octave)
        self.midi_handler.note_off(old_midi)
        self.midi_handler.note_on(new_midi, MidiConfig.DEFAULT_VELOCITY)

    def _on_selection_cleared(self, event: SelectionClearedEvent):
        """Handles clearing the grid by stopping all previously playing notes."""
        for coord, octave in event.cleared_tiles.items():
            midi_note = self.note_mapper.coord_to_midi(coord, octave)
            self.midi_handler.note_off(midi_note)
