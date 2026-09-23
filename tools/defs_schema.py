#!/usr/bin/env python3
"""defs_schema.py — SHIM de compatibilidade. A validação vive no pacote.

A implementação real é `gp100_architect.domain.validation` (regras puras) + o
carregador `gp100_architect.infrastructure.defs`. Este arquivo preserva o
contrato legado para os
consumidores de `tools/` (build_song_patches) e para `tests/test_defs_schema.py`:

* os nomes históricos continuam importáveis daqui;
* `carregar_e_validar` mantém o **SystemExit** com relatório acionável (o build
  imprime o relatório e para, em vez de vazar traceback);
* `python tools/defs_schema.py` continua validando e saindo 0/1.

Quando o último consumidor de `tools/` migrar para `gp100` (PKG-008), este
arquivo é removido: a porta oficial passa a ser `gp100 validate`.
"""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / 'src'
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from gp100_architect.domain.chain import CHAIN  # noqa: E402,F401
from gp100_architect.domain.errors import DefsInvalidos  # noqa: E402
from gp100_architect.domain.params import PARAM_NAMES  # noqa: E402,F401
from gp100_architect.domain.validation import CAMS, Erros, validar  # noqa: E402,F401
from gp100_architect.infrastructure.defs import (  # noqa: E402
    DEFS_PADRAO,
    carregar,
    carregar_e_validar as _carregar_e_validar,
)
from gp100_architect.infrastructure.defs import raiz_do_repo as _raiz

ROOT = _raiz()
DEFS = DEFS_PADRAO

PY_OK = (3, 14)
if sys.version_info[:2] < PY_OK:
    raise SystemExit(
        f"Este projeto exige Python {'.'.join(map(str, PY_OK))} — "
        f"encontrado {sys.version.split()[0]}. Atualize o interpretador "
        f"(o CI roda em 3.14; veja .github/workflows/ci.yml).")


def carregar_e_validar(caminho: Path = DEFS) -> dict:
    """Legado: carrega validando e converte o erro de domínio em SystemExit."""
    try:
        return _carregar_e_validar(caminho)
    except DefsInvalidos as erro:
        raise SystemExit(erro.relatorio) from erro


def main() -> int:
    dados = carregar()
    er = validar(dados)
    if er.ok():
        songs = dados.get('songs', [])
        patches = sum(len(s.get('patches', [])) for s in songs)
        print(f"✅ defs válido (tools/defs/, schema v2) — {len(songs)} músicas, "
              f"{patches} patches, {len(dados.get('albums', {}))} álbuns")
        return 0
    print(er.relatorio())
    return 1


if __name__ == '__main__':
    sys.exit(main())
