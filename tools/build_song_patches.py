#!/usr/bin/env python3
"""build_song_patches.py — shim de CLI do construtor de patches (issue #30).

A implementação vive em `src/gp100_architect/application/`:

* `biblioteca.gerar` — orquestra (slots, spec final, documentação, `.prst`);
* `rendering.patch_md` — o texto do `patch.md`;
* `infrastructure.ir_catalog` / `prst.codec` / `escrita` — catálogo de IRs,
  geração do XML e gravação.

Este arquivo fica com a cara de terminal: resolve a raiz, carrega o defs
validado (relatório acionável, sem traceback), avisa quando o catálogo de IRs
não pôde ser lido e escreve os artefatos.

Para cada patch:
  1. escreve <...>/patch.md  (documentação prática-primeiro, Markdown puro)
  2. gera <...>/<NOME>.prst  via codec (in-memory — ADR-0013: nenhum
     intermediário em disco)

Reexporta a fonte única que a suíte legada consome (`DEFS`, `CHAIN`,
`PARAM_NAMES`, `build_doc`) até a migração da suíte (issue #34).

Uso: python tools/build_song_patches.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))     # defs_schema/chain: shims do pacote

from gp100_architect.application import biblioteca  # noqa: E402
from gp100_architect.application.rendering import patch_md  # noqa: E402
from gp100_architect.domain.chain import CHAIN  # noqa: E402,F401
from gp100_architect.domain.errors import DefsInvalidos, Gp100Error  # noqa: E402
from gp100_architect.domain.params import PARAM_NAMES  # noqa: E402
from gp100_architect.infrastructure import ir_catalog  # noqa: E402
from gp100_architect.infrastructure.defs import carregar_e_validar  # noqa: E402
from gp100_architect.infrastructure.escrita import escrever_bytes, escrever_texto  # noqa: E402
from gp100_architect.infrastructure.prst.codec import (  # noqa: E402
    BUILD_TIME_PADRAO,
    load_templates,
)

IR_LIBRARY_JSON = ROOT / 'tools' / 'ir-library.json'
AVISO_SEM_CATALOGO = (
    'AVISO: não li tools/ir-library.json.\n'
    '       A seção 📡 dos patches vai indicar só o CAB de fábrica.\n'
    '       Rode: python tools/ir_library.py'
)


def _carregar_defs() -> dict:
    """Defs validado — erro previsto vira SystemExit com o relatório acionável."""
    try:
        return carregar_e_validar()
    except DefsInvalidos as erro:
        raise SystemExit(erro.relatorio) from erro


DEFS = _carregar_defs()


_IR_INDEX: list[dict[str, list[str]]] = []      # cache: lê/averte uma vez por execução


def _indice_de_irs() -> dict[str, list[str]]:
    """Índice `{gabinete: [arquivos]}` do catálogo local (ou {} + aviso, uma vez)."""
    if _IR_INDEX:
        return _IR_INDEX[0]
    manifesto = ir_catalog.carregar(IR_LIBRARY_JSON)
    if manifesto is None:
        print(AVISO_SEM_CATALOGO, file=sys.stderr)
        indice: dict[str, list[str]] = {}
    else:
        indice = ir_catalog.indice_por_cab(manifesto)
    _IR_INDEX.append(indice)
    return indice


def build_doc(song, patch, spec, slot):
    """Compatibilidade da suíte legada: renderiza com os dados do defs atual."""
    return patch_md.build_doc(song, patch, spec, slot, albums=DEFS['albums'],
                              ir_local=DEFS['ir_local'], ir_index=_indice_de_irs())


def main() -> None:
    """Gera e grava todos os patches; erro previsto sai acionável, sem traceback."""
    templates = load_templates()   # catálogo carregado UMA vez (dados puros)
    build_time = os.environ.get('GP100_BUILD_TIME', BUILD_TIME_PADRAO)
    try:
        gerados = biblioteca.gerar(DEFS, raiz=ROOT, ir_index=_indice_de_irs(),
                                   templates=templates, build_time=build_time)
    except Gp100Error as e:
        print(f'FALHA {e}')
        sys.exit(1)

    for patch in gerados:
        escrever_texto(patch.pasta / 'patch.md', patch.documentacao, crlf=True)
        escrever_bytes(patch.pasta / f'{patch.nome}.prst', patch.prst)

    print(f'✅ {len(gerados)} patches gerados e validados:\n')
    for patch in gerados:
        print(f'  {patch.musica:45s} → {patch.nome:9s} ({patch.camada})')


if __name__ == '__main__':
    main()
