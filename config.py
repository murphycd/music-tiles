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

    MIN_OCTAVE: int = 6
    MAX_OCTAVE: int = 3
    INITIAL_OCTAVE: int = 4


@dataclass
class MidiConfig:
    """Defines constants for MIDI output."""

    DEFAULT_VELOCITY: int = 127
    SOUNDFONT_PATH: str = "soundfonts/MuseScore_General.sf3"
    DEFAULT_INSTRUMENT: int = 78


@dataclass
class TuningConfig:
    """
    Defines constants for tuning systems.

    """

    DEFAULT_SELECTION_INDEX = 0  # choose first system defined on startup

    @classmethod
    def get_tuning_systems(cls):
        """Return a list of tuning system datastructures in the order they were defined below."""
        tuning_systems = []
        for value in cls.__dict__.values():
            if isinstance(value, cls.TuningSystem):
                tuning_systems.append(value)
        return tuning_systems

    @dataclass
    class TuningSystem:
        """Deviation defines, for each note in an octave, the deviation in cents from 12-TET for each note."""

        displayText: str
        definition: dict[int, float]

    #
    # Define tuning systems below. Their index will be the order they are defined.
    #

    # 12-Tone Equal Temperament (the default, no deviation)
    EQUAL_TEMPERAMENT = TuningSystem(
        "12-TET",
        {
            0: 0,  # Unison
            1: 0,  # Minor Second
            2: 0,  # Major Second
            3: 0,  # Minor Third
            4: 0,  # Major Third
            5: 0,  # Perfect Fourth
            6: 0,  # Tritone
            7: 0,  # Perfect Fifth
            8: 0,  # Minor Sixth
            9: 0,  # Major Sixth
            10: 0,  # Minor Seventh
            11: 0,  # Major Seventh
        },
    )

    # 5-Limit Just Intonation
    JUST_INTONATION = TuningSystem(
        "Just Intonation",
        {
            0: 0,  # 1/1
            1: -29.3,  # 16/15 (approx)
            2: 3.9,  # 9/8
            3: 15.6,  # 6/5
            4: -13.7,  # 5/4
            5: -2.0,  # 4/3
            6: -17.6,  # 45/32 (approx)
            7: 2.0,  # 3/2
            8: 17.6,  # 8/5
            9: -15.6,  # 5/3
            10: 19.6,  # 9/5 (approx)
            11: -11.7,  # 15/8
        },
    )

    # Pythagorean Tuning
    PYTHAGOREAN_TUNING = TuningSystem(
        "Pythagorean",
        {
            0: 0,  # 1/1
            1: -23.5,  # 256/243
            2: 3.9,  # 9/8
            3: -19.6,  # 32/27
            4: 7.8,  # 81/64
            5: -2.0,  # 4/3
            6: 11.7,  # 729/512
            7: 2.0,  # 3/2
            8: -21.5,  # 128/81
            9: 5.9,  # 27/16
            10: -17.6,  # 16/9
            11: 9.8,  # 243/128
        },
    )

    # Quarter-Comma Meantone
    MEANTONE_TUNING = TuningSystem(
        "Meantone",
        {
            0: 0,
            1: 19.6,
            2: -5.9,
            3: 13.7,
            4: -13.7,
            5: 5.9,
            6: 25.5,  # This is a "wolf" interval and will sound dissonant
            7: -3.9,
            8: 15.6,
            9: -9.8,
            10: 9.8,
            11: -19.6,
        },
    )
