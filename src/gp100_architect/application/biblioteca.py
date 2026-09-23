"""Casos de uso da biblioteca de patches — slots, documentação e `.prst` (#30).

Migração de `tools/build_song_patches.py`: o script vira biblioteca. A camada
de aplicação **orquestra** (numera slots, monta o spec final, chama a
renderização e o codec) e devolve dados tipados; quem escreve no disco é o
`infrastructure.escrita`, e quem imprime é o shim de `tools/`.

Contrato que a migração preserva byte a byte (provado pelo TestH):

* o slot de cada patch é a posição dele na travessia de `defs['songs']`, na
  mesma ordem que `gen_indexes` usa — numeração divergente é bug;
* `author`/`notes` do spec saem do nome da música e da camada do patch;
* o nome no painel (`ppName`) é conferido contra o nome do patch e contra o
  limite de 12 caracteres do display da pedaleira.

Camada: application (não imprime; recebe o catálogo de IRs já carregado).
"""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gp100_architect.application import nomes
from gp100_architect.application.rendering import patch_md
from gp100_architect.domain.errors import FormatoPrstInvalido, SpecInvalido
from gp100_architect.infrastructure.prst.codec import gerar_xml

__all__ = ['AUTOR', 'LIMITE_NOME', 'PatchGerado', 'gerar', 'slots', 'travessia']

AUTOR = 'GP-100 Patch Architect'
LIMITE_NOME = 12  # limite do display da GP-100 (nome no painel)


@dataclass(frozen=True)
class PatchGerado:
    """Um patch pronto para virar arquivo — o que o pipeline produz.

    `pasta` é o diretório do patch (`patches/<Banda>/<Álbum>/<Música>/<NOME>`);
    `documentacao` é o `patch.md` completo e `prst` são os bytes do `.prst`.
    """

    nome: str
    musica: str
    camada: str
    slot: str
    pasta: Path
    documentacao: str
    prst: bytes


def travessia(defs: dict[str, Any]) -> Iterator[tuple[dict[str, Any], dict[str, Any]]]:
    """`(song, patch)` na ordem que define a numeração de slots."""
    for song in defs['songs']:
        for patch in song['patches']:
            yield song, patch


def slots(defs: dict[str, Any]) -> dict[str, str]:
    """`{'NOME_DO_PATCH': 'U01'}` — numeração contínua entre álbuns.

    Mesma travessia de `application.indices` (e a que `gp100_setlist` consome):
    se um álbum novo entrar, os três continuam concordando sobre o slot.
    """
    mapa: dict[str, str] = {}
    for i, (_song, patch) in enumerate(travessia(defs), start=1):
        mapa[patch['nome']] = f'U{i:02d}'
    return mapa


def _pasta_do_patch(
    raiz: Path, defs: dict[str, Any], song: dict[str, Any], patch: dict[str, Any]
) -> Path:
    album = defs['albums'][song['idAlbum']]
    nome: str = patch['nome']
    return raiz / 'patches' / nomes.album_pasta(album) / nomes.song_pasta(song) / nome


def _spec_do_patch(
    song: dict[str, Any], patch: dict[str, Any], albums: dict[str, Any]
) -> dict[str, Any]:
    """Cópia do spec com `author`/`notes` derivados da música (nunca do patch irmão)."""
    spec: dict[str, Any] = copy.deepcopy(patch['spec'])
    spec['author'] = AUTOR
    spec['notes'] = f'{song["song"]} ({albums[song["idAlbum"]]["album"]}) - {patch["camada"]}'
    return spec


def _validar_nome_no_xml(prst: bytes, nome: str) -> None:
    """O `.prst` exporta o nome do patch; divergência impede o import correto."""
    try:
        root = ET.fromstring(prst)
    except ET.ParseError as exc:  # pragma: no cover — codec gera XML válido
        raise FormatoPrstInvalido(f'{nome}: o codec gerou XML inválido ({exc})') from exc
    presets = root.find('presets')
    painel = presets.get('ppName') if presets is not None else None
    if painel != nome:
        raise SpecInvalido(f'{nome}: nome no painel diverge do defs (ppName={painel!r})')
    if len(nome) > LIMITE_NOME:
        raise SpecInvalido(f'{nome}: nome > {LIMITE_NOME} chars (limite do display da GP-100)')


def gerar(
    defs: dict[str, Any],
    *,
    raiz: Path,
    ir_index: dict[str, list[str]],
    templates: dict[tuple[str, str], dict[str, Any]],
    build_time: str | None = None,
) -> list[PatchGerado]:
    """Gera todos os patches do defs **em memória** (sem tocar o disco).

    Devolve a lista na ordem da travessia — o mesmo ordem em que os slots foram
    numerados. `ir_index` é o índice do catálogo local de IRs (`{'Gabinete':
    [arquivos]}`); sem ele a documentação indica só o CAB de fábrica.
    """
    albuns = defs['albums']
    ir_local = defs['ir_local']
    mapa_slots = slots(defs)
    gerados: list[PatchGerado] = []
    for song in defs['songs']:
        for patch in song['patches']:
            slot = mapa_slots[patch['nome']]
            spec = _spec_do_patch(song, patch, albuns)
            documentacao = patch_md.build_doc(
                song, patch, spec, slot, albums=albuns, ir_local=ir_local, ir_index=ir_index
            )
            prst = gerar_xml(spec, templates, build_time=build_time)
            _validar_nome_no_xml(prst, patch['nome'])
            gerados.append(
                PatchGerado(
                    nome=patch['nome'],
                    musica=song['song'],
                    camada=patch['camada'],
                    slot=slot,
                    pasta=_pasta_do_patch(raiz, defs, song, patch),
                    documentacao=documentacao,
                    prst=prst,
                )
            )
    return gerados
