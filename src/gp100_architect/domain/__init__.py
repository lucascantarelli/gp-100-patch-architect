"""Camada de domínio — regras puras da GP-100.

Nada aqui importa `typer`, `rich`, `pathlib` de I/O ou toca arquivos. É a
camada que qualquer interface (CLI, API, UI) pode chamar sem efeito colateral.
"""

from gp100_architect.domain.chain import CHAIN, MODULOS_PROIBIDOS_EM_MOMENTO, posicao
from gp100_architect.domain.params import PARAM_NAMES, parametros, rotulo

__all__ = [
    'CHAIN',
    'MODULOS_PROIBIDOS_EM_MOMENTO',
    'PARAM_NAMES',
    'parametros',
    'posicao',
    'rotulo',
]
