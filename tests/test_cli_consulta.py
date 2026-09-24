"""Contrato da CLI do pacote — consulta (find/show/diff/export), issue #48.

Substitui os testes do shim `tools/gp100.py` (agora repasse puro ao pacote): a
CLI oficial é `gp100` (entry point do pacote) e os testes a exercitam via
CliRunner — o mesmo contrato que automação e agentes consomem. Leitura pura:
nenhum teste escreve no repositório (regra do projeto; export usa tmp_path).
"""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from gp100_architect.application.consulta import rotulo_param
from gp100_architect.interfaces.cli.main import app

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture(scope='module')
def defs():
    from gp100_architect.infrastructure.defs import carregar_e_validar

    return carregar_e_validar()


# ── find ────────────────────────────────────────────────────────────────────


def test_find_acha_por_musica_com_slot_e_caminho():
    r = runner.invoke(app, ['find', 'money'])
    assert r.exit_code == 0
    assert 'MNY01BA' in r.stdout
    assert 'U50' in r.stdout


def test_find_acha_por_banda():
    r = runner.invoke(app, ['find', 'santana'])
    assert r.exit_code == 0
    assert 'SMOO1SO' in r.stdout


def test_find_sem_resultado_sai_1():
    r = runner.invoke(app, ['find', 'zzznada'])
    assert r.exit_code == 1
    assert 'nada encontrado' in r.stdout


def test_find_json_shape_estavel():
    r = runner.invoke(app, ['find', 'money', '--json'])
    assert r.exit_code == 0
    dados = json.loads(r.stdout)
    assert dados and all(
        {'slot', 'nome', 'musica', 'camada', 'captador', 'arquivo'} <= set(item) for item in dados
    )
    assert any(i['nome'] == 'MNY01BA' and i['slot'] == 'U50' for i in dados)


# ── show ────────────────────────────────────────────────────────────────────


def test_show_mostra_cadeia_params_momentos():
    r = runner.invoke(app, ['show', 'smoo1so'])  # case-insensitive
    assert r.exit_code == 0
    assert 'U96' in r.stdout
    assert 'Yellow OD' in r.stdout
    assert 'Gain=48' in r.stdout


def test_show_json_tem_stomps_exp1_ir():
    r = runner.invoke(app, ['show', 'SMOO1SO', '--json'])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert {'nome', 'slot', 'cadeia', 'parametros', 'momentos', 'stomps', 'exp1', 'ir'} <= set(d)


def test_show_patch_inexistente_falha_com_dica():
    r = runner.invoke(app, ['show', 'ZZZZZZ'])
    assert r.exit_code == 1
    assert 'find' in r.output  # a dica manda usar o find


# ── diff ────────────────────────────────────────────────────────────────────


def test_diff_mostra_diferencas_reais():
    r = runner.invoke(app, ['diff', 'STH01BA', 'STH01SO'])
    assert r.exit_code == 0
    assert 'volume: 60 → 62' in r.stdout
    assert 'Blues OD → Green OD' in r.stdout


def test_diff_de_si_mesmo_nao_mostra_diferenca():
    r = runner.invoke(app, ['diff', 'SMOO1SO', 'SMOO1SO'])
    assert r.exit_code == 0
    assert '±' not in r.stdout


def test_diff_json_por_nome_oficial():
    r = runner.invoke(app, ['diff', 'STH01BA', 'STH01SO', '--json'])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert {'a', 'b', 'linhas', 'modulos'} <= set(d)
    assert d['a'] == 'STH01BA' and d['b'] == 'STH01SO'


def test_rotulo_oficial_e_usado():
    # família DLY no manual V2.0: Mix/Time/Fdbk (ordem dos params)
    assert rotulo_param('DLY', 'Sweet', 1) == 'Time'
    assert rotulo_param('DLY', 'Sweet', 0) == 'Mix'


# ── export ──────────────────────────────────────────────────────────────────


def test_listar_album_em_ordem_de_slot():
    r = runner.invoke(app, ['export', '--album', 'SN', '--listar'])
    assert r.exit_code == 0
    linhas = [ln for ln in r.stdout.splitlines() if 'SMOO' in ln]
    assert [ln.split()[0] for ln in linhas] == ['U94', 'U95', 'U96', 'U97']


def test_export_copia_para_destino(tmp_path):
    r = runner.invoke(app, ['export', '--album', 'SN', '--destino', str(tmp_path)])
    assert r.exit_code == 0
    copiados = sorted(p.name for p in tmp_path.glob('*.prst'))
    assert copiados == [
        'U94-SMOO1RI.prst',
        'U95-SMOO1CL.prst',
        'U96-SMOO1SO.prst',
        'U97-SMOO1FL.prst',
    ]


def test_album_invalido_erro_acionavel():
    r = runner.invoke(app, ['export', '--album', 'ZZ', '--listar'])
    assert r.exit_code == 1
    assert 'AR' in r.output  # lista os válidos
