"""Modelo tipado: o defs real vira objetos e a cadeia usada sai na ordem certa."""

from typing import Any

import pytest

from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.model import Album, Modulo, Patch, Song, albuns_do_defs, songs_do_defs

pytestmark = pytest.mark.unit


def test_album_from_dict_completa_o_display_opcional():
    album = Album.from_dict(
        'AR', {'banda': 'B', 'album': 'A', 'ano': 1973, 'pasta': 'P', 'rig': 'R'}
    )
    assert (album.id, album.ano, album.display) == ('AR', 1973, '')


def test_modulo_normaliza_indices_de_parametro_para_int():
    modulo = Modulo.from_dict({'name': 'Sweet', 'on': True, 'params': {'1': 320}})
    assert modulo.params == {1: 320.0}


def test_modulo_sem_on_assume_ligado():
    """O defs omite `on` quando o módulo está ativo — ausência não é desligado."""
    assert Modulo.from_dict({'name': 'D'}).ligado is True


def test_patch_usados_saem_na_ordem_da_cadeia():
    patch = Patch.from_dict(
        {
            'nome': 'X',
            'sufixo': 'BA',
            'camada': 'Base',
            'spec': {
                'type': 'Rock',
                'modules': {
                    'RVB': {'name': 'Plate', 'on': True},
                    'PRE': {'name': 'COMP', 'on': True},
                    'CAB': {'name': 'D', 'on': True},
                },
            },
        }
    )
    assert patch.usados == ('PRE', 'CAB', 'RVB')


def test_song_from_dict_traz_patches_tipados():
    song = Song.from_dict(
        {
            'id': 'X1',
            'song': 'X',
            'idAlbum': 'AR',
            'bpm': 120,
            'patches': [
                {'nome': 'X1BA', 'sufixo': 'BA', 'camada': 'Base', 'spec': {'modules': {}}}
            ],
        }
    )
    assert isinstance(song.patches[0], Patch)
    assert song.bpm == 120.0


def test_conveniencias_mapeiam_o_defs_real(defs_real: dict[str, Any]):
    albuns = albuns_do_defs(defs_real)
    songs = songs_do_defs(defs_real)
    assert len(albuns) == len(defs_real['albums'])
    assert len(songs) == len(defs_real['songs'])
    assert all(s.id_album in albuns for s in songs), 'toda música aponta para álbum declarado'


def test_todo_patch_do_defs_real_tem_camada_e_tipo(defs_real: dict[str, Any]):
    """O modelo não inventa default: campo obrigatório tem de estar no defs."""
    for song in songs_do_defs(defs_real):
        for patch in song.patches:
            assert patch.camada, f'{patch.nome}: camada vazia'
            assert patch.tipo, f'{patch.nome}: tipo vazio'
            assert patch.modulos['CAB'].nome, f'{patch.nome}: CAB sem modelo'


def test_cadeia_do_modelo_e_subconjunto_da_dominio(defs_real: dict[str, Any]):
    for song in songs_do_defs(defs_real):
        for patch in song.patches:
            assert set(patch.usados) <= set(CHAIN)
