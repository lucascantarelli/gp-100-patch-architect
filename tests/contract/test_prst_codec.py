"""Contrato do codec `.prst` — round-trip e bytes determinísticos (issue #29).

O ativo mais sensível do projeto: qualquer divergência de formato impede a
importação na pedaleira. Estes testes fixam o CONTRATO (não a implementação):

  - round-trip: gerar → ler → o modelo volta (o reader entende o que o codec
    escreveu, campo a campo);
  - bytes determinísticos: mesmo spec + build_time → mesmos bytes, e o
    `GP100_BUILD_TIME` controla o timestamp (build reprodutível);
  - invariáveis do formato single fw 2.1: SEM `<ppIRInfo>`, COM `<ppCtrl>` e
    `<ppEXP1>` (3 slots), atributos do `<Effect>` na ordem do export validado
    no aparelho, params além dos reais = 65535 e params_12..14 = 0;
  - erros de entrada: módulo desconhecido, modelo fora do catálogo, `ir_slot`
    fora do range e XML malformado no reader — cada um com mensagem acionável.

Marcação: `contract` — sem I/O no repositório (bytes e tmp_path).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from gp100_architect.domain.errors import (
    FormatoPrstInvalido,
    ModeloDesconhecido,
    SpecInvalido,
)
from gp100_architect.infrastructure.prst.codec import (
    gerar_xml,
    load_templates,
    validar_spec,
)
from gp100_architect.infrastructure.prst.reader import parse

pytestmark = pytest.mark.contract

TIME_FIXO = '1688207360000'

# spec mínimo válido: usa só modelos garantidos no catálogo (templates de
# fábrica); módulos omitidos ganham neutros do próprio codec
SPEC_MINIMO: dict = {
    'name': 'TST-CON-01',
    'type': 'Rock',
    'bpm': 120,
    'volume': 55,
    'ir_slot': None,
    'modules': {
        'PRE': {'name': 'COMP', 'on': True, 'params': {'0': 25}},
        'DST': {'name': 'Blues OD', 'on': True, 'params': {'0': 72}},
        'AMP': {'name': 'Dark Twin', 'on': True, 'params': {'0': 55}},
        'CAB': {'name': 'DarkTW 2x12', 'on': True, 'params': {'0': 72}},
    },
}


@pytest.fixture(scope='module')
def templates():
    return load_templates()


# ---- round-trip: gerar → ler → o modelo volta --------------------------------


def test_roundtrip_gerar_ler_mesmo_modelo(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO)
    root = ET.fromstring(xml.decode('utf-8'))
    info, irs, patches = parse_stream_compat(root)
    assert info['firmware'] == '2.1'
    assert irs == []  # formato single NUNCA tem ppIRInfo
    p = patches[0]
    assert p['name'] == 'TST-CON-01'
    assert p['volume'] == '55'
    assert p['bpm'] == '120'
    por_modulo = {e['module']: e for e in p['effects']}
    assert por_modulo['DST']['name'] == 'Blues OD'
    assert por_modulo['DST']['state'] == '1'
    assert por_modulo['DST']['params'][0] == '72'  # param do usuário venceu
    # módulos omitidos ganharam neutros OFF
    assert por_modulo['RVB']['name'] == 'Spring' or por_modulo['RVB']['name'] == 'Hall'
    assert por_modulo['RVB']['state'] == '0'


def parse_stream_compat(root: ET.Element):
    """parse() de um Element em memória (o parse oficial lê de caminho)."""
    import tempfile

    from gp100_architect.infrastructure.prst.reader import analyze  # noqa: F401

    # o contrato do reader é por caminho (o formato é arquivo); em memória,
    # serializa de volta — mesmo contrato, sem tmp na assinatura do teste
    with tempfile.NamedTemporaryFile(suffix='.prst', delete=False) as f:
        f.write(ET.tostring(root, encoding='utf-8'))
        caminho = f.name
    return parse(caminho)


# ---- bytes determinísticos -----------------------------------------------------


def test_mesmo_spec_mesmos_bytes(templates) -> None:
    a = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO)
    b = gerar_xml(dict(SPEC_MINIMO), templates, build_time=TIME_FIXO)
    assert a == b


def test_build_time_controla_o_timestamp(templates) -> None:
    a = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO)
    b = gerar_xml(SPEC_MINIMO, templates, build_time='1111111111111')
    assert a != b
    root_a = ET.fromstring(a.decode('utf-8'))
    assert root_a.find('preset_info').get('time') == TIME_FIXO  # type: ignore[union-attr]
    root_b = ET.fromstring(b.decode('utf-8'))
    assert root_b.find('preset_info').get('time') == '1111111111111'  # type: ignore[union-attr]


def test_ambiente_gp100_build_time_e_respeitado(templates, monkeypatch) -> None:
    monkeypatch.setenv('GP100_BUILD_TIME', '2222222222222')
    xml = gerar_xml(SPEC_MINIMO, templates)  # sem build_time explícito
    root = ET.fromstring(xml.decode('utf-8'))
    assert root.find('preset_info').get('time') == '2222222222222'  # type: ignore[union-attr]


# ---- invariáveis do formato single fw 2.1 --------------------------------------


def test_sem_ppIRInfo_e_com_ppCtrl_ppEXP1(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO).decode('utf-8')
    root = ET.fromstring(xml)
    assert root.find('ppIRInfo') is None, 'ppIRInfo é coisa do export "all"'
    preset = root.find('presets')
    assert preset is not None
    ctrl = preset.find('ppCtrl')
    assert ctrl is not None and ctrl.get('c12') == '1'
    exp = preset.find('ppEXP1')
    assert exp is not None
    slots = [exp.find(f'ppEXP1_{i}') for i in range(3)]
    assert all(s is not None for s in slots), 'formato single tem 3 slots de expressão'


def test_ordem_dos_atributos_e_a_do_export_validado(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO).decode('utf-8')
    root = ET.fromstring(xml)
    preset = root.find('presets')
    assert preset is not None
    dst = next(e for e in preset.findall('Effect') if e.get('effectModuleName') == 'DST')
    assert list(dst.keys())[:6] == [
        'effectModuleName',
        'effectName',
        'effectState',
        'effectCode',
        'params_0',
        'x',
    ]


def test_params_além_dos_reais_sao_65535_e_12_14_zero(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO).decode('utf-8')
    root = ET.fromstring(xml)
    preset = root.find('presets')
    assert preset is not None
    dst = next(e for e in preset.findall('Effect') if e.get('effectModuleName') == 'DST')
    # Blues OD: 5 params reais (primeiro junk no params_5 do template) e o user
    # só sobrescreveu params_0 — o template vence nos slots 1..4 que são reais.
    assert [dst.get(f'params_{i}') for i in range(5, 12)] == ['65535'] * 7
    assert [dst.get(f'params_{i}') for i in (12, 13, 14)] == ['0', '0', '0']


def test_x_e_a_posicao_fixa_da_cadeia(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO).decode('utf-8')
    root = ET.fromstring(xml)
    preset = root.find('presets')
    assert preset is not None
    xs = {e.get('effectModuleName'): e.get('x') for e in preset.findall('Effect')}
    assert xs == {
        'RVB': '8',
        'DLY': '7',
        'MOD': '6',
        'EQ': '5',
        'CAB': '4',
        'NR': '3',
        'AMP': '2',
        'DST': '1',
        'PRE': '0',
    }


def test_ppName_truncado_em_12_chars(templates) -> None:
    spec = dict(SPEC_MINIMO, name='NOME-DE-PAINEL-LONGO-DEMAIS')
    xml = gerar_xml(spec, templates, build_time=TIME_FIXO).decode('utf-8')
    root = ET.fromstring(xml)
    preset = root.find('presets')
    assert preset is not None
    assert len(preset.get('ppName')) <= 12


def test_ir_slot_fora_do_range_reprova(templates) -> None:
    spec = dict(SPEC_MINIMO, ir_slot=25)
    with pytest.raises(SpecInvalido, match=r'0\.\.19'):
        gerar_xml(spec, templates)


def test_spec_com_modulo_desconhecido_reprova(templates) -> None:
    spec = {**SPEC_MINIMO, 'modules': {'FUZZ': SPEC_MINIMO['modules']['DST']}}
    with pytest.raises(SpecInvalido, match='módulo desconhecido'):
        gerar_xml(spec, templates)


def test_modelo_fora_do_catalogo_reprova(templates) -> None:
    spec = {**SPEC_MINIMO, 'modules': {'DST': {'name': 'Não Existe', 'on': True}}}
    with pytest.raises(ModeloDesconhecido, match='reference/15'):
        gerar_xml(spec, templates)


def test_validar_spec_aprova_o_minimo(templates) -> None:
    validar_spec(SPEC_MINIMO, templates)  # não levanta


# ---- reader: parse defensivo ---------------------------------------------------


def test_xml_malformado_reprova_com_mensagem_acionavel(tmp_path: Path) -> None:
    ruim = tmp_path / 'ruim.prst'
    ruim.write_text('<GP-100><preset_info sem fechar', encoding='utf-8')
    with pytest.raises(FormatoPrstInvalido, match='XML malformado'):
        parse(ruim)


def test_arquivo_sem_preset_info_reprova(tmp_path: Path) -> None:
    estranho = tmp_path / 'estranho.prst'
    estranho.write_text('<outra-coisa><x/></outra-coisa>', encoding='utf-8')
    with pytest.raises(FormatoPrstInvalido, match='preset_info'):
        parse(estranho)


def test_arquivo_ausente_reprova(tmp_path: Path) -> None:
    with pytest.raises(FormatoPrstInvalido, match='não foi possível'):
        parse(tmp_path / 'fantasma.prst')


# ---- EXP1: spec.exp1 → wiring do <ppEXP1> (issue #9) --------------------------


def _exp_ch(root: ET.Element, idx: int) -> ET.Element:
    return root.find(f'.//ppEXP1_{idx}')  # type: ignore[return-value]


def test_exp1_amarra_o_slot_1_ao_modulo_alvo(templates) -> None:
    spec = {
        **SPEC_MINIMO,
        'modules': {
            **SPEC_MINIMO['modules'],
            'DST': {'name': 'La Charger', 'on': True, 'params': {'0': 64}},
        },
        'exp1': {'módulo': 'DST', 'param': 'Gain', 'min': 30, 'max': 85},
    }
    xml = gerar_xml(spec, templates, build_time=TIME_FIXO)
    root = ET.fromstring(xml.decode('utf-8'))
    codigo_dst = templates[('DST', 'La Charger')]['code']
    slot1 = _exp_ch(root, 1)
    assert slot1.get('expCode') == str(codigo_dst)
    assert slot1.get('expMin') == '30'
    assert slot1.get('expMax') == '85'
    # slot 0 segue a premissa do gerador (auto-PRE/fábrica) e 2 segue dummy
    assert _exp_ch(root, 2).get('expCode') == '524295'


def test_exp1_ausente_mantem_os_tres_slots_dummy(templates) -> None:
    xml = gerar_xml(SPEC_MINIMO, templates, build_time=TIME_FIXO)
    root = ET.fromstring(xml.decode('utf-8'))
    for idx in range(3):
        assert _exp_ch(root, idx).get('expCode') == '524295'
        assert _exp_ch(root, idx).get('expMin') == '0'
        assert _exp_ch(root, idx).get('expMax') == '99'


def test_exp1_modulo_nao_declarado_no_spec_reprova(templates) -> None:
    spec = {**SPEC_MINIMO, 'exp1': {'módulo': 'MOD', 'param': 'Depth'}}
    with pytest.raises(SpecInvalido, match=r'não está em spec\.modules'):
        gerar_xml(spec, templates)


def test_exp1_min_max_nao_numerico_reprova_no_codec(templates) -> None:
    spec = {**SPEC_MINIMO, 'exp1': {'módulo': 'DST', 'param': 'Gain', 'max': 'alto'}}
    with pytest.raises(SpecInvalido, match='não é número'):
        gerar_xml(spec, templates)
