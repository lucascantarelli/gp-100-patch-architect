"""
add_pulse_defs.py — Injeta as 21 músicas do álbum Pulse (Pink Floyd, 1995) no
tools/patches-defs.json.

Cada música segue o schema vigente (id, song, idAlbum, bpm, resumo,
referencias, patches[]) e cada patch traz camada/sufixo/nome/emoji/timbre,
spec (cadeia GP-100 com nomes REAIS do fw 2.0, 9 módulos sempre presentes) e
doc (guitarra, técnica, teste, ajustes, evite, irNota). Refs com fontes da
pesquisa (gilmourish.com, Wikipedia, Discogs). Idempotente: re-executar reordena/reinsere o Pulse sem duplicar.

Uso: python tools/add_pulse_defs.py
"""
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS_PATH = ROOT / 'tools' / 'patches-defs.json'
# Idempotente: re-executar remove e re-insere as músicas do Pulse (ordem do álbum).
# Versionamento do defs é responsabilidade do git — nenhum arquivo de backup é criado.

# ---------- helpers (construção plana) ------------------------------------------
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

def song(id_, song_name, bpm, resumo, refs, patches):
    return {"id": id_, "song": song_name, "idAlbum": "PL", "bpm": bpm,
            "resumo": resumo, "referencias": refs, "patches": patches,
            "banda": "Pink Floyd", "album": "Pulse (live)", "ano": 1995}

def P(camada, suf, nome, emoji, timbre, spec, riff, drum, escutar, ajustes, evite, irnota,
      sel, selc, vol, tone, rec, tec, tipo='Rock', bpm=120):
    spec_full = {"name": nome, "type": tipo, "bpm": bpm, "volume": 60,
                 "ir_slot": None, "modules": spec}
    return {"camada": camada, "sufixo": suf, "nome": nome, "emoji": emoji,
            "timbre": timbre, "spec": spec_full,
            "doc": {"guitarra": {"seletor": sel, "seletorCurto": selc, "volume": vol,
                                 "tone": tone, "receita": rec, "tecnicas": tec},
                    "comoTocar": [],
                    "teste": {"riff": riff, "drum": drum, "escutar": escutar},
                    "ajustes": ajustes, "evite": evite, "irNota": irnota}}

# ---------- presets reutilizáveis ------------------------------------------------
AMP_FLAG_CLEAN = mod('Flagman', True, 35, 55, 62, 50, 55, 58)
AMP_FLAG_CRUNCH = mod('Flagman', True, 44, 55, 62, 50, 55, 58)
AMP_FLAG_LEAD = mod('Flagman', True, 50, 58, 64, 50, 55, 58)
AMP_FLAG_FUZZ = mod('Flagman', True, 40, 50, 58, 50, 52, 56)
AMP_KN_CLEAN = mod('Knights CL', True, 38, 62, 62, 48, 52, 58)
AMP_KN_LEAD = mod('Knights CL', True, 42, 62, 62, 48, 52, 58)
CAB_UKLD = mod('UK-LD 4x12', True, 78, 62)
NR_26 = mod('Gate 1', True, 26)
NR_30 = mod('Gate 1', True, 30)
TD_BASE = mod('Saturate', True, 35, 55, 60)   # Tube Driver de base (Saturate p0/p1/p2)
TD_LEAD = mod('Saturate', True, 50, 60, 62)   # Tube Driver quente de solo
TD_HOT = mod('Saturate', True, 58, 65, 64)    # Tube Driver no talo (solo final CNW01S2)
CHORUS_SUAVE = mod('A-Chorus', True, 28, 0.5, 28)
DLY_NOTA_570 = mod('Sweet', True, 20, 570, 30)
DLY_NOTA_430 = mod('Sweet', True, 15, 430, 25)
RVB_HALL = mod('Hall', True, 38, 45, 50, 1)
RVB_HALL_LONG = mod('Hall', True, 55, 50, 50, 1)
RVB_PLATE = mod('Plate', True, 30, 40, 50, 1)

REF_GIL = ref("Rig 1994: Hiwatt DR103 + Alembic F-2B + WEM/Marshall 4x12 + pedalboard completo", "gilmourish.com — Division Bell Tour")
IR_TWIN = 'Recomendada: American Twin 2x12 Medium Mix (User IR 1) — limpo americano de alto headroom (Low Cut 5 · High Cut 9000 · Level 0).'
IR_UKLD = 'Recomendada: British Straight 4x12 Medium Mix (User IR 4) — o 4x12 britânico da pilha de 1994 (Low Cut 4 · High Cut 8500 · Level 0).'
IR_FAB = 'Fábrica é o alvo: nenhum gabinete do banco casa melhor que o CAB já escolhido para este papel.'

PULSE_SONGS = []

# ---------- Speak to Me ----------------------------------------------------------
PULSE_SONGS.append(song('SFTM01', 'Speak to Me', 60,
    "Abertura com efeitos; sem guitarra — patch de ambiente para texturas e swells.",
    [ref("Sem guitarra na faixa: só efeitos/ambient", "Wikipedia/Discogs (Pulse) · gilmourish.com"), REF_GIL],
    [P('Texturas', 'AM', 'SFTM01AM', '🎛️',
       "Timbre ambiente: delay longo com feedback e reverb amplo — para texturas e swells da abertura",
       chain(amp=mod('Flagman', True, 25, 50, 55, 50, 50, 55), cab=CAB_UKLD,
             dly=mod('Sweet', True, 45, 620, 35), rvb=RVB_HALL_LONG),
       "texturas e swells com a chave de volume", "—",
       ["eco longo e respirável", "sem lama nos graves"],
       ["eco embolando → DLY Fdbk -10", "muito seco → RVB decay +10"],
       ["Tocar riffs: a faixa não tem guitarra — é ambiente"],
       IR_FAB,
       "Posição 2 (middle+bridge)", "middle+bridge", "5-8 (swells)", "8",
       "SWELLS com a chave de volume · Seletor 2 · Tone 8",
       ["Swell lento com a chave de volume (sem palhetada visível)",
        "Deixe o delay acumular entre os swells"],
    )],
))

# ---------- Astronomy Domine -----------------------------------------------------
PULSE_SONGS.append(song('AD01', 'Astronomy Domine', 100,
    "Syd Barrett (1967) revisitado ao vivo: guitarra de eco metálico — o delay é instrumento.",
    [ref("Versão Pulse: solo com eco curto repetido, estilo Space Echo", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base/Eco', 'EC', 'AD01EC', '🛰️',
       "Base com eco curto: o repetidor faz o ritmo — limpo crocante estilo Syd",
       chain(amp=AMP_KN_LEAD, cab=CAB_UKLD, nr=NR_26,
             dly=mod('Sweet', True, 30, 180, 22), rvb=mod('Room', True, 22, 20, 31, 0)),
       "riffs de eco entre os acordes", "Rock espacial",
       ["eco curto repetindo o ataque", "crocante sem sumir na lama"],
       ["eco embolando → DLY Fdbk -8", "falta mordida → Knights CL Gain +5"],
       ["Reverb longo no riff — o espaço vem do delay curto"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "9", "8-9",
       "SELETOR 2 · Volume 9 · Tone 8-9",
       ["Ataques curtos e secos — o delay cria o padrão rítmico",
        "Experimente tocar ENTRE as batidas do eco"],
    )],
))

# ---------- What Do You Want From Me ---------------------------------------------
PULSE_SONGS.append(song('WDF01', 'What Do You Want From Me', 110,
    "Blues rock direto: base com crunch e um dos solos mais 'SRV' do Gilmour.",
    [ref("Base crunch + solo bluesy com bend largo e vibrato largo", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'WDF01BA', '🎸',
       "Base de crunch: Tube Driver leve empurrando o Hiwatt — o som de acorde que anda",
       chain(pre=mod('Saturate', True, 38, 55, 62), amp=AMP_FLAG_CRUNCH, nr=NR_26,
             cab=CAB_UKLD, rvb=RVB_PLATE),
       "acordes do riff com palhetada alternada", "Blues rock 110 BPM",
       ["crunch que responde à palhetada", "graves definidos"],
       ["lamacento → CAB High Cut -5", "seco → RVB mix +5"],
       ["Distorção moderna: a música é valvulada e aberta"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Palhetada alternada no riff — a base é percussiva",
        "Dinâmica: mais forte = mais crunch (o Tube Driver responde)"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'WDF01SO', '🔥',
    "Solo bluesy: Tube Driver quente, bend largo de 1 tom, vibrato do pulso — Gilmour em modo SRV",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30,
          cab=CAB_UKLD, dly=DLY_NOTA_430, rvb=RVB_HALL),
    "solo do meio e final", "Blues rock 110 BPM",
    ["sustain longo nos bends", "definição nas notas rápidas"],
    ["falta sustain → PRE +5", "sibilando → NR Thr +2"],
    ["Vibrato de dedo rápido — o vibrato do Gilmour é do pulso, largo"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Bends de 1 tom inteiro com sustain",
     "Frases com espaço — o delay preenche o vazio"],
))

# ---------- Learning to Fly ------------------------------------------------------
PULSE_SONGS.append(song('LTF01', 'Learning to Fly', 104,
    "Anos 80 etéreo: base limpa com chorus, arpejos de eco e solo aéreo.",
    [ref("Base limpa com chorus + delay; solo com o mesmo pad", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'LTF01BA', '☁️',
       "Base aérea: limpo com chorus lento — o som de nuvem da intro",
       chain(amp=AMP_KN_CLEAN, modfx=CHORUS_SUAVE, cab=CAB_UKLD, rvb=RVB_HALL),
       "acordes abertos da intro e refrão", "Rock 104 BPM",
       ["chorus amplo sem 'aquário'", "clareza nos acordes abertos"],
       ["chorus forte demais → MOD Mix -10", "seco → RVB decay +5"],
       ["Distorção: a música vive do clean modulado"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "8",
       "SELETOR 4 · Volume 8 · Tone 8",
       ["Acordes abertos (add9/sus2) com palhetada lenta",
        "Deixe o chorus fazer o movimento"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo/Eco', 'SO', 'LTF01SO', '🕊️',
    "Solo aéreo com delay: frases curtas que o eco responde — diálogo com o delay",
    chain(amp=AMP_KN_LEAD, modfx=CHORUS_SUAVE, cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL),
    "solo central", "Rock 104 BPM",
    ["frases respondidas pelo eco", "notas flutuando no reverb"],
    ["eco alto demais → DLY Mix -8", "solo afogado → RVB mix -5"],
    ["Tocar corridas rápidas: o estilo é frases com espaço"],
    IR_UKLD,
    "Posição 4 (middle+neck)", "middle+neck", "9", "9",
    "SELETOR 4 · Volume 9 · Tone 9",
    ["Toque UMA frase e espere o eco responder",
     "Bends lentos com vibrato largo"],
))

# ---------- Keep Talking ---------------------------------------------------------
PULSE_SONGS.append(song('KTB01', 'Keep Talking', 122,
    "A épica de 1994: solo principal com Tube Driver + delay, e solo psicotélico com Big Muff.",
    [ref("Solo principal TD+delay; 2º solo Big Muff Civil War", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'KTB01BA', '⚙️',
       "Base do épico: crunch firme para as seções de refrão",
       chain(pre=TD_BASE, amp=AMP_FLAG_CRUNCH, nr=NR_26, cab=CAB_UKLD, rvb=RVB_PLATE),
       "riff e refrões", "Rock épico",
       ["crunch firme e definido", "boa separação de graves"],
       ["lamacento → CAB High Cut -5", "falta corpo → EQ Mid +2"],
       ["Distorção total na base — o refrão pede crunch controlado"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Acordes com palhetada marcada",
        "Deixe o espaço do refrão respirar"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo 1 (TD)', 'SO', 'KTB01SO', '🗣️',
    "Solo principal: Tube Driver quente + delay da nota — a voz que responde Stephen Hawking",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30, cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL),
    "solo após o 2º refrão", "Rock épico",
    ["sustain longo nos bends", "eco preenchendo os espaços"],
    ["falta sustain → PRE +5", "eco alto → DLY Mix -8"],
    ["Vibrato estreito — o vibrato do Gilmour é largo"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Bends de 1 tom com sustain longo",
     "Frase com espaço: o delay responde"],
))

PULSE_SONGS[-1]['patches'].append(P('Solo 2 (Fuzz)', 'FZ', 'KTB01FZ', '🌪️',
    "Solo psicotélico: Big Muff saturado — o uivo de fuzz do clímax",
    chain(dst=mod('Red Haze', True, 62, 45, 55), amp=AMP_FLAG_FUZZ, nr=NR_30,
          cab=CAB_UKLD, dly=mod('Sweet', True, 12, 570, 22), rvb=RVB_HALL),
    "2º solo (clímax)", "Rock épico",
    ["fuzz sustentado sem virar ruído", "notas definidas dentro do fuzz"],
    ["fuzz embolando → DST p1 -5", "sibilo entre frases → NR Thr +2"],
    ["Reduzir o ganho do amp: o fuzz já satura"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "8",
    "SELETOR 2 · Volume 10 · Tone 8",
    ["Notas longas com vibrato largo",
     "Frases esparsas: o fuzz sustenta tudo"],
))

# ---------- Shine On You Crazy Diamond -------------------------------------------
PULSE_SONGS.append(song('SOF01', 'Shine On You Crazy Diamond', 60,
    "A assinatura: intro com delay a cada nota (assinatura absoluta), base AOR e solo final.",
    [ref("Intro: delay a cada nota tocada (assinatura); solo final com TD", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Intro Eco', 'EC', 'SOF01EC', '💠',
       "A intro icônica: cada nota ecoa uma vez — o delay É o riff (toque a cada 2 tempos)",
       chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD,
             dly=mod('Sweet', True, 25, 530, 26), rvb=mod('Hall', True, 35, 45, 50, 1)),
       "intro inteira (parte I)", "AOR lento",
       ["cada nota ecoada uma vez", "espaço entre as notas preenchido pelo eco"],
       ["eco embolando → toque mais devagar", "eco baixo → DLY Mix +5"],
       ["Tocar a intro de forma corrida — o delay pede pausa entre as notas"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "9", "8",
       "SELETOR 2 · Volume 9 · Tone 8",
       ["Toque a nota e CONTE 2 tempos antes da próxima",
        "Bend na 4ª corda com vibrato lento",
        "O volume da guitarra controla o brilho do eco"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Base', 'BA', 'SOF01BA', '🔷',
    "Base AOR: acordes abertos com brilho e espaço — o colchão das partes cantadas",
    chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD, rvb=RVB_HALL),
    "acordes das partes cantadas", "AOR lento",
    ["acordes abertos respirando", "brilho sem dureza"],
    ["muito brilho → CAB High Cut -5", "seco → RVB decay +5"],
    ["Crunch na base: as partes cantadas pedem limpo"],
    IR_UKLD,
    "Posição 4 (middle+neck)", "middle+neck", "8", "8",
    "SELETOR 4 · Volume 8 · Tone 8",
    ["Acordes abertos com palhetada suave",
     "Deixe os acordes soar completos"],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'SOF01SO', '💎',
    "Solo final: Tube Driver quente com delay — a despedida de Syd em frases largas",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30,
          cab=CAB_UKLD, dly=mod('Sweet', True, 20, 530, 28), rvb=RVB_HALL),
    "solo final (parte IX)", "AOR lento",
    ["frases largas com sustain", "eco preenchendo os espaços"],
    ["falta sustain → PRE +5", "afogado → RVB mix -5"],
    ["Corridas rápidas: o solo é melódico, com espaço"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases melódicas largas com bend longo",
     "Espaço entre frases — o delay responde"],
))

# ---------- Breathe --------------------------------------------------------------
PULSE_SONGS.append(song('BRT01', 'Breathe', 63,
    "DSOTM: acordes com chorus suave e reverb amplo — a base do respiro.",
    [ref("Base com chorus sutil + reverb; clima spacey", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'BRT01BA', '🌫️',
       "Base spacey: chorus sutil e reverb amplo — o respiro do DSOTM",
       chain(amp=AMP_KN_CLEAN, modfx=mod('A-Chorus', True, 25, 0.5, 25), cab=CAB_UKLD, rvb=RVB_HALL),
       "acordes da intro e refrões", "DSOTM 63 BPM",
       ["chorus sutil", "espaço amplo"],
       ["chorus forte → MOD Mix -8", "seco → RVB decay +5"],
       ["Crunch: a base é limpa e modulada"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "7",
       "SELETOR 4 · Volume 8 · Tone 7",
       ["Acordes Em7/A7 com palhetada lenta",
        "Deixe as cordas soar — pouco mute"],
    )],
))

# ---------- Time -----------------------------------------------------------------
PULSE_SONGS.append(song('TM01', 'Time', 121,
    "Solo de 'Time': TD + delay curto, bend de 1 tom e agressividade controlada — icônico.",
    [ref("Solo: Tube Driver + delay curto, bend 1 tom, vibrato largo", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'TM01BA', '⏳',
       "Base do DSOTM: acordes com crunch suave — o relógio no fundo",
       chain(pre=mod('Saturate', True, 32, 55, 60), amp=AMP_FLAG_CRUNCH, nr=NR_26,
             cab=CAB_UKLD, rvb=RVB_PLATE),
       "acordes dos versos e refrão", "DSOTM 121 BPM",
       ["crunch suave", "boa definição nos graves"],
       ["lamacento → CAB High Cut -5", "seco → RVB mix +5"],
       ["Crunch pesado no verso — leve e aberto"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Acordes F#m7/A com palhetada marcada",
        "Sincronize com os acordes do piano"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'TM01SO', '⏱️',
    "O solo de Time: Tube Driver quente, delay curto, bend de 1 tom e a agressividade do relógio",
    chain(pre=TD_LEAD, amp=mod('Flagman', True, 52, 58, 64, 50, 55, 58), nr=NR_30,
          cab=CAB_UKLD, dly=mod('Sweet', True, 18, 380, 24), rvb=RVB_HALL),
    "solo central", "DSOTM 121 BPM",
    ["agressividade controlada", "bend de 1 tom com sustain", "delay curto preenchendo"],
    ["falta sustain → PRE +5", "sibilo → NR Thr +2"],
    ["Delay longo: o solo pede eco curto e agressivo"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Bend de 1 tom na 1ª e 2ª corda",
     "Vibrato largo do pulso",
     "Frases ascendentes com sustain"],
))

# ---------- Breathe (Reprise) ----------------------------------------------------
PULSE_SONGS.append(song('BTK02', 'Breathe (Reprise)', 63,
    "Reprise: base com crunch suave e clima mais escuro.",
    [ref("Base com crunch suave e clima escuro", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'BTK02BA', '🌗',
       "Reprise: crunch suave e escuro — a ponte entre Time e Money",
       chain(pre=mod('Saturate', True, 30, 55, 60), amp=AMP_FLAG_CRUNCH, nr=NR_26,
             cab=CAB_UKLD, rvb=RVB_PLATE),
       "acordes da reprise", "DSOTM 63 BPM",
       ["crunch escuro", "clima sombrio"],
       ["muito brilho → CAB High Cut -5", "muito escuro → EQ High +2"],
       ["Limpo: a reprise é mais escura e crunch"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "9", "8",
       "SELETOR 2 · Volume 9 · Tone 8",
       ["Acordes com palhetada lenta e pesada",
        "Deixe o sustain completar os acordes"],
    )],
))

# ---------- Money ----------------------------------------------------------------
PULSE_SONGS.append(song('MNY01', 'Money', 128,
    "O blues de 7/4: solo com TD + delay, base com crunch e aquele groove irregular.",
    [ref("Solo TD+delay; base crunch no 7/4", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'MNY01BA', '💰',
       "Base do 7/4: crunch firme e groove — o blues do dinheiro",
       chain(pre=TD_BASE, amp=AMP_FLAG_CRUNCH, nr=NR_26, cab=CAB_UKLD, rvb=RVB_PLATE),
       "riff e refrões no 7/4", "Blues 7/4",
       ["crunch firme no groove", "graves definidos"],
       ["lamacento → CAB High Cut -5", "seco → RVB mix +5"],
       ["Crunch pesado no riff — leve e aberto"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Conte o 7/4: 1-2-3-4-5-6-7 (não force o 4/4)",
        "Riff com palhetada alternada"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'MNY01SO', '💱',
    "Solo de Money: Tube Driver quente + delay — o blues de 7/4 com frases que caem no groove",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30,
          cab=CAB_UKLD, dly=DLY_NOTA_430, rvb=RVB_HALL),
    "solo central", "Blues 7/4",
    ["frases que caem no groove 7/4", "bend com sustain"],
    ["falta sustain → PRE +5", "afogado → RVB mix -5"],
    ["Corridas rápidas: o solo é melódico e no groove"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases no 7/4 com pausas",
     "Bend de meio tom no final das frases"],
))

# ---------- Us and Them ----------------------------------------------------------
PULSE_SONGS.append(song('USAT01', 'Us and Them', 79,
    "A balada épica: base limpa com chorus e reverb, solos aéreos com delay.",
    [ref("Base limpa com chorus e reverb; solos aéreos", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'USAT01BA', '🕊️',
       "Base da balada: limpo com chorus e reverb amplo — o colchão de piano e sax",
       chain(amp=AMP_KN_CLEAN, modfx=CHORUS_SUAVE, cab=CAB_UKLD, rvb=RVB_HALL),
       "acordes dos versos", "Balada épica",
       ["limpo respirando", "chorus sutil"],
       ["chorus forte → MOD Mix -8", "seco → RVB decay +5"],
       ["Crunch: a base é limpa e etérea"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "7",
       "SELETOR 4 · Volume 8 · Tone 7",
       ["Acordes com palhetada suave",
        "Deixe os acordes soar completos"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'USAT01SO', '🌌',
    "Solo aéreo: delay longo + reverb — as frases flutuando sobre a balada",
    chain(amp=AMP_KN_LEAD, cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL_LONG),
    "solo central", "Balada épica",
    ["frases flutuando no reverb", "eco preenchendo"],
    ["afogado → RVB mix -8", "eco alto → DLY Mix -8"],
    ["Tocar corridas: as frases são longas e aéreas"],
    IR_UKLD,
    "Posição 4 (middle+neck)", "middle+neck", "9", "9",
    "SELETOR 4 · Volume 9 · Tone 9",
    ["Frases longas com sustain",
     "Deixe o reverb completar o final das frases"],
))

# ---------- Any Colour You Like --------------------------------------------------
PULSE_SONGS.append(song('CLR01', 'Any Colour You Like', 120,
    "Jam do DSOTM: guitarra espacial com fuzz e delays, diálogo com os sintetizadores.",
    [ref("Fuzz + delays espaciais; jam improvisada", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Jam Espacial', 'JM', 'CLR01JM', '🎨',
       "Jam espacial: fuzz + delay longo — a guitarra conversa com os sintetizadores",
       chain(dst=mod('Red Haze', True, 55, 50, 55), amp=AMP_FLAG_FUZZ, nr=NR_30,
             cab=CAB_UKLD, dly=mod('Sweet', True, 35, 570, 28), rvb=RVB_HALL_LONG),
       "jam improvisada", "Instrumental espacial",
       ["fuzz sustentado", "delay criando padrões"],
       ["fuzz embolando → DST p1 -5", "delay embolando → Fdbk -8"],
       ["Tocar de forma corrida: a jam pede espaço e improviso"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "8",
       "SELETOR 2 · Volume 10 · Tone 8",
       ["Frases longas com vibrato",
        "Deixe o delay criar os padrões"],
    )],
))

# ---------- Brain Damage ---------------------------------------------------------
PULSE_SONGS.append(song('BD01', 'Brain Damage', 77,
    "Base folk do DSOTM: acordes abertos com brilho, clima leve e sombrio ao mesmo tempo.",
    [ref("Base folk com acordes abertos", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'BD01BA', '🧠',
       "Base folk: acordes abertos com brilho — o lado leve e sombrio do DSOTM",
       chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD, rvb=RVB_HALL),
       "acordes dos versos e refrão", "DSOTM 77 BPM",
       ["brilho folk", "boa definição nos acordes abertos"],
       ["muito brilho → CAB High Cut -5", "seco → RVB decay +5"],
       ["Crunch: a base é limpa e folk"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "8",
       "SELETOR 4 · Volume 8 · Tone 8",
       ["Acordes D/F# com palhetada folk",
        "Deixe as cordas soar entre as trocas"],
    )],
))

# ---------- Eclipse --------------------------------------------------------------
PULSE_SONGS.append(song('ECL01', 'Eclipse', 84,
    "Final do DSOTM: acordes maciços com crunch e reverb — o clímax do álbum.",
    [ref("Acordes maciços com crunch e reverb", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'ECL01BA', '🌑',
       "Clímax: acordes maciços com crunch e reverb amplo — o fecho do DSOTM",
       chain(pre=mod('Saturate', True, 36, 55, 62), amp=AMP_FLAG_CRUNCH, nr=NR_26,
             cab=CAB_UKLD, rvb=RVB_HALL),
       "acordes finais", "DSOTM 84 BPM",
       ["acordes maciços", "reverb amplo"],
       ["lamacento → CAB High Cut -5", "seco → RVB decay +5"],
       ["Distorção total: o clímax pede crunch massivo"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Acordes longos e maciços",
        "Sincronize com o coro final"],
    )],
))

# ---------- Wish You Were Here ---------------------------------------------------
PULSE_SONGS.append(song('WYWH01', 'Wish You Were Here', 60,
    "A intro de 12 cordas (adaptada para a Strat) e o solo de abertura com delay curto.",
    [ref("Intro 12 cordas (adaptada) + solo com delay curto", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Intro/Solo', 'IN', 'WYWH01IN', '📻',
       "Intro icônica: '12 cordas' simulado na Strat (posição 4 + tone aberto) com o solo respondendo",
       chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD,
             dly=mod('Sweet', True, 18, 380, 20), rvb=mod('Room', True, 22, 20, 31, 0)),
       "intro de 12 cordas + solo de abertura", "WYWH 60 BPM",
       ["som de '12 cordas' simulado", "solo respondendo a base"],
       ["eco alto → DLY Mix -8", "falta corpo → EQ Mid +2"],
       ["Distorção: a música é toda limpa e acústica"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "9", "9",
       "SELETOR 4 · Volume 9 · Tone 9",
       ["Arpejos da intro com a mão relaxada",
        "Solo no meio da intro (respondendo a base)"],
    )],
))

# ---------- Comfortably Numb -----------------------------------------------------
PULSE_SONGS.append(song('CNW01', 'Comfortably Numb', 134,
    "O solo dos solos: duas subidas épicas com TD + delay — o hino do rock.",
    [ref("2 solos épicos: Tube Driver + delay na duração da nota", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Solo 1', 'SO', 'CNW01SO', '🏥',
       "1º solo (após os versos): Tube Driver quente + delay — a subida que atravessa o muro",
       chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30, cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL),
       "1º solo", "Épico 134 BPM",
       ["frases ascendentes com sustain", "eco na duração da nota"],
       ["falta sustain → PRE +5", "eco alto → DLY Mix -8"],
       ["Corridas rápidas: as frases são largas e melódicas"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Bend de 1 tom na subida",
        "Frases com espaço — o delay responde"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo 2', 'S2', 'CNW01S2', '👑',
    "2º solo (final): o hino — Tube Driver no talo + delay, vibrato largo e sustain infinito",
    chain(pre=TD_HOT, amp=mod('Flagman', True, 54, 60, 66, 50, 55, 58), nr=NR_30,
          cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL_LONG),
    "2º solo (final)", "Épico 134 BPM",
    ["sustain infinito", "vibrato largo", "frases icônicas reconhecíveis"],
    ["falta sustain → PRE +5", "afogado → RVB mix -5"],
    ["Acelerar: as frases são icônicas, respeite o ritmo"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Toque as frases icônicas com o ritmo original",
     "Vibrato largo no final de cada frase"],
))

# ---------- Another Brick in the Wall, Part 2 ------------------------------------
PULSE_SONGS.append(song('ABIETW01', 'Another Brick in the Wall, Part 2', 123,
    "O solo do 'Muro': um dos mais icônicos — TD + delay, frases esparsas com propósito.",
    [ref("Solo icônico: TD + delay, frases esparsas com propósito", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'ABIETWBA', '🧱',
       "Base do muro: crunch seco e groove disco — o refrão coral pede firmeza",
       chain(pre=TD_BASE, amp=AMP_FLAG_CRUNCH, nr=NR_26, cab=CAB_UKLD, rvb=RVB_PLATE),
       "riff e refrões", "Rock/groove 123 BPM",
       ["crunch seco no groove", "boa definição nos graves"],
       ["lamacento → CAB High Cut -5", "seco → RVB mix +5"],
       ["Crunch pesado no riff — leve e seco"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Riff com palhetada firme",
        "Mute com a mão direita no groove"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'ABIETWSO', '🎓',
    "O solo do muro: TD quente + delay — frases esparsas, cada nota com propósito",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30, cab=CAB_UKLD, dly=DLY_NOTA_430, rvb=RVB_HALL),
    "solo central", "Rock/groove 123 BPM",
    ["frases esparsas e melódicas", "eco preenchendo os espaços"],
    ["falta sustain → PRE +5", "eco alto → DLY Mix -8"],
    ["Tocar de forma corrida: o solo é esparso e melódico"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Toque as frases icônicas com o ritmo original",
     "Deixe o delay responder entre as frases"],
))

# ---------- Mother ---------------------------------------------------------------
PULSE_SONGS.append(song('MOTB01', 'Mother', 81,
    "A balada do muro: acordes limpos com arpejos e clima de pergunta à mãe.",
    [ref("Base limpa com arpejos + clima de balada", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base', 'BA', 'MOTB01BA', '👩',
       "Base da balada: arpejos limpos com reverb — o colchão da pergunta à mãe",
       chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD, rvb=RVB_HALL),
       "arpejos dos versos", "Balada 81 BPM",
       ["arpejos limpos e definidos", "reverb respirando"],
       ["afogado → RVB mix -8", "seco → RVB decay +5"],
       ["Crunch: a base é limpa e delicada"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "8",
       "SELETOR 4 · Volume 8 · Tone 8",
       ["Arpejos com a mão relaxada",
        "Deixe cada nota soar completa"],
    )],
))

# ---------- Sorrow ---------------------------------------------------------------
PULSE_SONGS.append(song('SIA01', 'Sorrow', 116,
    "A abertura épica do Division Bell: Big Muff em acordes gigantes e solo final pesado.",
    [ref("Intro/feitiço: Big Muff + intervalos largos; solo final pesado", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Intro (Fuzz)', 'FZ', 'SIA01FZ', '⚡',
       "Intro gigante: Big Muff em acordes com intervalos largos — o feitiço que abre o show",
       chain(dst=mod('Red Haze', True, 58, 48, 56), amp=AMP_FLAG_FUZZ, nr=NR_30,
             cab=CAB_UKLD, rvb=RVB_HALL),
       "intro e feitiço", "Épico 116 BPM",
       ["acordes de fuzz gigantes", "sustain sem fim"],
       ["fuzz embolando → DST p1 -5", "sibilo → NR Thr +2"],
       ["Reduzir o ganho do amp: o fuzz já satura"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "8",
       "SELETOR 2 · Volume 10 · Tone 8",
       ["Acordes com intervalos largos (D5+10ª)",
        "Sustain longo com vibrato do braço"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'SIA01SO', '⛈️',
    "Solo final: Tube Driver + fuzz no mesmo patch — a tempestade do fechamento",
    chain(dst=mod('Red Haze', True, 45, 52, 58), amp=AMP_FLAG_LEAD, nr=NR_30,
          cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL),
    "solo final", "Épico 116 BPM",
    ["peso e sustain", "frases largas com vibrato"],
    ["pesado demais → DST p0 -5", "afogado → RVB mix -5"],
    ["Tocar de forma corrida: o solo é épico e pesado"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases largas com sustain",
     "Vibrato largo no final das frases"],
))

# ---------- One of These Days ----------------------------------------------------
PULSE_SONGS.append(song('OEOD01', 'One of These Days', 110,
    "Abertura instrumental: slide com delay longo e a tempestade de ruído.",
    [ref("Slide com delay + tempestade de ruído (não há base de acordes)", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Slide/Ruído', 'SL', 'OEOD01SL', '🌪️',
       "Abertura instrumental: slide com delay longo + tempestade de ruído",
       chain(amp=AMP_KN_LEAD, cab=CAB_UKLD,
             dly=mod('T-Echo', True, 30, 480, 20), rvb=RVB_HALL_LONG),
       "slide e tempestade de ruído", "Instrumental 110 BPM",
       ["slide flutuando no delay", "tempestade controlada"],
       ["delay embolando → Fdbk -8", "tempestade forte → RVB mix -8"],
       ["Tocar riffs de acordes: a música é slide e ambiente"],
       IR_UKLD,
       "Posição 1 (bridge)", "bridge", "9", "8",
       "SELETOR 1 · Volume 9 · Tone 8",
       ["Slide na 4ª/5ª corda com o delay fazendo o padrão",
        "Deixe o delay criar o ciclo"],
    )],
))

# ---------- Coming Back to Life -------------------------------------------------
PULSE_SONGS.append(song('CBK01', 'Coming Back to Life', 104,
    "Arpejos limpos com delay que crescem para o solo épico — a ressurreição do álbum.",
    [ref("Arpejos de abertura com delay; solo com Tube Driver", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Base/Arpejo', 'AR', 'CBK01AR', '🌅',
       "Arpejos de abertura: limpo com delay — o despertar em 6/8",
       chain(amp=AMP_KN_CLEAN, cab=CAB_UKLD, dly=DLY_NOTA_430, rvb=RVB_HALL),
       "arpejos da intro e versos", "Rock 104 BPM",
       ["arpejos com eco respondendo", "dinâmica crescendo"],
       ["eco alto → DLY Mix -8", "seco → RVB decay +5"],
       ["Crunch nos arpejos: a intro é limpa e espaçosa"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "8", "8",
       "SELETOR 4 · Volume 8 · Tone 8",
       ["Arpejos em 6/8 com palhetada híbrida",
        "Cresça de volume a cada volta do ciclo"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'CBK01SO', '🌄',
    "Solo principal: Tube Driver quente + delay — a frase longa que abre o céu",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30, cab=CAB_UKLD, dly=DLY_NOTA_570, rvb=RVB_HALL),
    "solo central", "Rock 104 BPM",
    ["frase longa com sustain", "eco preenchendo os espaços"],
    ["falta sustain → PRE +5", "afogado → RVB mix -5"],
    ["Acelerar: as frases são longas e melódicas"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases longas com bend de 1 tom",
     "Vibrato largo no final das frases"],
))

# ---------- Run Like Hell --------------------------------------------------------
PULSE_SONGS.append(song('RLH01', 'Run Like Hell', 148,
    "O fechamento: riff em G com delay fazendo a parede de som — efeito e riff são a mesma coisa.",
    [ref("Riff com delay longo (parede de eco); solo curto", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Riff', 'RI', 'RLH01RI', '🏃',
       "O riff com parede de eco: Flagman crunch + delay com feedback — o delay É o arranjo",
       chain(amp=AMP_FLAG_CRUNCH, nr=NR_26, cab=CAB_UKLD,
             dly=mod('Sweet', True, 35, 450, 30), rvb=RVB_PLATE),
       "riff principal (G5-A5) com espaço entre os ataques", "Rock 148 BPM",
       ["eco preenchendo os espaços do riff", "crunch firme e seco"],
       ["eco embolando → DLY Fdbk -8", "lamacento → CAB High Cut -5"],
       ["Tocar o riff corrido: os ESPAÇOS entre os ataques são o que o eco preenche"],
       IR_UKLD,
       "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
       "SELETOR 2 · Volume 10 · Tone 9",
       ["Riff em G5-A5 com ataques sincopados",
        "Toque e solte — o delay completa o padrão",
        "Mute firme com a mão direita"],
    )],
))

PULSE_SONGS[-1]['patches'].append(P('Solo', 'SO', 'RLH01SO', '🚨',
    "Solo: Tube Driver + o mesmo delay — frases gritadas sobre a parede de eco",
    chain(pre=TD_LEAD, amp=AMP_FLAG_LEAD, nr=NR_30, cab=CAB_UKLD,
          dly=mod('Sweet', True, 30, 450, 28), rvb=RVB_HALL),
    "solo central", "Rock 148 BPM",
    ["frases sobre a parede de eco", "definição em andamento rápido"],
    ["eco alto → DLY Mix -8", "falta sustain → PRE +5"],
    ["Corridas: as frases são curtas e angulares"],
    IR_UKLD,
    "Posição 2 (middle+bridge)", "middle+bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases curtas e angulares em Mi menor",
     "Use o delay como terceiro braço"],
))

# ---------- On the Run (ambiente) ------------------------------------------------
PULSE_SONGS.append(song('ONR01', 'On the Run', 160,
    "Sem guitarra na faixa (sintetizadores/efeitos) — patch de ambiente para camadas caseiras.",
    [ref("Sem guitarra: VCS3, sequenciador e efeitos de aeroporto", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Texturas', 'AM', 'ONR01AM', '✈️',
       "Ambiente sintetizado: delay com feedback e reverb longo — camada de textura para a faixa",
       chain(amp=mod('Flagman', True, 25, 50, 55, 50, 50, 55), cab=CAB_UKLD,
             dly=mod('T-Echo', True, 40, 590, 30), rvb=RVB_HALL_LONG),
       "texturas, ruídos e swells", "—",
       ["eco longo e industrial", "sem lama nos graves"],
       ["eco embolando → DLY Fdbk -10", "muito seco → RVB decay +10"],
       ["Tocar riffs: a faixa original não tem guitarra — use como camada"],
       IR_FAB,
       "Posição 2 (middle+bridge)", "middle+bridge", "5-8 (swells)", "8",
       "SWELLS com a chave de volume · Seletor 2 · Tone 8",
       ["Swells com a chave de volume sobre o delay",
        "Ruídos controlados com o braço na ponte"],
    )],
))

# ---------- The Great Gig in the Sky (ambiente) ----------------------------------
PULSE_SONGS.append(song('GGS01', 'The Great Gig in the Sky', 108,
    "Sem guitarra na faixa (piano + vocal improvisado) — patch de ambiente para camadas caseiras.",
    [ref("Sem guitarra: piano elétrico e vocal improvisado", "Pulse (1995) · gilmourish.com"), REF_GIL],
    [P('Texturas', 'AM', 'GGS01AM', '🎺',
       "Ambiente etéreo: chorus + reverb longo — camada sutil que respeita o vocal da faixa",
       chain(amp=AMP_KN_CLEAN, modfx=CHORUS_SUAVE, cab=CAB_UKLD, rvb=RVB_HALL_LONG),
       "texturas suaves e swells", "Balada",
       ["camada sutil sem brigar com o vocal", "clima etéreo"],
       ["brigar com o vocal → toque quase nada", "muito presente → VOL da guitarra -2"],
       ["Tocar melodia: a faixa pertence ao vocal — só camadas discretas"],
       IR_UKLD,
       "Posição 4 (middle+neck)", "middle+neck", "5-7 (suave)", "7",
       "VOLUME 5-7 · Seletor 4 · Tone 7 (suave, atrás do vocal)",
       ["Swells discretos seguindo a dinâmica do vocal",
        "Menos é mais — sombra, não protagonista"],
    )],
))

# ---------- escreve no defs (idempotente + ordem do álbum) -----------------------
ALBUM_ORDER = ['SOF01', 'AD01', 'WDF01', 'LTF01', 'KTB01', 'CBK01', 'SIA01',
               'ABIETW01', 'OEOD01', 'SFTM01', 'BRT01', 'ONR01', 'TM01', 'BTK02',
               'GGS01', 'MNY01', 'USAT01', 'CLR01', 'BD01', 'ECL01',
               'WYWH01', 'CNW01', 'MOTB01', 'RLH01']
data = json.loads(DEFS_PATH.read_text(encoding='utf-8'))
data['songs'] = [s for s in data['songs'] if s['idAlbum'] != 'PL']
por_id = {s['id']: s for s in PULSE_SONGS}
novas = [por_id[i] for i in ALBUM_ORDER if i in por_id]
data['songs'].extend(novas)
DEFS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
n = sum(len(s['patches']) for s in novas)
print(f"OK: {len(novas)} músicas / {n} patches do Pulse (ordem do álbum) em patches-defs.json")

# Reinsere os momentos de toggle (o add_pulse_defs substitui as músicas do Pulse
# inteiras; sem isto, os momentos seriam perdidos)
r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'add_momentos.py')])
sys.exit(r.returncode)
