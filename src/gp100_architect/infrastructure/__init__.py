"""Infraestrutura — tudo que toca o mundo externo.

Aqui vivem o carregamento do `patches-defs.json`, o formato `.prst` e o
empacotamento de release. A regra da casa: o domínio nunca importa daqui.
"""

from gp100_architect.infrastructure.defs import (
    DEFS_PADRAO,
    carregar,
    carregar_e_validar,
    raiz_do_repo,
)

__all__ = ['DEFS_PADRAO', 'carregar', 'carregar_e_validar', 'raiz_do_repo']
