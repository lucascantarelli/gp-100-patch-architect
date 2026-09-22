#!/usr/bin/env python3
"""
add_wishkah_defs.py — Injeta as 17 músicas do álbum From the Muddy Banks of
the Wishkah (Nirvana, 1996) no tools/patches-defs.json.

Primeiro teste do fluxo novo: desenvolvido na branch
feature/nirvanna-from-the-muddy-banks-of-the-wishkah, PR para a develop.

Álbum ao vivo (gravações 1989–1994, DGC 1996): o rig é o do Kurt ao vivo —
Fender Jaguar/Jag-Stang/Mustang · Boss DS-1 (e DST-2 de 92 em diante) →
Fender Twin Reverb (base) ou Mesa/Boogie Studio Preamp (grandes shows).
Mapeamento GP-100: DST La Charger (família DS do catálogo fw 2.0) · MOD
A-Chorus (Small Clone) · AMP Dark Twin + CAB DarkTW 2x12 (Twin) · DST Red Haze
(fuzz Big Muff de Blew). Tudo com CAB de fábrica no .prst e IR do banco local
documentada (política de 4 passos), nunca embutida.

Momentos de toggle (os stomps do pedido) ficam em tools/add_momentos.py
(bloco "Nirvana (Wishkah)"). Idempotente: re-executar remove e reinsere as músicas do
álbum (ordem da tracklist oficial).

Uso: python tools/add_wishkah_defs.py
"""
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS_PATH = ROOT / 'tools' / 'patches-defs.json'
# Idempotente: re-executar remove e re-insere as músicas do Wishkah (ordem da
# tracklist). Versionamento do defs é responsabilidade do git — nenhum backup.

# ---------- helpers (construção plana, padrão dos seeders de álbum) --------------
OFF = {'PRE': 'Boost', 'DST': 'Blues OD', 'AMP': 'Dark Twin', 'NR': 'Gate 1',
       'CAB': 'DarkTW 2x12', 'EQ': 'EQ 1', 'MOD': 'A-Chorus', 'DLY': 'Slapbk', 'RVB': 'Room'}

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

REF_WISH = ref("Show caseiro/prática: rig ao vivo do álbum (1989–1994)",
               "From the Muddy Banks of the Wishkah (DGC, 1996) · Wikipedia · livenirvana.com")
REF_RIG = ref("Rig: Jaguar/Jag-Stang/Mustang · Boss DS-1 (DST-2 de 92) → Twin Reverb/Mesa",
              "groundguitar.com/kurt-cobain-gear · equipboard.com/pros/kurt-cobain")

def song(id_, song_name, bpm, resumo, refs, patches):
    """Uma música do Wishkah no schema vigente do defs."""
    return {"id": id_, "song": song_name, "idAlbum": "WM", "bpm": bpm,
            "resumo": resumo, "referencias": refs, "patches": patches}

def P(camada, sufixo, nome, emoji, timbre, spec, seletor, seletor_curto,
      volume, tone, receita, tecnicas, teste_riff, teste_drum, escutar,
      ajustes, evite, ir_nota, tipo='Rock', bpm=120):
    """Um patch do Wishkah: spec completo (envelope + modules) + doc."""
    spec_full = {"name": nome, "type": tipo, "bpm": bpm, "volume": 60,
                 "ir_slot": None, "modules": spec}
    return {"camada": camada, "sufixo": sufixo, "nome": nome, "emoji": emoji,
            "timbre": timbre, "spec": spec_full,
            "doc": {"guitarra": {"seletor": seletor, "seletorCurto": seletor_curto,
                                 "volume": volume, "tone": tone, "receita": receita,
                                 "tecnicas": tecnicas},
                    "comoTocar": [], "teste": {"riff": teste_riff, "drum": teste_drum,
                                               "escutar": escutar},
                    "ajustes": ajustes, "evite": evite, "irNota": ir_nota,
                    "momentos": [], "slotSugestao": None}}

# ---------- blocos reutilizáveis --------------------------------------------------
def ds1(gain, tone=48, level=62):
    return mod('La Charger', True, gain, tone, level)

SMALL = mod('A-Chorus', True, 30, 0.5, 50, 0)          # Small Clone "levemente fora"
TWIN_ON = mod('Dark Twin', True, 55, 62, 52, 48, 55, 0)
CAB_TWD = mod('DarkTW 2x12', True, 75, 50)
GATE1 = mod('Gate 1', True, 26)
CHORUS_OFF = mod('A-Chorus', False, 30, 0.5, 50, 0)   # sobressalente = Small Clone do verso


def SPARE_DS(gain):
    """DST desligado com o La Charger do riff-irmão: stomp ON = o som pesado prometido."""
    return mod('La Charger', False, gain, 48, 62)


def SPARE_EQ():
    """EQ desligado com realce pronto: stomp ON = solo com presença."""
    m = mod('EQ 1', False)
    m['params'] = {"1": 3, "5": 56}          # Mid +3 · Level +6
    return m

ROOM_CURTA = mod('Room', True, 20, 19, 31, 0)
ROOM_MEDIA = mod('Room', True, 22, 19, 33, 0)

IR_TWIN = ("Recomendada: American Twin 2x12 — Medium Mix do banco local (User IR 1) — "
           "captura do Twin Reverb, o amp do álbum (Low Cut 4 · High Cut 6500 · Level 0).")

VERSO_LIMPO_DOC = ("Posição 4 (middle+neck)", "middle+neck", "9", "8",
                   "SELETOR 4 · Volume 9 · Tone 8")

# ---------- School (Amsterdam 1991) ------------------------------------------------
SCHOOL_RIF = P('Riff Punk', 'RI', 'SCH01RI', '🎸',
    "O riff mais copyado do grunge: três acordes estourados, ganho no limite do lo-fi — "
    "_DS-1 direto no Twin_",
    chain(dst=ds1(62, 42, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10 (aberto, sem dó)",
    ["Palhetada FORTE e para baixo — o DS-1 vive da agressividade da mão",
     "Deixe as notas se embolarem um pouco: é o som do disco"],
    "riff da intro", "punk rápido 160 bpm",
    ["três acordes estourados e embolados", "ring do Room curto após o corte"],
    ["chipando demais → La Charger Gain -4", "falta corpo → EQ Mid +3"],
    ["Não equalize o embolamento fora: ele é a assinatura"],
    IR_TWIN)

SCHOOL_SO = P('Solo Sujo', 'SO', 'SCH01SO', '🎸',
    "Solo central: mesma distorção, seletor na ponte — _o solo é quase um outro riff_",
    chain(dst=ds1(66, 45, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 1 (bridge)", "bridge", "10", "10",
    "SELETOR 2 · Volume 10 · Tone 10",
    ["Bends de tom inteiro com vibrato pesado",
     "Use o captador da ponte: o solo precisa morder"],
    "solo central", "punk rápido",
    ["lead cortando o embalo do riff", "guia com a mão, não com o pedal"],
    ["some no mix → La Charger Level +4", "agudo gelando → Tone da guitarra 8"],
    ["Gravar em casa: NR ON sempre que o ganho estiver alto"],
    IR_TWIN)

# ---------- Drain You (Del Mar 1991) ------------------------------------------------
DRAIN_AR = P('Arpejo Limpo', 'AR', 'DRY01AR', '✨',
    "Verso: arpejos limpos com chorus, pós-punk — _o verso não tem distorção nenhuma_",
    chain(dst=SPARE_DS(64), amp=TWIN_ON, cab=CAB_TWD, modfx=SMALL,
          rvb=mod('Room', True, 18, 15, 28, 0)), *VERSO_LIMPO_DOC,
    ["Arpeje entre a 5ª e a 2ª cordas, palhetada alternada suave",
     "O chorus entra DEPOIS da mão: se a mão for pesada, nenhum pedal conserta"],
    "verso inteiro (arpejos)", "grunge 122 bpm",
    ["arpejo cristalino com brilho aquático", "transição limpa → punk no refrão"],
    ["chorus nadando demais → A-Chorus Depth -2", "sem corpo → seletor 3"],
    ["NÃO ligue o DST: o contraste limpo/distorcido é a dinâmica da música"],
    IR_TWIN)

DRAIN_RIF = P('Refrão Punk', 'RI', 'DRY01RI', '⚡',
    "Refrão: wall of sound de DS-1 — _do quiet-grunge para o estouro absoluto_",
    chain(dst=ds1(64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Acordes cheios, palhetada total (6 cordas), para baixo",
     "Intensidade vem do braço: o ganho já está no teto útil"],
    "refrão (\"one baby to another says I'm lucky…\")", "grunge 122 bpm",
    ["parede de ruído controlada", "nada do arpejo vazando no refrão"],
    ["embolando demais → seletor 3 · Tone 8", "grilos com ganho alto → NR Thr -2"],
    ["O stomp do DST É o refrão inteiro: ligue e afogue tudo"],
    IR_TWIN)

DRAIN_SO = P('Solo', 'SO', 'DRY01SO', '🎸',
    "Solo central: distorção com pico de médios para cortar o paredão",
    chain(dst=ds1(68, 55, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 1 (bridge)", "bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases curtas e deformadas — o solo é feedback e atitude, não virtuosismo",
     "Bend forte e vibrato largo no final da frase"],
    "solo central", "grunge 122 bpm",
    ["lead cortando o wall of sound", "distorção gorda mas articulada"],
    ["perdido no mix → La Charger Tone +5", "susto de volume → Level -3"],
    ["Entre verso e solo o seletor muda 4 → 2: meia música no seletor"],
    IR_TWIN)

# ---------- Aneurysm (Del Mar 1991) -------------------------------------------------
ANE_AR = P('Arpejo Quebrado', 'AR', 'ANE01AR', '✨',
    "Quiet-loud: arpejo lento (\"come on over, do the twist…\") que explode no refrão",
    chain(dst=SPARE_DS(66), amp=TWIN_ON, cab=CAB_TWD, modfx=SMALL,
          rvb=mod('Room', True, 18, 15, 28, 0)), *VERSO_LIMPO_DOC,
    ["Arpejo descendo, tempo largo — é hipnose",
     "No refrão, raiva: palhetada total e para baixo"],
    "intro/verso (quiet)", "90 bpm quiet-loud",
    ["arpejo quebrado e hipnótico", "explosão de refrão dá contraste total"],
    ["arpejo rápido demais → volte ao tempo: é hipnose, não corrida"],
    ["Tocar o refrão neste patch não: o contraste é o momento de toggle"],
    IR_TWIN)

ANE_RIF = P('Refrão Pesado', 'RI', 'ANE01RI', '⚡',
    "O refrão inteiro de DS-1 no talo, bateria e baixo por cima",
    chain(dst=ds1(66), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Palhetada total, dinâmica no braço",
     "Deixe o Room curto dar a sala do show ao vivo"],
    "refrão", "grunge 90 bpm",
    ["parede de som com ataque de palhetada", "corte seco no fim da frase"],
    ["faltou grão → La Charger Gain +3"],
    ["NÃO suavize: o refrão é propositalmente esburracado"],
    IR_TWIN)

ANE_SO = P('Solo Livre', 'SO', 'ANE01SO', '🎸',
    "Solo de fechamento: jam livre — distorção solta, vibrato largo",
    chain(dst=ds1(70, 52, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_MEDIA),
    "Posição 1 (bridge)", "bridge", "10", "10",
    "SELETOR 2 · Volume 10 · Tone 10",
    ["Frases longas com vibrato largo, sem pressa",
     "Deixe a distorção trabalhar os harmônicos"],
    "solo final", "grunge 90 bpm",
    ["lead solto sobre a jam", "vibrato largo carregando a frase"],
    ["gelando → Tone 8", "engolindo o baixo → La Charger Level -3"],
    ["É o single do álbum: o patch de solo completa o de arpejo"],
    IR_TWIN)

# ---------- Smells Like Teen Spirit (Del Mar 1991) -----------------------------------
SLTS_CL = P('Verso Limpo', 'CL', 'SLT01CL', '✨',
    "Verso: power chord limpo com chorus — _o erro clássico é tocar o verso sujo_",
    chain(dst=SPARE_DS(66), amp=TWIN_ON, cab=CAB_TWD, modfx=SMALL, eq=SPARE_EQ(),
          rvb=mod('Room', True, 18, 15, 28, 0)),
    "Posição 2 (bridge+middle)", "bridge+middle", "9", "9",
    "SELETOR 3 · Volume 9 · Tone 9",
    ["Power chords com palhetada firme, mas sem distorção",
     "O chorus dá o \"não estou em casa\" do verso"],
    "verso (F–Bb–Ab–Db)", "grunge 117 bpm",
    ["acordes LIMPOS com leve brilho de chorus", "dinâmica de verso para pré-refrão"],
    ["sujo demais → Vol da guitarra 8", "chorus escondido → A-Chorus Mix +4"],
    ["Nunca ligue o DST no verso: o contraste é tudo"],
    IR_TWIN)

SLTS_RIF = P('Riff Punk', 'RI', 'SLT01RI', '⚡',
    "O riff do século: F–Bb–Ab–Db com DS-1 e ataque total",
    chain(dst=ds1(66), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Palhetada para baixo, com STOP seco no \"hello, hello…\"",
     "Segure o acorde no staccato: o espaço é parte do riff"],
    "riff principal", "grunge 117 bpm",
    ["quatro acordes com peso máximo", "corte seco no break"],
    ["embolando → Tone 8", "sem mordida → La Charger Tone +4"],
    ["Stomp DST = liga o peso do refrão; desligue para o verso deste mesmo patch"],
    IR_TWIN)

SLTS_SO = P('Solo Gaguejado', 'SO', 'SLT01SO', '🎸',
    "Solo: a melodia do vocal gaguejada na distorção — praticável e icônico",
    chain(dst=ds1(66, 50, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF,
          eq=SPARE_EQ(), rvb=mod('Room', True, 20, 19, 31, 0)),
    "Posição 1 (bridge)", "bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Toque a melodia do vocal em blocos de duas notas",
     "Repita a frase com pequenas variações (a gagueira é proposital)"],
    "solo (após o 2º refrão)", "grunge 117 bpm",
    ["melodia do vocal reconhecível na distorção", "blocos de duas notas"],
    ["falta mordida → Tone +3", "passando do ponto → Gain -3"],
    ["É o solo mais praticável do álbum: comece por aqui"],
    IR_TWIN)

# ---------- Polly (London Astoria 1989 — elétrica, rara) -----------------------------
POLLY_CL = P('Clean Espanhol', 'CL', 'POL01CL', '🧺',
    "A elétrica RARA (1989): verso em palm mute limpo e refrão que explode — "
    "_o antônimo da Unplugged_",
    chain(dst=SPARE_DS(66), amp=TWIN_ON, cab=CAB_TWD, eq=SPARE_EQ(), rvb=ROOM_CURTA),
    "Posição 4 (middle+neck)", "middle+neck", "8", "6",
    "SELETOR 4 · Volume 8 · Tone 6 (escuro, quase jazz)",
    ["Verso: acordes em palm mute, seco",
     "Refrão: palhetada total e para baixo — aqui o Tone da guitarra sobe para 9"],
    "verso + refrão (elétrica 1989)", "80 bpm",
    ["palm mute seco no verso", "explosão de refrão (stomp DST)"],
    ["refrão fraco → Vol 10 + Tone 9", "verso brilhante demais → Tone 5"],
    ["Este patch é o contraste da Unplugged: mesmo acorde, corpo elétrico"],
    IR_TWIN)

# ---------- Breed (London Astoria 1989 — \"Imodium\", mais lenta) ----------------------
BREED_RIF = P('Riff Lo-Fi', 'RI', 'BRE01RI', '⚡',
    "Riff com raiz grave: a versão aqui é mais lenta que o disco (era \"Imodium\")",
    chain(dst=ds1(68, 40, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Riff com pestana na 6ª corda, dinâmica no braço",
     "Deixe a distorção lo-fi embolar as notas graves"],
    "riff principal", "grunge 140 bpm",
    ["riff grave e embolado", "energia bruta sem definição cirúrgica"],
    ["graves virando lama → CAB High Cut +2", "falta mordida → Tone +4"],
    ["A versão de 1989 é mais lenta: não acelere para o Nevermind"],
    IR_TWIN)

# ---------- Lithium (Paradiso 1991) --------------------------------------------------
LITH_AR = P('Arpejo Pop', 'AR', 'LIT01AR', '✨',
    "Verso: arpejos pop com chorus — a base da música é um colchão limpo",
    chain(dst=SPARE_DS(64), amp=TWIN_ON, cab=CAB_TWD, modfx=SMALL,
          rvb=mod('Room', True, 18, 15, 28, 0)), *VERSO_LIMPO_DOC,
    ["Arpejo pop, palhetada alternada",
     "Com o chorus quase imperceptível: sustentação, não efeito"],
    "verso (\"I'm so happy…\")", "grunge 120 bpm",
    ["arpejo pop redondo", "transição para o refrão sujo"],
    ["muito brilho → Tone 7", "sem redondeza → seletor 4"],
    ["O contraste verso/refrão faz a música: seletor + stomp DST"],
    IR_TWIN)

LITH_RIF = P('Refrão Punk', 'RI', 'LIT01RI', '⚡',
    "Refrão: \"yeah, yeah\" com acordes estourados",
    chain(dst=ds1(64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Acordes cheios, palhetada total",
     "Leve embolamento é aceitável: é grunge"],
    "refrão", "grunge 120 bpm",
    ["acordes estourados com \"yeah, yeah\"", "energia do refrão inteiro"],
    ["lama nos graves → Tone 8", "sem corpo → seletor 3 · Gain +2"],
    ["Stomp DST = refrão inteiro; sem ele o patch é o verso limpo"],
    IR_TWIN)

LITH_SO = P('Solo', 'SO', 'LIT01SO', '🎸',
    "Solo curto e direto: distorção com o seletor na ponte",
    chain(dst=ds1(66, 50, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF,
          eq=SPARE_EQ(), rvb=mod('Room', True, 20, 19, 31, 0)),
    "Posição 1 (bridge)", "bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Frases curtas, poucas notas",
     "Bend no final para fechar"],
    "solo (após 2º refrão)", "grunge 120 bpm",
    ["lead enxuto e direto", "respirando no espaço do refrão"],
    ["falta presença → Tone +3"],
    ["Não estique: o solo é curto e pontual"],
    IR_TWIN)

# ---------- Been a Son (Paradiso 1991) -----------------------------------------------
BEEN_RIF = P('Riff Punk', 'RI', 'BEE01RI', '⚡',
    "Base punk rápida e rasgada — a banda em modo rambo",
    chain(dst=ds1(64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Palhetada punk para baixo, constante",
     "Acordes curtos, com acento no 2 e no 4"],
    "base inteira", "punk 160 bpm",
    ["base rápida e rasgada", "consistência rítmica sem perder o ataque"],
    ["cansando o braço → Gain +2 para compensar", "embolando → Tone 8"],
    ["É uma base: o foco é o pulso, não a harmonia"],
    IR_TWIN)

BEEN_SO = P('Solo Sujo', 'SO', 'BEE01SO', '🎸',
    "Solo: curto, doente e espectral — pura atitude",
    chain(dst=ds1(68, 55, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 1 (bridge)", "bridge", "10", "10",
    "SELETOR 2 · Volume 10 · Tone 10",
    ["Frases dissonantes, bends furiosos",
     "Não busque \"bonito\": busque tenso"],
    "solo central", "punk 160 bpm",
    ["lead tenso e dissonante", "atitude por cima da base rápida"],
    ["passando do ponto → Gain -3"],
    ["É o oposto do solo-pop de Lithium: rasgue o pick"],
    IR_TWIN)

# ---------- Sliver (Springfield 1993 — era In Utero) ---------------------------------
SLIV_RIF = P('Riff Alternado', 'RI', 'SLV01RI', '⚡',
    "\"Grandma take me home\": palm mute no verso, DS-1 no refrão — "
    "_o stomp DST troca a seção_",
    chain(dst=ds1(64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF, rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Verso: acordes secos em palm mute com o DST DESLIGADO (stomp)",
     "Refrão: ligue o DST e afogue tudo"],
    "verso + refrão", "grunge 140 bpm",
    ["contraste claro entre verso seco e refrão sujo", "punch do palm mute"],
    ["refrão fraco → Gain +3", "verso sujo demais → Vol da guitarra 8"],
    ["Aqui o stomp não é detalhe: É a estrutura da música"],
    IR_TWIN)

SLIV_AR = P('Intro do Coro', 'AR', 'SLV01AR', '🎺',
    "A intro do coro infantil (sample no show): colchão limpo com vibe",
    chain(dst=SPARE_DS(70), amp=TWIN_ON, cab=CAB_TWD, modfx=mod('Vibe', True, 45, 0.5, 0),
          rvb=ROOM_CURTA),
    "Posição 4 (middle+neck)", "middle+neck", "8", "7",
    "SELETOR 4 · Volume 8 · Tone 7",
    ["Acordes longos com swells de volume",
     "A vibe dá o ar psicodélico do sample"],
    "intro (antes do \"grandma\")", "grunge 140 bpm",
    ["colchão ondulante com vibe", "entrada do riff com contraste total"],
    ["vibe enjoativa → Vibe Intensidade -5"],
    ["É um patch de textura: não brigue com o SLV01RI"],
    IR_TWIN)

# ---------- Spank Thru (Roma 1991) ----------------------------------------------------
SPAN_SO = P('Solo Instrumental', 'SO', 'SPK01SO', '🎸',
    "A única versão lançada do show de Roma: jam instrumental do início da banda",
    chain(dst=ds1(66, 50, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_MEDIA),
    "Posição 1 (bridge)", "bridge", "10", "9",
    "SELETOR 2 · Volume 10 · Tone 9",
    ["Jam: toque o que a base pede, com bends e vibrato",
     "A estrutura é solta: escute a base e responda"],
    "música inteira (instrumental)", "jam 130 bpm",
    ["jam instrumental coesa", "frases respondendo à base"],
    ["falta coesão → toque menos notas", "gelando → Tone 8"],
    ["É a música mais antiga do set: mais improvisada, menos \"certa\""],
    IR_TWIN)

# ---------- Negative Creep (Paramount 1991) -------------------------------------------
NEGA_RIF = P('Riff Drop D', 'RI', 'NEG01RI', '⚡',
    "Drop D cromático e doente: o riff mais pesado do álbum",
    chain(dst=ds1(70, 40, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Drop D: afine a 6ª em D e riff cromático na corda grave",
     "Palm mute no verso, aberto no refrão"],
    "riff principal", "grunge 110 bpm",
    ["riff cromático pesado com drop D", "sujeira controlada nos graves"],
    ["lama total → Tone +4", "sem peso → Gain +3"],
    ["Precisa da 6ª em D: sem drop D, o riff não existe"],
    IR_TWIN)

NEGA_SO = P('Feedback Solo', 'SO', 'NEG01SO', '🎸',
    "Solo: grito de guitarra — bent notes, feedback e caos controlado",
    chain(dst=ds1(72, 45, 64), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD,
          rvb=mod('Room', True, 24, 22, 35, 0)),
    "Posição 1 (bridge)", "bridge", "10", "10",
    "SELETOR 2 · Volume 10 · Tone 10",
    ["Bend com o vibrato do braço e sustente",
     "Encoste o corpo da guitarra na caixa para FEEDBACK (em casa: ganho alto + Room)"],
    "solo central", "grunge 110 bpm",
    ["lead caótico e gritado", "feedback respondendo ao bend"],
    ["caos demais → Gain -4", "sem sustain → Vol 10 · Room Mix +5"],
    ["É o solo mais \"errado\" do álbum — e é assim que ele é bom"],
    IR_TWIN)

# ---------- Blew (Paradiso 1991 — com fuzz) -------------------------------------------
BLEW_RIF = P('Riff Fuzz', 'RI', 'BLE01RI', '🌊',
    "O riff em Em com FUZZ: o som do desespero — _Red Haze no lugar do DS-1_",
    chain(dst=mod('Red Haze', True, 62, 45), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD,
          eq=SPARE_EQ(), rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "7",
    "SELETOR 3 · Volume 10 · Tone 7 (o fuzz escurece o grave da Strat)",
    ["Riff lento e hipnótico, com muito sustain",
     "O fuzz sustenta: deixe as notas morrerem sozinhas"],
    "riff principal", "grunge 98 bpm",
    ["fuzz denso e encorpado", "sustain longo nas notas terminais"],
    ["fuzz embolando → Red Haze VOL -3", "sem grão → VOL +3"],
    ["Fuzz é diferente de DS-1: ele SUSTENTA, não corta"],
    IR_TWIN)

BLEW_SO = P('Solo Psicodélico', 'SO', 'BLE01SO', '🎸',
    "Solo final: harmônicos e bends sobre o fuzz — o momento mais \"stoner\" da banda",
    chain(dst=mod('Red Haze', True, 66, 48), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD,
          rvb=mod('Room', True, 24, 22, 35, 0)),
    "Posição 1 (bridge)", "bridge", "10", "7",
    "SELETOR 2 · Volume 10 · Tone 7",
    ["Bends longos com harmônicos naturais",
     "Deixe o fuzz trabalhar os harmônicos"],
    "solo final", "grunge 98 bpm",
    ["harmônicos gritando no fuzz", "vibrato largo fechando a música"],
    ["muito seco → Room Mix +5", "fuzz estrangulando → VOL -2"],
    ["É o único patch do álbum sem DS-1: o fuzz é a identidade"],
    IR_TWIN)

# ---------- tourette's (Reading 1992) --------------------------------------------------
TOUR_RIF = P('Riff Caótico', 'RI', 'TOU01RI', '⚡',
    "O caos de 1:30 do Reading '92: screamo punk, sem respiro",
    chain(dst=ds1(70), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Palhetada total, sem pausa para respirar",
     "É gritado na voz E na guitarra: tudo no máximo"],
    "música inteira", "screamo 170 bpm",
    ["caos alegre e controlado", "energia sem pausa por 90 segundos"],
    ["cansaço no braço → Gain +2", "embolando → Tone 8"],
    ["Não tente \"arrumar\": o caos É a música"],
    IR_TWIN)

# ---------- Scentless Apprentice (Seattle 1993 — era In Utero) -------------------------
SCE_RIF = P('Riff Denso', 'RI', 'SCE01RI', '⚡',
    "O riff coescrito com Grohl: denso e repetitivo — _a banda empurrando na mesma direção_",
    chain(dst=ds1(68, 42, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Riff em loop com acentuação forte no tempo",
     "Deixe a distorção embolar: é densidade, não definição"],
    "riff principal", "grunge 120 bpm",
    ["riff denso em loop", "acento de braço marcando a levada"],
    ["lama total → Tone +4", "sem peso → Gain +2"],
    ["O riff é um loop: a expressão está no ataque, não nas notas"],
    IR_TWIN)

# ---------- Heart-Shaped Box (Seattle 1993) ---------------------------------------------
HSB_AR = P('Verso Claro', 'AR', 'HSB01AR', '✨',
    "Verso: o colchão limpo entre as explosões — _o quiet-loud mais famoso de In Utero_",
    chain(dst=SPARE_DS(66), amp=TWIN_ON, cab=CAB_TWD, modfx=SMALL,
          rvb=mod('Room', True, 20, 17, 30, 0)),
    "Posição 4 (middle+neck)", "middle+neck", "9", "7",
    "SELETOR 4 · Volume 9 · Tone 7",
    ["Toque o colchão de acordes com a mão solta",
     "Deixe o chorus e a mão direita fazerem o embalo"],
    "verso (colchão)", "grunge 100 bpm",
    ["colchão limpo embalado", "explosão do refrão por cima"],
    ["muito escuro → Tone 8", "chorus forte demais → Depth -2"],
    ["Não ligue o DST no verso: o contraste é o refrão inteiro"],
    IR_TWIN)

HSB_RIF = P('Refrão Pesado', 'RI', 'HSB01RI', '⚡',
    "Refrão: DS-1 no talo com o grave da single coil mordendo",
    chain(dst=ds1(66, 44, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, modfx=CHORUS_OFF,
          eq=SPARE_EQ(), rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Palhetada total e para baixo",
     "Deixe o Room curto dar a sala do show"],
    "refrão ('hey! wait!')", "grunge 100 bpm",
    ["parede de som com o grave presente", "corte seco no fim do refrão"],
    ["embolando → Tone 8", "sem mordida → La Charger Tone +4"],
    ["Stomp DST = o refrão; desligue e volte ao colchão do verso"],
    IR_TWIN)

# ---------- Milk It (Seattle 1994) ------------------------------------------------------
MIL_RIF = P('Quiet-Loud', 'RI', 'MIL01RI', '⚡',
    "A montanha-russa de In Utero: pausa seca → parede de DS-1 — _stomp DST é a música_",
    chain(dst=ds1(70, 42, 62), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD, eq=SPARE_EQ(),
          rvb=ROOM_CURTA),
    "Posição 2 (bridge+middle)", "bridge+middle", "10", "10",
    "SELETOR 3 · Volume 10 · Tone 10",
    ["Verso: acordes secos e espaçados com DST OFF (stomp)",
     "Refrão: DST ON e a parede desce"],
    "verso + refrão", "grunge 110 bpm",
    ["silêncio e peso alternando", "punch do corte seco"],
    ["refrão fraco → Gain +2", "verso sujo demais → Vol da guitarra 8"],
    ["A estrutura É o stomp: sem trocar de patch, a música inteira cabe aqui"],
    IR_TWIN)

# ---------- Intro (London Astoria 1989 — aquecimento) ----------------------------------
INTRO_AM = P('Texturas', 'AM', 'WIS01AM', '🎺',
    "O aquecimento do show: acorde distorcido + feedback sob a fala — textura para camadas caseiras",
    chain(dst=ds1(70), amp=TWIN_ON, nr=GATE1, cab=CAB_TWD,
          rvb=mod('Room', True, 26, 22, 38, 0)),
    "Posição 1 (bridge)", "bridge", "10", "10",
    "SELETOR 2 · Volume 10 · Tone 10",
    ["Toque o acorde e deixe o feedback crescer",
     "O volume da guitarra controla a densidade da textura"],
    "acorde inicial + fala", "livre",
    ["textura crescendo devagar", "feedback controlado"],
    ["muito denso → Vol 8", "sem corpo → Room Mix +4"],
    ["Não toque melodia: a faixa é a fala do Kurt com a guitarra por trás"],
    IR_TWIN)

# ---------- assemble -------------------------------------------------------------------
WISHKAH_SONGS = [
    song('WIS01', 'Intro', 120,
         "Fala do Kurt + acorde distorcido de aquecimento (Londres 1989) — patch de textura para camadas caseiras.",
         [REF_WISH, REF_RIG], [INTRO_AM]),
    song('SCH01', 'School', 160,
         "O riff mais copyado do grunge: três acordes, ganho no teto, solo central.",
         [REF_WISH, REF_RIG], [SCHOOL_RIF, SCHOOL_SO]),
    song('DRY01', 'Drain You', 122,
         "Verso em arpejos limpos com chorus; refrão é parede de DS-1; solo no meio.",
         [REF_WISH, REF_RIG], [DRAIN_AR, DRAIN_RIF, DRAIN_SO]),
    song('ANE01', 'Aneurysm', 90,
         "Quiet-loud: arpejo quebrado no verso, explosão no refrão, solo de jam no final.",
         [REF_WISH, REF_RIG], [ANE_AR, ANE_RIF, ANE_SO]),
    song('SLT01', 'Smells Like Teen Spirit', 117,
         "O hino: verso limpo com chorus (o erro clássico é tocar sujo), refrão de DS-1, solo gaguejado.",
         [REF_WISH, REF_RIG], [SLTS_CL, SLTS_RIF, SLTS_SO]),
    song('BEE01', 'Been a Son', 160,
         "Base punk rápida e rasgada com solo curto e dissonante (Paradiso 1991).",
         [REF_WISH, REF_RIG], [BEEN_RIF, BEEN_SO]),
    song('LIT01', 'Lithium', 120,
         "Arpejos pop no verso, \"yeah yeah\" estourado no refrão, solo curto na ponte.",
         [REF_WISH, REF_RIG], [LITH_AR, LITH_RIF, LITH_SO]),
    song('SLV01', 'Sliver', 140,
         "\"Grandma take me home\": palm mute no verso, DS-1 no refrão; intro de coro com vibe (era In Utero).",
         [REF_WISH, REF_RIG], [SLIV_RIF, SLIV_AR]),
    song('SPK01', 'Spank Thru', 130,
         "Jam instrumental do show de Roma (nov/1991) — a única versão lançada dessa noite.",
         [REF_WISH, REF_RIG], [SPAN_SO]),
    song('SCE01', 'Scentless Apprentice', 120,
         "Riff denso coescrito com Grohl (Seattle 1993, era In Utero).",
         [REF_WISH, REF_RIG], [SCE_RIF]),
    song('HSB01', 'Heart-Shaped Box', 100,
         "Colchão limpo no verso, parede de DS-1 no refrão (Seattle 1993).",
         [REF_WISH, REF_RIG], [HSB_AR, HSB_RIF]),
    song('MIL01', 'Milk It', 110,
         "Pausa seca → parede de DS-1: a montanha-russa quiet-loud (Seattle 1994).",
         [REF_WISH, REF_RIG], [MIL_RIF]),
    song('NEG01', 'Negative Creep', 110,
         "Drop D cromático e doente; solo é grito de guitarra com feedback (Paramount 1991).",
         [REF_WISH, REF_RIG], [NEGA_RIF, NEGA_SO]),
    song('POL01', 'Polly', 80,
         "A elétrica rara de 1989: palm mute seco no verso, explosão no refrão — antônimo da Unplugged.",
         [REF_WISH, REF_RIG], [POLLY_CL]),
    song('BRE01', 'Breed', 140,
         "A \"Imodium\" de 1989: mais lenta que o disco, riff com raiz grave.",
         [REF_WISH, REF_RIG], [BREED_RIF]),
    song('TOU01', "Tourette's", 170,
         "90 segundos de caos punk do Reading '92 — gritado na voz e na guitarra.",
         [REF_WISH, REF_RIG], [TOUR_RIF]),
    song('BLE01', 'Blew', 98,
         "O fecho: riff com fuzz (Red Haze) e solo psicodélico — o momento stoner da banda (Paradiso 1991).",
         [REF_WISH, REF_RIG], [BLEW_RIF, BLEW_SO]),
]

# ---------- escreve no defs (idempotente + ordem da tracklist oficial) -----------------
ALBUM_ORDER = ['WIS01', 'SCH01', 'DRY01', 'ANE01', 'SLT01', 'BEE01', 'LIT01',
               'SLV01', 'SPK01', 'SCE01', 'HSB01', 'MIL01', 'NEG01', 'POL01',
               'BRE01', 'TOU01', 'BLE01']
data = json.loads(DEFS_PATH.read_text(encoding='utf-8'))

# álbum novo (idempotente)
data['albums']['WM'] = {
    "banda": "Nirvana",
    "album": "From the Muddy Banks of the Wishkah (live)",
    "ano": 1996,
    "display": "Muddy Banks (1996)",
    "pasta": "Nirvana/From the Muddy Banks (1996)",
    "rig": "## 📚 Rig real (fontes)\n\n"
           "- **Kurt Cobain ao vivo (1989–1994)**: Fender **Jaguar / Jag-Stang / Mustang** "
           "(single coils) · pedal **Boss DS-1** (e **DST-2** de 92 em diante) → "
           "**Fender Twin Reverb** (base) ou **Mesa/Boogie Studio Preamp** (grandes shows).\n"
           "- **Chorus**: Electro-Harmonix **Small Clone** (versos limpos do período).\n"
           "- **Fuzz**: Big Muff em \"Blew\".\n"
           "- Recriação GP-100: DST **La Charger** (família DS do catálogo fw 2.0) · MOD "
           "**A-Chorus** · AMP **Dark Twin** + CAB **DarkTW 2x12** (Twin) · fuzz **Red Haze**.\n"
           "- 📖 Fontes: Wikipedia (From the Muddy Banks of the Wishkah, 1996 — tracklist e "
           "venues) · livenirvana.com (guia oficial do álbum) · groundguitar.com/kurt-cobain-gear "
           "· equipboard.com/pros/kurt-cobain."
}

# músicas do álbum (idempotente): remove e reinsere na ordem da tracklist
data['songs'] = [s for s in data['songs'] if s['idAlbum'] != 'WM']
por_id = {s['id']: s for s in WISHKAH_SONGS}
data['songs'].extend([por_id[i] for i in ALBUM_ORDER if i in por_id])

DEFS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
n = sum(len(s['patches']) for s in data['songs'] if s['idAlbum'] == 'WM')
print(f"OK: {len(ALBUM_ORDER)} músicas / {n} patches do Wishkah (ordem da tracklist) em patches-defs.json")

# momentos de toggle (os stomps) para os patches novos
r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'add_momentos.py')])
sys.exit(r.returncode)
