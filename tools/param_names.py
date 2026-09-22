"""param_names.py — nomes oficiais de parâmetro por (módulo, modelo).

FONTE ÚNICA (manual do firmware V2.0 + catálogo empírico reference/15).
Consumidores: build_song_patches (gerador), defs_schema (validador),
gp100.py (CLI). Módulo próprio para evitar importação circular entre
build e validador.
"""

PARAM_NAMES = {
    ('PRE', 'COMP'): ['Sens', 'Attack', 'Sustain', 'Level'],
    ('PRE', 'COMP4'): ['Thresh', 'Attack', 'Tone', 'Level'],
    ('PRE', 'Boost'): ['Ganho', 'Boost'],
    ('PRE', 'AC Sim'): ['Body', 'Top', 'Vol', 'Mode'],
    ('PRE', 'Saturate'): ['Gain', 'Mix', 'Output', 'H-Cut'],
    ('DST', 'Blues OD'): ['Gain', 'Tone', 'Level'],
    ('DST', 'Green OD'): ['Gain', 'Tone', 'Level'],
    ('DST', 'La Charger'): ['Gain', 'Tone', 'Volume'],
    ('DST', 'Super OD'): ['Drive', 'Tone', 'Level'],
    ('DST', 'Red Haze'): ['Fuzz', 'VOL'],
    ('DST', 'Yellow OD'): ['Gain', 'Tone', 'Level'],
    ('AMP', 'Dark Twin'): ['Vol', 'Output', 'Bass', 'Middle', 'Treble', 'Bright'],
    ('AMP', 'Foxy 30TB'): ['Vol', 'Cut', 'Master', 'Bass', 'Treble', 'Char'],
    ('AMP', 'Flagman'): ['Gain', 'PRSE', 'Master', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'Knights CL'): ['Gain', 'Vol', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'Bellman 59N'): ['Vol', 'PRSE', 'Output', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'UK 45'): ['Vol', 'PRSE', 'Output', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'L-Star CL'): ['Vol', 'PRSE', 'Master', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'Solo100 LD'): ['Vol', 'PRSE', 'Master', 'Bass', 'Middle', 'Treble'],
    ('NR', 'Gate 1'): ['Thr'],
    ('NR', 'Gate 2'): ['Thr', 'Release'],
    ('CAB', 'DarkTW 2x12'): ['Level', 'High Cut'],
    ('CAB', 'Foxy 1x12'): ['Level', 'High Cut'],
    ('CAB', 'TWD 2x12'): ['Level', 'High Cut'],
    ('CAB', 'J-120 2x12'): ['Level', 'High Cut'],
    ('CAB', 'UK-GN 2x12'): ['Level', 'High Cut'],
    ('CAB', 'UK-LD 4x12'): ['Level', 'High Cut'],
    ('CAB', 'Mess-D 4x12'): ['Level', 'High Cut'],
    ('CAB', 'L-Star 2x12'): ['Level', 'High Cut'],
    ('CAB', 'D'): ['Level', 'High Cut'],
    ('EQ', 'EQ 1'): ['Low', 'Mid', 'High', 'Mid Freq', 'Presença', 'Level'],
    ('MOD', 'A-Chorus'): ['Rate', 'Depth', 'Mix', 'Level'],
    ('MOD', 'Vibe'): ['Intensidade', 'Velocidade', 'Sync'],
    ('DLY', 'Sweet'): ['Mix', 'Time', 'Fdbk'],
    ('DLY', 'Slapbk'): ['Mix', 'Time', 'Fdbk'],
    ('DLY', 'T-Echo'): ['Mix', 'Time', 'Fdbk'],
    # RVB: o manual (fw V2.0) lista Mix PRIMEIRO e cada modelo tem seu conjunto —
    # Room/Hall/Church = Mix · Pre Delay · Decay · Trail; Plate = Mix · Decay ·
    # H-Damp · Trail; Spring/N-Star/Deep Sea = Mix · Decay · Trail (+ slot interno).
    ('RVB', 'Room'): ['Mix', 'Pre Delay', 'Decay', 'Trail'],
    ('RVB', 'Hall'): ['Mix', 'Pre Delay', 'Decay', 'Trail'],
    ('RVB', 'Plate'): ['Mix', 'Decay', 'H-Damp', 'Trail'],
    ('RVB', 'Spring'): ['Mix', 'Decay'],       # Trail fica no default (Off); slot 2 é interno
}
