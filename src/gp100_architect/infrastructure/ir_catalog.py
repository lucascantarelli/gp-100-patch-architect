"""Catálogo local de IRs — leitura do manifesto e consulta por gabinete (issue #30).

Migração de `tools/build_song_patches.py` (`ir_catalog`, `ir_mixes`): a leitura
do manifesto `data/ir-library.json` e a escolha do mix recomendado viram
biblioteca, e o aviso de manifesto ilegível é responsabilidade da CLI — a
camada de aplicação nunca imprime (contrato do `application/__init__`).

O manifesto é INSUMO da documentação: `build_song_patches` cita o arquivo exato
na seção 📡 de cada `patch.md` e `gen_indexes` marca 📁 no mapa do álbum. Sem
ele, os dois caem juntos para o CAB de fábrica — por isso o aviso existe.

Camada: infrastructure (o domínio nunca importa daqui).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ['carregar', 'indice_por_cab', 'melhor_mix']

# ordem de preferência do mix (o banco traz Bright/Medium/Dark por gabinete)
PREFERENCIA_DE_MIX: tuple[str, ...] = ('Medium Mix', 'Bright Mix', 'Dark Mix')


def carregar(caminho: Path) -> dict[str, Any] | None:
    """Lê o manifesto `ir-library.json`; `None` quando ilegível ou ausente.

    Não imprime e não levanta: quem chama decide o aviso (cada consumidor tem o
    seu texto) e o comportamento degradado é "só o CAB de fábrica" — nunca
    interromper o build por causa do catálogo.
    """
    try:
        dados = json.loads(caminho.read_text(encoding='utf-8'))
    except Exception:
        return None
    return dados if isinstance(dados, dict) else None


def indice_por_cab(manifesto: dict[str, Any]) -> dict[str, list[str]]:
    """`{gabinete: [arquivos compatíveis]}` — só os WAVs marcados `compatible`.

    O gabinete é a pasta do arquivo, subindo um nível quando ela termina em
    `Mics` (as capturas individuais ficam em `<Gabinete> Mics/`).
    """
    indice: dict[str, list[str]] = {}
    for pack in (manifesto.get('packs') or {}).values():
        for arquivo in pack.get('files') or []:
            if not arquivo.get('compatible'):
                continue
            partes = Path(arquivo['file']).parts
            cab = partes[-2].replace(' Mics', '')
            indice.setdefault(cab, []).append(partes[-1])
    return indice


def melhor_mix(arquivos: list[str]) -> str | None:
    """Arquivo Mix recomendado da captura local (Medium > Bright > Dark > primeiro)."""
    for preferido in PREFERENCIA_DE_MIX:
        for arquivo in arquivos:
            if preferido in arquivo:
                return arquivo
    return arquivos[0] if arquivos else None
