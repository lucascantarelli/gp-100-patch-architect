"""Writer do formato "all" (issue #83) — parte de software da investigação.

O que é testável SEM o aparelho: a receita (count=N, blocos `<presets>`
idênticos ao single, `<ppIRInfo>` conforme o doc 15) e o round-trip com o
reader. O que NÃO é: o import real — issue permanece aberta para o
veredito empírico do mantenedor (GP-100 Edits + aparelho).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from gp100_architect.infrastructure.prst.all_writer import (
    SLOTS_IR,
    SpecAllInvalido,
    gerar_xml_all,
)
from gp100_architect.infrastructure.prst.codec import (
    BUILD_TIME_PADRAO,
    gerar_xml,
    load_templates,
)
from gp100_architect.infrastructure.prst.reader import parse

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]
TEMPO = BUILD_TIME_PADRAO

SPEC_A = {
    'name': 'SMOO1RI',
    'type': 'Rock',
    'bpm': 103,
    'volume': 50,
    'modules': {
        'PRE': {'name': 'COMP', 'on': True, 'params': {'0': '25'}},
        'DST': {'name': 'Red Haze', 'on': False},
        'AMP': {'name': 'UK 50JP', 'on': True, 'params': {'0': '70', '1': '60'}},
        'NR': {'name': 'Gate 2', 'on': True, 'params': {'0': '5'}},
        'CAB': {'name': 'UK-75 4x12', 'on': True, 'params': {'0': '50'}},
        'EQ': {'name': 'EQ 1', 'on': True, 'params': {'0': '0', '1': '0'}},
        'MOD': {'name': 'A-Chorus', 'on': False},
        'DLY': {'name': 'M-Echo', 'on': False},
        'RVB': {'name': 'Plate', 'on': False},
    },
}
SPEC_B = {
    'name': 'MONEY1CL',
    'type': 'Rock',
    'bpm': 148,
    'volume': 60,
    'modules': {
        'PRE': {'name': 'Boost', 'on': True},
        'DST': {'name': 'Red Haze', 'on': False},
        'AMP': {'name': 'UK 50JP', 'on': True, 'params': {'0': '55'}},
        'NR': {'name': 'Gate 2', 'on': True},
        'CAB': {'name': 'UK-75 4x12', 'on': True},
        'EQ': {'name': 'EQ 1', 'on': True},
        'MOD': {'name': 'A-Chorus', 'on': False},
        'DLY': {'name': 'M-Echo', 'on': False},
        'RVB': {'name': 'Plate', 'on': False},
    },
}


@pytest.fixture(scope='module')
def templates() -> dict:
    return load_templates(RAIZ / 'data' / 'factory-catalog.json')


# ── receita do formato ───────────────────────────────────────────────────────


def test_count_e_numero_de_presets(templates) -> None:
    xml = gerar_xml_all([SPEC_A, SPEC_B], templates, build_time=TEMPO)
    root = ET.fromstring(xml.decode('utf-8'))
    info = root.find('preset_info')
    assert info.get('count') == '2'
    assert info.get('firmware') == '2.1'
    assert len(root.findall('presets')) == 2


def test_bloco_preset_e_byte_a_byte_o_do_single(templates) -> None:
    """A receita: all = single repetido — bloco `<presets>` não muda um byte."""
    single = gerar_xml(SPEC_A, templates, build_time=TEMPO).decode('utf-8')
    bloco_single = single[
        single.index('<presets') : single.rindex('</presets>') + len('</presets>')
    ]

    all_bytes = gerar_xml_all([SPEC_A, SPEC_B], templates, build_time=TEMPO)
    texto = all_bytes.decode('utf-8')
    assert bloco_single in texto


def test_ppirinfo_presente_com_20_slots(templates) -> None:
    xml = gerar_xml_all(
        [SPEC_A],
        templates,
        build_time=TEMPO,
        user_irs=[{'crc': '12345', 'crc_type': '1'}],
    )
    root = ET.fromstring(xml.decode('utf-8'))
    ir_info = root.find('ppIRInfo')
    assert ir_info is not None
    slots = list(ir_info)
    assert len(slots) == SLOTS_IR
    primeiro, segundo = slots[0], slots[1]
    assert primeiro.get('ppIRNum') == '168820736'
    assert primeiro.get('ppIRCRC') == '12345'
    assert primeiro.get('ppIRCRCType') == '1'
    assert segundo.get('ppIRCRC') == '0'  # slot sem IR informado


def test_sem_user_irs_nao_tem_ppirinfo(templates) -> None:
    """Biblioteca sem IR local: o bloco nem precisa existir no candidato."""
    root = ET.fromstring(gerar_xml_all([SPEC_A], templates, build_time=TEMPO).decode('utf-8'))
    assert root.find('ppIRInfo') is None


def test_mesma_serializacao_crlf_e_timestamp(templates) -> None:
    xml = gerar_xml_all([SPEC_A], templates, build_time=TEMPO)
    assert xml.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n')
    assert b'\n' not in xml.replace(b'\r\n', b'')  # só CRLF
    assert f'time="{TEMPO}"'.encode() in xml


def test_lista_vazia_reprova(templates) -> None:
    with pytest.raises(SpecAllInvalido):
        gerar_xml_all([], templates)


# ── round-trip com o reader ──────────────────────────────────────────────────


def test_reader_le_o_all_como_le_o_export_de_fabrica(tmp_path: Path, templates) -> None:
    """O reader (treinado no export de fábrica) lê o all gerado sem surpresa."""
    arquivo = tmp_path / 'biblioteca.prst'
    arquivo.write_bytes(gerar_xml_all([SPEC_A, SPEC_B], templates, build_time=TEMPO))
    info, irs, patches = parse(arquivo)
    assert info['count'] == '2'
    assert irs == []
    assert [p['name'] for p in patches] == ['SMOO1RI', 'MONEY1CL']
    pre = next(e for e in patches[0]['effects'] if e['module'] == 'PRE')
    assert pre['params'][0] == '25'
