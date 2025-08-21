# game_controller.py
"""
Manages the Game of Life simulation - handels the timing and
updating the tonnetz model.
"""
import tkinter as tk 
from typing import Optional, TYPE_CHECKING

from tonnetz import TonnetzModel
from game_of_life import GameOfLifeLogic

if TYPE_CHECKING:
    from __main__ import App

class GameOfLifeController:
    """Handeling of the Game of Life simulation."""

    def __init__(self, model: TonnetzModel, app: 'App'):
        """
        Initializes the controller

        Args:
            model: The main TonnetzModel to be updated.
            root: The Tkinter root window, used for scheduling updates.
        """
        self.model = model
        self.app = app
        self.root = app.root 
        self.is_running = False
        self.tick_interval_ms = 2000  # Default interval: 2000ms (4 beats @ 120 BPM)
        self._job_id: Optional[str] = None

    def start(self):
        """Starts the simulation loop."""
        if not self.is_running:
            self.is_running = True
            self._tick()
            print("Game of Life started.")

    def stop(self):
        """Stops the simulation loop."""
        if self.is_running:
            self.is_running = False
            if self._job_id:
                self.root.after_cancel(self._job_id)
                self._job_id = None
            print("Game of Life stopped.")

    def step(self):
        """Advances the simulation by a single step. Does not start the loop."""
        if not self.is_running:
            self._calculate_and_apply_next_generation()
            print("Game of Life advanced one step.")

    def set_tick_interval(self, interval_ms: int):
        """Sets the time between simulation ticks."""
        self.tick_interval_ms = max(50, interval_ms) # Enforce a minimum delay
        print(f"Game of Life interval set to {self.tick_interval_ms}ms.")

    def _tick(self):
        """The main simulation loop logic."""
        if not self.is_running:
            return

        self._calculate_and_apply_next_generation()

        # Schedule the next tick
        self._calculate_and_apply_next_generation()
        self._job_id = self.root.after(self.tick_interval_ms, self._tick)

    def _calculate_and_apply_next_generation(self):
        """Gets the current state, calculates the next, and updates the model."""
        current_live_cells = set(self.model.selected_tiles.keys())
        next_gen_cells = GameOfLifeLogic.get_next_generation(current_live_cells)

        # Preserve the octaves of the cells that survive TODO: maybe don't do this? the longer a note survives the higher it gets?
        next_selection = {
            coord: self.model.selected_tiles.get(coord, self.app.global_octave)
            for coord in next_gen_cells
        }

        self.model.set_selection(next_selection)