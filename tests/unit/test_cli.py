"""Contrato da CLI: códigos de saída, mensagens e o `--version`.

Testar a CLI como contrato (e não a função interna) é o que garante que um
script de automação ou o `release.yml` possam contar com ela.
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from gp100_architect import __version__
from gp100_architect.infrastructure import defs as carregador
from gp100_architect.interfaces.cli.main import app

pytestmark = pytest.mark.unit

runner = CliRunner()


def test_version_e_atalho_de_uso():
    resultado = runner.invoke(app, ['--version'])
    assert resultado.exit_code == 0
    assert __version__ in resultado.stdout


def test_comando_version_responde_a_versao():
    resultado = runner.invoke(app, ['version'])
    assert resultado.exit_code == 0
    assert resultado.stdout.strip() == __version__


def test_validate_aprova_o_defs_commitado():
    resultado = runner.invoke(app, ['validate'])
    assert resultado.exit_code == 0
    assert 'válido' in resultado.stdout


def test_saida_da_cli_e_escrevivel_no_console_padrao_do_windows():
    """Regressão: um `✅` na saída derrubou o comando com UnicodeEncodeError.

    Em console legado (cp1252) o emoji não é escrevível e o usuário via stack
    trace em vez de diagnóstico. Regra da CLI: só caractere que o console padrão
    escreve — acento sim, ideograma não.
    """
    resultado = runner.invoke(app, ['validate'])
    resultado.stdout.encode('cp1252')  # levanta UnicodeEncodeError se falhar


def test_validate_reprova_defs_quebrado_com_codigo_1(tmp_path: Path):
    quebrado = tmp_path / 'quebrado.json'
    quebrado.write_text(json.dumps({'albums': {}, 'songs': [], 'ir_local': {}}), encoding='utf-8')
    resultado = runner.invoke(app, ['validate', str(quebrado)])
    assert resultado.exit_code == 1
    assert 'problema(s) no patches-defs.json' in resultado.output


def test_validate_aponta_arquivo_inexistente_com_erro_claro(tmp_path: Path):
    resultado = runner.invoke(app, ['validate', str(tmp_path / 'nao-existe.json')])
    assert resultado.exit_code != 0


def test_validate_respeita_a_variante_de_ambiente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    copia = tmp_path / 'defs.json'
    copia.write_text((carregador.DEFS_PADRAO).read_text(encoding='utf-8'), encoding='utf-8')
    monkeypatch.setenv(carregador.VAR_DEFS, str(copia))
    resultado = runner.invoke(app, ['validate'])
    assert resultado.exit_code == 0
    assert 'defs.json válido' in resultado.stdout


def test_sem_argumento_mostra_a_ajuda():
    resultado = runner.invoke(app, [])
    assert resultado.exit_code != 0, 'CLI sem argumento não pode falhar em silêncio'
    assert 'Usage' in resultado.output or 'gp100' in resultado.output
