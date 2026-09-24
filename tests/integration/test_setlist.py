"""Setlist sobre o defs real — resolução, otimização e relatórios (issue #34).

Migração de `tests/test_setlist.py` (a suíte do shim `tools/gp100_setlist.py`):
as REGRAS puras já têm camada unit (`tests/unit/test_setlist.py`) e a aplicação
tem `tests/unit/test_consulta_setlist.py` — aqui fica o que só o **dado
commitado** prova: o catálogo inteiro, a ordem de palco sobre patches reais e
os relatórios com os slots da numeração da biblioteca.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from gp100_architect.application import setlist as setlist_app
from gp100_architect.domain.errors import EntradaInvalida
from gp100_architect.domain.setlist import (
    assinatura,
    dif_cadeia,
    distancia,
    otimizar,
    trocas_totais,
)
from gp100_architect.infrastructure.defs import carregar_e_validar

pytestmark = pytest.mark.integration


@pytest.fixture(scope='module')
def lib() -> setlist_app.BibliotecaSetlist:
    return setlist_app.BibliotecaSetlist(carregar_e_validar())


def itens_de(lib: setlist_app.BibliotecaSetlist, pedidos: list[str]) -> list[Any]:
    return [lib.resolver(p) for p in pedidos]


# ── resolução de pedidos sobre o catálogo real ──────────────────────────────


COM_SECOES = ['CT01', 'STH01', 'OHB01', 'SMOO1', 'SLT01']


def test_padrao_e_um_patch_com_secao(lib: setlist_app.BibliotecaSetlist) -> None:
    for sid in COM_SECOES:
        _musica, patch = lib.resolver(sid)
        assert patch['nome'].startswith(sid)


def test_secao_explicita_por_dois_pontos(lib: setlist_app.BibliotecaSetlist) -> None:
    _m, patch = lib.resolver('SMOO1:SO')
    assert patch['nome'] == 'SMOO1SO'


def test_patch_completo_aceito(lib: setlist_app.BibliotecaSetlist) -> None:
    musica, patch = lib.resolver('CT01VOX')
    assert patch['nome'] == 'CT01VOX'
    assert musica['id'] == 'CT01'


def test_secao_inexistente_sugere_as_disponiveis(lib: setlist_app.BibliotecaSetlist) -> None:
    with pytest.raises(EntradaInvalida) as e:
        lib.resolver('SMOO1:XX')
    assert 'não tem seção' in str(e.value)
    assert 'RI' in str(e.value)  # as seções disponíveis entram na mensagem


def test_catalogo_cobre_a_biblioteca(lib: setlist_app.BibliotecaSetlist) -> None:
    assert len(lib.catalogo()) == 58


# ── ordem de palco sobre patches reais ──────────────────────────────────────


def test_comeca_na_primeira_e_termina_sem_repeticao(lib: setlist_app.BibliotecaSetlist) -> None:
    itens = itens_de(lib, ['CT01', 'STH01', 'MNY01', 'PMH01'])
    plano = otimizar(itens)
    assert plano[0] == itens[0]
    assert len({m['id'] for m, _ in plano}) == len(itens)


def test_vizinho_mais_proximo_escolhido(lib: setlist_app.BibliotecaSetlist) -> None:
    itens = itens_de(lib, ['SLT01', 'CT01', 'SCH01'])  # Nirvanas idênticos
    plano = otimizar(itens)
    # começa no default (RI), vai ao Nirvana idêntico (0 trocas) e só
    # então cruza para os Beatles
    assert [p['nome'] for _, p in plano] == ['SLT01RI', 'SCH01RI', 'CT01RIF']


def test_total_trocas_nunca_pior_que_ordem_dada(lib: setlist_app.BibliotecaSetlist) -> None:
    itens = itens_de(lib, ['CT01', 'PMH01', 'SLT01', 'STH01', 'MNY01'])
    ordem_dada = sum(
        distancia(assinatura(itens[i][1]), assinatura(itens[i + 1][1]))
        for i in range(len(itens) - 1)
    )
    plano = otimizar(itens)
    assert trocas_totais(plano) <= ordem_dada


# ── dif de cadeia entre patches reais ───────────────────────────────────────


def test_nada_muda_entre_nirvanas(lib: setlist_app.BibliotecaSetlist) -> None:
    _m, ri = lib.resolver('SLT01:RI')
    _m, so = lib.resolver('SLT01:SO')
    assert dif_cadeia(ri, so) == []


def test_modelo_diferente_aparece(lib: setlist_app.BibliotecaSetlist) -> None:
    _m, ba = lib.resolver('STH01:BA')
    _m, so = lib.resolver('STH01:SO')
    diffs = dif_cadeia(ba, so)
    assert any('DST' in d and 'Green OD' in d for d in diffs)


def test_ligar_desligar_aparece(lib: setlist_app.BibliotecaSetlist) -> None:
    _m, ri = lib.resolver('SMOO1:RI')
    _m, fl = lib.resolver('SMOO1:FL')
    assert any('DST' in d for d in dif_cadeia(ri, fl))


# ── relatórios com os slots da biblioteca ───────────────────────────────────


@pytest.fixture(scope='module')
def plano_real(lib: setlist_app.BibliotecaSetlist):
    plano = otimizar(itens_de(lib, ['CT01', 'SLT01', 'STH01']))
    total = trocas_totais(plano)
    return plano, total


def test_markdown_tem_slot_e_trocas(plano_real, lib: setlist_app.BibliotecaSetlist) -> None:
    plano, total = plano_real
    md = setlist_app.plano_markdown(plano, total, lib.slots)
    assert '| # | Slot | Música | Patch |' in md
    assert '`SLT01RI`' in md
    assert 'U' in md  # slots vêm do slot_map


def test_json_bate_com_o_plano(plano_real, lib: setlist_app.BibliotecaSetlist) -> None:
    plano, total = plano_real
    out = setlist_app.plano_json(plano, total, lib.slots)
    assert len(out['itens']) == len(plano)
    assert out['itens'][0]['patch'] == plano[0][1]['nome']
    assert out['itens'][0]['slot'] == 'U01'  # slot real, não morto


def test_cabecalho_conta_trocas_reais(lib: setlist_app.BibliotecaSetlist) -> None:
    """Regressão: main() media dicts (sempre 0); deve medir chaves de cadeia."""
    plano = otimizar(itens_de(lib, ['CT01', 'SMOO1']))
    total = trocas_totais(plano)
    md = setlist_app.plano_markdown(plano, total, lib.slots)
    assert re.search(r'\b[1-9]\d* troca', md)  # zero é bug aqui
