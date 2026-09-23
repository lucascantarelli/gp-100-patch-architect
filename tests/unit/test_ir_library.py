"""Regras puras da biblioteca de IRs — manifesto, catálogo e guarda (issue #30).

Os três alvos:

* `wav_order` — a ordem estável entre sistemas (o CI reprovava no Windows);
* `montar_manifesto` / `encolhimento` — o manifesto por pack e o guarda que
  impede uma rodada de ENCOLHER o catálogo que documenta os patches;
* `catalogo_md` — o `reference/16-ir-library.md`, com pack conhecido (fonte e
  licença citadas) e pack desconhecido (registrado sem fonte).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import ir_library

pytestmark = pytest.mark.unit


def _reg(file: str, **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        'file': file,
        'size_kb': 12,
        'rate': 44100,
        'channels': 1,
        'bits': 24,
        'duration_ms': 500,
        'compatible': True,
        'over_1024': False,
    }
    base.update(extra)
    return base


def _manifesto(**packs: tuple[int, list[str]]) -> dict[str, Any]:
    return {
        'generated_by': 'tools/ir_library.py',
        'packs': {
            nome: {'wavs': n, 'cabs': cabs, 'all_compatible': True, 'meta': {}, 'files': []}
            for nome, (n, cabs) in packs.items()
        },
    }


def test_wav_order_e_estavel_e_usa_o_caminho_posix(tmp_path: Path):
    ir_dir = tmp_path / 'ir'
    (ir_dir / 'Pack' / 'Cab').mkdir(parents=True)
    a = ir_dir / 'Pack' / 'Cab' / 'Z.wav'
    b = ir_dir / 'Pack' / 'Cab' / 'a.wav'
    a.touch()
    b.touch()
    # ordem de code point: maiúsculas antes das minúsculas (igual em todo OS)
    assert ir_library.wav_order(a, ir_dir) == 'Pack/Cab/Z.wav'
    assert sorted([a, b], key=lambda p: ir_library.wav_order(p, ir_dir))[0] is a


def test_cab_of_sobe_um_nivel_quando_a_pasta_e_de_microfones():
    base = 'Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library'
    assert (
        ir_library.cab_of(f'{base}/American Twin 2x12/American Twin 2x12 Medium Mix.wav')
        == 'American Twin 2x12'
    )
    assert (
        ir_library.cab_of(f'{base}/American Twin 2x12/American Twin 2x12 Mics/Bright 87.wav')
        == 'American Twin 2x12'
    )
    assert ir_library.cab_of('25 Analog Cab IRs/1x12 American.wav') == '25 Analog Cab IRs'
    assert ir_library.cab_of('solto.wav') == '(raiz)'


def test_montar_manifesto_agrupa_por_pack_e_cita_o_conhecido():
    registros = [
        _reg('Pack Novo/Cab A/Cab A Medium Mix.wav'),
        _reg('Pack Novo/Cab A/Cab A Mics/Bright 87.wav'),
        _reg(
            'Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/'
            'American Twin 2x12/American Twin 2x12 Medium Mix.wav'
        ),
        _reg('solto.wav'),
    ]
    manifesto = ir_library.montar_manifesto(registros)

    assert sorted(manifesto['packs']) == [
        '(raiz)',
        'Origin Effects - IR-Cab Library V3',
        'Pack Novo',
    ]
    assert manifesto['generated_by'] == 'tools/ir_library.py'
    novo = manifesto['packs']['Pack Novo']
    assert novo['wavs'] == 2
    assert novo['cabs'] == ['Cab A']  # Mics não vira um "gabinete"
    assert novo['all_compatible'] is True
    assert novo['meta'] == {}  # pack sem procedência citável
    conhecido = manifesto['packs']['Origin Effects - IR-Cab Library V3']
    assert conhecido['meta']['license'].startswith('Gratuita')
    assert manifesto['packs']['(raiz)']['cabs'] == ['(raiz)']


def test_montar_manifesto_registra_wav_corrompido_sem_contar():
    registros = [
        _reg('Pack/Cab/ok.wav'),
        {
            'file': 'Pack/Cab/quebrado.wav',
            'size_kb': 1,
            'error': 'wave.Error: bad header',
            'compatible': False,
        },
    ]
    pack = ir_library.montar_manifesto(registros)['packs']['Pack']
    assert pack['wavs'] == 1  # o corrompido não conta
    assert len(pack['files']) == 2  # mas continua registrado
    assert pack['all_compatible'] is True  # decidido só pelos válidos


def test_encolhimento_reprova_pack_ausente_e_reduzido():
    antigo = _manifesto(
        **{
            'Pack A': (10, ['Cab']),
            'Pack B': (5, ['Cab']),
            'Pack C': (3, ['Cab']),
        }
    )
    novo = _manifesto(**{'Pack B': (4, ['Cab']), 'Pack C': (3, ['Cab'])})
    problemas = ir_library.encolhimento(antigo, novo)
    assert len(problemas) == 2
    assert any('pack ausente nesta rodada: Pack A (10 WAVs)' in p for p in problemas)
    assert any('pack reduzido: Pack B (5 → 4 WAVs)' in p for p in problemas)


def test_encolhimento_aprova_crescimento_e_rodada_igual():
    antigo = _manifesto(**{'Pack A': (10, ['Cab'])})
    assert ir_library.encolhimento(antigo, _manifesto(**{'Pack A': (11, ['Cab'])})) == []
    assert ir_library.encolhimento(antigo, antigo) == []
    # catálogo antigo ausente/vazio não inventa problema
    assert ir_library.encolhimento({}, antigo) == []
    assert ir_library.encolhimento(antigo, {}) == [
        'pack ausente nesta rodada: Pack A (10 WAVs)',
    ]


def test_catalogo_md_cita_fonte_e_lista_apenas_os_mixes():
    manifesto = {
        'generated_by': 'tools/ir_library.py',
        'packs': {
            'Origin Effects - IR-Cab Library V3': {
                'wavs': 2,
                'cabs': ['American Twin 2x12'],
                'all_compatible': False,
                'meta': ir_library.CONHECIDOS['Origin Effects - IR-Cab Library V3'],
                'files': [
                    _reg(
                        'Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/'
                        'American Twin 2x12/American Twin 2x12 Medium Mix.wav',
                        over_1024=True,
                    ),
                    _reg(
                        'Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/'
                        'American Twin 2x12/American Twin 2x12 Mics/Bright 87.wav'
                    ),
                    {
                        'file': 'Origin Effects - IR-Cab Library V3/quebrado.wav',
                        'error': 'bad header',
                        'compatible': False,
                    },
                ],
            },
        },
    }
    md = ir_library.catalogo_md(manifesto)

    assert '## 📦 Origin Effects - IR-Cab Library V3 ⚠️ (parte precisa conversão)' in md
    assert 'https://origineffects.com/product/ir-cab-library/' in md
    assert '- WAVs: 2 · Gabinetes: American Twin 2x12' in md
    # o caminho no catálogo é relativo ao pack, e a cauda longa ganha o aviso
    misturado = (
        '| `44.1kHz Origin Effects IR Cab Library/American Twin 2x12/'
        'American Twin 2x12 Medium Mix.wav` | 44100 | 24 | 500 ms | '
        '✅ direto · aparar >1024 samp. |'
    )
    assert misturado in md
    assert 'Mics/Bright 87.wav' not in md  # mic individual fica no JSON
    assert '> Variações de microfone individuais: 1 arquivos' in md
    assert '## 🔌 Como carregar uma IR local na GP-100' in md
    assert 'escolha o **slot (1–20)**' in md


def test_catalogo_md_registra_pack_sem_procedencia():
    md = ir_library.catalogo_md(
        {
            'generated_by': 'tools/ir_library.py',
            'packs': {
                'Pack Novo': {
                    'wavs': 1,
                    'cabs': ['Cab'],
                    'all_compatible': True,
                    'meta': {},
                    'files': [_reg('Pack Novo/Cab/Cab Mix.wav')],
                }
            },
        }
    )
    assert '## 📦 Pack Novo ✅' in md
    assert '- Fonte:' not in md
    assert '- Licença:' not in md
    assert '| `Cab/Cab Mix.wav` | 44100 | 24 | 500 ms | ✅ direto |' in md
