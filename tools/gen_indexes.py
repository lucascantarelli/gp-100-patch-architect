#!/usr/bin/env python3
"""gen_indexes.py — shim de CLI dos índices da biblioteca (issue #30).

A implementação vive em `src/gp100_architect/application/indices.py` (mapas
dos álbuns e o `patches/README.md`) e os nomes derivados do defs, em
`application/nomes.py`. Este arquivo resolve a raiz, carrega o defs validado,
lê o catálogo de IRs (avisando quando não puder) e escreve os índices.

Regenera a partir da FONTE ÚNICA (`tools/patches-defs.json`):
  - MAPA-DO-ALBUM.md de cada álbum (bloco `albums` do defs)
  - patches/README.md (índice geral da biblioteca)

Nenhum dado de música/álbum/IR vive aqui: nome de pasta, título de exibição,
dossiê do rig real e recomendação de IR vêm de `albums`, `ir_local` e dos
campos `pasta`/`display` de cada música no defs. Antes esses literais existiam
aqui E em build_song_patches.py — e divergiram (o mapa recomendava "fábrica"
onde o patch.md mandava carregar uma IR do banco local, nos 38 patches do
Pulse).

Reexporta os nomes que a suíte legada consome (`load_defs`, `load_ir_library`,
`song_pasta`, `song_display`, `slot_map`, `build_all`) até a migração da suíte
(issue #34).

Uso: python tools/gen_indexes.py
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 → UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))     # defs_schema: shim do pacote

from gp100_architect.application import nomes  # noqa: E402
from gp100_architect.application import indices  # noqa: E402
from gp100_architect.application.biblioteca import slots as slot_map  # noqa: E402,F401
from gp100_architect.infrastructure import ir_catalog  # noqa: E402
from gp100_architect.infrastructure.escrita import escrever_texto  # noqa: E402

IR_LIBRARY_JSON = ROOT / 'tools' / 'ir-library.json'

song_pasta = nomes.song_pasta       # noqa: F401 — reexportado para a suíte legada
song_display = nomes.song_display   # noqa: F401


def load_defs():
    """Lê o defs pela via do projeto (validação acionável, sem traceback)."""
    from defs_schema import carregar_e_validar
    return carregar_e_validar()


def load_ir_library():
    """Manifesto `tools/ir-library.json` (`{'packs': ...}`) ou None + UM aviso.

    Sem o manifesto o mapa passaria a dizer "o CAB de fábrica já é o alvo" em
    todos os álbuns sem que ninguém percebesse; o aviso existe para isso.
    """
    manifesto = ir_catalog.carregar(IR_LIBRARY_JSON)
    if manifesto is None:
        print(f"AVISO: não li tools/ir-library.json — o mapa vai marcar todos os "
              f"cabs como 'fábrica'. Rode: python tools/ir_library.py", file=sys.stderr)
    return manifesto


def _indice_de_irs() -> dict[str, list[str]] | None:
    manifesto = load_ir_library()
    return None if manifesto is None else ir_catalog.indice_por_cab(manifesto)


def build_all(defs=None, ir_index=None):
    """Compatibilidade da suíte legada: monta os índices sem escrever.

    `ir_index` aceita o índice `{gabinete: [arquivos]}` já pronto; sem ele, lê
    o catálogo (avisando se não puder).
    """
    defs = defs or load_defs()
    if ir_index is None:
        ir_index = _indice_de_irs()
    return indices.build_all(defs, raiz=ROOT, ir_index=ir_index)


def main() -> None:
    """Gera os mapas dos álbuns + patches/README.md e resume no console."""
    defs = load_defs()
    saidas, total = indices.build_all(defs, raiz=ROOT, ir_index=_indice_de_irs())
    for caminho, texto in saidas.items():
        escrever_texto(caminho, texto, crlf=True)
    print(f"✅ {len(defs['albums'])} mapas + patches/README.md regenerados "
          f"({total} patches, slots U01–U{total:02d}).")


if __name__ == '__main__':
    main()
