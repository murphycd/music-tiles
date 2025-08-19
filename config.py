# config.py
"""
Contains all configuration constants and enumerations for the application.
"""
from dataclasses import dataclass
from enum import Enum, auto


class DragMode(Enum):
    """Defines the possible modes for a mouse drag action."""

    NONE = auto()
    SELECT = auto()
    PAN = auto()


@dataclass
class StyleConfig:
    """Defines the visual styling of the application."""

    COLOR_TILE_DEFAULT: str = "#f0f0f0"
    COLOR_TILE_SELECTED: str = "#3498db"
    COLOR_TILE_OUTLINE: str = "#cccccc"
    COLOR_TEXT_DEFAULT: str = "#1c1c1c"
    COLOR_TEXT_SELECTED: str = "#ffffff"
    COLOR_UI_BACKGROUND: str = "#e0e0e0"
    COLOR_DRAG_LINE: str = "red"
    FONT_FAMILY: str = "Arial"


@dataclass
class ViewConfig:
    """Defines the configuration for the viewport and zoom behavior."""

    MIN_TILES_ON_SCREEN: int = 3
    MAX_TILES_ON_SCREEN: int = 18
    INITIAL_TILES_ON_SCREEN: int = 5
    NOTE_VISIBILITY_ZOOM_THRESHOLD: float = 25.0


@dataclass
class InteractionConfig:
    """Defines constants related to user interaction."""

    CLICK_VS_DRAG_THRESHOLD_SQ: int = 25  # Distance squared
    ZOOM_FACTOR: float = 1.1


@dataclass
class MusicConfig:
    """
    Defines music theory constants and the Tonnetz grid geometry.

    The grid maps (row, col) coordinates to MIDI pitches using a sheared
    grid formula to create the triangular Tonnetz layout. The formula is:
    midi(r, c) = ORIGIN_MIDI
                 + (-r) * PITCH_INCR_VERTICAL
                 + c * (PITCH_INCR_HORIZONTAL_EVEN if r % 2 == 0 else PITCH_INCR_HORIZONTAL_ODD)
    """

    ORIGIN_NOTE: str = "C4"
    DEFAULT_USE_SHARPS: bool = True

    # The pitch change for moving one step vertically in the grid (e.g., C -> G).
    # This corresponds to the interval of a Perfect Fifth.
    PITCH_INCR_VERTICAL: int = 7

    # The pitch change for moving one step horizontally. This value
    # alternates by row to create the characteristic triangular pattern.
    PITCH_INCR_HORIZONTAL_EVEN: int = 4  # Major Third
    PITCH_INCR_HORIZONTAL_ODD: int = 3  # minor Third


@dataclass
class OctaveConfig:
    """Defines constants for MIDI octave handling."""

    MIN_OCTAVE: int = 2
    MAX_OCTAVE: int = 6
    INITIAL_OCTAVE: int = 4


@dataclass
class MidiConfig:
    """Defines constants for MIDI output."""

    DEFAULT_VELOCITY: int = 100
