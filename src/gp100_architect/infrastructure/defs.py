"""Carregamento do `patches-defs.json` — a fonte única do projeto.

Regra que este módulo impõe (review doc 21, achado M2): **toda** porta de
entrada carrega o defs por aqui, já validado. Antes, só o build validava e os
outros três consumidores liam JSON cru — um defs quebrado passava silencioso
por `gp100`, `gen_indexes` e `build_release` até estourar longe da causa.

O caminho do defs é resolvido a partir da raiz do repositório (o pacote é
desenvolvido dentro dele) e pode ser apontado por `GP100_DEFS`, o que deixa os
testes trabalharem em dirs temporários sem tocar no repositório.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from gp100_architect.domain.errors import DefsInvalidos
from gp100_architect.domain.validation import validar

__all__ = ['DEFS_PADRAO', 'VAR_DEFS', 'carregar', 'carregar_e_validar', 'raiz_do_repo']

VAR_DEFS = 'GP100_DEFS'


def raiz_do_repo() -> Path:
    """Raiz do repositório — onde estão `tools/`, `patches/` e `VERSION`."""
    return Path(__file__).resolve().parents[3]


DEFS_PADRAO: Path = raiz_do_repo() / 'tools' / 'patches-defs.json'


def caminho_defs(caminho: Path | None = None) -> Path:
    """Prioridade: argumento → `GP100_DEFS` → `tools/patches-defs.json`."""
    if caminho is not None:
        return caminho
    do_ambiente = os.environ.get(VAR_DEFS)
    return Path(do_ambiente) if do_ambiente else DEFS_PADRAO


def carregar(caminho: Path | None = None) -> dict[str, Any]:
    """Lê o defs **sem** validar — só para diagnóstico e ferramentas de migração."""
    return json.loads(caminho_defs(caminho).read_text(encoding='utf-8'))  # type: ignore[no-any-return]


def carregar_e_validar(caminho: Path | None = None) -> dict[str, Any]:
    """Lê o defs validando todas as regras do domínio.

    Levanta `DefsInvalidos` (com relatório acionável) quando o arquivo não passa.
    """
    alvo = caminho_defs(caminho)
    dados = carregar(alvo)
    erros = validar(dados)
    if not erros.ok():
        raise DefsInvalidos(erros.relatorio(), len(erros.itens))
    return dados
