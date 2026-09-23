"""Nomes oficiais de parâmetro por (módulo, modelo) — fonte única do domínio.

Derivado do manual do firmware V2.0, conferido contra o catálogo empírico
(`reference/15-*`) e validado pelo guarda de sincronia. Consumidores: gerador de
patch, validador do defs e CLI.

Este catálogo é o que permite ao validador falar a língua do músico: um erro em
`modules.DLY.params.1` só é acionável quando sabemos que o slot 1 é `Time`.
"""

from __future__ import annotations

__all__ = ['PARAM_NAMES', 'ROTULOS_EM_MS', 'parametros', 'rotulo']

# (módulo, modelo) -> nomes na ordem dos índices params_0..n do firmware
PARAM_NAMES: dict[tuple[str, str], list[str]] = {
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
    ('RVB', 'Room'): ['Mix', 'Pre Delay', 'Decay', 'Trail'],
    ('RVB', 'Hall'): ['Mix', 'Pre Delay', 'Decay', 'Trail'],
    ('RVB', 'Plate'): ['Mix', 'Decay', 'H-Damp', 'Trail'],
    ('RVB', 'Spring'): ['Mix', 'Decay'],  # Trail fica no default (Off); slot 2 é interno
}

# rótulos cujo valor é tempo em milissegundos, não percentual 0–100
ROTULOS_EM_MS: frozenset[str] = frozenset({'Time', 'Pre Delay'})


def parametros(modulo: str, modelo: str) -> tuple[str, ...]:
    """Rótulos dos parâmetros do modelo — vazio se o par não está no catálogo."""
    return tuple(PARAM_NAMES.get((modulo, modelo), ()))


def rotulo(modulo: str, modelo: str, indice: int) -> str | None:
    """Rótulo de um índice de parâmetro, ou None quando fora do catálogo."""
    nomes = PARAM_NAMES.get((modulo, modelo))
    if nomes is None or not 0 <= indice < len(nomes):
        return None
    return nomes[indice]
