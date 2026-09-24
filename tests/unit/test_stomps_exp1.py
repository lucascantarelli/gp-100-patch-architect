"""Validação do defs: doc.stomps e spec.exp1 (issue #9).

Módulos declarativos novos do schema — herdam o padrão da suíte: a asserção
não é "deu erro", é "o relatório aponta o caminho JSON e a correção".
"""

from __future__ import annotations

from typing import Any

import pytest

from gp100_architect.domain.validation import (
    EXP_PARAM_MAX,
    EXP_PARAM_MIN,
    Erros,
    validar,
)

pytestmark = pytest.mark.unit


def relatorio(defs: dict[str, Any]) -> str:
    erros: Erros = validar(defs)
    assert not erros.ok(), 'esperava problema e o defs passou'
    return erros.relatorio()


# ---- spec.exp1 ---------------------------------------------------------------


def test_exp1_valido_passa(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    dst = patch['spec']['modules'].get('DST')
    if dst is None:
        pytest.skip('primeiro patch do defs não tem DST')
    patch['spec']['exp1'] = {'módulo': 'DST', 'param': 'Gain'}
    er = validar(defs_mutavel)
    assert er.ok()


def test_exp1_fora_da_cadeia_aponta_a_cadeia(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['spec']['exp1'] = {'módulo': 'FUZZ', 'param': 'Gain'}
    texto = relatorio(defs_mutavel)
    assert 'spec.exp1.módulo' in texto
    assert 'fora da cadeia fixa' in texto


def test_exp1_modulo_fora_do_spec_reprova(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['spec']['exp1'] = {'módulo': 'MOD', 'param': 'Depth'}
    patch['spec']['modules'].pop('MOD', None)
    texto = relatorio(defs_mutavel)
    assert 'spec.exp1.módulo' in texto
    assert 'não está no spec.modules' in texto
    assert 'declare o módulo' in texto


def test_exp1_param_fora_do_modelo_lista_os_oficiais(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    dst = patch['spec']['modules'].get('DST')
    if dst is None:
        pytest.skip('primeiro patch do defs não tem DST')
    patch['spec']['exp1'] = {'módulo': 'DST', 'param': 'GainX'}
    texto = relatorio(defs_mutavel)
    assert 'spec.exp1.param' in texto
    assert 'não é parâmetro oficial' in texto
    assert 'nunca (pN)' in texto


def test_exp1_sem_parametro_nomeado_no_catalogo_reprova(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    nr = patch['spec']['modules'].get('NR')
    if nr is None or nr.get('name') != 'Gate 1':
        pytest.skip('primeiro patch do defs não tem NR Gate 1')
    patch['spec']['exp1'] = {'módulo': 'NR', 'param': 'Gain'}
    texto = relatorio(defs_mutavel)
    assert 'não é parâmetro oficial de NR Gate 1' in texto
    assert 'nunca (pN)' in texto


def test_exp1_min_fora_da_faixa(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    dst = patch['spec']['modules'].get('DST')
    if dst is None:
        pytest.skip('primeiro patch do defs não tem DST')
    patch['spec']['exp1'] = {'módulo': 'DST', 'param': 'Gain', 'min': 150}
    texto = relatorio(defs_mutavel)
    assert 'fora da faixa do pedal' in texto
    assert f'use {EXP_PARAM_MIN}–{EXP_PARAM_MAX}' in texto


def test_exp1_max_menor_que_min_reprova(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    dst = patch['spec']['modules'].get('DST')
    if dst is None:
        pytest.skip('primeiro patch do defs não tem DST')
    patch['spec']['exp1'] = {'módulo': 'DST', 'param': 'Gain', 'min': 80, 'max': 20}
    assert 'max (20) < min (80)' in relatorio(defs_mutavel)


def test_exp1_min_max_nao_numericos_reprova(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['spec']['exp1'] = {'módulo': 'MOD', 'param': 'Depth', 'max': 'alto'}
    patch['spec']['modules'].setdefault('MOD', {'name': 'A-Chorus', 'on': False})
    texto = relatorio(defs_mutavel)
    assert 'deve ser número' in texto


# ---- doc.stomps --------------------------------------------------------------


def test_stomps_valido_invertendo_fabrica_passa(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    fab = patch['spec']['modules']
    alvo = next(m for m in fab if m not in ('AMP', 'CAB'))
    novo = 'OFF' if fab[alvo].get('on') else 'ON'
    patch['doc']['stomps'] = [{'fs': 'A', 'mods': [[alvo, novo]], 'quando': 'na virada de seção'}]
    assert validar(defs_mutavel).ok()


def test_stomps_que_nao_invertem_reprova_com_a_correcao(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    fab = patch['spec']['modules']
    alvo, _m = next((m, mm) for m, mm in fab.items() if mm.get('on') and m not in ('AMP', 'CAB'))
    patch['doc']['stomps'] = [{'fs': 'A', 'mods': [[alvo, 'ON']], 'quando': 'x'}]
    texto = relatorio(defs_mutavel)
    assert 'não faria nada' in texto
    assert f'[{alvo}, OFF]' in texto


def test_stomp_de_amp_e_proibido(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['doc']['stomps'] = [{'fs': 'A', 'mods': [['AMP', 'OFF']], 'quando': 'x'}]
    assert 'toggle de AMP/CAB é proibido' in relatorio(defs_mutavel)


def test_stomp_fs_invalido(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['doc']['stomps'] = [{'fs': 'C', 'mods': [['DST', 'OFF']], 'quando': 'x'}]
    texto = relatorio(defs_mutavel)
    assert 'fs' in texto and 'use A, B ou A+B' in texto


def test_stomp_sem_campo_obrigatorio(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['doc']['stomps'] = [{'fs': 'A', 'mods': [['DST', 'OFF']]}]
    assert 'stomps[0].quando: obrigatório' in relatorio(defs_mutavel)


def test_stomps_lista_vazia_ped_para_omitir(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['doc']['stomps'] = []
    texto = relatorio(defs_mutavel)
    assert 'lista vazia' in texto
    assert 'omita doc.stomps' in texto


def test_stomps_modulo_fora_da_cadeia(defs_mutavel: dict[str, Any]):
    patch = defs_mutavel['songs'][0]['patches'][0]
    patch['doc']['stomps'] = [{'fs': 'A', 'mods': [['FUZZ', 'OFF']], 'quando': 'x'}]
    assert 'módulo FUZZ fora da cadeia' in relatorio(defs_mutavel)
