"""
gen_indexes.py — Regenera os índices a partir de tools/patches-defs.json:
  - MAPA-DO-ALBUM.md de cada álbum (Beatles/Abbey Road, Zappa/Apostrophe, Janis/Piece of My Heart)
  - patches/README.md

Slots são numerados continuamente entre álbuns (U01…Uxx) na ordem dos álbuns abaixo.

Uso: python tools/gen_indexes.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS = json.load(open(ROOT / 'tools' / 'patches-defs.json', encoding='utf-8'))

ALBUMS = [
    {'key': 'AR',  'root': ROOT / 'patches' / 'Beatles' / 'Abbey Road (1969)', 'display': 'Abbey Road (1969)', 'banda': 'The Beatles'},
    {'key': 'ZP',  'root': ROOT / 'patches' / 'Frank Zappa' / 'Apostrophe (1974)', 'display': 'Apostrophe (\u2019) (1974)', 'banda': 'Frank Zappa'},
    {'key': 'PMH', 'root': ROOT / 'patches' / 'Janis Joplin' / 'Piece of My Heart (1968)', 'display': 'Cheap Thrills — Piece of My Heart (1968)', 'banda': 'Janis Joplin'},
    {'key': 'PL',  'root': ROOT / 'patches' / 'Pink Floyd' / 'Pulse (1995)', 'display': 'Pulse (1995)', 'banda': 'Pink Floyd'},
]

SONG_DIR = {
    'CT01': 'Come Together', 'STH01': 'Something', 'MAX01': "Maxwell's Silver Hammer",
    'OHB01': 'Oh! Darling', 'OTG01': "Octopus's Garden", 'IWY01': "I Want You (She's So Heavy)",
    'HCTS01': 'Here Comes the Sun', 'BCS01': 'Because', 'SKG01': 'Sun King - Mean Mr. Mustard',
    'YNG01': 'You Never Give Me Your Money', 'PTP01': 'Polythene Pam - Bathroom Window',
    'GSC01': 'Golden Slumbers - Carry That Weight', 'END01': 'The End', 'HM201': 'Her Majesty',
    'URM01': 'Uncle Remus', 'PMH01': 'Piece of My Heart',
    'AD01': 'Astronomy Domine', 'WDF01': 'What Do You Want From Me', 'LTF01': 'Learning to Fly',
    'KTB01': 'Keep Talking', 'SOF01': 'Shine On You Crazy Diamond', 'BRT01': 'Breathe',
    'TM01': 'Time', 'BTK02': 'Breathe (Reprise)', 'MNY01': 'Money', 'USAT01': 'Us and Them',
    'CLR01': 'Any Colour You Like', 'BD01': 'Brain Damage', 'ECL01': 'Eclipse',
    'WYWH01': 'Wish You Were Here', 'CNW01': 'Comfortably Numb', 'SFTM01': 'Speak to Me',
    'ABIETW01': 'Another Brick in the Wall', 'MOTB01': 'Mother', 'SIA01': 'Sorrow',
    'OEOD01': 'One of These Days',
    'CBK01': 'Coming Back to Life', 'RLH01': 'Run Like Hell', 'ONR01': 'On the Run',
    'GGS01': 'The Great Gig in the Sky',
}

DISPLAY_SONG = {
    'CT01': 'Come Together', 'STH01': 'Something', 'MAX01': "Maxwell's Silver Hammer",
    'OHB01': 'Oh! Darling', 'OTG01': "Octopus's Garden", 'IWY01': "I Want You (She's So Heavy)",
    'HCTS01': 'Here Comes the Sun', 'BCS01': 'Because', 'SKG01': 'Sun King / Mean Mr. Mustard',
    'YNG01': 'You Never Give Me Your Money', 'PTP01': 'Polythene Pam / Bathroom Window',
    'GSC01': 'Golden Slumbers / Carry That Weight', 'END01': 'The End', 'HM201': 'Her Majesty',
    'URM01': 'Uncle Remus', 'PMH01': 'Piece of My Heart',
    'AD01': 'Astronomy Domine', 'WDF01': 'What Do You Want From Me', 'LTF01': 'Learning to Fly',
    'KTB01': 'Keep Talking', 'SOF01': 'Shine On You Crazy Diamond', 'BRT01': 'Breathe',
    'TM01': 'Time', 'BTK02': 'Breathe (Reprise)', 'MNY01': 'Money', 'USAT01': 'Us and Them',
    'CLR01': 'Any Colour You Like', 'BD01': 'Brain Damage', 'ECL01': 'Eclipse',
    'WYWH01': 'Wish You Were Here', 'CNW01': 'Comfortably Numb', 'SFTM01': 'Speak to Me',
    'ABIETW01': 'Another Brick in the Wall', 'MOTB01': 'Mother', 'SIA01': 'Sorrow',
    'OEOD01': 'One of These Days',
    'CBK01': 'Coming Back to Life', 'RLH01': 'Run Like Hell', 'ONR01': 'On the Run',
    'GGS01': 'The Great Gig in the Sky',
}

# Dossiês do rig real por álbum (bloco "📚 Rig real" do mapa)
ALBUM_RIG = {
    'AR': """## 📚 Rig real do álbum (fontes)

- **John**: Casino (P90) — Come Together direto no canal da mesa; AC30 no crunch; Leslie nos lentos.
- **George**: Les Paul **Lucy**, Strat e Tele — Twin/Bassman/AC30; **Leslie 147RV** nos solos de Something/Because/Sun King.
- **Paul**: Casino no AC30 (Oh! Darling), baixo no resto; primeiro solo de The End.
- **Zero pedais** — todo ganho vem de amp estufado ou do canal da mesa.
- 📖 Fontes: Guitar World *\"Abbey Road guitar gear: the complete guide\"* (Geoff Emerick) · boostguitarpedals.co.uk.""",
    'ZP': """## 📚 Rig real (fontes)

- **Tony Duran**: slide/rhythm guitar (créditos de Apostrophe ('); MusicBrainz) — brilho agudo com ataque crocante.
- **Frank Zappa**: solos cirúrgicos e secos (Rock & Roll Globe: \"scalpel-sharp guitar solos\") — sem reverb, médios à frente.
- **George Duke**: piano elétrico e clavinet preenchendo o meio (co-autor da faixa).
- Sessões: basic track 1972 (Paramount Studios, LA) + overdubs 1973–74.
- 📖 Fontes: Rock & Roll Globe (\"How Frank Zappa Embraced the Mainstream with Apostrophe (')\", 2024) · MusicBrainz (créditos) · Wikipedia (Apostrophe (')).""",
    'PL': """## 📚 Rig real da turnê (fontes)

- **David Gilmour 1994**: Hiwatt **DR103** + preamp Alembic F-2B → WEM Starfinder 4x12 (Fane) **+ Marshall 4x12**; Yamaha RA-200 (rotary) na base limpa.
- **Pedalboard**: Boss CS-2/DynaComp (compressão) · BK Butler Tube Driver (overdrive) · Big Muff "Civil War" (fuzz) · Electric Mistress (flanger) · Uni-Vibe · Boss CE-2 (chorus) · Tremulator · GE-7 · delays TC 2290 + PCM-70 (efeito Binson Echorec).
- **Tim Geaney / Chester Kamen**: guitarras base nos refrões e camadas rítmicas.
- Assinaturas: solos com **delay duração da nota** (1 repetição), espaço entre as frases, **sem speed** — a mão fala.
- 📖 Fontes: gilmourish.com (seção Division Bell Tour 1994 — equipamento confirmado faixa a faixa) · Wikipedia (Pulse, 1995) · Discogs (tracklist).""",
}

# Política de IR (igual ao build_song_patches.py): captura local recomendada por CAB de fábrica.
IR_LOCAL_POR_CAB = {
    'DarkTW 2x12': 'American Twin 2x12',
    'Foxy 1x12':   'Brown Deluxe 1x12',
    'TWD 2x12':    'Tweed Combo 1x12',
    'UK-GN 2x12':  'British Straight 4x12',
}


def ir_recomendada(cab_nome):
    """Arquivo da captura local (Medium Mix) para o CAB do patch, ou None se a fábrica é o alvo."""
    cab_lib = IR_LOCAL_POR_CAB.get(cab_nome)
    if not cab_lib:
        return None
    try:
        data = json.load(open(ROOT / 'tools' / 'ir-library.json', encoding='utf-8'))
    except Exception:
        return None
    for pack in data.get('packs', {}).values():
        for f in pack.get('files', []):
            if f.get('compatible') and Path(f['file']).parts[-2].replace(' Mics', '') == cab_lib:
                nome = Path(f['file']).parts[-1]
                if 'Medium Mix' in nome:
                    return f"{cab_lib} — {nome}"
    return f"{cab_lib} (ver reference/16-ir-library.md)"


def song_row(song, counter, root_rel):
    """Gera (linha da tabela, sequência de slots) de uma música.

    A linha entra na tabela "Música → patches" do mapa (patch · captador ·
    IR recomendada · slots); a sequência alimenta a tabela de slots. Cada
    patch consome um slot do contador global (numeração contínua U01…Uxx
    entre álbuns). Links relativos com espaços escapados para %20.
    """
    parts, slots, pus, irs = [], [], [], []
    for p in song['patches']:
        n = next(counter)
        slot = f"U{n:02d}"
        slots.append(slot)
        link = f"./{SONG_DIR[song['id']]}/{p['nome']}/patch.md".replace(' ', '%20')
        parts.append(f"[`{p['emoji']} {p['nome']}`]({link}) ({p['camada'].split()[0]})")
        pus.append(f"{p['camada'].split()[0]}: {p['doc']['guitarra']['seletorCurto']}")
        cab = p['spec']['modules'].get('CAB', {}).get('name', '')
        ir = ir_recomendada(cab)
        irs.append(f"📁 `{ir}`" if ir else f"⚙️ fábrica `{cab}`")
    row = (f"| **{DISPLAY_SONG[song['id']]}** | {' · '.join(parts)} | "
           f"{' · '.join(pus)} | {' · '.join(irs)} | {', '.join(slots)} |")
    seq = [(s, p['nome'], song['song'], p['camada'], i)
           for s, p, i in zip(slots, song['patches'], irs)]
    return row, seq


def build_mapa(album_key, album, songs, total, rows, seq):
    """Renderiza o MAPA-DO-ALBUM.md de um álbum.

    Recebe as linhas/sequência prontas (uma chamada de song_row por música,
    já com slots numerados) e monta: tabela música→patches, sequência de
    slots, análise das camadas e o dossiê do rig real — bloco dedicado para
    Zappa (ZP) e genérico de Abbey Road para os demais.
    """
    song_rows = '\n'.join(rows)
    slot_rows = '\n'.join(f"| {s} | `{n}` | {m} — {c} | {i} |" for s, n, m, c, i in seq)

    if album_key == 'ZP':
        rig = ALBUM_RIG['ZP']
    elif album_key == 'PL':
        rig = ALBUM_RIG['PL']
    else:
        rig = ALBUM_RIG['AR']

    return f"""# 🎸 {album['display']} — Mapa de patches

### *{album['banda']} · {len(songs)} música(s) · {total} patches (1 conjunto exclusivo por música)*

![Patches](https://img.shields.io/badge/patches-{total}-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Nomes](https://img.shields.io/badge/nome-MÚSICA--CAMADA-6f42c1?style=flat-square)

> 💡 Cada música tem **seus próprios patches**, divididos nas camadas que ela contém (base, solo, riff, clean, arpejos…). Nomenclatura: `MÚSICA+versão` + `CAMADA` — ex.: `STH01BA` = Something 01, **BA**se · `URM01SL` = Uncle Remus 01, **SL**ide.

## 🗺️ Música → patches

| Música | Patches (camada) | Captador (Strat) | IR recomendada | Slots |
|---|---|---|---|---|
{song_rows}

> **📡 IR**: 📁 = o banco local (`impulse_responses/`) tem captura melhor do gabinete real — arquivo indicado na seção 3 do `patch.md`. ⚙️ = o CAB de fábrica já é o alvo correto. Em ambos os casos o `.prst` funciona imediatamente, sem carregar IR.

## 🎛️ Sequência de slots sugerida

| Slot | Patch | Uso | IR (se usar User IR) |
|---|---|---|---|
{slot_rows}

## 🧬 Como as camadas foram decididas

Cada faixa foi analisada isoladamente: o que a guitarra faz em cada seção e se o timbre muda entre elas. Só há mais de um patch quando o **timbre muda de verdade** na gravação.

{rig}

## 📥 Importação

1. **GP-100 Edits** (≥ 1.2.0) conectado à pedaleira (firmware 2.1).
2. Importe cada `patches/<Banda>/{album['display']}/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue os WAVs 📁 da tabela nos slots **User IR 1–4** (GP-100 Edits → IR Manager) e troque o CAB do patch para o User IR correspondente — passo a passo na seção **📡 3** de cada `patch.md`.

---

[`🎸 Biblioteca de patches`](../../README.md) · [`📖 README do projeto`](../../../README.md)
"""


def build_readme(album_blocks, total):
    """Renderiza o patches/README.md (índice geral da biblioteca)."""
    return f"""# 🎸 Biblioteca de patches — GP-100

![Organização](https://img.shields.io/badge/organização-banda%2Fálbum%2Fmúsica%2Fpatch-2ea44f?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Patches](https://img.shields.io/badge/patches-{total}-e02d2d?style=flat-square)

## 🗂️ Estrutura

```
patches/
├── <Banda>/
│   └── <Álbum> (<ano>)/
│       ├── MAPA-DO-ALBUM.md            # música → patches + slots
│       └── <Música>/
│           └── <MUSICA-CAMADA>/        # 1 pasta por patch
│               ├── <MUSICA-CAMADA>.prst  # ✅ importável (single, fw 2.1)
│               ├── patch.md              # documentação prática-primeiro
│               └── spec.json             # fonte do .prst
└── README.md
```

## 🏷️ Nomenclatura (leia-se em 2 segundos)

`MUSICA## + CAMADA` — máximo 12 caracteres (limite do painel da GP-100).

| Código | Significado | | Código | Significado |
|---|---|---|---|---|
| `BA` | base | | `FL` | fills |
| `SO` | solo | | `AR` | arpejos |
| `RI` | riff | | `AC` | acústico |
| `CL` | clean | | `SL` | slide |
| `VO` | voz-líder | | | |

Exemplos: `STH01BA` = Something 01 · Base · `CT01RIF` = Come Together 01 · Riff · `URM01SL` = Uncle Remus 01 · Slide.

> **Regra**: cada música tem patches **exclusivos**. Músicas só ganham mais de um patch quando o timbre muda de verdade entre as seções.

## 📚 Álbuns

| Banda | Álbum | Músicas | Patches | Mapa |
|---|---|---|---|---|
{album_blocks}

## 📄 Cada patch contém

| Arquivo | O que é |
|---|---|
| `<NOME>.prst` | Arquivo **importável** no GP-100 Edits ou direto na pedaleira (single-patch, fw 2.1) |
| `patch.md` | Doc prática-primeiro: guitarra já na seção 1, ajustes finos, objetivo do som, dossiê, técnica |
| `spec.json` | Definição estruturada — regenerável via `tools/build_song_patches.py` |

## 🔧 Regenerar tudo

```bash
python tools/build_song_patches.py   # specs + patch.md + .prst a partir de tools/patches-defs.json
python tools/gen_indexes.py          # mapas dos álbuns + este README
```

---

[`📖 README do projeto`](../README.md)
"""


# ---- monta tudo ----
counter = iter(range(1, 200))
rows_by_album, total_all = {}, 0
for alb in ALBUMS:
    songs = [s for s in DEFS['songs'] if s['idAlbum'] == alb['key']]
    n = sum(len(s['patches']) for s in songs)
    start = total_all + 1
    total_all += n

    local_rows, local_seq = [], []
    for song in songs:
        row, s = song_row(song, counter, alb['root'])
        local_rows.append(row)
        local_seq.extend(s)
    rows_by_album[alb['key']] = (local_rows, local_seq, n, start)

    alb['root'].mkdir(parents=True, exist_ok=True)
    (alb['root'] / 'MAPA-DO-ALBUM.md').write_text(
        build_mapa(alb['key'], alb, songs, n, local_rows, local_seq), encoding='utf-8', newline='\r\n')

album_rows = '\n'.join(
    f"| 🎸 **{alb['banda']}** | **{alb['display']}** | "
    f"{len([s for s in DEFS['songs'] if s['idAlbum'] == alb['key']])} | "
    f"{rows_by_album[alb['key']][2]} | [`MAPA-DO-ALBUM.md`]({(alb['root'].relative_to(ROOT / 'patches')).as_posix().replace(' ', '%20')}/MAPA-DO-ALBUM.md) |"
    for alb in ALBUMS)

(ROOT / 'patches' / 'README.md').write_text(build_readme(album_rows, total_all), encoding='utf-8', newline='\r\n')

print(f"✅ {len(ALBUMS)} mapas + patches/README.md regenerados ({total_all} patches, slots U01–U{total_all:02d}).")
