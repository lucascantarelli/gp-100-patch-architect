"""Formato `.prst` da GP-100 — o contrato binário do projeto (CODEOWNER).

`codec` escreve (geração single-patch fw 2.1); `reader` lê (parse e
estatísticas de qualquer export). A regra da casa: o domínio nunca importa
daqui, e qualquer mudança de formato é breaking (exige ADR).

Convenção de import: direto do submodule (`from gp100_architect.infrastructure.prst.codec
import gerar_xml`) — este `__init__` não reexporta.
"""
