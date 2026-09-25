# -*- coding: utf-8 -*-
"""Scorer protocolado do golden set (doc 20) — rodada 2026-09.

Avaliação dos agentes gp100-tone-research + gp100-tone-mapper:
- esperado: cadeias do doc 20 (derivadas do defs, transcritas aqui como dados);
- mapeado: simulação protocolada do PAR de agentes (sem auth de spawn real),
  âncora a âncora, com as fontes que o research acha + catálogo fw 2.0;
- pontuação: pesos do doc 20 (AMP x2 · DST/CAB x1 · resto x0,5) e regras de
  casamento do doc (exato 100% · família 60% · classe 30%).
"""

from __future__ import annotations

# --- regras de casamento (doc 20) -----------------------------------------
FAMILIA: dict[str, tuple[str, ...]] = {
    # AMP
    'UK 45': ('UK 50JP', 'UK 800'),
    'UK 50JP': ('UK 45', 'UK 800'),
    'UK 800': ('UK 45', 'UK 50JP'),
    'Dark Twin': ('Tweedy',),
    'Tweedy': ('Dark Twin',),
    'Foxy 30TB': ('Foxy 30N',),
    'Foxy 30N': ('Foxy 30TB',),
    'Knights CL': ('Knights OD', 'Z38 CL'),
    'Knights OD': ('Knights CL',),
    'Z38 CL': ('Knights CL',),
    'Flagman': ('Flagman+',),
    'Flagman+': ('Flagman',),
    'Solo100 LD': ('Solo100 OD',),
    'Solo100 OD': ('Solo100 LD',),
    'Mess DualV': ('Mess DualM',),
    'Mess DualM': ('Mess DualV',),
    'J-120 CL': ('J-120 2x12',),  # amp/cab da mesma família JC-120
    # CAB
    'DarkTW 2x12': ('Dark 1x12',),
    'Dark 1x12': ('DarkTW 2x12',),
    'UK-LD 4x12': ('UK-GN 4x12', 'UK-LD 2x12'),
    'UK-GN 4x12': ('UK-LD 4x12',),
    'UK-GN 2x12': ('UK-LD 2x12',),
    'L-Star 2x12': ('L-Star 1x12',),
    'Mess-D 4x12': ('Mess-D 2x12',),
    'J-120 2x12': ('J-120 CL',),
    'Foxy 1x12': ('Foxy 2x12',),
    # DST
    'Blues OD': ('Super OD', 'Green OD'),
    'Green OD': ('Blues OD',),
    'Super OD': ('Blues OD',),
    'Yellow OD': ('Green OD',),
    'La Charger': ('RIP', 'SM Dist'),
    'RIP': ('La Charger',),
    'Red Haze': ('Fat Fuzz',),
    'Fat Fuzz': ('Red Haze',),
    'BIG Fuzz': ('TRI Fuzz',),
    'TRI Fuzz': ('BIG Fuzz',),
    # PRE/MOD/DLY/RVB: família = a própria (mesmo modelo; família trivial)
}
CLASSE: dict[str, str] = {
    # DST: classe de textura
    'La Charger': 'distorcao',
    'RIP': 'distorcao',
    'SM Dist': 'distorcao',
    'Darktale': 'distorcao',
    'Blues OD': 'overdrive',
    'Green OD': 'overdrive',
    'Super OD': 'overdrive',
    'Yellow OD': 'overdrive',
    'Tube Clipper': 'overdrive',
    'Lazaro': 'overdrive',
    'Chief': 'overdrive',
    'Flex OD': 'overdrive',
    'Red Haze': 'fuzz',
    'Fat Fuzz': 'fuzz',
    'BIG Fuzz': 'fuzz',
    'TRI Fuzz': 'fuzz',
    'OCT Fuzz': 'fuzz',
    # AMP: classe de carater
    'Dark Twin': 'clean-americano',
    'Tweedy': 'clean-americano',
    'Foxy 30TB': 'clean-britanico',
    'Foxy 30N': 'clean-britanico',
    'J-120 CL': 'solid-state',
    'J-120 2x12': 'solid-state',
    'Knights CL': 'clean-boutique',
    'Z38 CL': 'clean-boutique',
    'L-Star CL': 'clean-boutique',
    'UK 45': 'rock-britanico',
    'UK 50JP': 'rock-britanico',
    'UK 800': 'rock-britanico',
    'Flagman': 'hard-britanico',
    'Flagman+': 'hard-britanico',
    'Solo100 LD': 'lead-fase-alta',
    'Solo100 OD': 'lead-fase-alta',
    'Mess DualV': 'caixa-americana',
    'Mess DualM': 'caixa-americana',
}
PESO = {
    'AMP': 2.0,
    'DST': 1.0,
    'CAB': 1.0,
    'PRE': 0.5,
    'NR': 0.5,
    'EQ': 0.5,
    'MOD': 0.5,
    'DLY': 0.5,
    'RVB': 0.5,
}
ORDEM = ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']


def parse_cadeia(texto: str) -> dict[str, tuple[str, bool]]:
    """'PRE:Boost+ AMP:Dark Twin-' -> por BLOCO: (modelos tem espacos)."""
    import re

    partes = re.split(r'(?=\b(?:PRE|DST|AMP|NR|CAB|EQ|MOD|DLY|RVB):)', texto)
    blocos: dict[str, tuple[str, bool]] = {}
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
        nome, resto = parte.split(':', 1)
        blocos[nome] = (resto[:-1].strip(), resto.endswith('+'))
    return blocos


def pontos(e: str, m: str) -> float:
    """0.0 / 0.3 / 0.6 / 1.0 pelas regras do doc 20."""
    if e == m:
        return 1.0
    if m in FAMILIA.get(e, ()):  # família
        return 0.6
    if CLASSE.get(e) is not None and CLASSE.get(e) == CLASSE.get(m):
        return 0.3
    return 0.0


def avaliar(patch: str, esperado: str, mapeado: str) -> dict:
    E, M = parse_cadeia(esperado), parse_cadeia(mapeado)
    linhas, obt, maxp = [], 0.0, 0.0
    for b in ORDEM:
        em, mm = E[b], M[b]
        p = pontos(em[0], mm[0])
        if em[1] != mm[1]:
            p = 0.0  # estado errado = 0 no bloco
        w = PESO[b]
        obt += p * w
        maxp += w
        linhas.append((b, em, mm, p, w, p * w))
    return {
        'patch': patch,
        'linhas': linhas,
        'obtido': obt,
        'maximo': maxp,
        'pct': obt / maxp * 100,
        'amp_ok': M['AMP'] == E['AMP'],
    }


# --- esperado (doc 20, derivado do defs) -----------------------------------
ESPERADO: dict[str, str] = {
    # Abbey Road
    'CT01RIF': 'PRE:COMP- DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'CT01VOX': 'PRE:Boost+ DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'STH01BA': 'PRE:COMP- DST:Blues OD- AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'STH01SO': 'PRE:COMP- DST:Green OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Sweet- RVB:Hall+',
    'OHB01BA': 'PRE:COMP- DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+',
    'OHB01SO': 'PRE:Boost+ DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+',
    # Apostrophe
    'URM01SL': 'PRE:COMP4+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'URM01SO': 'PRE:COMP- DST:Super OD+ AMP:UK 45+ NR:Gate 1+ CAB:UK-GN 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    # Cheap Thrills
    'PMH01BA': 'PRE:COMP- DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Spring+',
    'PMH01SO': 'PRE:Boost+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe- DLY:Sweet- RVB:Spring+',
    # DSOTM
    'SOF01EC': 'PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'SOF01BA': 'PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Hall+',
    'SOF01SO': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'TM01BA': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'TM01SO': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'MNY01BA': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'MNY01SO': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'WYWH01IN': 'PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+',
    'CNW01SO': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'CNW01S2': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'RLH01RI': 'PRE:Boost- DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Plate+',
    'RLH01SO': 'PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    # Muddy Banks
    'WIS01AM': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'SCH01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'SCH01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'DRY01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'DRY01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'DRY01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'ANE01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'ANE01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'ANE01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'SLT01CL': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'SLT01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'SLT01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'LIT01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'LIT01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'LIT01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'HSB01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'HSB01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    'POL01CL': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    # Supernatural
    'SMOO1RI': 'PRE:COMP+ DST:Yellow OD+ AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'SMOO1CL': 'PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus+ DLY:Sweet+ RVB:Room+',
    'SMOO1SO': 'PRE:COMP+ DST:Yellow OD+ AMP:Solo100 LD+ NR:Gate 1+ CAB:Mess-D 4x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet+ RVB:Plate+',
    'SMOO1FL': 'PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+',
    # AYE
    'FOXY01BA': 'PRE:Boost+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate+',
    'FOXY01SO': 'PRE:Boost+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate+',
    'PURP01BA': 'PRE:COMP- DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate-',
    'PURP01SO': 'PRE:Saturate+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:M-Echo- RVB:Plate-',
    'WIND01BA': 'PRE:COMP+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:M-Echo- RVB:Spring+',
    'WIND01SO': 'PRE:COMP+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:T-Echo+ RVB:Spring+',
}

# --- mapeado: simulação protocolada por âncora ------------------------------
# Cada âncora é uma transcrição do que o research (dossiê) + mapper (catálogo
# fw 2.0) produziriam para TODAS as camadas daquela música.
MAPEADO: dict[str, str] = {
    # Abbey Road: Fender Twins de estúdio (media: repute Vox AC30/EF86) — amp
    # limpo/preso, drive moderado do próprio amp, slapback leve; JC-120 p/ fog.
    'CT01RIF': 'PRE:Boost+ DST:Blues OD+ AMP:Dark Twin- NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'CT01VOX': 'PRE:Boost+ DST:Blues OD+ AMP:Dark Twin- NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'STH01BA': 'PRE:Boost+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'STH01SO': 'PRE:Boost+ DST:Super OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Sweet- RVB:Hall+',
    'OHB01BA': 'PRE:Boost+ DST:Blues OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'OHB01SO': 'PRE:Boost+ DST:Blues OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+',
    # Apostrophe: Pignose (sem equivalente) + Marshall JMP; SG; drive denso.
    'URM01SL': 'PRE:COMP+ DST:Super OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'URM01SO': 'PRE:Boost+ DST:Super OD+ AMP:UK 50JP+ NR:Gate 1+ CAB:UK-GN 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    # Cheap Thrills: Twin Reverb + Maestro FZ-1 nos solos (blues drive).
    'PMH01BA': 'PRE:Boost+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Spring+',
    'PMH01SO': 'PRE:Boost+ DST:Fat Fuzz+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Spring+',
    # DSOTM: Hiwatt DR103 limpo (sem equivalente) → Knights CL; solos Big Muff
    # + Booster em Flagman; Echorec → Sweet; Hall.
    'SOF01EC': 'PRE:Boost+ DST:Blues OD- AMP:Knights CL+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'SOF01BA': 'PRE:Boost+ DST:Blues OD- AMP:Knights CL+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Hall+',
    'SOF01SO': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'TM01BA': 'PRE:Saturate+ DST:Fat Fuzz- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'TM01SO': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'MNY01BA': 'PRE:Saturate+ DST:Fat Fuzz- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+',
    'MNY01SO': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'WYWH01IN': 'PRE:Boost+ DST:Blues OD- AMP:Knights CL+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+',
    'CNW01SO': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'CNW01S2': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    'RLH01RI': 'PRE:Boost+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Plate+',
    'RLH01SO': 'PRE:Saturate+ DST:Fat Fuzz+ AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+',
    # Muddy Banks: Twin + DS-1/RAT; chorus Small Clone no limpo; slapback leve.
    'WIS01AM': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus+ DLY:Slapbk+ RVB:Room+',
    'SCH01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'SCH01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'DRY01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'DRY01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'DRY01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'ANE01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'ANE01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'ANE01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'SLT01CL': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'SLT01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'SLT01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'LIT01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'LIT01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'LIT01SO': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'HSB01AR': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'HSB01RI': 'PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+',
    'POL01CL': 'PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+',
    # Supernatural: PRS + Mesa Mark IV → L-Star CL (clean) / Solo100 LD (solo);
    # OD amarelo; delay curto + plate.
    'SMOO1RI': 'PRE:COMP+ DST:Yellow OD+ AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+',
    'SMOO1CL': 'PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus+ DLY:Sweet+ RVB:Room+',
    'SMOO1SO': 'PRE:COMP+ DST:Yellow OD+ AMP:Solo100 LD+ NR:Gate 1+ CAB:Mess-D 4x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet+ RVB:Plate+',
    'SMOO1FL': 'PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+',
    # AYE: JTM45 → UK 45; Fuzz Face → Red Haze (catálogo: based on FF);
    # Octavia sem equivalente dedicado no DST (OCTA é PRE); vibe/trem no MOD.
    'FOXY01BA': 'PRE:Boost+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:Slapbk- RVB:Plate+',
    'FOXY01SO': 'PRE:Boost+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:Slapbk- RVB:Plate+',
    'PURP01BA': 'PRE:Boost+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:Slapbk- RVB:Room+',
    'PURP01SO': 'PRE:Saturate+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Slapbk- RVB:Room+',
    'WIND01BA': 'PRE:COMP+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Slapbk- RVB:Spring+',
    'WIND01SO': 'PRE:COMP+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:Slapbk+ RVB:Spring+',
}

ESCOLA = {}
for nome in ESPERADO:
    if nome.startswith(('CT', 'STH', 'OHB')):
        ESCOLA[nome] = 'Beatles'
    elif nome.startswith('URM'):
        ESCOLA[nome] = 'Zappa'
    elif nome.startswith('PMH'):
        ESCOLA[nome] = 'Janis'
    elif nome.startswith(('SOF', 'TM', 'MNY', 'WYWH', 'CNW', 'RLH')):
        ESCOLA[nome] = 'Floyd'
    elif nome.startswith(('WIS', 'SCH', 'DRY', 'ANE', 'SLT', 'LIT', 'HSB', 'POL')):
        ESCOLA[nome] = 'Nirvana'
    elif nome.startswith('SMOO'):
        ESCOLA[nome] = 'Santana'
    elif nome.startswith(('FOXY', 'PURP', 'WIND')):
        ESCOLA[nome] = 'Hendrix'

AGENTE = {
    'AMP': 'mapper',
    'DST': 'mapper',
    'CAB': 'mapper',
    'PRE': 'mapper',
    'NR': 'mapper',
    'EQ': 'mapper',
    'MOD': 'mapper',
    'DLY': 'ambos',
    'RVB': 'ambos',
}

if __name__ == '__main__':
    assert set(ESPERADO) == set(MAPEADO), 'simulacao incompleta'
    resultados = {p: avaliar(p, ESPERADO[p], MAPEADO[p]) for p in ESPERADO}

    # placar global
    obt = sum(r['obtido'] for r in resultados.values())
    mx = sum(r['maximo'] for r in resultados.values())
    print(f'GLOBAL: {obt:.1f}/{mx:.1f} = {obt / mx * 100:.1f}%')
    aprovados = [p for p, r in resultados.items() if r['pct'] >= 70 and r['amp_ok']]
    print(f'aprovados (>=70% e AMP): {len(aprovados)}/{len(resultados)}')

    # por bloco (agente responsavel)
    print('\n== POR BLOCO ==')
    for b in ORDEM:
        o = m = 0.0
        for r in resultados.values():
            for bb, em, mm, p, w, pw in r['linhas']:
                if bb == b:
                    o += pw
                    m += w
        print(f'{b:4} {o:6.1f}/{m:6.1f} = {o / m * 100:5.1f}%  ({AGENTE[b]})')

    # por escola
    print('\n== POR ESCOLA ==')
    for esc in ['Beatles', 'Zappa', 'Janis', 'Floyd', 'Nirvana', 'Santana', 'Hendrix']:
        rs = [r for p, r in resultados.items() if ESCOLA[p] == esc]
        o = sum(r['obtido'] for r in rs)
        m = sum(r['maximo'] for r in rs)
        ok = sum(1 for r in rs if r['pct'] >= 70 and r['amp_ok'])
        print(f'{esc:9} {o:6.1f}/{m:6.1f} = {o / m * 100:5.1f}%  ({ok}/{len(rs)} aprovados)')

    # piores patches
    print('\n== PIORES 10 ==')
    for p, r in sorted(resultados.items(), key=lambda kv: kv[1]['pct'])[:10]:
        errs = [
            f'{b}:{em[0]}{"" if em[1] else "-"}→{mm[0]}{"" if mm[1] else "-"}'
            for (b, em, mm, p_, w, pw) in r['linhas']
            if p_ == 0.0
        ]
        print(f'{p:9} {r["pct"]:5.1f}%  {"; ".join(errs[:4])}')
