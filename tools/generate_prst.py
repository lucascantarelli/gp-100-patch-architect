#!/usr/bin/env python3
"""Gera arquivos .prst (XML) no formato SINGLE PATCH para a Valeton GP-100.

Uso:
    python tools/generate_prst.py patch.json saida.prst

IMPORTANTE (aprendido na prática): a GP-100 distingue export "all" (biblioteca
inteira, com <ppIRInfo>) do arquivo de PATCH ÚNICO. Importar arquivo no formato
errado dá o erro "Wrong patch file type (single/all)". Este gerador emite o
formato SINGLE, réplica do export de patch único feito pelo GP-100 Edits:

  - preset_info com firmware="2.1" (firmware atual do GP-100)
  - SEM o bloco <ppIRInfo> (isso é coisa do export "all")
  - cada preset termina com <ppCtrl> e <ppEXP1> (3 slots de expressão)
  - atributos do <Effect> na ordem: name, state, code, params_0, x, y, params_1..
  - x = posição fixa do módulo na cadeia: PRE=0 DST=1 AMP=2 NR=3 CAB=4 EQ=5
    MOD=6 DLY=7 RVB=8
  - params além dos reais do modelo = 65535; params_12..14 = 0

Formato do JSON de entrada (conforme reference/15-firmware2-effects.md):
{
  "name": "BL-CRN-D01",
  "type": "Blues",              // ver mapa em reference/15
  "bpm": 96,
  "volume": 55,                  // ppVolume 0-99
  "ir_slot": null,               // 0-19 p/ user IR, ou null p/ IR de fábrica (27)
                                 // OBS.: em exports de fábrica, ppIRNum NÃO muda o CAB do preset
                                 // (99 presets = "27" com CABs diferentes). Serve como associação
                                 // do patch a um slot de IR; o CAB muda via effectCode.
  "ir_cab_user_slot": null,      // EXPERIMENTAL: aponta o CAB p/ o User IR deste slot (0-19).
                                 // Emite effectCode = 168820736+slot e effectName "User IR n".
                                 // Requer o .wav carregado no slot; TESTE na pedaleira antes de adotar.
  "modules": {
    "PRE":  {"name": "COMP", "on": true,  "params": {"0": 25, "1": 40, "2": 50}},
    "DST":  {"name": "Blues OD", "on": true, "params": {"0": 72, "1": 92, "2": 73}},
    "AMP":  {"name": "Dark Twin", "on": true, "params": {"0": 55, "3": 45, "5": 60}},
    "NR":   {"name": "Gate 1", "on": true, "params": {"0": 30}},
    "CAB":  {"name": "DarkTW 2x12", "on": true, "params": {"0": 72}},
    "EQ":   {"name": "EQ 1", "on": true, "params": {"0": 0, "1": -2, "2": 1}},
    "MOD":  {"name": "A-Chorus", "on": false},
    "DLY":  {"name": "Sweet", "on": true, "params": {"0": 25, "1": 400, "2": 20}},
    "RVB":  {"name": "Spring", "on": true, "params": {"0": 40, "1": 99, "2": 50}}
  }
}

Base de templates de params: export de fábrica (tools/factory-catalog.json).
Somente parâmetros declarados no JSON sobrescrevem o template.
"""
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

CATALOG = Path(__file__).parent / 'factory-catalog.json'

GENRE_CODES = {
    'Metal': '0', 'World': '1', 'Indie': '2', 'Country': '3', 'Rock': '4',
    'Funk': '5', 'Pop': '6', 'Blues': '7', 'Jazz': '8', 'Bass': '9', 'Acoustic': '10',
}
CHAIN = ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']
CHAIN_POS = {'PRE': 0, 'DST': 1, 'AMP': 2, 'NR': 3, 'CAB': 4,
             'EQ': 5, 'MOD': 6, 'DLY': 7, 'RVB': 8}
FACTORY_IR = '27'  # IR padrão dos 99 patches de fábrica
BASE_IR_NUM = 168820736
EXP_DUMMY_CODE = '524295'  # slot de expressão vazio (observado no export single)

# Contagem de params REAIS por modelo (slots além deste índice viram 65535).
# Fontes: export single real que importou com sucesso no aparelho + manual V1.8.
PARAM_COUNT_OVERRIDES = {
    'Plate': 4, 'M-Echo': 5, 'A-Chorus': 4, 'EQ 1': 6, 'UK-75 4x12': 2,
    'Gate 2': 3, 'UK 50JP': 7, 'Green OD': 3, 'V-Wah': 3,
    # modelos PRE que o export de fábrica zera (sem "junk" para detectar):
    'COMP': 4, 'COMP4': 4, 'Boost': 2, 'AC Sim': 4, 'T-WAH': 4, 'A-WAH': 4,
    'C-Wah': 4, 'OCTA': 2,
}

# ordem dos módulos nos blocos <Effect> observada no export de fábrica
EXPORT_ORDER = ['RVB', 'DLY', 'MOD', 'EQ', 'CAB', 'NR', 'AMP', 'DST', 'PRE']

# Modelos REAIS do fw 2.0 ausentes no export de fábrica (nenhum preset os usava).
# Códigos/params de referência: reference/15-firmware2-effects.md (PRE, linha Saturate).
EXTRA_TEMPLATES = {
    ('PRE', 'Saturate'): {
        'module': 'PRE', 'name': 'Saturate', 'code': '16777267', 'state': '1',
        'params': ['50', '99', '70', '30', '50', '50', '1',
                   '65535', '65535', '65535', '65535', '65535', '0', '0', '0'],
    },
}


def load_templates():
    """Carrega tools/factory-catalog.json como dicionário {(módulo, modelo): template}.

    Cada template traz effectCode e os 15 params_0..14 observados no export de
    fábrica; servem de base para o patch — só os params declarados no JSON do
    usuário sobrescrevem. Primeira ocorrência de cada (módulo, modelo) vence.
    """
    data = json.load(open(CATALOG, encoding='utf-8'))
    templates = {}
    for p in data['patches']:
        for e in p['effects']:
            key = (e['module'], e['name'])
            if key not in templates:
                templates[key] = {
                    'module': e['module'], 'name': e['name'], 'code': e['code'],
                    'state': e['state'], 'params': list(e['params']),
                }
    templates.update(EXTRA_TEMPLATES)
    return templates


def is_junk(v):
    """Slot opaco do firmware (não é param real): 65535, múltiplos de 256 >= 256
    ou valores grandes internos (10495, 20736, ...). Params reais ficam 0-99,
    decimais (ex.: 0.5) ou tempos em ms (< 1000)."""
    if v is None:
        return True
    s = str(v)
    if s == '65535':
        return True
    if '.' in s:
        return False
    try:
        n = int(s)
    except ValueError:
        return False
    return n >= 1000 or (n >= 256 and n % 256 == 0)


def real_param_count(name, tpl_params):
    """Número de params REAIS de um modelo (slots além disso viram 65535).

    Consulta PARAM_COUNT_OVERRIDES; sem override, usa o primeiro slot "junk"
    do template como limite (ver is_junk).
    """
    if name in PARAM_COUNT_OVERRIDES:
        return PARAM_COUNT_OVERRIDES[name]
    for i, v in enumerate(tpl_params):
        if is_junk(v):
            return i
    return len(tpl_params)


def build_effect(module, spec, templates):
    """Monta o <Effect> de um módulo no formato do export single do GP-100 Edits.

    Parte do template do modelo, aplica os params do usuário, preenche 65535
    além da contagem real (0 nos params_12..14) e grava os atributos NA ORDEM
    OBSERVADA no arquivo que funciona: name, state, code, params_0, x, y, params_1…
    A posição x é fixa por módulo (PRE=0 … RVB=8). Falha com erro explicativo
    se o modelo não existir no catálogo do firmware.
    """
    name = spec.get('name')
    key = (module, name)
    if key not in templates:
        raise SystemExit(f"ERRO: modelo '{name}' do módulo {module} não existe no catálogo do firmware 2.0.\n"
                         f"Consulte reference/15-firmware2-effects.md")
    tpl = templates[key]
    raw = list(tpl['params'])
    if len(raw) < 15:
        raw += [None] * (15 - len(raw))
    count = min(15, max(0, real_param_count(name, raw)))

    user = spec.get('params') or {}
    params = {}
    for i in range(15):
        if i >= 12:
            params[i] = '0'
        elif i >= count:
            params[i] = '65535'
        else:
            v = user.get(str(i), raw[i])
            params[i] = '0' if v is None else str(v)

    eff = ET.Element('Effect')
    # ordem de atributos idêntica ao export single do GP-100 Edits
    eff.set('effectModuleName', module)
    eff.set('effectName', name)
    eff.set('effectState', '1' if spec.get('on', False) else '0')
    eff.set('effectCode', tpl['code'])
    eff.set('params_0', params[0])
    eff.set('x', str(CHAIN_POS[module]))
    eff.set('y', '0')
    for i in range(1, 15):
        eff.set(f'params_{i}', params[i])
    return eff


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    spec = json.load(open(sys.argv[1], encoding='utf-8'))
    templates = load_templates()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    modules = spec.get('modules', {})
    for m in modules:
        if m not in CHAIN:
            raise SystemExit(f"Módulo desconhecido: {m}")

    root = ET.Element('GP-100')
    info = ET.SubElement(root, 'preset_info')
    info.set('software', '1.2.0')
    info.set('firmware', '2.1')  # firmware atual — 2.0 no export antigo rejeita
    info.set('product', 'GP-100')
    info.set('count', '1')
    info.set('platform', 'WINDOWS')
    info.set('time', str(int(time.time() * 1000)))

    genre = spec.get('type', 'Rock')
    if genre not in GENRE_CODES:
        raise SystemExit(f"Gênero '{genre}' inválido. Use: {', '.join(GENRE_CODES)}")

    preset = ET.SubElement(root, 'presets')
    preset.set('ppBank', '0')
    preset.set('ppName', spec.get('name', 'PATCH')[:12])
    preset.set('ppVolume', str(spec.get('volume', 50)))
    preset.set('ppID', '0')
    preset.set('ppBPM', str(spec.get('bpm', 120)))
    ir_slot = spec.get('ir_slot')
    if ir_slot is None:
        preset.set('ppIRNum', FACTORY_IR)
    else:
        if not 0 <= int(ir_slot) <= 19:
            raise SystemExit("ir_slot deve ser 0..19 (user IR) ou null")
        preset.set('ppIRNum', str(BASE_IR_NUM + int(ir_slot)))
    ir_cab_slot = spec.get('ir_cab_user_slot')
    if ir_cab_slot is not None and not 0 <= int(ir_cab_slot) <= 19:
        raise SystemExit("ir_cab_user_slot deve ser 0..19 (slot de User IR carregada)")
    preset.set('ppType', GENRE_CODES[genre])
    preset.set('ppAuthor', spec.get('author', ''))
    preset.set('ppNotes', spec.get('notes', ''))
    preset.set('ppTypeName', genre)

    for module in EXPORT_ORDER:
        mspec = modules.get(module)
        if mspec is None:
            neutral = ('Sweet' if module == 'DLY' else 'Hall' if module == 'RVB'
                       else 'A-Chorus' if module == 'MOD' else 'EQ 1' if module == 'EQ'
                       else 'Gate 1' if module == 'NR' else None)
            if neutral and (module, neutral) in templates:
                mspec = {'name': neutral, 'on': False}
            else:
                raise SystemExit(
                    f"Módulo {module} não declarado no JSON e sem template neutro. "
                    f"Declare 'name' e 'on' em modules.{module} (ver reference/15).")
        eff = build_effect(module, mspec, templates)
        if module == 'CAB' and ir_cab_slot is not None:
            eff.set('effectCode', str(BASE_IR_NUM + int(ir_cab_slot)))
            eff.set('effectName', f'User IR {int(ir_cab_slot) + 1}')
        preset.append(eff)

    # blocos de controle/expressão — presentes em TODO preset do formato single
    ctrl = ET.SubElement(preset, 'ppCtrl')
    ctrl.set('c11', '65535')
    ctrl.set('c12', '1')
    ctrl.set('c13', '65535')
    ctrl.set('c21', '65535')
    ctrl.set('c22', '65535')
    ctrl.set('c23', '8')
    exp1 = ET.SubElement(preset, 'ppEXP1')
    exp1.set('expTarget', '0')
    exp1.set('expVolume', '0')
    exp1.set('expVolumeMin', '0')
    exp1.set('expVolumeMax', '99')
    pre_name = (modules.get('PRE') or {}).get('name')
    pre_code = templates.get(('PRE', pre_name), {}).get('code') if pre_name else None
    for idx in range(3):
        ch = ET.SubElement(exp1, f'ppEXP1_{idx}')
        if idx == 0 and pre_code not in (None, '0'):
            ch.set('expMId', '0')
            ch.set('expCode', str(pre_code))
        else:
            ch.set('expMId', '65535')
            ch.set('expCode', EXP_DUMMY_CODE)
        ch.set('expIndex', '0')
        ch.set('expMin', '0')
        ch.set('expMax', '99')

    ET.indent(root, space='  ')
    xml = ET.tostring(root, encoding='unicode')
    lines = xml.splitlines()
    out = '\r\n'.join(lines) + '\r\n'
    with open(sys.argv[2], 'w', encoding='utf-8', newline='') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n' + out)
    print(f"OK: {sys.argv[2]}")
    print("Formato single-patch (firmware 2.1). Importe no GP-100 Edits ou direto na pedaleira.")
    if ir_cab_slot is not None:
        print(f"EXPERIMENTAL: CAB = User IR slot {int(ir_cab_slot) + 1} (code {BASE_IR_NUM + int(ir_cab_slot)}).")
        print("Carregue o .wav no slot antes de importar e teste na pedaleira.")


if __name__ == '__main__':
    main()
