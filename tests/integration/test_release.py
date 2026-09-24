"""Bibliotecas de release e changelog sobre o repositório real (issue #34).

Migração do que restou de `tests/test_scripts.py`: as bibliotecas
(`application.release`, `application.changelog`) já têm camada unit — aqui
ficam os casos de integração que leem o repo commitado (leitura pura) e o
empacotamento completo em tmpdir.

Marcador `integration`: toca o disco do repositório (só leitura) e
`tmp_path` (escrita).
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from gp100_architect.application import changelog, release
from gp100_architect.domain.errors import ReleaseInvalida
from gp100_architect.infrastructure.defs import carregar
from gp100_architect.infrastructure.prst.reader import analyze, fmt_stat, parse

pytestmark = pytest.mark.integration

PRST = Path('patches') / 'Santana' / 'Supernatural (1999)' / 'Smooth' / 'SMOO1RI' / 'SMOO1RI.prst'


@pytest.fixture(scope='module')
def parseado(raiz: Path):
    return parse(raiz / PRST)


# ── reader do .prst sobre o arquivo commitado (ex-analyze_prst) ─────────────


def test_info_tem_campos_essenciais(parseado) -> None:
    info, _irs, _patches = parseado
    for campo in ('software', 'firmware', 'product', 'count'):
        assert campo in info


def test_formato_single_fw21(parseado) -> None:
    info, _irs, _patches = parseado
    assert info.get('firmware') == '2.1'


def test_um_preset_com_nome_do_patch(parseado) -> None:
    _info, _irs, patches = parseado
    assert len(patches) == 1
    assert patches[0]['name'] == 'SMOO1RI'


def test_sem_bloco_ppirinfo_no_formato_single(parseado) -> None:
    """`<ppIRInfo>` só existe no export "all" — o single não o tem (e o guarda
    de None em parse() existe exatamente por isso)."""
    _info, irs, _patches = parseado
    assert irs == []


def test_effect_exposto_com_nome_e_params_15_slots(parseado) -> None:
    _info, _irs, patches = parseado
    e = patches[0]['effects'][0]
    assert 'module' in e
    assert isinstance(e['params'], list)
    assert len(e['params']) == 15


def test_analyze_conta_uso_e_param_stats_por_modelo(parseado) -> None:
    _info, _irs, patches = parseado
    models, param_stats = analyze(patches)
    assert models
    for key, m in models.items():
        assert m['count'] > 0
        assert len(param_stats[key]) == 15


def test_fmt_stat_linhas_formadas(parseado) -> None:
    _info, _irs, patches = parseado
    models, param_stats = analyze(patches)
    stat = param_stats[sorted(models)[0]]
    out = fmt_stat(stat)
    assert all(linha.startswith('  p') for linha in out.splitlines())


# ── release sobre o repo real (leitura) + tmpdir (escrita) ──────────────────


def test_ler_versao_da_versao_commitada(raiz: Path) -> None:
    esperado = (raiz / 'VERSION').read_text(encoding='utf-8').strip()
    assert release.ler_versao(raiz) == esperado


def test_ler_versao_rejeita_nao_semver(tmp_path: Path) -> None:
    (tmp_path / 'VERSION').write_text('1.2', encoding='utf-8')
    with pytest.raises(ReleaseInvalida, match='SemVer'):
        release.ler_versao(tmp_path)


def test_collect_patches_espelha_o_defs(raiz: Path) -> None:
    defs = carregar(raiz / 'data' / 'defs')
    items = release.collect_patches(defs, raiz / 'patches')
    n_definidos = sum(len(s['patches']) for s in defs['songs'])
    assert len(items) == n_definidos
    nomes = {nome for _, nome in items}
    assert 'SMOO1RI' in nomes


def test_package_em_tmpdir_produz_zips_e_notas(raiz: Path, tmp_path: Path) -> None:
    """Empacota tudo num tmpdir lendo os `.prst` do repositório (só leitura)."""
    defs = carregar(raiz / 'data' / 'defs')
    relatorio = release.package('9.9.9', defs=defs, patches_dir=raiz / 'patches', destino=tmp_path)

    completo = tmp_path / 'gp100-patches-v9.9.9.zip'
    assert completo.exists()
    with zipfile.ZipFile(completo) as z:
        prst = [n for n in z.namelist() if n.endswith('.prst')]
        assert prst
        assert all(n.endswith('.prst') or n.endswith('patch.md') for n in z.namelist())
    # um zip por álbum presente
    assert any('Santana' in n.name for n in tmp_path.glob('*.zip'))
    notas = tmp_path / 'RELEASE-NOTES-v9.9.9.md'
    assert notas.exists()
    texto = notas.read_text(encoding='utf-8')
    assert '9.9.9' in texto
    assert 'Como usar' in texto
    assert relatorio['total'] > 0


# ── changelog sobre a história real (git de verdade) ────────────────────────


def test_coletar_rodando_git_real(raiz: Path) -> None:
    """Roda `git log` de verdade sobre a história do repositório: deve
    retornar itens 5-upla sem crash."""
    itens = changelog.coletar(None, raiz=raiz)
    assert isinstance(itens, list)
    for it in itens:
        assert len(it) == 5


def test_ultima_tag_achavel_ou_none(raiz: Path) -> None:
    tag = changelog.ultima_tag(raiz)
    assert tag is None or tag.startswith('v')
