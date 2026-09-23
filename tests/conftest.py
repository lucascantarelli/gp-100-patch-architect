"""Fixtures compartilhadas — o mínimo para os testes novos não repetirem caminho.

Regra do projeto: **nenhum teste escreve no repositório**. Quem precisa de
arquivo de saída usa `tmp_path` e aponta `GP100_DEFS` para lá.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope='session')
def raiz() -> Path:
    """Raiz do repositório (onde vivem tools/, patches/ e VERSION)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session')
def defs_real(raiz: Path) -> dict[str, Any]:
    """O defs commitado, consolidado pelo loader v2 — a fonte de verdade."""
    src = str(raiz / 'src')
    if src not in sys.path:
        sys.path.insert(0, src)
    from gp100_architect.infrastructure.defs import carregar

    return carregar(raiz / 'tools' / 'defs')


@pytest.fixture
def defs_mutavel(defs_real: dict[str, Any]) -> dict[str, Any]:
    """Cópia profunda do defs real para mutações em memória."""
    import copy

    return copy.deepcopy(defs_real)
