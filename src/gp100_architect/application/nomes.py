"""Nomes derivados do defs — pasta e título de exibição de música/álbum (issue #30).

Regra única que antes estava copiada: o nome da pasta da música vem de
`pasta` (só quando difere do nome) e o título das tabelas vem de `display`.
`build_song_patches` e `gen_indexes` liam esses campos cada um do seu jeito —
aqui existe uma resposta só, e o mapa e a árvore de pastas não podem discordar.

Camada: application (regras puras sobre dados já carregados).
"""

from __future__ import annotations

from typing import Any

__all__ = ['album_pasta', 'song_display', 'song_pasta']


def song_pasta(song: dict[str, Any]) -> str:
    """Nome da pasta da música (`defs['pasta']`, ou o próprio nome da música)."""
    return str(song.get('pasta') or song['song'])


def song_display(song: dict[str, Any]) -> str:
    """Título de exibição da música nas tabelas (`defs['display']`, ou o nome)."""
    return str(song.get('display') or song['song'])


def album_pasta(album: dict[str, Any]) -> str:
    """Pasta do álbum dentro de `patches/` (`albums[..]['pasta']`)."""
    return str(album['pasta'])
