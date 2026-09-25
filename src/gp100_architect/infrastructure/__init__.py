"""Infraestrutura — tudo que toca o mundo externo.

Aqui vivem o carregamento do `patches-defs.json`, o formato `.prst` e o
empacotamento de release. A regra da casa: o domínio nunca importa daqui.

Convenção de import: direto do submodule (`from gp100_architect.infrastructure.defs
import carregar_e_validar`) — este `__init__` não reexporta.
"""
