# game_of_life.py
"""
Contains the core, stateless logic for Conway's Game of Life.
"""
from typing import Set, Tuple
from collections import Counter


class GameOfLifeLogic:
    """a collection of static methods to apply the rules of the game"""

    @staticmethod
    def get_neighbors(coord: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """
        Gets all 8 neighbors for a given coordinate
        This assumes a standard rectangular grid layout for neighbors

        TODO: different logic for 3x3 grid and hexagional grid?
        """
        q, r = coord
        return {
            (q - 1, r + 1), (q, r + 1), (q + 1, r + 1),
            (q - 1, r),                 (q + 1, r),
            (q - 1, r - 1), (q, r - 1), (q + 1, r - 1),
        }

    @staticmethod
    def get_next_generation(live_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """
        Calculates the next state of the grid

        Args:
            live_cells: A set of (q, r) coordinates for the currently live cells.

        Returns:
            A new set of (q, r) coordinates for the cells that will be alive
            in the next generation.
        """
        if not live_cells:
            return set()

        # Count the number of live neighbors for all relevant cells
        neighbor_counts = Counter(
            neighbor for cell in live_cells for neighbor in GameOfLifeLogic.get_neighbors(cell)
        )

        next_gen_cells = set()

        # Rule 1 & 2: Survival and Death
        for cell in live_cells:
            if neighbor_counts[cell] in {2, 3}:
                next_gen_cells.add(cell)

        # Rule 3: Birth
        for cell, count in neighbor_counts.items():
            if count == 3 and cell not in live_cells:
                next_gen_cells.add(cell)

        return next_gen_cells