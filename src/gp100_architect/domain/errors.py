"""Exceções do domínio — erros de entrada do usuário, não bugs de execução.

Regra do projeto: erro acionável diz **onde** (caminho JSON) e **como corrigir**.
Uma exceção que não consegue dizer as duas coisas é bug do validador, não do
defs.
"""

from __future__ import annotations

__all__ = ['DefsInvalidos', 'Gp100Error']


class Gp100Error(Exception):
    """Base de todos os erros previstos do projeto (nunca vaza traceback cru)."""


class DefsInvalidos(Gp100Error):
    """O `patches-defs.json` não passou na validação.

    Carrega o relatório completo com caminho e correção de cada problema.
    """

    def __init__(self, relatorio: str, problemas: int) -> None:
        super().__init__(relatorio)
        self.relatorio = relatorio
        self.problemas = problemas
