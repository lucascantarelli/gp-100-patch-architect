"""Índices da biblioteca — mapa por álbum e README geral (issue #30).

O `TestG` do TestH compara os índices em disco com o que o gerador produz (via
shim). Aqui o alvo é o caso de uso em si: ordem dos álbuns, tabela de IR com e
sem catálogo, e os nomes derivados do defs — tudo em `tmp_path`.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import indices, nomes

pytestmark = pytest.mark.unit


def test_album_order_segue_a_ordem_das_musicas(defs_real: dict[str, Any]):
    defs = copy.deepcopy(defs_real)
    ordem = indices.album_order(defs)
    assert len(ordem) == len(defs['albums'])
    assert set(ordem) == set(defs['albums'])
    # a primeira chave é a do primeiro idAlbum em songs (ordem dos slots)
    assert ordem[0] == defs['songs'][0]['idAlbum']


def test_build_all_gera_mapa_de_cada_album_mais_o_readme(defs_real: dict[str, Any], tmp_path: Path):
    defs = copy.deepcopy(defs_real)
    saidas, total = indices.build_all(defs, raiz=tmp_path, ir_index={})

    assert total == sum(len(s['patches']) for s in defs['songs'])
    assert len(saidas) == len(defs['albums']) + 1  # mapas + README
    assert tmp_path / 'patches' / 'README.md' in saidas
    for caminho, texto in saidas.items():
        assert caminho.is_relative_to(tmp_path / 'patches')
        assert caminho.name in ('MAPA-DO-ALBUM.md', 'README.md')
        assert texto.startswith('#')
    # o README geral lista todos os álbuns, com o total de patches
    assert f'patches-{total}-e02d2d' in saidas[tmp_path / 'patches' / 'README.md']


def test_mapa_usa_a_fonte_unica_de_nomes(defs_real: dict[str, Any], tmp_path: Path):
    defs = copy.deepcopy(defs_real)
    saidas, _total = indices.build_all(defs, raiz=tmp_path, ir_index={})
    primeira = defs['songs'][0]

    album = defs['albums'][primeira['idAlbum']]
    mapa = saidas[tmp_path / 'patches' / nomes.album_pasta(album) / 'MAPA-DO-ALBUM.md']
    assert nomes.song_display(primeira) in mapa
    assert primeira['patches'][0]['nome'] in mapa
    assert album['display'] in mapa


def test_ir_recomendada_distingue_banco_de_fabrica(defs_real: dict[str, Any]):
    defs = copy.deepcopy(defs_real)
    cab, par = next(iter(defs['ir_local'].items()))
    captura = par['captura']

    assert indices.ir_recomendada(defs, {}, cab) == f'{captura} (ver reference/16-ir-library.md)'
    assert indices.ir_recomendada(defs, None, cab) is None  # catálogo ilegível
    assert indices.ir_recomendada(defs, {}, 'CAB Que Não Existe') is None
    com_mix = {captura: [f'{captura} Medium Mix.wav']}
    assert indices.ir_recomendada(defs, com_mix, cab) == f'{captura} — {captura} Medium Mix.wav'


def test_ir_recomendada_sem_mix_medium_cai_para_a_referencia(defs_real: dict[str, Any]):
    defs = copy.deepcopy(defs_real)
    cab, par = next(iter(defs['ir_local'].items()))
    captura = par['captura']
    assert (
        indices.ir_recomendada(defs, {captura: [f'{captura} Bright Mix.wav']}, cab)
        == f'{captura} (ver reference/16-ir-library.md)'
    )


def test_mapa_marca_irmao_quando_ha_captura_local(defs_real: dict[str, Any], tmp_path: Path):
    defs = copy.deepcopy(defs_real)
    _cab, par = next(iter(defs['ir_local'].items()))
    ir_index = {par['captura']: [f'{par["captura"]} Medium Mix.wav']}
    saidas, _total = indices.build_all(defs, raiz=tmp_path, ir_index=ir_index)
    textos = '\n'.join(saidas.values())
    assert '📁' in textos  # alguma linha recomenda o banco
    assert '⚙️ fábrica' in textos  # e outras seguem na fábrica


def test_build_readme_resume_albuns_e_total(tmp_path: Path):
    album_blocks = '| 🎸 **Banda** | **Álbum** | 2 | 5 | [`MAPA-DO-ALBUM.md`](a/MAPA-DO-ALBUM.md) |'
    readme = indices.build_readme(album_blocks, 5)
    assert 'patches-5-e02d2d' in readme
    assert album_blocks in readme
    assert 'uv run gp100 build' in readme


def test_nomes_derivados_do_defs():
    assert nomes.song_pasta({'song': 'X'}) == 'X'
    assert nomes.song_pasta({'song': 'X', 'pasta': 'X (ao vivo)'}) == 'X (ao vivo)'
    assert nomes.song_display({'song': 'X'}) == 'X'
    assert nomes.song_display({'song': 'X', 'display': 'X, Pt. 2'}) == 'X, Pt. 2'
    assert nomes.album_pasta({'pasta': 'Banda/Álbum (1999)'}) == 'Banda/Álbum (1999)'
