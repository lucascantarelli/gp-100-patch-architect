"""Camada integration do defs — o dado commitado contra o validador do pacote.

Migração de `tests/test_defs_schema.py` (issue #34): o alvo agora é
`domain.validation.validar` + o loader `infrastructure.defs` (o shim
`tools/defs_schema.py` é delegação a estes). Cobertura em três frentes:

* **o defs commitado é válido** — sempre (o build inteiro depende disso);
* **as invariâncias de base** — álbuns declarados e completos, ids e pastas
  únicos, nomes de patch únicos e dentro do limite do painel (12 chars);
* **cada mutação produz erro acionável** — caminho JSON + como corrigir, o
  padrão do projeto para erro de dado.

Mutações em memória via `fixtures.mutado` — zero escrita em disco.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gp100_architect.domain import validation
from tests.fixtures import defs_sintetico, musica_sintetica, patch_sintetico

pytestmark = pytest.mark.integration


# ── o dado commitado é válido — sempre ──────────────────────────────────────


def test_defs_commitado_e_valido(defs_real: dict[str, Any]) -> None:
    er = validation.validar(defs_real)
    assert er.ok(), er.relatorio()


def test_loader_v2_consolidado_tem_as_quatro_chaves(defs_real: dict[str, Any]) -> None:
    """O consolidado dos fragmentos mantém o shape do monólito (issue #8)."""
    assert {'meta', 'albums', 'ir_local', 'songs'} <= set(defs_real)


# ── invariâncias de base (seção A do guardião de dados) ─────────────────────


def test_albuns_declarados(defs_real: dict[str, Any]) -> None:
    for song in defs_real['songs']:
        assert song['idAlbum'] in defs_real['albums'], (
            f'{song["id"]}: idAlbum {song["idAlbum"]} não está em albums'
        )


def test_albuns_completos(defs_real: dict[str, Any], raiz: Path) -> None:
    for key, alb in defs_real['albums'].items():
        for campo in ('banda', 'album', 'ano', 'display', 'pasta'):
            assert alb.get(campo) not in (None, ''), f"albums.{key} sem '{campo}'"
        assert (raiz / 'patches' / alb['pasta']).is_dir(), (
            f'albums.{key}: pasta {alb["pasta"]} não existe em patches/'
        )


def test_ids_de_musica_unicos(defs_real: dict[str, Any]) -> None:
    ids = [s['id'] for s in defs_real['songs']]
    assert len(ids) == len(set(ids)), 'id de música repetido'


def test_nomes_de_patch_unicos_e_no_limite_do_painel(defs_real: dict[str, Any]) -> None:
    nomes = [p['nome'] for s in defs_real['songs'] for p in s['patches']]
    assert len(nomes) == len(set(nomes)), 'nome de patch repetido'
    for nome in nomes:
        assert len(nome) <= 12, f'{nome}: mais de 12 caracteres'
        assert nome.isascii() and nome.isupper(), f'{nome}: use só A-Z e 0-9'


# ── mutações acionáveis (erros com caminho JSON + correção) ─────────────────


def _um_erro_contem(defs: dict[str, Any], *termos: str) -> None:
    er = validation.validar(defs)
    assert not er.ok(), 'esperava erro e veio OK'
    txt = er.relatorio()
    for t in termos:
        assert t in txt, f"'{t}' ausente no relatório:\n{txt}"


def _patch(defs: dict[str, Any], nome: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """(song, patch) localizado pelo nome do painel — para mutações realistas."""
    for song in defs['songs']:
        for patch in song['patches']:
            if patch['nome'] == nome:
                return song, patch
    raise KeyError(nome)


def test_nome_maior_que_12(defs_mutavel: dict[str, Any]) -> None:
    _patch(defs_mutavel, 'CT01RIF')[1]['nome'] = 'NOMEGRANDE134'
    _um_erro_contem(defs_mutavel, '13 chars', 'máx. 12')


def test_nome_duplicado(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['songs'][0]['patches'][0]['nome'] = defs_mutavel['songs'][1]['patches'][0]['nome']
    _um_erro_contem(defs_mutavel, 'duplicado')


def test_idalbum_desconhecido(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['songs'][0]['idAlbum'] = 'XX'
    _um_erro_contem(defs_mutavel, 'idAlbum', 'XX', 'ids válidos')


def test_bpm_impossivel(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['songs'][0]['bpm'] = 999
    _um_erro_contem(defs_mutavel, 'bpm', '30–300')


def test_modulo_fora_da_cadeia(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['songs'][0]['patches'][0]['spec']['modules']['ZZ'] = {'name': 'X', 'on': False}
    _um_erro_contem(defs_mutavel, 'modules.ZZ', 'cadeia fixa')


def test_toggle_de_amp_proibido(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['songs'][0]['patches'][0]['doc']['momentos'] = [
        {'nome': 'x', 'mods': [['AMP', 'OFF']], 'quando': 'nunca'}
    ]
    _um_erro_contem(defs_mutavel, 'momentos', 'AMP/CAB é proibido')


def test_time_fora_de_ms(defs_mutavel: dict[str, Any]) -> None:
    _patch(defs_mutavel, 'SMOO1SO')[1]['spec']['modules']['DLY']['params']['1'] = 5000
    _um_erro_contem(defs_mutavel, 'ms fora de 0–1000')


def test_param_nao_numerico(defs_mutavel: dict[str, Any]) -> None:
    _patch(defs_mutavel, 'SMOO1SO')[1]['spec']['modules']['DLY']['params']['1'] = 'muito'
    _um_erro_contem(defs_mutavel, 'não numérico')


def test_genero_invalido(defs_mutavel: dict[str, Any]) -> None:
    _patch(defs_mutavel, 'SMOO1SO')[1]['spec']['type'] = 'Samba'
    _um_erro_contem(defs_mutavel, 'type', 'Samba', 'gênero válido')


def test_ir_local_orfao(defs_mutavel: dict[str, Any]) -> None:
    defs_mutavel['ir_local']['Cab Fantasma'] = {'captura': 'x.wav', 'slot': 'User IR 9'}
    _um_erro_contem(defs_mutavel, 'ir_local.Cab Fantasma', 'nenhum patch usa')


def test_momento_aponta_modulo_inexistente() -> None:
    """Regra de momentos exercitada em defs sintético (sem depender do commitado)."""
    p = patch_sintetico(
        'TST01SO',
        momentos=[{'nome': 'x', 'mods': [['ZZ', 'OFF']], 'quando': 'nunca'}],
    )
    _um_erro_contem(defs_sintetico(songs=[musica_sintetica(patches=[p])]), 'ZZ', 'fora da cadeia')
