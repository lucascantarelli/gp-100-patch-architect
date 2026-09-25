"""Derivação do golden set (issue #131) — doc 20 como artefato do pipeline.

Por que este teste existe: a tabela era editada à mão e a "prova" era a
inspeção visual. Agora a região entre as marcas nasce do defs
(`spec.modules`) + seleção (`data/golden-set.json`), o `gp100 build`
regenera e o guarda de sincronia (TestH) vigia o arquivo inteiro.

Mesmo padrão da suíte: casos sintéticos em `tmp_path` (seleção com
contexto real — grupos existentes do defs) e a realidade commitada lida,
nunca alterada.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import golden_set
from gp100_architect.infrastructure.defs import carregar_e_validar

RAIZ = Path(__file__).resolve().parents[2]


def _spec_padrao(**overrides: Any) -> dict[str, Any]:
    """Spec sintético com os 9 blocos (mesma forma do defs)."""
    spec: dict[str, Any] = {
        'name': 'TESTE01BA',
        'type': 'Rock',
        'bpm': 120,
        'volume': 55,
        'modules': {
            'PRE': {'name': 'Boost', 'on': True, 'params': {'0': 30}},
            'DST': {'name': 'Blues OD', 'on': False},
            'AMP': {'name': 'Dark Twin', 'on': True, 'params': {'0': 60}},
            'NR': {'name': 'Gate 1', 'on': True, 'params': {'0': 30}},
            'CAB': {'name': 'DarkTW 2x12', 'on': True, 'params': {'0': 50}},
            'EQ': {'name': 'EQ 1', 'on': True, 'params': {'0': 0}},
            'MOD': {'name': 'A-Chorus', 'on': False},
            'DLY': {'name': 'Sweet', 'on': False},
            'RVB': {'name': 'Room', 'on': True, 'params': {'0': 20}},
        },
    }
    for modulo, mudancas in overrides.items():
        spec['modules'][modulo].update(mudancas)
    return spec


def _patch(nome: str, spec: dict[str, Any]) -> dict[str, Any]:
    return {'nome': nome, 'spec': spec}


def _defs_sintetico() -> dict[str, Any]:
    """Dois grupos com contexto real: AR (3 patches em 2 músicas) + SN (1)."""
    return {
        'albums': {
            'AR': {'banda': 'The Beatles', 'display': 'Abbey Road (1969)'},
            'SN': {'banda': 'Santana', 'display': 'Supernatural (1999)'},
        },
        'songs': [
            {
                'id': 'CT01',
                'song': 'Come Together',
                'idAlbum': 'AR',
                'patches': [
                    _patch('CT01RIF', _spec_padrao()),
                    _patch('CT01VOX', _spec_padrao(PRE={'name': 'COMP', 'on': False})),
                ],
            },
            {
                'id': 'STH01',
                'song': 'Something',
                'idAlbum': 'AR',
                'patches': [_patch('STH01BA', _spec_padrao(DST={'name': 'Green OD', 'on': True}))],
            },
            {
                'id': 'SMOO1',
                'song': 'Smooth',
                'idAlbum': 'SN',
                'patches': [_patch('SMOO1SO', _spec_padrao(AMP={'name': 'L-Star CL'}))],
            },
        ],
    }


@pytest.mark.unit
def test_cadeia_esperada_notacao_e_ordem(tmp_path: Path) -> None:
    """Cadeia completa: notação BLOCO:Modelo± e a ordem canônica dos 9 blocos."""
    cadeia = golden_set.cadeia_esperada(_spec_padrao())
    partes = re.split(r'(?=\b(?:PRE|DST|AMP|NR|CAB|EQ|MOD|DLY|RVB):)', cadeia)
    partes = [p for p in partes if p.strip()]
    assert [p.split(':')[0] for p in partes] == list(golden_set.ORDEM_BLOCOS)
    assert partes[0].strip() == 'PRE:Boost+' and partes[1].strip() == 'DST:Blues OD-'
    assert partes[2].strip() == 'AMP:Dark Twin+' and partes[-1].strip() == 'RVB:Room+'


@pytest.mark.unit
def test_cadeia_esperada_bloco_ausente_reprova(tmp_path: Path) -> None:
    spec = _spec_padrao()
    del spec['modules']['MOD']
    with pytest.raises(golden_set.Gp100GoldenSetError, match='MOD'):
        golden_set.cadeia_esperada(spec)


@pytest.mark.unit
def test_regiao_derivada_sintetica(tmp_path: Path) -> None:
    """Região derivada: heading de defs, música por seleção, cadeia por spec."""
    defs = _defs_sintetico()
    selecao = {
        'porAlbum': ['AR', 'SN'],
        'musicas': ['CT01', 'STH01', 'SMOO1'],
    }
    regiao = golden_set.regiao_derivada(defs, selecao)
    assert '### The Beatles — Abbey Road (1969)' in regiao
    assert '### Santana — Supernatural (1999)' in regiao
    assert '| `CT01RIF` |' in regiao
    # cadeia do spec sintético aparece montada
    assert 'DST:Blues OD- AMP:Dark Twin+' in regiao
    assert regiao.startswith('> 3 músicas · 4 patches · 2 álbum(ns)')


@pytest.mark.unit
def test_selecao_fora_do_defs_reprova(tmp_path: Path) -> None:
    defs = _defs_sintetico()
    selecao = {'porAlbum': ['AR'], 'musicas': ['XX99']}
    with pytest.raises(golden_set.Gp100GoldenSetError, match='XX99'):
        golden_set.regiao_derivada(defs, selecao)


@pytest.mark.unit
def test_aplicar_no_doc_preserva_prosa_fora_das_marcas() -> None:
    antes = (
        '# Doc\n\n'
        + golden_set.MARCA_INICIO
        + '\n\n| tabela antiga |\n\n'
        + golden_set.MARCA_FIM
        + '\n\nProsa editorial aqui.\n'
    )
    novo = golden_set.aplicar_no_doc(antes, '| tabela nova |')
    assert '| tabela nova |' in novo
    assert '| tabela antiga |' not in novo
    assert 'Prosa editorial aqui.' in novo
    # marcas preservadas exatamente uma vez
    assert novo.count(golden_set.MARCA_INICIO) == 1
    assert novo.count(golden_set.MARCA_FIM) == 1


@pytest.mark.unit
def test_aplicar_no_doc_sem_marcas_reprova() -> None:
    with pytest.raises(golden_set.Gp100GoldenSetError, match='marcas'):
        golden_set.aplicar_no_doc('# sem marcas\n', 'x')


@pytest.mark.unit
def test_selecao_carregar_valida_forma(tmp_path: Path) -> None:
    (tmp_path / 'data').mkdir()
    caminho = tmp_path / golden_set.ARQUIVO_SELECAO
    caminho.write_text('{"porAlbum": ["AR"], "musicas": []}', encoding='utf-8')
    with pytest.raises(golden_set.Gp100GoldenSetError, match='musicas'):
        golden_set.selecao_carregar(tmp_path)


@pytest.mark.unit
def test_doc_commitado_e_derivado_do_defs(raiz: Path) -> None:
    """A realidade: o doc commitado é exatamente o que a derivação produz."""
    defs = carregar_e_validar()
    selecao = json.loads((RAIZ / golden_set.ARQUIVO_SELECAO).read_text(encoding='utf-8'))
    doc = (raiz / golden_set.DOC_ALVO).read_text(encoding='utf-8')
    esperado = golden_set.aplicar_no_doc(doc, golden_set.regiao_derivada(defs, selecao))
    assert esperado == doc


@pytest.mark.e2e
def test_doc20_esta_sob_vigilia_do_guarda(raiz: Path) -> None:
    from tests.e2e.test_sincronia import ARTEFATOS_FIXOS, artefatos

    monitorados = set(artefatos(raiz))
    assert golden_set.DOC_ALVO.as_posix() in monitorados
    assert golden_set.DOC_ALVO.as_posix() in ARTEFATOS_FIXOS
    # smoke: os passos conhecidos do pipeline incluem o novo
    from gp100_architect.application import pipeline

    assert 'golden_set' in pipeline.PIPELINE_PASSOS


@pytest.mark.e2e
def test_linter_calibrado_para_golden_set() -> None:
    """O linter segue tratando doc 20 como subconjunto (contagens fora)."""
    texto = RAIZ.joinpath('.github/scripts/audit_docs.py').read_text(encoding='utf-8')
    assert '"reference/20-golden-set.md": {"contagens"}' in texto
