"""Fixtures compartilhadas — o mínimo para os testes novos não repetirem caminho.

Regra do projeto: **nenhum teste escreve no repositório**. Quem precisa de
arquivo de saída usa `tmp_path` e aponta `GP100_DEFS` para lá.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope='session')
def raiz() -> Path:
    """Raiz do repositório (onde vivem tools/, patches/ e VERSION)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope='session')
def defs_real(raiz: Path) -> dict[str, Any]:
    """O defs commitado, parseado uma vez — a fonte de verdade da biblioteca."""
    return json.loads((raiz / 'tools' / 'patches-defs.json').read_text(encoding='utf-8'))


@pytest.fixture
def defs_mutavel(defs_real: dict[str, Any]) -> dict[str, Any]:
    """Cópia profunda do defs real para mutações em memória."""
    import copy

    return copy.deepcopy(defs_real)
