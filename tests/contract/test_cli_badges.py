"""Contrato do `gp100 badges` — a CLI grava os derivados no destino (issue #117).

Por que este teste existe: o badge é consumido pelo shields.io via URL do
Pages; o comando tem de gravar os JSON no destino certo e a saída tem de ser
acionável. Mesmo padrão do teste do `gp100 site`: CliRunner apontando
`GP100_DEFS` para o defs real (nunca escreve no repo) e destino em `tmp_path`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gp100_architect.interfaces.cli.main import app

pytestmark = pytest.mark.contract

runner = CliRunner()


def test_badges_grava_no_destino(tmp_path: Path):
    destino = tmp_path / 'site'
    r = runner.invoke(app, ['badges', '--destino', str(destino)])
    assert r.exit_code == 0
    gerados = sorted(p.name for p in (destino / 'badges').glob('*.json'))
    assert gerados == [
        'agentes.json',
        'cobertura.json',
        'patches.json',
        'python.json',
        'release.json',
        'skills.json',
        'testes.json',
    ]
    dados = json.loads((destino / 'badges' / 'agentes.json').read_text(encoding='utf-8'))
    assert dados['message'] == '21'
    assert '7 badge(s)' in r.output
    assert 'regenera' in r.output


@pytest.mark.slow
def test_badges_e_deterministico(tmp_path: Path):
    """Mesma fonte → mesmos bytes (o deploy pode rodar 2x sem churn)."""
    um, dois = tmp_path / 'a', tmp_path / 'b'
    assert runner.invoke(app, ['badges', '--destino', str(um)]).exit_code == 0
    assert runner.invoke(app, ['badges', '--destino', str(dois)]).exit_code == 0
    for nome in ('release.json', 'patches.json', 'agentes.json'):
        assert (um / 'badges' / nome).read_bytes() == (dois / 'badges' / nome).read_bytes()
