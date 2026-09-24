"""Fixtures compartilhadas da pirâmide (issue #34).

Regras da casa materializadas no conftest:

* **nenhum teste escreve no repositório** — quem precisa de arquivo usa
  `tmp_path` e aponta `GP100_DEFS` para lá; com `--guarda-repo` (padrão no CI),
  o fim da sessão compara o working tree e reprova qualquer sujeira de teste;
* **Python 3.14 apenas** — a política guardada em `tools/defs_schema.py`
  (`PY_OK`) fica repetida aqui para a mensagem sair antes do primeiro import
  do pacote (a suíte inteira se recusa a rodar em runtime diferente, com a
  mesma mensagem acionável do validador);
* os **markers** (`unit`, `integration`, `contract`, `e2e`, `slow`) nascem
  aqui — única fonte; o `pyproject.toml` só declara `--strict-markers`, então
  marker mal escrito reprova a sessão em vez de rodar sem camada.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# ── guarda de runtime (a mesma política de tools/defs_schema.py) ────────────
_PY_ALVO = (3, 14)
if sys.version_info[:2] < _PY_ALVO:
    raise SystemExit(
        f'Este projeto roda Python 3.14 APENAS — detectado '
        f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}. '
        f'O CI roda em 3.14 (ver .github/workflows/ci.yml).'
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        '--guarda-repo',
        action='store_true',
        default=False,
        help='Auditoria de escrita no repo (git status no fim da sessão) — padrão no CI.',
    )


def _estado_repo(raiz: Path) -> set[str]:
    r = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=str(raiz),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    return set(r.stdout.splitlines())


def pytest_configure(config: pytest.Config) -> None:
    for marker in ('unit', 'integration', 'contract', 'e2e', 'slow'):
        config.addinivalue_line('markers', f'{marker}: camada da pirâmide (issue #34)')


@pytest.fixture(scope='session')
def raiz() -> Path:
    """Raiz do repositório (onde vivem tools/, patches/ e VERSION)."""
    return Path(__file__).resolve().parent.parent


def pytest_sessionstart(session: pytest.Session) -> None:
    """Guarda da auditoria: o estado do working tree QUANDO a suíte começa.

    A comparação é relativa ao início da sessão — não ao HEAD — por dois
    motivos: o CI constrói os derivados (patches/**) ANTES do pytest (e isso é
    escrita legítima do passo de build, não de teste), e a sua máquina pode ter
    WIP não commitado que não é culpa de nenhum teste.
    """
    if session.config.getoption('--guarda-repo'):
        session.config._repo_antes = _estado_repo(session.config.rootpath)  # type: ignore[attr-defined]


@pytest.fixture(scope='session')
def defs_real(raiz: Path) -> dict[str, Any]:
    """O defs commitado, consolidado pelo loader v2 — a fonte de verdade."""
    from gp100_architect.infrastructure.defs import carregar

    return carregar(raiz / 'tools' / 'defs')


@pytest.fixture
def defs_mutavel(defs_real: dict[str, Any]) -> dict[str, Any]:
    """Cópia profunda do defs real para mutações em memória."""
    import copy

    return copy.deepcopy(defs_real)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Auditoria automática de efeito colateral no repositório (critério da #34).

    Compara o `git status --porcelain` do fim com o do início da sessão: qualquer
    arquivo criado/alterado por um teste reprova a sessão com a lista do que
    ficou sujo. Roda com `--guarda-repo` (o CI passa a flag; localmente é
    opcional, para não atrapalhar quem está depurando).
    """
    if not session.config.getoption('--guarda-repo'):
        return
    antes: set[str] = getattr(session.config, '_repo_antes', set())
    depois = _estado_repo(session.config.rootpath)
    sujo = sorted(depois - antes)
    if sujo:
        relatorio = '\n'.join(f'  {ln}' for ln in sujo[:20])
        raise pytest.UsageError(
            'auditoria de escrita no repositório: a suíte alterou o working tree '
            f'({len(sujo)} caminho(s)) — nenhum teste pode escrever no repo '
            f'(regra do projeto; use tmp_path):\n{relatorio}'
        )
