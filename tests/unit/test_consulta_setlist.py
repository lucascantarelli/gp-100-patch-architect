"""Camadas de consulta e setlist da aplicação (issues #48/#49) — in-process.

Os testes de CLI (`tests/test_cli_consulta.py`, `tests/test_cli_producao.py`)
exercitam o contrato externo; estes cobrem as bibliotecas diretamente —
incluindo os caminhos de erro que a CLI traduz em saída acionável.
"""

from __future__ import annotations

import pytest

from gp100_architect.application import consulta
from gp100_architect.application import setlist as setlist_app
from gp100_architect.domain.errors import EntradaInvalida
from gp100_architect.infrastructure.defs import carregar_e_validar

pytestmark = pytest.mark.unit


@pytest.fixture(scope='module')
def defs():
    return carregar_e_validar()


@pytest.fixture(scope='module')
def lib(defs):
    return setlist_app.BibliotecaSetlist(defs)


# ── consulta ────────────────────────────────────────────────────────────────


def test_buscar_encontra_por_varios_campos(defs, raiz):
    por_musica = consulta.buscar(defs, 'something', raiz=raiz)
    por_banda = consulta.buscar(defs, 'pink floyd', raiz=raiz)
    por_captador = consulta.buscar(defs, 'bridge', raiz=raiz)
    assert {a.nome for a in por_musica} >= {'STH01BA', 'STH01SO'}
    assert len(por_banda) == 38
    assert len(por_captador) > 0


def test_buscar_sem_resultado_devolve_lista_vazia(defs, raiz):
    assert consulta.buscar(defs, 'zzznada', raiz=raiz) == []


def test_dossie_traz_stomps_exp1_e_ir(defs, raiz):
    d = consulta.dossie(defs, 'DRY01SO', raiz=raiz)
    assert d.exp1 is not None  # demo da #9: Gain do La Charger no pedal
    assert d.exp1['módulo'] == 'DST'
    assert d.slot and d.arquivo.endswith('DRY01SO.prst')


def test_achar_patch_desconhecido_diz_como_achar(defs, raiz):
    with pytest.raises(EntradaInvalida) as e:
        consulta.achar_patch(defs, 'ZZZZ99', raiz=raiz)
    assert 'gp100 find' in str(e.value)


def test_diferencas_por_nome_oficial_de_parametro(defs, raiz):
    d = consulta.diferencas(defs, 'STH01BA', 'STH01SO', raiz=raiz)
    texto = '\n'.join(d['linhas'])
    assert 'volume: 60 → 62' in texto
    assert not any('p0' in linha or 'p1' in linha for linha in d['linhas'])


def test_planejar_exportacao_ordena_por_slot(defs, raiz):
    plano = consulta.planejar_exportacao(defs, raiz=raiz, album='SN')
    slots = [int(d.name.split('-')[0][1:]) for _o, d in plano.itens]
    assert slots == sorted(slots)
    assert len(plano.itens) == 4


def test_planejar_exportacao_album_invalido(defs, raiz):
    with pytest.raises(EntradaInvalida) as e:
        consulta.planejar_exportacao(defs, raiz=raiz, album='ZZ')
    assert 'válidos' in str(e.value)


# ── setlist (aplicação) ─────────────────────────────────────────────────────


def test_resolver_por_nome_id_e_patch(lib):
    assert lib.resolver('smooth')[1]['nome'] == 'SMOO1RI'  # nome → sufixo padrão
    assert lib.resolver('SMOO1')[1]['nome'] == 'SMOO1RI'  # id do defs
    assert lib.resolver('SMOO1:SO')[1]['nome'] == 'SMOO1SO'  # seção explícita
    assert lib.resolver('CT01VOX')[1]['nome'] == 'CT01VOX'  # patch completo


def test_resolver_desconhecido_sugere_o_catalogo(lib):
    with pytest.raises(EntradaInvalida) as e:
        lib.resolver('não-existe')
    assert '--list' in str(e.value)


def test_resolver_repertorio_repetido_erro(lib):
    with pytest.raises(EntradaInvalida) as e:
        setlist_app.resolver_repertorio(lib, ['Smooth', 'SMOO1:SO'], [], False)
    assert 'repetida' in str(e.value)


def test_resolver_repertorio_patch_orfao_erro(lib):
    with pytest.raises(EntradaInvalida) as e:
        setlist_app.resolver_repertorio(lib, ['Smooth'], ['Money:BA'], False)
    assert 'fora do repertório' in str(e.value)


def test_plano_json_slots_da_biblioteca(lib, defs):
    itens = [lib.resolver(p) for p in ['Smooth', 'Money']]
    from gp100_architect.application.setlist import otimizar

    plano = otimizar(itens)
    d = setlist_app.plano_json(plano, 7, lib.slots)
    assert d['trocas_totais'] == 7
    assert d['itens'][0]['slot'] == lib.slots[d['itens'][0]['patch']]
    assert d['itens'][0]['trocas'] == []  # primeira música não tem trocas
