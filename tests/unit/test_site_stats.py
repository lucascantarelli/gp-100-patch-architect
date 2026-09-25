"""Página /stats/ do site (issue #119) — a derivação dos badges, legível e consumível.

Por que este teste existe: a página publica `badges.dados_derivados` — se ela
duplicar a lógica de contagem, volta a divergir (o apodrecimento da #113/#115).
O teste fixa que HTML e JSON são A MESMA derivação, que o JSON tem shape
estável (contrato para agentes, como o /catalog/ da #90) e que o `gerar_site`
básico NÃO inclui /stats/ (opt-in puro: custo e testes onde estão).

Sintéticos rodam 100% offline (root falsificada); o caso real roda a CLI —
lendo o que ela gravou em `tmp_path`, nunca escrevendo no repo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from gp100_architect.application import badges, site
from gp100_architect.interfaces.cli.main import app

pytestmark = pytest.mark.unit

runner = CliRunner()


@pytest.fixture()
def raiz_falsa(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repo mínimo: VERSION, pyproject e contagens falsas — sem git, sem pytest."""
    (tmp_path / 'VERSION').write_text('7.7.7\n', encoding='utf-8')
    (tmp_path / 'pyproject.toml').write_text(
        '[project]\nrequires-python = ">=3.12,<3.13"\n[tool.coverage.report]\nfail_under = 55\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(badges, '_rastreados', lambda _raiz: ['.agents/a.ts'])
    monkeypatch.setattr(badges, '_contagem_testes', lambda _raiz: '12')
    return tmp_path


def test_stats_json_tem_shape_estavel(defs_real: dict[str, Any], raiz_falsa: Path):
    """O contrato para agentes: chaves fixas, valores derivados (nunca faltando)."""
    arquivos = site.gerar_stats(defs_real, raiz=raiz_falsa)
    assert set(arquivos) == {'stats/index.html', 'stats/stats.json'}
    dados = json.loads(arquivos['stats/stats.json'])
    assert set(dados) == {
        'geradoPor',
        'versao',
        'agentes',
        'skills',
        'musicas',
        'albuns',
        'patches',
        'python',
        'pisoCobertura',
        'testes',
    }
    assert dados['versao'] == '7.7.7'
    assert dados['agentes'] == 1
    assert dados['testes'] == '12'
    assert dados['pisoCobertura'] == 55
    # patches = soma no defs (a mesma fórmula do /catalog/index.json)
    assert dados['patches'] == sum(len(s['patches']) for s in defs_real['songs'])


def test_stats_html_e_o_mesmo_dado(defs_real: dict[str, Any], raiz_falsa: Path):
    """HTML e JSON nascem da MESMA derivação — um não diverge do outro."""
    arquivos = site.gerar_stats(defs_real, raiz=raiz_falsa)
    html = arquivos['stats/index.html']
    dados = json.loads(arquivos['stats/stats.json'])
    for fragmento in (
        'Estatísticas derivadas',
        'nunca editadas à mão',
        f'<strong>{dados["versao"]}</strong>',
        f'<strong>{dados["agentes"]}</strong>',
        '../index.html',
        '../style.css',
    ):
        assert fragmento in html, fragmento


def test_gerar_site_basico_nao_inclui_stats(defs_real: dict[str, Any], raiz_falsa: Path):
    """Opt-in puro: sem a flag, nenhum caminho stats/ no site (custo onde está)."""
    paginas = site.gerar_site(defs_real)
    assert not any(c.startswith('stats/') for c in paginas)
    assert 'stats/index.html' not in paginas


def test_stats_e_deterministico(defs_real: dict[str, Any], raiz_falsa: Path):
    um = site.gerar_stats(defs_real, raiz=raiz_falsa)
    dois = site.gerar_stats(defs_real, raiz=raiz_falsa)
    assert um == dois


@pytest.mark.contract
def test_cli_site_com_stats_grava_no_destino(defs_real: dict[str, Any], tmp_path: Path):
    """`gp100 site --stats` grava stats/ junto do site, no destino pedido."""
    destino = tmp_path / 'site'
    r = runner.invoke(app, ['site', '--destino', str(destino), '--stats'])
    assert r.exit_code == 0
    j = json.loads((destino / 'stats' / 'stats.json').read_text(encoding='utf-8'))
    assert j['patches'] == 103
    assert j['agentes'] == 21
    assert (destino / 'index.html').is_file()  # o site continua lá
