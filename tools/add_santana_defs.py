"""
add_santana_defs.py — Injeta "Smooth" (Santana feat. Rob Thomas, Supernatural,
1999) em tools/patches-defs.json: 1 música → 4 patches (riff, base limpa, solo,
camada), cada um com momentos de toggle (stomps) embutidos.

Schema vigente: modules como DICT ({"DST": {"name": ..., "on": ..., "params": {...}}}),
9 módulos sempre presentes, nomes REAIS do fw 2.0/2.1 (reference/15).

Rig pesquisado (fontes no álbum): PRS Santana signature (humbuckers gordos,
sustain longo) direto na Mesa/Boogie — o tom "gordo e liso". No catálogo GP-100:
L-Star CL/L-Star 2x12 (Mesa Lone Star, o clean gordo) para riff/base e
Solo100 LD (Soldano SLO-100, o lead denso e cantável) + Mess-D 4x12 para o solo.

Uso: python tools/add_santana_defs.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS_PATH = ROOT / 'tools' / 'patches-defs.json'

# ---------- helpers (mesma forma do add_pulse_defs.py; importaria e rodaria
# o main dele — por isso cópia, não import) --------------------------------------
OFF = {'PRE': 'Boost', 'DST': 'Blues OD', 'AMP': 'Dark Twin', 'NR': 'Gate 1',
       'CAB': 'DarkTW 2x12', 'EQ': 'EQ 1', 'MOD': 'A-Chorus', 'DLY': 'Sweet', 'RVB': 'Hall'}

def mod(name, on, *p):
    return {"name": name, "on": on, "params": {str(i): v for i, v in enumerate(p)}}

def chain(pre=None, dst=None, amp=None, nr=None, cab=None, eq=None, modfx=None, dly=None, rvb=None):
    out = {}
    for key, m in (('PRE', pre), ('DST', dst), ('AMP', amp), ('NR', nr), ('CAB', cab),
                   ('EQ', eq), ('MOD', modfx), ('DLY', dly), ('RVB', rvb)):
        out[key] = m if m is not None else {"name": OFF[key], "on": False, "params": {}}
    return out

def ref(role, src, conf="alta"):
    return {"role": role, "conf": conf, "src": src}

def P(camada, suf, nome, emoji, timbre, spec, riff, drum, escutar, ajustes, evite, irnota,
      sel, selc, vol, tone, rec, tec, tipo='Rock', bpm=112, momentos=None):
    spec_full = {"name": nome, "type": tipo, "bpm": bpm, "volume": 60,
                 "ir_slot": None, "modules": spec}
    doc = {"guitarra": {"seletor": sel, "seletorCurto": selc, "volume": vol,
                        "tone": tone, "receita": rec, "tecnicas": tec},
           "comoTocar": [],
           "teste": {"riff": riff, "drum": drum, "escutar": escutar},
           "ajustes": ajustes, "evite": evite, "irNota": irnota}
    if momentos:
        doc['momentos'] = [{'nome': n, 'mods': [list(a) for a in alvos],
                            'quando': q, 'dica': d} for (n, alvos, q, d) in momentos]
    return {"camada": camada, "sufixo": suf, "nome": nome, "emoji": emoji,
            "timbre": timbre, "spec": spec_full, "doc": doc}

# ---------- blocos reutilizados entre camadas ------------------------------------
NR_28 = mod('Gate 1', True, 28)                 # single coils brilhantes: gate leve
LS_RIFF = mod('L-Star CL', True, 42, 52, 62, 55, 55, 58)    # Lone Star aberto (gordo)
LS_CLEAN = mod('L-Star CL', True, 30, 48, 60, 50, 52, 58)   # Lone Star CH1 mais limpo
SOLO_LD = mod('Solo100 LD', True, 46, 52, 62, 55, 58, 62)   # Soldano lead: denso e liso
CAB_LS = mod('L-Star 2x12', True, 62, 55)       # 1x12 vintage — casa com o Lone Star
CAB_MESA = mod('Mess-D 4x12', True, 85, 80)     # gabinete Mesa (fábrica) para o solo
EQ_GORDO = mod('EQ 1', True, 2, 3, -1, 5, 5, 50)            # Mid +3: a voz "cantada"
BLUES_LIFT = mod('Blues OD', False, 55, 92, 73) # sobressalente: quase-riff num clique
BLUES_LEV = mod('Blues OD', False, 50, 92, 73)  # sobressalente mais suave
CHORUS_DOBRO = mod('A-Chorus', False, 35, 0.5, 30)          # sobressalente: dobro de estúdio

REF_GUITAR = ref("Guitarra: PRS Santana signature — humbuckers gordos, sustain longo",
                 "guitarchalk.com — 'Amp Settings for Smooth' (PRS Santana + Mesa)")
REF_MESA = ref("Amp: Mesa/Boogie — o Mark I é o clássico dele desde Woodstock; gain moderado",
               "guitarchalk.com · tonesmatch.com — Smooth riff tone")
REF_GROOVE = ref("Groove: riff festonado em Am–D sobre percussão afro (timba/conga)",
                 "Supernatural (1999), Arista · Wikipedia")

IR_MESA = ('Ambos valem aqui: Modern Boutique 4x12 Medium Mix (User IR 4) para o '
           'recorte de mesa de gravação, ou fique no Mess-D de fábrica (o mapa '
           'registra as duas rotas).')
IR_LOCAL_LS = ('Recomendada: Magma Vintage 1x12 Medium Mix (User IR 5) — a alma '
               'vintage 1x12 do combo do Santana (Low Cut 5 · High Cut 8500 · Level 0).')
IR_FAB = 'Fábrica é o alvo: nenhum gabinete do banco casa melhor que o CAB já escolhido para este papel.'

SMOOTH = []

# ---------- Riff (groove) ---------------------------------------------------------
SMOOTH.append(P(
    'Riff', 'RI', 'SMOO1RI', '🔥',
    "Groove do riff: Lone Star aberto com drive na frente — gordo, liso e festonado, "
    "a mão no groove de timba",
    chain(pre=mod('COMP', True, 25, 40, 50), dst=mod('Yellow OD', True, 40, 83, 55),
          amp=LS_RIFF, nr=NR_28, cab=CAB_LS, eq=EQ_GORDO,
          rvb=mod('Room', True, 20, 19, 31, 0)),
    "riff festonado de Am–D", "Rock latino 112 BPM (groove de timba)",
    ["gordo e liso ao mesmo tempo", "midrange presente que corta sem piar",
     "graves acompanhando o baixo, sem embolar"],
    ["lamacento → CAB High Cut -5 ou EQ Mid -2", "seco/durpo → Yellow OD Tone +5",
     "falta sustain → L-Star CL Vol +3"],
    ["Hi-gain moderno: a mordida do Smooth é de amp aberto, não de distorção",
     "Reverb longo: o groove é seco"],
    IR_LOCAL_LS,
    "Posição 3 (middle) — mordida sem perder o corpo", "middle",
    "8 (groove constante)", "7",
    "SELETOR 3 · Volume 8 · Tone 7 — DRIVE NO STOMP: religue no refrão se quiser o refrão mais aberto",
    ["Palhetada alternada na corda A/D — o riff vive da mão direita",
     "Toque À FRENTE da batida nas transições Am→D (o empurrão do groove)"],
    momentos=[('Refrão aberto (sem drive)', [('DST', 'OFF')],
               'No refrão, desligue o drive: o Lone Star aberto engrossa sem a mordida.',
               'Religue para o riff.')],
))

# ---------- Base limpa (versos, respondendo ao vocal) ------------------------------
SMOOTH.append(P(
    'Base limpa', 'CL', 'SMOO1CL', '✨',
    "Base limpa dos versos: Lone Star no canal mais limpo com chorus ralo — colchão "
    "que conversa com o vocal",
    chain(pre=mod('COMP', True, 25, 40, 50), dst=BLUES_LEV,
          amp=LS_CLEAN, nr=NR_28, cab=CAB_LS,
          modfx=mod('A-Chorus', True, 28, 0.5, 28),
          dly=mod('Sweet', True, 18, 320, 18),
          rvb=mod('Room', True, 24, 19, 33, 0)),
    "acordes Am–D respondendo ao vocal", "Verso 112 BPM",
    ["limpo gordo (não estéril)", "chorus ralo — textura, não efeito",
     "espaço para o vocal respirar"],
    ["brigar com o vocal → Volume da guitarra -2", "chorus forte → A-Chorus Depth -10",
     "falta corpo → L-Star CL Vol +4"],
    ["Clima 'molhado' demais: a base seca segura o verso",
     "Triângulo de agudos: Tone 7 já é suficiente"],
    IR_LOCAL_LS,
    "Posição 4 (middle+neck) — corpo e doçura", "middle+neck",
    "6-7", "6-7",
    "VOLUME 6-7 · Seletor 4 · Tone 6-7 — suave, atrás do vocal",
    ["Dispare as nota-célula do riff entre as frases do vocal",
     "Dinâmica pela mão: choque no acorde, relaxe no enchimento"],
    momentos=[('Levante para frases (drive)', [('DST', 'ON')],
               'Frases no fim do verso: religue o drive e você tem o território do riff num clique.',
               '')],
))

# ---------- Solo (o lead "cantado") ------------------------------------------------
SMOOTH.append(P(
    'Solo', 'SO', 'SMOO1SO', '🎺',
    "Solo lead: Soldano denso e cantável sobre gabinete Mesa — o sustain infinito "
    "que faz a guitarra 'cantar' por cima do vocal do Rob Thomas",
    chain(pre=mod('COMP', True, 25, 40, 50), dst=mod('Yellow OD', True, 48, 83, 55),
          amp=SOLO_LD, nr=NR_28, cab=CAB_MESA, eq=EQ_GORDO,
          dly=mod('Sweet', True, 20, 420, 24),
          rvb=mod('Plate', True, 30, 40, 50, 1)),
    "solo de Am pentatônica menor com frases longas", "Solo 112 BPM",
    ["sustain infinito nas notas presas", "midrange cantável (a assinatura Santana)",
     "legato liso, sem granulado"],
    ["granulado/áspero → Yellow OD Gain -4", "agudo piante → EQ High -2",
     "falta corte → Solo100 LD PRSE +4"],
    ["Delay longo: o eco do solo é curto e discreto",
     "Distorção extra no DST: o sustain já vem do amp + sustain do dedo"],
    IR_MESA,
    "Posição 1 (bridge humbucker) — sustain e mordida", "bridge",
    "10", "8",
    "SELETOR 1 · Volume 10 · Tone 8 — VINTE segundos de solo: frases que começam e não param",
    ["Frases longas com vibrato de dedo largo (não de tremolo)",
     "Puxe a escala de Am com bends até a 12ª casa — deixe a nota CHORAR antes de resolver"],
    momentos=[('Ponte espessa (dobro)', [('MOD', 'ON')],
               'Na ponte, o chorus dá o dobro de estúdio da gravação.',
               'Religue para o solo seco.')],
))

# ---------- Camada (fills/percussiva para gravar em casa) --------------------------
SMOOTH.append(P(
    'Camada', 'FL', 'SMOO1FL', '🪘',
    "Camada percussiva/fills: clean crocante para dobrar o groove em outra passagem "
    "na gravação de casa",
    chain(pre=mod('COMP', True, 30, 40, 50), dst=BLUES_LIFT,
          amp=mod('L-Star CL', True, 36, 50, 60, 52, 54, 58),
          nr=NR_28, cab=CAB_LS,
          dly=mod('Sweet', True, 15, 240, 15),
          rvb=mod('Room', True, 22, 19, 31, 0)),
    "fills curtos e percussivos sobre o groove", "Camada 112 BPM",
    ["crocante e curto — preenche sem ocupar o lugar da base",
     "ataque seco que 'bate' com a conga"],
    ["sumir na mixagem → EQ Level +4", "crocante demais → L-Star CL Vol -3"],
    ["Fills longos: esta camada é percussiva — frases de 1 ou 2 compassos"],
    IR_LOCAL_LS,
    "Posição 2 (middle+bridge)", "middle+bridge",
    "6-7", "7",
    "VOLUME 6-7 · Seletor 2 · Tone 7 — grava essa passagem como CAMADA, não como base",
    ["Mute com a mão esquerda entre os fills (o 'trabalho' percussivo)",
     "Dobre o riff do patch SMOO1RI com 2 compassos de diferença"],
    momentos=[('Solo (lead herdado)', [('DST', 'ON')],
               'Religue o drive e o patch sobe para o território do solo.',
               'A camada religa o drive só em breaks.')],
))

# ---------- escreve no defs (idempotente + ordem do álbum) ------------------------
ALBUM = {
    "banda": "Santana", "album": "Supernatural", "ano": 1999,
    "display": "Supernatural (1999)", "pasta": "Santana/Supernatural (1999)",
    "rig": ("## 📚 Rig real (fontes)\n\n"
            "- **Carlos Santana**: PRS Santana signature (humbuckers gordos, sustain longo) "
            "direto na **Mesa/Boogie** — o Mark I é o clássico dele desde Woodstock; em "
            "estúdio o tom do *Smooth* é o 'gordo e liso' de Mesa com gain moderado.\n"
            "- **Groove**: riff festonado em Am–D sobre percussão afro (timba/conga); "
            "o baixo dokiisha dobra o riff — por isso a base do patch acompanha, não disputa.\n"
            "- **Solo**: pentatônica menor de Am com frases longas e vibrato largo — "
            "sustain de amp + sustain do dedo, sem pedal de distorção extra.\n"
            "- 📖 Fontes: guitarchalk.com ('Amp Settings for \"Smooth\"' — PRS Santana + Mesa) · "
            "tonesmatch.com (Smooth riff tone) · Supernatural (1999), Arista · Wikipedia.")
}

data = json.loads(DEFS_PATH.read_text(encoding='utf-8'))
data['albums']['SN'] = ALBUM
SONG = {
    "id": "SMOO1", "song": "Smooth", "idAlbum": "SN", "bpm": 112,
    "resumo": ("Santana com Rob Thomas: groove de Am–D, riff festonado sobre o groove "
               "de timba e o solo mais radioativo da década — o tom 'gordo e liso' da "
               "PRS na Mesa."),
    "referencias": [REF_GUITAR, REF_MESA, REF_GROOVE],
    "patches": SMOOTH,
    "banda": "Santana", "album": "Supernatural", "ano": 1999,
}
data['songs'] = [s for s in data['songs'] if s['idAlbum'] != 'SN']
data['songs'].append(SONG)
DEFS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f"OK: 1 música / {len(SMOOTH)} patches do Smooth (Santana, Supernatural 1999) em patches-defs.json")
