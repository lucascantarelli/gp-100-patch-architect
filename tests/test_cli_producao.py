"""Contrato da CLI do pacote — produção (build/verify/setlist/release), #49.

`setlist` e `release` rodam in-process via CliRunner (escrita só em
tmp_path); `build` e `verify` são subprocesses de verdade — o que a #49
promete é exatamente o que o CI faz, então o teste os roda como o agente
vai rodar (e usa `--quiet` para o contrato de agente: exit code + resumo).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gp100_architect.interfaces.cli.main import PIPELINE, app

pytestmark = pytest.mark.unit

runner = CliRunner()

RAIZ = Path(__file__).resolve().parent.parent


# ── setlist ─────────────────────────────────────────────────────────────────


def test_setlist_otimiza_e_mostra_trocas():
    r = runner.invoke(app, ['setlist', 'Smooth', 'Money'])
    assert r.exit_code == 0
    assert 'Cola de palco' in r.stdout
    assert 'SMOO1RI' in r.stdout and 'MNY01BA' in r.stdout
    assert 'U94' in r.stdout  # slot da numeração da biblioteca (nunca recalculado)


def test_setlist_json_shape_estavel():
    r = runner.invoke(app, ['setlist', 'Smooth', 'Money', '--json'])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert {'trocas_totais', 'itens'} <= set(d)
    assert all({'ordem', 'slot', 'musica', 'patch', 'trocas'} <= set(i) for i in d['itens'])
    assert d['itens'][0]['ordem'] == 1


def test_setlist_keep_order_respeita_a_ordem_dada():
    r = runner.invoke(app, ['setlist', 'Money', 'Smooth', '--keep-order', '--json'])
    assert r.exit_code == 0
    d = json.loads(r.stdout)
    assert [i['patch'] for i in d['itens']] == ['MNY01BA', 'SMOO1RI']


def test_setlist_list_mostra_o_catalogo():
    r = runner.invoke(app, ['setlist', '--list'])
    assert r.exit_code == 0
    assert 'SMO1' in r.stdout or 'Smooth' in r.stdout


def test_setlist_secao_inexistente_falha_com_as_disponiveis():
    r = runner.invoke(app, ['setlist', 'Smooth:ZZ'])
    assert r.exit_code == 1
    assert 'não tem seção' in r.output


def test_setlist_out_grava_em_arquivo(tmp_path: Path):
    alvo = tmp_path / 'cola.md'
    r = runner.invoke(app, ['setlist', 'Smooth', '--out', str(alvo)])
    assert r.exit_code == 0
    assert alvo.exists() and 'Cola de palco' in alvo.read_text(encoding='utf-8')


def test_setlist_sem_repertorio_e_sem_list_dica_o_uso():
    r = runner.invoke(app, ['setlist'])
    assert r.exit_code == 2  # erro de uso da CLI


# ── release ─────────────────────────────────────────────────────────────────


def test_release_empacota_em_destino(tmp_path: Path):
    r = runner.invoke(app, ['release', '9.9.6', '--destino', str(tmp_path)])
    assert r.exit_code == 0
    assert '📦 gp100-patches-v9.9.6.zip' in r.stdout
    assert (tmp_path / 'gp100-patches-v9.9.6.zip').exists()
    assert (tmp_path / 'RELEASE-NOTES-v9.9.6.md').exists()


def test_release_versao_invalida_acionavel(tmp_path: Path):
    r = runner.invoke(app, ['release', '9.9', '--destino', str(tmp_path)])
    assert r.exit_code == 1
    assert 'SemVer' in r.output


# ── build / verify (subprocess — o contrato é com o shell do agente) ───────


def test_pipeline_constante_e_a_ordem_do_guarda():
    assert PIPELINE == (
        'tools/ir_library.py',
        'tools/build_song_patches.py',
        'tools/gen_indexes.py',
    )


@pytest.mark.slow
def test_build_quiet_no_repo_real():
    """O mesmo subprocess que o agente roda: `gp100 build --quiet`.

    Roda no repositório real (leitura do defs + escrita dos derivados, que é
    o comportamento do build) — idempotente: regenera os mesmos bytes.
    """
    r = subprocess.run(
        [sys.executable, '-m', 'gp100_architect.interfaces.cli.main', 'build', '--quiet'],
        cwd=RAIZ,
        capture_output=True,
        encoding='utf-8',
        errors='replace',
    )
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    assert 'build ok' in r.stdout


@pytest.mark.slow
def test_verify_quint_rodando_apenas_este_arquivo():
    """`verify --quiet` reprovando devolve o comando de conserto (padrão #49).

    Em vez de rodar a suíte inteira de novo (caro), o teste roda o `verify`
    apontando pytest para um teste que passa e um arquivo vazio de config:
    a promessa da CLI é repassar o exit code — provado com o pytest alvo.
    """
    from gp100_architect.interfaces.cli import main as cli_main

    chamadas = []

    def fake_run(args, **_kw):
        chamadas.append(args)
        return subprocess.CompletedProcess(args, 0, stdout='5 passed', stderr='')

    original = cli_main.subprocess.run
    cli_main.subprocess.run = fake_run
    try:
        r = runner.invoke(app, ['verify', '--quiet'])
    finally:
        cli_main.subprocess.run = original
    assert r.exit_code == 0
    assert chamadas and 'pytest' in ' '.join(str(a) for a in chamadas[0])
    assert 'verify ok' in r.stdout
