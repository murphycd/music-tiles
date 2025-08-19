# tuning.py
"""
Values represent the deviation in cents from 12-TET for each note
"""

# 12-Tone Equal Temperament (the default, no deviation)
EQUAL_TEMPERAMENT = {
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
    10: 0, # Minor Seventh
    11: 0  # Major Seventh
}

# 5-Limit Just Intonation
JUST_INTONATION = {
    0: 0,          # 1/1
    1: -29.3,      # 16/15 (approx)
    2: 3.9,        # 9/8
    3: 15.6,       # 6/5
    4: -13.7,      # 5/4
    5: -2.0,       # 4/3
    6: -17.6,      # 45/32 (approx)
    7: 2.0,        # 3/2
    8: 17.6,       # 8/5
    9: -15.6,      # 5/3
    10: 19.6,      # 9/5 (approx)
    11: -11.7       # 15/8
}


# Pythagorean Tuning
PYTHAGOREAN_TUNING = {
    0: 0,          # 1/1
    1: -23.5,      # 256/243
    2: 3.9,        # 9/8
    3: -19.6,      # 32/27
    4: 7.8,        # 81/64
    5: -2.0,       # 4/3
    6: 11.7,       # 729/512
    7: 2.0,        # 3/2
    8: -21.5,      # 128/81
    9: 5.9,        # 27/16
    10: -17.6,     # 16/9
    11: 9.8         # 243/128
}

# Quarter-Comma Meantone
MEANTONE_TUNING = {
    0: 0,
    1: 19.6,
    2: -5.9,
    3: 13.7,
    4: -13.7,
    5: 5.9,
    6: 25.5, # This is a "wolf" interval and will sound dissonant
    7: -3.9,
    8: 15.6,
    9: -9.8,
    10: 9.8,
    11: -19.6
}