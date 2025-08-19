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


class RenderMode(Enum):
    """Defines the rendering style for the grid."""

    RECTANGLE = auto()
    HEXAGON = auto()


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
    FONT_FAMILY: str = "Century"


@dataclass
class ViewConfig:
    """Defines the configuration for the viewport and zoom behavior."""

    MIN_TILES_ON_SCREEN: int = 3
    MAX_TILES_ON_SCREEN: int = 21
    INITIAL_TILES_ON_SCREEN: int = 7
    NOTE_VISIBILITY_ZOOM_THRESHOLD: float = 25.0
    DEFAULT_RENDER_MODE: RenderMode = RenderMode.RECTANGLE


@dataclass
class InteractionConfig:
    """Defines constants related to user interaction."""

    CLICK_VS_DRAG_THRESHOLD_SQ: int = 25  # Distance squared
    ZOOM_FACTOR: float = 1.1


@dataclass
class MusicConfig:
    """
    Defines music theory constants and the Tonnetz grid geometry using
    an axial coordinate system (q, r).

    The grid maps (q, r) coordinates to MIDI pitches using a linear
    transformation, which is ideal for representing the consistent intervals
    of a Tonnetz grid. The formula is:
    midi(q, r) = ORIGIN_MIDI + q * PITCH_INCR_Q + r * PITCH_INCR_R
    """

    ORIGIN_NOTE: str = "C4"
    DEFAULT_USE_SHARPS: bool = False

    # The pitch change for moving one step along the 'q' axis.
    # Corresponds to the interval of a Major Third.
    PITCH_INCR_Q: int = 4

    # The pitch change for moving one step along the 'r' axis.
    # Corresponds to the interval of a Perfect Fifth.
    PITCH_INCR_R: int = 7


@dataclass
class OctaveConfig:
    """Defines constants for MIDI octave handling."""

    MIN_OCTAVE: int = 2
    MAX_OCTAVE: int = 6
    INITIAL_OCTAVE: int = 4


@dataclass
class MidiConfig:
    """Defines constants for MIDI output."""

    DEFAULT_VELOCITY: int = 127
    SOUNDFONT_PATH: str = "soundfonts/MuseScore_General.sf3"
    DEFAULT_INSTRUMENT: int = 85
