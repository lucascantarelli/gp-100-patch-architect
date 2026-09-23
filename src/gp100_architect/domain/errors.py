"""Exceções do domínio — erros de entrada do usuário, não bugs de execução.

Regra do projeto: erro acionável diz **onde** (caminho JSON) e **como corrigir**.
Uma exceção que não consegue dizer as duas coisas é bug do validador, não do
defs.
"""

from __future__ import annotations

__all__ = [
    'DefsInvalidos',
    'FormatoPrstInvalido',
    'Gp100Error',
    'ModeloDesconhecido',
    'SpecInvalido',
]


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


class SpecInvalido(Gp100Error):
    """O spec JSON do patch viola o contrato de entrada do gerador `.prst`.

    Mensagem acionável: diz o campo, o valor recebido e o valor aceito
    (ex.: `ir_slot deve ser 0..19 (user IR) ou null — recebi 25`).
    """


class ModeloDesconhecido(Gp100Error):
    """O modelo do módulo não existe no catálogo do firmware 2.0/2.1.

    A mensagem aponta `reference/15-firmware2-effects.md` — a fonte dos
    modelos válidos (mesma orientação do erro original do gerador).
    """


class FormatoPrstInvalido(Gp100Error):
    """O arquivo `.prst` lido não é um XML no formato esperado da GP-100.

    Parse defensivo (issue #29): XML malformado ou sem `<preset_info>`/
    `<presets>` reprova com mensagem acionável em vez de AttributeError.
    """
