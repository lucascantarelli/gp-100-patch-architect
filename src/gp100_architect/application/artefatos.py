"""Tipos de produto da camada de aplicação — o que o pipeline entrega.

`PatchGerado` é o contrato entre quem **gera** (`biblioteca`, `variantes`) e
quem **grava** (o comando `gp100 build`): um patch pronto para virar
arquivo, em memória. Mora num módulo folha de propósito — variante e canônico
são o MESMO tipo de produto, e assim nenhuma das duas camadas importa a outra.

Camada: application — tipo de dados puro, sem I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ['PatchGerado']


@dataclass(frozen=True)
class PatchGerado:
    """Um patch pronto para virar arquivo — o que o pipeline produz.

    `pasta` é o diretório do patch (`patches/<Banda>/<Álbum>/<Música>/<NOME>`);
    `documentacao` é o `patch.md` completo (ou o `<NOME>-USERIR.md` na variante
    experimental) e `prst` são os bytes do `.prst`.
    """

    nome: str
    musica: str
    camada: str
    slot: str
    pasta: Path
    documentacao: str
    prst: bytes
