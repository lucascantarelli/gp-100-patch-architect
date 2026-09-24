"""Bibliotecas de release e changelog (issue #32) — testes in-process.

O contrato que os testes legados (`tests/test_scripts.py`) já cobrem via shims
ganha aqui o lado da biblioteca: funções puras com tmp_path (nenhum teste
escreve no repositório — regra do projeto) e erros de domínio em vez de
`SystemExit` — é o que a CLI (`gp100 release`, #49) vai consumir.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from gp100_architect.application import changelog, release
from gp100_architect.domain.errors import ReleaseInvalida

pytestmark = pytest.mark.unit


# ── release.validar_versao / bump ───────────────────────────────────────────


@pytest.mark.parametrize('versao', ['1.2.3', '0.0.0', '10.20.30'])
def test_versao_semver_valida(versao: str):
    assert release.validar_versao(versao) == versao


@pytest.mark.parametrize('versao', ['1.2', 'v1.2.3', '1.2.3.4', '', 'abc'])
def test_versao_invalida_levanta_release_invalida_com_dica(versao: str):
    with pytest.raises(ReleaseInvalida) as e:
        release.validar_versao(versao)
    assert 'SemVer' in str(e.value)


def test_bump_tres_componentes_e_parte_invalida():
    assert release.bump('1.2.3', 'major') == '2.0.0'
    assert release.bump('1.2.3', 'minor') == '1.3.0'
    assert release.bump('1.2.3', 'patch') == '1.2.4'
    with pytest.raises(ReleaseInvalida):
        release.bump('1.2.3', 'beta')


# ── release.package (leitura do repo real, escrita em tmp_path) ─────────────


@pytest.fixture
def defs_real_pkg(raiz: Path):
    from gp100_architect.infrastructure.defs import carregar

    return carregar(raiz / 'tools' / 'defs')


def test_package_produz_zips_e_notas_em_destino(raiz: Path, defs_real_pkg, tmp_path: Path):
    relatorio = release.package(
        '9.9.9', defs=defs_real_pkg, patches_dir=raiz / 'patches', destino=tmp_path
    )
    completo = tmp_path / 'gp100-patches-v9.9.9.zip'
    assert relatorio['completo'] == completo and completo.exists()
    with zipfile.ZipFile(completo) as z:
        nomes = z.namelist()
    assert 'Beatles/Abbey Road (1969)/Something/STH01BA/STH01BA.prst' in nomes
    assert 'Beatles/Abbey Road (1969)/Something/STH01BA/patch.md' in nomes
    # um zip por álbum, notas com a contagem
    assert (tmp_path / 'gp100-patches-v9.9.9-Beatles.zip').exists()
    notas = (tmp_path / 'RELEASE-NOTES-v9.9.9.md').read_text(encoding='utf-8')
    assert '**97 patches · 58 músicas' in notas
    assert relatorio['total'] == 97


def test_package_versao_invalida_nao_escreve_nada(defs_real_pkg, tmp_path: Path):
    with pytest.raises(ReleaseInvalida):
        release.package('9.9', defs=defs_real_pkg, patches_dir=tmp_path, destino=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_notas_markdown_lista_albuns_ordenados():
    texto = release.notas_markdown('1.2.3', 10, 4, {'Zappa': 3, 'Beatles': 7})
    assert '- [`gp100-patches-v1.2.3-Beatles.zip`] — Beatles' in texto
    assert texto.index('Beatles') < texto.index('Zappa')  # ordenado


# ── changelog: parsing e regras (puras) ─────────────────────────────────────


def test_coletar_do_log_parseia_assunto_escopo_e_breaking():
    bruto = (
        'h1\x1ffeat(cli): comando novo\x1f\x1e'
        'h2\x1ffix(release)!: quebra uso\x1f\x1e'
        'h3\x1fdata: corrige patch\x1fBREAKING CHANGE: formato muda\x1e'
        'h4\x1fMerge pull request #17\x1f\x1e'
        'h5\x1fchore: rotina [skip ci]\x1f\x1e'
        'h6\x1ffora do padrao\x1f\x1e'
    )
    itens = changelog.coletar_do_log(bruto)
    assert [(i[0], i[1], i[2], i[4]) for i in itens] == [
        ('feat', 'cli', 'comando novo', False),
        ('fix', 'release', 'quebra uso', True),
        ('data', '', 'corrige patch', True),
    ]
    assert itens[2][3] == 'formato muda'


def test_bump_sugerido_tres_niveis():
    def item(tipo: str, breaking: bool = False) -> changelog.ItemCommit:
        return (tipo, '', 'x', '', breaking)

    assert changelog.bump_sugerido([item('fix')], '1.2.3') == '1.2.4'
    assert changelog.bump_sugerido([item('feat')], '1.2.3') == '1.3.0'
    assert changelog.bump_sugerido([item('fix', breaking=True)], '1.2.3') == '2.0.0'


def test_secao_ordena_e_esconde_ocultos():
    itens = [
        ('fix', '', 'conserta', '', False),
        ('feat', 'cli', 'comando', '', False),
        ('chore', '', 'ruido', '', False),
    ]
    texto = changelog.secao('1.2.3', itens, incluir_ocultos=False)
    assert '✨ Funcionalidades' in texto and '**cli**: comando' in texto
    assert '🐞 Correções' in texto and 'conserta' in texto
    assert 'ruido' not in texto
    com_tudo = changelog.secao('1.2.3', itens, incluir_ocultos=True)
    assert 'ruido' in com_tudo


def test_escrever_no_changelog_idempotente(tmp_path: Path):
    alvo = tmp_path / 'CHANGELOG.md'
    bloco = changelog.secao('1.0.0', [('feat', '', 'x', '', False)], False)
    changelog.escrever_no_changelog(bloco, '1.0.0', alvo)
    primeira = alvo.read_text(encoding='utf-8')
    changelog.escrever_no_changelog(bloco, '1.0.0', alvo)
    assert alvo.read_text(encoding='utf-8') == primeira
    assert primeira.count('## [1.0.0]') == 1
    assert primeira.startswith('# Changelog')


def test_ler_versao_atual_sem_arquivo_da_zero(tmp_path: Path):
    assert changelog.ler_versao_atual(tmp_path) == '0.0.0'
    (tmp_path / 'VERSION').write_text('2.3.4\n', encoding='utf-8')
    assert changelog.ler_versao_atual(tmp_path) == '2.3.4'
