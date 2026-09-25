"""Teste de fronteira do domínio — a regra vira verificação (issue #28).

O critério \"domínio não importa I/O nem as outras camadas\" era prosa no
`domain/__init__.py`; aqui ele vira guarda, no espírito do
`audit_workflows.py`: lê os módulos do pacote por AST e reprova qualquer
`import` proibido, com arquivo e linha.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from gp100_architect.domain import __file__ as _domain_init

pytestmark = pytest.mark.unit

# módulos que o domínio não toca, por família:
#  - stdlib de I/O e ambiente (o domínio recebe dados prontos, nunca lê)
#  - dependências de interface (typer/rich são da camada interfaces)
#  - as outras camadas do próprio pacote (a fronteira é uma via de mão contrária)
PROIBIDOS = frozenset(
    {
        'pathlib',
        'json',
        'os',
        'sys',
        'subprocess',
        'shutil',
        'pickle',
        'urllib',
        'socket',
        'typer',
        'rich',
        'requests',
    }
)
CAMADAS = (
    'gp100_architect.application',
    'gp100_architect.infrastructure',
    'gp100_architect.interfaces',
)


def _modulos_do_dominio() -> list[Path]:
    return sorted(Path(_domain_init).parent.glob('*.py'))


def _imports_proibidos(arquivo: Path) -> list[str]:
    """Imports proibidos no arquivo, no formato `arquivo:linha: o que`."""
    arvore = ast.parse(arquivo.read_text(encoding='utf-8'))
    achados: list[str] = []
    for node in ast.walk(arvore):
        if isinstance(node, ast.Import):
            for alias in node.names:
                raiz = alias.name.split('.')[0]
                if alias.name in PROIBIDOS or raiz in PROIBIDOS:
                    achados.append(f'{arquivo.name}:{node.lineno}: import {alias.name}')
                for camada in CAMADAS:
                    if alias.name == camada or alias.name.startswith(camada + '.'):
                        achados.append(f'{arquivo.name}:{node.lineno}: import {alias.name}')
        elif isinstance(node, ast.ImportFrom):
            modulo = node.module or ''
            raiz = modulo.split('.')[0]
            if modulo in PROIBIDOS or raiz in PROIBIDOS:
                achados.append(f'{arquivo.name}:{node.lineno}: from {modulo} import …')
            for camada in CAMADAS:
                if modulo == camada or modulo.startswith(camada + '.'):
                    achados.append(f'{arquivo.name}:{node.lineno}: from {modulo} import …')
    return achados


def test_dominio_nao_importa_io_nem_outras_camadas():
    """A fronteira do domínio, verificada — não prometida.

    Módulo novo no domínio que precise de I/O é sinal de que a regra dele
    pertence a outra camada (application/infrastructure), não de que este
    teste deve abrir exceção.
    """
    violacoes = [achado for f in _modulos_do_dominio() for achado in _imports_proibidos(f)]
    assert not violacoes, 'domínio violou a fronteira:\n  ' + '\n  '.join(violacoes)


def test_dominio_tem_guarda_contra_ele_mesmo():
    """O guarda existe porque o domínio cresce — este teste é a prova de que
    os módulos atuais estão sendo varridos (não um teste vazio)."""
    arquivos = {f.name for f in _modulos_do_dominio()}
    assert {'__init__.py', 'chain.py', 'errors.py', 'params.py', 'validation.py'} <= arquivos
