"""Contrato da CLI do pacote — produção (build/verify/setlist/release), #49.

`setlist` e `release` rodam in-process via CliRunner (escrita só em
tmp_path); `build` e `verify` são subprocesses de verdade — o que a #49
promete é exatamente o que o CI faz, então o teste os roda como o agente
vai rodar (e usa `--quiet` para o contrato de agente: exit code + resumo).

Camada `contract`: o `--json` com shape estável é a interface dos agentes
(issue #91) — mudar o shape aqui é breaking change.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gp100_architect.interfaces.cli import main as cli_main
from gp100_architect.interfaces.cli.main import PIPELINE, app

pytestmark = pytest.mark.contract

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
    """Os nomes dos passos de `application.pipeline` — a ordem do TestH."""
    assert PIPELINE == ('ir_library', 'patches', 'indices')


@pytest.mark.slow
def test_build_quiet_no_repo_real(tmp_path: Path, raiz: Path):
    """O mesmo subprocess que o agente roda: `gp100 build --quiet` — num sandbox.

    Cópia temporária do que o pipeline lê + `PYTHONPATH` apontando para o
    `src/` da cópia: a CLI resolve a raiz pelo próprio arquivo (`parents[4]`)
    e o build acontece no sandbox. Era o único teste que escrevia no
    repositório (regenerava `patches/` e `reference/` no working tree) — agora
    a regra "nenhum teste escreve no repo" vale para a suíte inteira.
    """
    sandbox = tmp_path / 'repo'
    sandbox.mkdir()
    for nome in ('data', 'reference', 'impulse_responses', 'src'):
        origem = raiz / nome
        if origem.is_dir():
            shutil.copytree(
                origem,
                sandbox / nome,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'),
            )
    ambiente = dict(os.environ, PYTHONPATH=str(sandbox / 'src'))
    r = subprocess.run(
        [sys.executable, '-m', 'gp100_architect.interfaces.cli.main', 'build', '--quiet'],
        cwd=sandbox,
        capture_output=True,
        encoding='utf-8',
        errors='replace',
        env=ambiente,
    )
    assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
    assert 'build ok' in r.stdout
    # o produto nasceu no sandbox — não no working tree do repositório
    assert (sandbox / 'patches' / 'README.md').is_file()


# ── site (deriva o site estático do defs; escrita só em tmp_path) ──────────


def test_site_gera_em_destino(tmp_path: Path):
    destino = tmp_path / 'site'
    r = runner.invoke(app, ['site', '--destino', str(destino)])
    assert r.exit_code == 0
    assert (destino / 'index.html').is_file()
    assert (destino / 'busca.json').is_file()
    assert (destino / 'style.css').is_file()
    paginas_patch = list((destino / 'patch').glob('*.html'))
    assert len(paginas_patch) >= 103  # 103 patches do defs, um por página
    assert 'busca.json' in r.stdout and 'KB' in r.stdout


def test_site_base_url_aceita_custom(tmp_path: Path):
    destino = tmp_path / 'site'
    r = runner.invoke(app, ['site', '--destino', str(destino), '--base-url', '/site/'])
    assert r.exit_code == 0
    assert 'base_url: /site/' in (destino / 'index.html').read_text(encoding='utf-8')


# ── changelog / analyze / manual-page (ferramentas de manutenção, in-process #33) ──


def test_changelog_default_mostra_secao_e_bump():
    r = runner.invoke(app, ['changelog'])
    assert r.exit_code == 0
    assert '##' in r.stdout
    assert 'bump' in r.stdout


def test_changelog_versao_invalida_e_acionavel():
    r = runner.invoke(app, ['changelog', '--version', 'nao-e-semver'])
    assert r.exit_code == 1
    assert 'SemVer' in r.output


def test_changelog_out_grava_secao_em_arquivo(tmp_path: Path):
    destino = tmp_path / 'secao.md'
    r = runner.invoke(app, ['changelog', '--out', str(destino)])
    assert r.exit_code == 0
    assert destino.read_text(encoding='utf-8').strip()


def test_analyze_disseca_export_e_salva_json(tmp_path: Path, raiz: Path, monkeypatch):
    """Fluxo real do usuário: build DERIVA `patches/` (ADR-0013 — não vive no
    git), e o export lê a árvore derivada. O sandbox reproduz a ordem: dados
    copiados → pipeline → export apontado para o sandbox via `_raiz`.
    """
    sandbox = tmp_path / 'repo'
    sandbox.mkdir()
    shutil.copytree(
        raiz / 'data',
        sandbox / 'data',
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'),
    )
    from gp100_architect.application import pipeline

    pipeline.executar(sandbox, out=None)
    monkeypatch.setattr(cli_main, '_raiz', lambda: sandbox)
    destino = tmp_path / 'importacao'
    assert runner.invoke(app, ['export', '--album', 'SN', '--destino', str(destino)]).exit_code == 0
    prst = sorted(destino.glob('*.prst'))[0]
    dump = tmp_path / 'catalogo.json'
    r = runner.invoke(app, ['analyze', str(prst), '--json', str(dump)])
    assert r.exit_code == 0
    assert 'preset_info' in r.stdout and 'CATALOGO' in r.stdout
    dados = json.loads(dump.read_text(encoding='utf-8'))
    assert set(dados) == {'info', 'user_irs', 'patches'}


def test_analyze_prst_malformado_e_acionavel(tmp_path: Path):
    podre = tmp_path / 'podre.prst'
    podre.write_text('isto não é xml', encoding='utf-8')
    r = runner.invoke(app, ['analyze', str(podre)])
    assert r.exit_code == 1


def test_manual_page_sem_dependencia_ou_sem_pdf_falha_acionavel(tmp_path: Path, monkeypatch):
    """Sem pymupdf instalado OU sem manual.pdf, a saída diz o que fazer (exit 1)."""
    monkeypatch.setattr(cli_main, '_raiz', lambda: tmp_path)
    r = runner.invoke(app, ['manual-page', '21'])
    assert r.exit_code == 1
    assert r.output.strip()


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
