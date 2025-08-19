# utils.py
"""
Contains pure, standalone utility functions for geometry and music theory.
"""
from typing import Generator, Tuple
from config import MusicConfig

# Tuples contain enharmonic equivalents. The first is preferred for sharps, the second for flats.
_PITCH_CLASS_NAMES = (
    ("C",),
    ("C#", "Db"),
    ("D",),
    ("D#", "Eb"),
    ("E",),
    ("F",),
    ("F#", "Gb"),
    ("G",),
    ("G#", "Ab"),
    ("A",),
    ("A#", "Bb"),
    ("B",),
)


def bresenham_line(
    r0: int, c0: int, r1: int, c1: int
) -> Generator[Tuple[int, int], None, None]:
    """
    Yields all integer coordinates on a line from (r0, c0) to (r1, c1).
    Uses Bresenham's line algorithm.
    """
    dr, dc = abs(r1 - r0), abs(c1 - c0)
    sr, sc = 1 if r0 < r1 else -1, 1 if c0 < c1 else -1
    err = dr - dc

    while True:
        yield (r0, c0)
        if r0 == r1 and c0 == c1:
            break
        e2 = 2 * err
        if e2 > -dc:
            err -= dc
            r0 += sr
        if e2 < dr:
            err += dr
            c0 += sc


def note_to_midi(note_str: str) -> int:
    """Converts a note name like 'C4' or 'Db5' to a MIDI number."""
    note_str = note_str.strip()
    if not note_str or not note_str[-1].isdigit():
        raise ValueError(f"Invalid note format, missing octave: {note_str}")

    octave = int(note_str[-1])
    # Note name can be multi-character (e.g., "C#")
    pitch_name = note_str[:-1].capitalize()
    if not pitch_name:
        raise ValueError(f"Invalid note format, missing pitch name: {note_str}")

    pitch_class = -1
    for i, names in enumerate(_PITCH_CLASS_NAMES):
        if pitch_name in names:
            pitch_class = i
            break

    # Handle edge cases like B# or Cb that are not in the primary tuple list
    if pitch_class == -1:
        base_name = pitch_name[:-1]
        if pitch_name.endswith("#"):
            for i, names in enumerate(_PITCH_CLASS_NAMES):
                if base_name in names:
                    pitch_class = (i + 1) % 12
                    break
        elif pitch_name.endswith("b"):
            for i, names in enumerate(_PITCH_CLASS_NAMES):
                if base_name in names:
                    pitch_class = (i - 1 + 12) % 12
                    break

    if pitch_class == -1:
        raise ValueError(f"Cannot parse note name: {note_str}")

    return 12 * (octave + 1) + pitch_class


def coord_to_midi(coord: Tuple[int, int], base_midi: int) -> int:
    """
    Calculates the absolute MIDI value for a given axial grid coordinate (q, r).
    """
    q, r = coord
    q_offset = q * MusicConfig.PITCH_INCR_Q
    r_offset = r * MusicConfig.PITCH_INCR_R
    return base_midi + q_offset + r_offset


def midi_to_pitch_class_name(midi: int, use_sharps: bool) -> str:
    """Converts a MIDI number to its pitch class name (e.g., 'C#')."""
    note_index = midi % 12
    names = _PITCH_CLASS_NAMES[note_index]

    # Prefer the flat name (index 1) if it exists and use_sharps is False.
    if len(names) > 1 and not use_sharps:
        return names[1]
    # Default to the first name (sharp or natural).
    return names[0]


def midi_to_note_name(midi: int, use_sharps: bool) -> str:
    """Converts a MIDI number to a full note name with octave (e.g., 'C#4')."""
    pitch_class = midi_to_pitch_class_name(midi, use_sharps)
    octave = midi // 12 - 1
    return f"{pitch_class}{octave}"
