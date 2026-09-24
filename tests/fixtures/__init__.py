"""Factories da suíte — dados sintéticos em memória, zero escrita no repositório.

Duas regras da casa materializadas aqui (issue #34):

1. **teste de unidade não lê o defs commitado** — usa um factory (`defs_sintetico`,
   `patch_sintetico`) para exercitar a regra; o dado real é aderência, coberta
   nos níveis integration/e2e;
2. **nenhum teste escreve no repositório** — quem precisa de disco usa `tmp_path`
   e aponta `GP100_DEFS` para lá.

As factories espelham o shape do schema v2 (issue #8) — as chaves que o
domínio lê de verdade — e **nada mais**: chaves inventadas aqui morreriam no
primeiro refactor do defs sem um único teste acender.
"""

from __future__ import annotations

import copy
from typing import Any

__all__ = ['album_sintetico', 'defs_sintetico', 'musica_sintetica', 'patch_sintetico']

# a cadeia fixa do fw 2.1 (a mesma do domínio — assinatura de 9 posições)
_MODULOS = ('PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB')


def patch_sintetico(
    nome: str = 'TST01RI',
    *,
    sufixo: str | None = None,
    modules: dict[str, dict[str, Any]] | None = None,
    momentos: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Patch do defs com o shape que o domínio lê (`nome`, `sufixo`, `spec`, `doc`).

    `modules` recebe `{MOD: {'name': ..., 'on': ...}}` — os módulos omitidos não
    entram no spec (o que o pipeline considera "nada setado").
    """
    mods = {m: dict(v) for m, v in (modules or {}).items() if m in _MODULOS}
    for v in mods.values():
        v.setdefault('name', '')
        v.setdefault('on', False)
    return {
        'nome': nome,
        'sufixo': sufixo or nome[5:],
        'spec': {
            'type': 'Rock',
            'bpm': 120,
            'volume': 55,
            'ir_slot': None,
            'modules': mods,
        },
        'doc': {'momentos': momentos or []},
    }


def musica_sintetica(
    id_: str = 'TST',
    song: str = 'Testing',
    id_album: str = 'TST',
    patches: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Música do defs — `pasta` explícita (o que `nomes.song_pasta` respeita)."""
    return {
        'id': id_,
        'song': song,
        'pasta': song.replace(' ', '-'),
        'idAlbum': id_album,
        'patches': patches or [patch_sintetico(f'{id_}01RI')],
    }


def album_sintetico(
    id_: str = 'TST',
    album: str = 'Testing (2026)',
    banda: str = 'The Factories',
    ano: int = 2026,
    pasta: str | None = None,
) -> dict[str, Any]:
    """Álbum do defs — os 5 campos que `validar` exige preenchidos."""
    return {
        'idAlbum': id_,
        'banda': banda,
        'album': album,
        'ano': ano,
        'display': f'{banda} — {album}',
        'pasta': pasta or f'{banda.replace(" ", "-")}/{album.replace(" ", "-")}',
    }


def defs_sintetico(
    songs: list[dict[str, Any]] | None = None,
    albums: list[dict[str, Any]] | None = None,
    *,
    ir_local: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Defs consolidado mínimo — o mesmo shape que `infrastructure.defs` devolve.

    Vem com uma música default e `ir_local` vazio: as regras de assinatura e
    otimização precisam de pelo menos uma música; quem quer IRs locais injeta
    (`ir_local={'Cab': {'captura': 'x.wav', 'slot': 'User IR 1'}}`).
    """
    return {
        'meta': {'formato': 2},
        'albums': {a['idAlbum']: a for a in (albums or [album_sintetico()])},
        'ir_local': ir_local or {},
        'songs': songs or [musica_sintetica()],
    }


def mutado(defs: dict[str, Any], *aplicar: Any) -> dict[str, Any]:
    """Cópia profunda do defs com mutações aplicadas por callback — padrão da casa.

    A herança dos testes do validador (test_defs_schema.py legado): cada teste
    descreve a mutação como função e valida a mensagem de erro resultante —
    zero escrita em disco.
    """
    d = copy.deepcopy(defs)
    for a in aplicar:
        a(d)
    return d
