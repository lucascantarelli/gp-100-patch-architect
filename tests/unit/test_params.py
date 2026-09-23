"""Catálogo de parâmetros: consultas e aderência ao defs commitado."""

from typing import Any

import pytest

from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.params import PARAM_NAMES, ROTULOS_EM_MS, parametros, rotulo

pytestmark = pytest.mark.unit


def test_consultas_de_parametro():
    assert parametros('CAB', 'D') == ('Level', 'High Cut')
    assert rotulo('DLY', 'Sweet', 1) == 'Time'
    assert rotulo('RVB', 'Spring', 1) == 'Decay'


def test_consultas_fora_do_catalogo_nao_inventam_nome():
    """Sem tabela, o validador deve calar — nunca chutar um rótulo."""
    assert parametros('MOD', 'Modelo Novo') == ()
    assert rotulo('MOD', 'Modelo Novo', 0) is None
    assert rotulo('CAB', 'D', 9) is None


def test_tempo_em_ms_e_conjunto_proprio():
    assert ROTULOS_EM_MS == {'Time', 'Pre Delay'}
    assert rotulo('DLY', 'T-Echo', 1) in ROTULOS_EM_MS


def test_todo_modelo_setado_no_defs_tem_tabela_de_nomes(defs_real: dict[str, Any]):
    """A asserção que o pipeline não pode perder (seção F do TestH).

    Um modelo novo com params e sem tabela faz o validador parar de checar o
    range dos valores — silêncio perigoso. Este teste falha alto e o conserto é
    entrar no catálogo (reference/15) ou zerar os params.
    """
    sem_tabela = sorted(
        {
            (mod, modulo['name'])
            for song in defs_real['songs']
            for patch in song['patches']
            for mod, modulo in (patch['spec'].get('modules') or {}).items()
            if modulo.get('params') and (mod, modulo.get('name')) not in PARAM_NAMES
        }
    )
    assert not sem_tabela, f'modelos com params sem tabela de nomes: {sem_tabela}'


def test_defs_so_usa_modulos_da_cadeia(defs_real: dict[str, Any]):
    usados = {
        mod
        for song in defs_real['songs']
        for patch in song['patches']
        for mod in patch['spec']['modules']
    }
    assert usados <= set(CHAIN)
