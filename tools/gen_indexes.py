"""
gen_indexes.py — Regenera os índices da biblioteca a partir da FONTE ÚNICA
(tools/patches-defs.json):
  - MAPA-DO-ALBUM.md de cada álbum (bloco `albums` do defs)
  - patches/README.md (índice geral da biblioteca)

Nenhum dado de música/álbum/IR vive neste arquivo: nome de pasta, título de
exibição, dossiê do rig real e recomendação de IR vêm de `albums`, `ir_local` e
do campo `pasta`/`display` de cada música no defs. Antes esses literais existiam
aqui E em build_song_patches.py — e divergiram (o mapa recomendava "fábrica"
onde o patch.md mandava carregar uma IR do banco local, nos 38 patches do Pulse).

Os slots U01…Uxx saem de uma passada única sobre defs['songs'], na MESMA ordem
usada por build_song_patches.py: as duas pontas não podem mais ficar defasadas.

Uso: python tools/gen_indexes.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 → UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS_PATH = ROOT / 'tools' / 'patches-defs.json'


# ---- carregamento ---------------------------------------------------------------

def load_defs():
    """Lê tools/patches-defs.json (fonte única: meta, albums, ir_local, songs)."""
    return json.loads(DEFS_PATH.read_text(encoding='utf-8'))


def load_ir_library():
    """Manifesto tools/ir-library.json ({'packs': ...}) ou None — com UM aviso no stderr.

    Sem o manifesto o mapa passaria a dizer "o CAB de fábrica já é o alvo" em
    todos os álbuns sem que ninguém percebesse; o aviso existe para isso.
    """
    try:
        return json.loads((ROOT / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
    except Exception as exc:
        print(f"AVISO: não li tools/ir-library.json ({exc}) — o mapa vai marcar todos os "
              f"cabs como 'fábrica'. Rode: python tools/ir_library.py", file=sys.stderr)
        return None


# ---- dados derivados ------------------------------------------------------------

def album_order(defs):
    """Chaves de álbum na ordem em que aparecem em defs['songs'] (ordem dos slots)."""
    vistos = []
    for song in defs['songs']:
        if song['idAlbum'] not in vistos:
            vistos.append(song['idAlbum'])
    return vistos


def slot_map(defs):
    """{'NOME_DO_PATCH': 'U01'} — numeração contínua entre álbuns, ordem do defs.

    Mesma passada de build_song_patches.main(): se um álbum novo entrar, os dois
    scripts continuam concordando sobre o slot de cada patch.
    """
    mapa, n = {}, 0
    for song in defs['songs']:
        for patch in song['patches']:
            n += 1
            mapa[patch['nome']] = f"U{n:02d}"
    return mapa


def song_pasta(song):
    """Nome da pasta da música (defs['pasta'], ou o próprio nome da música)."""
    return song.get('pasta') or song['song']


def song_display(song):
    """Título de exibição da música nas tabelas (defs['display'], ou o nome)."""
    return song.get('display') or song['song']


def album_root(album):
    """Path da pasta do álbum dentro de patches/ (derivado de albums[..]['pasta'])."""
    return ROOT / 'patches' / album['pasta']


def ir_recomendada(defs, ir_lib, cab_nome):
    """Arquivo da captura local (Medium Mix) para o CAB do patch, ou None.

    None significa "o CAB de fábrica já é o alvo" — inclusive quando o manifesto
    de IRs não pôde ser lido (o aviso já foi dado por load_ir_library).
    """
    par = defs['ir_local'].get(cab_nome)
    if not par or not ir_lib:
        return None
    cab_lib = par['captura']
    for pack in ir_lib.get('packs', {}).values():
        for f in pack.get('files', []):
            if f.get('compatible') and Path(f['file']).parts[-2].replace(' Mics', '') == cab_lib:
                nome = Path(f['file']).parts[-1]
                if 'Medium Mix' in nome:
                    return f"{cab_lib} — {nome}"
    return f"{cab_lib} (ver reference/16-ir-library.md)"


def song_row(defs, song, slots, ir_lib):
    """Gera (linha da tabela, sequência de slots) de uma música.

    A linha entra na tabela "Música → patches" do mapa (patch · captador ·
    IR recomendada · slots); a sequência alimenta a tabela de slots. Links
    relativos com espaços escapados para %20.
    """
    parts, linha_slots, pus, irs = [], [], [], []
    for p in song['patches']:
        slot = slots[p['nome']]
        linha_slots.append(slot)
        link = f"./{song_pasta(song)}/{p['nome']}/patch.md".replace(' ', '%20')
        parts.append(f"[`{p['emoji']} {p['nome']}`]({link}) ({p['camada'].split()[0]})")
        pus.append(f"{p['camada'].split()[0]}: {p['doc']['guitarra']['seletorCurto']}")
        cab = p['spec']['modules'].get('CAB', {}).get('name', '')
        ir = ir_recomendada(defs, ir_lib, cab)
        irs.append(f"📁 `{ir}`" if ir else f"⚙️ fábrica `{cab}`")
    row = (f"| **{song_display(song)}** | {' · '.join(parts)} | "
           f"{' · '.join(pus)} | {' · '.join(irs)} | {', '.join(linha_slots)} |")
    seq = [(s, p['nome'], song['song'], p['camada'], i)
           for s, p, i in zip(linha_slots, song['patches'], irs)]
    return row, seq


# ---- renderização ---------------------------------------------------------------

def build_mapa(album_key, album, songs, total, rows, seq):
    """Renderiza o MAPA-DO-ALBUM.md de um álbum.

    Recebe as linhas/sequência prontas (uma chamada de song_row por música,
    já com slots numerados) e monta: tabela música→patches, sequência de
    slots, análise das camadas e o dossiê do rig real (album['rig'], definido
    por álbum no defs — nunca reaproveitado de outro álbum).
    """
    song_rows = '\n'.join(rows)
    slot_rows = '\n'.join(f"| {s} | `{n}` | {m} — {c} | {i} |" for s, n, m, c, i in seq)
    rig = album.get('rig', '')

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
2. Importe cada `patches/{album['pasta']}/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue nos slots de User IR (GP-100 Edits → IR Manager) os WAVs 📁 marcados na tabela — **o slot é sua escolha** (User IR 1–20): anote em qual slot subiu cada arquivo e carregue no patch correspondente. Passo a passo na seção **📡 3** de cada `patch.md`.

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
│               └── patch.md              # documentação prática-primeiro
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

## 🔧 Regenerar tudo

```bash
python tools/build_song_patches.py   # patch.md + .prst a partir de tools/patches-defs.json
python tools/gen_indexes.py          # mapas dos álbuns + este README
```

---

[`📖 README do projeto`](../README.md)
"""


def build_all(defs=None, ir_lib=None):
    """Monta (sem escrever) todo o conteúdo dos índices: {Path: texto}.

    Função pura em relação ao disco (só lê o defs/manifesto quando não recebem
    argumento) — é o que os testes usam para conferir o mapa sem gerar arquivos.
    """
    defs = defs or load_defs()
    if ir_lib is None:
        ir_lib = load_ir_library()
    slots = slot_map(defs)
    albums = defs['albums']

    saidas, rows_by_album = {}, {}
    total_all = 0
    for key in album_order(defs):
        album = albums[key]
        songs = [s for s in defs['songs'] if s['idAlbum'] == key]
        n = sum(len(s['patches']) for s in songs)
        total_all += n

        local_rows, local_seq = [], []
        for song in songs:
            row, s = song_row(defs, song, slots, ir_lib)
            local_rows.append(row)
            local_seq.extend(s)
        rows_by_album[key] = (local_rows, local_seq, n)

        saidas[album_root(album) / 'MAPA-DO-ALBUM.md'] = build_mapa(
            key, album, songs, n, local_rows, local_seq)

    album_rows = '\n'.join(
        f"| 🎸 **{albums[k]['banda']}** | **{albums[k]['display']}** | "
        f"{len([s for s in defs['songs'] if s['idAlbum'] == k])} | "
        f"{rows_by_album[k][2]} | "
        f"[`MAPA-DO-ALBUM.md`]({albums[k]['pasta'].replace(' ', '%20')}/MAPA-DO-ALBUM.md) |"
        for k in album_order(defs))

    saidas[ROOT / 'patches' / 'README.md'] = build_readme(album_rows, total_all)
    return saidas, total_all


def main():
    """Gera os mapas dos álbuns + patches/README.md e resume no console."""
    defs = load_defs()
    saidas, total = build_all(defs)
    for path, texto in saidas.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(texto, encoding='utf-8', newline='\r\n')
    print(f"✅ {len(defs['albums'])} mapas + patches/README.md regenerados "
          f"({total} patches, slots U01–U{total:02d}).")


if __name__ == '__main__':
    main()
