"""Formato `.prst` da GP-100 — o contrato binário do projeto (CODEOWNER).

`codec` escreve (geração single-patch fw 2.1); `reader` lê (parse e
estatísticas de qualquer export). A regra da casa: o domínio nunca importa
daqui, e qualquer mudança de formato é breaking (exige ADR).
"""

from gp100_architect.infrastructure.prst.codec import (
    gerar_xml,
    load_templates,
    validar_spec,
)
from gp100_architect.infrastructure.prst.reader import analyze, fmt_stat, parse

__all__ = [
    'analyze',
    'fmt_stat',
    'gerar_xml',
    'load_templates',
    'parse',
    'validar_spec',
]
