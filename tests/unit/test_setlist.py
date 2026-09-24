"""Regras puras de setlist: assinatura, distância, otimizador e dif.

Unidade de verdade: patches sintéticos mínimos (não o defs) — cada regra
testada isolada do dado. A aderência ao defs real é coberta pela camada
integration (tests/integration/test_setlist.py, issue #34).
"""

from typing import Any

import pytest

from gp100_architect.domain.setlist import (
    assinatura,
    dif_cadeia,
    distancia,
    modulos_da_assinatura,
    otimizar,
    trocas_totais,
)

pytestmark = pytest.mark.unit


def patch(nome_modulos: dict[str, tuple[str, bool]]) -> dict[str, Any]:
    """Patch cru mínimo: `{MOD: (modelo, ligado)}` → spec/modules do defs."""
    return {
        'spec': {
            'modules': {
                mod: {'name': nome, 'on': ligado} for mod, (nome, ligado) in nome_modulos.items()
            }
        }
    }


def p_default() -> dict[str, Any]:
    return patch({'CAB': ('D', True)})


# ── assinatura ───────────────────────────────────────────────────────────────


def test_assinatura_tem_nove_posicoes_pre_a_rvb():
    a = assinatura(p_default())
    assert len(a) == 9
    assert a[0] == ('', False)  # PRE não setado
    assert a[4] == ('D', True)  # CAB


def test_assinatura_capta_modelo_e_estado():
    p = patch({'PRE': ('COMP', True), 'DST': ('Blues OD', False), 'CAB': ('D', True)})
    a = assinatura(p)
    assert a[0] == ('COMP', True)
    assert a[1] == ('Blues OD', False)
    assert a[4] == ('D', True)


def test_patch_sem_spec_nao_explode():
    """Consumidor pode passar patch cru do defs sem spec — assina tudo vazio."""
    assert assinatura({}) == tuple(('', False) for _ in range(9))


# ── distância ────────────────────────────────────────────────────────────────


def test_iguais_tem_distancia_zero():
    assert distancia(assinatura(p_default()), assinatura(p_default())) == 0


def test_distancia_conta_modelo_e_estado_independente():
    a = assinatura(patch({'PRE': ('COMP', False), 'DST': ('X', True), 'CAB': ('D', True)}))
    b = assinatura(patch({'PRE': ('COMP', True), 'DST': ('Y', True), 'CAB': ('D', True)}))
    assert distancia(a, b) == 2  # trocou estado de PRE e modelo de DST; CAB igual


def test_distancia_simetrica():
    a = assinatura(patch({'PRE': ('COMP', True), 'CAB': ('D', True)}))
    b = assinatura(patch({'CAB': ('D', True), 'NR': ('Gate 1', True)}))
    assert distancia(a, b) == distancia(b, a)


# ── dif acionável ────────────────────────────────────────────────────────────


def test_dif_nada_muda_entre_iguais():
    assert dif_cadeia(p_default(), p_default()) == []


def test_dif_troca_de_modelo_diz_de_e_para():
    a = patch({'DST': ('Blues OD', True), 'CAB': ('D', True)})
    b = patch({'DST': ('La Charger', True), 'CAB': ('D', True)})
    assert dif_cadeia(a, b) == ['DST: Blues OD → La Charger']


def test_dif_ligar_e_desligar_tem_estado():
    a = patch({'DST': ('X', True), 'CAB': ('D', True)})
    b = patch({'DST': ('X', False), 'CAB': ('D', True)})
    assert dif_cadeia(a, b) == ['DST: desligar X']
    assert dif_cadeia(b, a) == ['DST: ligar X']


def test_dif_entrar_modulo_novo_sai_do_vazio():
    a = p_default()
    b = patch({'MOD': ('A-Chorus', True), 'CAB': ('D', True)})
    assert dif_cadeia(a, b) == ['MOD: (vazio) → A-Chorus']


# ── otimizador ───────────────────────────────────────────────────────────────


def item(song_id: str, patch_dado: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    return ({'id': song_id, 'song': song_id}, patch_dado)


def test_lista_vazia_vira_plano_vazio():
    assert otimizar([]) == []


def test_primeira_musica_fixa_e_nenhuma_repetida():
    itens = [item('A', p_default()), item('B', p_default()), item('C', p_default())]
    plano = otimizar(itens)
    assert plano[0] == itens[0]
    assert len({s['id'] for s, _ in plano}) == 3


def test_vizinho_mais_proximo_e_escolhido():
    nirvana = p_default()
    beatles = patch({'PRE': ('COMP', True), 'CAB': ('D', True)})
    zappa = patch({'CAB': ('D', True), 'RVB': ('Plate', True)})
    itens = [item('BEATLES', beatles), item('ZAPPA', zappa), item('NIRVANA', nirvana)]
    plano = otimizar(itens)
    # do Beatles (1 troca de qualquer coisa), o Nirvana (idêntico ao vazio+COMP?
    # não: Nirvana é o mais próximo) — ordem esperada: Beatles → Nirvana → Zappa
    assert [s['id'] for s, _ in plano] == ['BEATLES', 'NIRVANA', 'ZAPPA']


def test_otimizado_nunca_pior_que_a_ordem_dada():
    """Garantia que justifica o algoritmo: otimizar não piora o placar."""
    itens = [
        item('A', patch({'PRE': ('COMP', True), 'CAB': ('D', True)})),
        item('B', patch({'CAB': ('D', True), 'RVB': ('Plate', True)})),
        item('C', patch({'PRE': ('COMP', True), 'CAB': ('D', True), 'DLY': ('Sweet', True)})),
        item('D', patch({'CAB': ('D', True)})),
    ]
    dada = trocas_totais(itens)
    plano = otimizar(itens)
    assert trocas_totais(plano) <= dada


# ── placar ───────────────────────────────────────────────────────────────────


def test_trocas_totais_soma_o_plano():
    plano = [
        (item('A', p_default())[0], p_default()),
        (
            item('B', patch({'PRE': ('COMP', True), 'CAB': ('D', True)}))[0],
            patch({'PRE': ('COMP', True), 'CAB': ('D', True)}),
        ),
        (item('C', patch({'CAB': ('D', True)}))[0], patch({'CAB': ('D', True)})),
    ]
    assert trocas_totais(plano) == 2  # +PRE (A→B) e −PRE (B→C, volta ao vazio)


def test_modulos_da_assinatura_rotula_as_posicoes():
    pares = dict(modulos_da_assinatura(assinatura(p_default())))
    assert tuple(pares) == ('PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB')
    assert pares['CAB'] == ('D', True)


# ── regressão contra o defs real (o dado não mente) ─────────────────────────


def test_toda_assinatura_do_defs_real_tem_nove_posicoes(defs_real: dict[str, Any]):
    for song in defs_real['songs']:
        for p in song['patches']:
            assert len(assinatura(p)) == 9, p['nome']


def test_dif_do_defs_real_so_fala_de_modulos(defs_real: dict[str, Any]):
    """Mensagens da cola são sempre `MOD: …` — nenhum texto de dict vaza."""
    for song in defs_real['songs']:
        for p in song['patches']:
            for linha in dif_cadeia(p_default(), p):
                assert linha.split(':', 1)[0] in (
                    'PRE',
                    'DST',
                    'AMP',
                    'NR',
                    'CAB',
                    'EQ',
                    'MOD',
                    'DLY',
                    'RVB',
                )
