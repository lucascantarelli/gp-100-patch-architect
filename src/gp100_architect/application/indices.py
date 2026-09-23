"""Índices da biblioteca — MAPA-DO-ALBUM.md e `patches/README.md` (issue #30).

Migração de `tools/gen_indexes.py`: as funções puras vêm para cá e passam a
receber caminhos explícitos (`raiz`, `ir_index`) em vez de resolver `ROOT` do
próprio arquivo — é o que permite gerar o mapa num diretório temporário e
testar sem escrever na biblioteca.

Nenhum dado de música/álbum/IR vive aqui: nome de pasta, título de exibição,
dossiê do rig e recomendação de IR vêm do defs/do catálogo. Antes esses
literais existiam aqui E em `build_song_patches` — e divergiram (o mapa
recomendava "fábrica" onde o `patch.md` mandava carregar uma IR do banco
local, nos 38 patches do Pulse).

Camada: application (devolve `{Path: texto}`; quem escreve é o shim, via
`infrastructure.escrita`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gp100_architect.application import nomes
from gp100_architect.application.biblioteca import slots

__all__ = ['album_order', 'build_all', 'build_mapa', 'build_readme', 'ir_recomendada']

# ordem de preferência do mix recomendado no mapa (igual à da doc do patch)
_MIX_PREFERIDO = 'Medium Mix'


def album_order(defs: dict[str, Any]) -> list[str]:
    """Chaves de álbum na ordem em que aparecem em `defs['songs']` (ordem dos slots)."""
    vistos: list[str] = []
    for song in defs['songs']:
        if song['idAlbum'] not in vistos:
            vistos.append(song['idAlbum'])
    return vistos


def ir_recomendada(
    defs: dict[str, Any], ir_index: dict[str, list[str]] | None, cab_nome: str
) -> str | None:
    """Arquivo da captura local (Medium Mix) para o CAB do patch, ou None.

    `None` significa "o CAB de fábrica já é o alvo" — inclusive quando o
    manifesto de IRs não pôde ser lido (`ir_index is None`; o aviso já foi
    dado por quem carregou o catálogo).
    """
    par = defs['ir_local'].get(cab_nome)
    if not par or ir_index is None:
        return None
    cab_lib = par['captura']
    for arquivo in ir_index.get(cab_lib, []):
        if _MIX_PREFERIDO in arquivo:
            return f'{cab_lib} — {arquivo}'
    return f'{cab_lib} (ver reference/16-ir-library.md)'


def song_row(
    defs: dict[str, Any],
    song: dict[str, Any],
    mapa_slots: dict[str, str],
    ir_index: dict[str, list[str]] | None,
) -> tuple[str, list[tuple[Any, ...]]]:
    """Gera (linha da tabela, sequência de slots) de uma música.

    A linha entra na tabela "Música → patches" do mapa (patch · captador ·
    IR recomendada · slots); a sequência alimenta a tabela de slots. Links
    relativos com espaços escapados para %20.
    """
    parts, linha_slots, pus, irs = [], [], [], []
    for p in song['patches']:
        slot = mapa_slots[p['nome']]
        linha_slots.append(slot)
        link = f'./{nomes.song_pasta(song)}/{p["nome"]}/patch.md'.replace(' ', '%20')
        parts.append(f'[`{p["emoji"]} {p["nome"]}`]({link}) ({p["camada"].split()[0]})')
        pus.append(f'{p["camada"].split()[0]}: {p["doc"]["guitarra"]["seletorCurto"]}')
        cab = p['spec']['modules'].get('CAB', {}).get('name', '')
        ir = ir_recomendada(defs, ir_index, cab)
        irs.append(f'📁 `{ir}`' if ir else f'⚙️ fábrica `{cab}`')
    row = (
        f'| **{nomes.song_display(song)}** | {" · ".join(parts)} | '
        f'{" · ".join(pus)} | {" · ".join(irs)} | {", ".join(linha_slots)} |'
    )
    seq = [
        (s, p['nome'], song['song'], p['camada'], i)
        for s, p, i in zip(linha_slots, song['patches'], irs, strict=True)
    ]
    return row, seq


def build_mapa(
    album: dict[str, Any],
    songs: list[dict[str, Any]],
    total: int,
    rows: list[str],
    seq: list[tuple[Any, ...]],
) -> str:
    """Renderiza o MAPA-DO-ALBUM.md de um álbum.

    Recebe as linhas/sequência prontas (uma chamada de `song_row` por música,
    já com slots numerados) e monta: tabela música→patches, sequência de
    slots, análise das camadas e o dossiê do rig real (`album['rig']`, definido
    por álbum no defs — nunca reaproveitado de outro álbum).
    """
    song_rows = '\n'.join(rows)
    slot_rows = '\n'.join(f'| {s} | `{n}` | {m} — {c} | {i} |' for s, n, m, c, i in seq)
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


def build_readme(album_blocks: str, total: int) -> str:
    """Renderiza o `patches/README.md` (índice geral da biblioteca)."""
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


def build_all(
    defs: dict[str, Any], *, raiz: Path, ir_index: dict[str, list[str]] | None = None
) -> tuple[dict[Path, str], int]:
    """Monta (sem escrever) todo o conteúdo dos índices: `{Path: texto}` + total.

    Função pura em relação ao disco: recebe o defs já validado e o índice de
    IRs; devolve os caminhos absolutos (sob `raiz`) e o total de patches — é o
    que os testes usam para conferir o mapa sem gerar arquivo.
    """
    mapa_slots = slots(defs)
    albums = defs['albums']

    saidas: dict[Path, str] = {}
    rows_by_album: dict[str, tuple[list[str], list[tuple[Any, ...]], int]] = {}
    total_all = 0
    for key in album_order(defs):
        album = albums[key]
        songs = [s for s in defs['songs'] if s['idAlbum'] == key]
        n = sum(len(s['patches']) for s in songs)
        total_all += n

        local_rows, local_seq = [], []
        for song in songs:
            row, seq = song_row(defs, song, mapa_slots, ir_index)
            local_rows.append(row)
            local_seq.extend(seq)
        rows_by_album[key] = (local_rows, local_seq, n)

        saidas[raiz / 'patches' / nomes.album_pasta(album) / 'MAPA-DO-ALBUM.md'] = build_mapa(
            album, songs, n, local_rows, local_seq
        )

    album_rows = '\n'.join(
        f'| 🎸 **{albums[k]["banda"]}** | **{albums[k]["display"]}** | '
        f'{len([s for s in defs["songs"] if s["idAlbum"] == k])} | '
        f'{rows_by_album[k][2]} | '
        f'[`MAPA-DO-ALBUM.md`]({nomes.album_pasta(albums[k]).replace(" ", "%20")}/MAPA-DO-ALBUM.md) |'
        for k in album_order(defs)
    )

    saidas[raiz / 'patches' / 'README.md'] = build_readme(album_rows, total_all)
    return saidas, total_all
