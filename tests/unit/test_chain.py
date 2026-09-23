"""Cadeia de módulos: ordem canônica, imutabilidade e consultas."""

import pytest

from gp100_architect.domain.chain import (
    CHAIN,
    MODULOS_PROIBIDOS_EM_MOMENTO,
    nomeados,
    posicao,
    valido,
)

pytestmark = pytest.mark.unit


def test_cadeia_tem_os_nove_modulos_na_ordem_de_sinal():
    assert CHAIN == ('PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB')


def test_cadeia_e_imutavel_no_dominio():
    """Ordem de sinal é regra do firmware, não estado de execução."""
    assert isinstance(CHAIN, tuple)
    with pytest.raises(TypeError):
        CHAIN[0] = 'XXX'  # type: ignore[index]


def test_posicao_reflete_a_ordem_de_sinal():
    assert [posicao(m) for m in CHAIN] == list(range(9))
    assert posicao('PRE') == 0
    assert posicao('RVB') == 8


def test_posicao_de_modulo_desconhecido_e_menos_um():
    assert posicao('VOX') == -1
    assert posicao('') == -1


def test_valido_reconhece_apenas_modulos_da_cadeia():
    assert all(valido(m) for m in CHAIN)
    assert not valido('VOX')
    assert not valido('pre')


def test_nomeados_lista_a_cadeia_para_mensagem_acionavel():
    assert nomeados(None) == 'PRE, DST, AMP, NR, CAB, EQ, MOD, DLY, RVB'


def test_amp_e_cab_nunca_sao_alternados():
    """Regra do doc 12: toggle de AMP/CAB muda volume e corpo ao vivo."""
    assert MODULOS_PROIBIDOS_EM_MOMENTO == {'AMP', 'CAB'}
    assert 'MOD' not in MODULOS_PROIBIDOS_EM_MOMENTO
