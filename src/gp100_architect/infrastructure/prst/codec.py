"""Codec de escrita do `.prst` — geração do XML single-patch fw 2.1 (issue #29).

O ativo mais sensível do projeto: se o formato divergir uma linha, o patch
deixa de importar na pedaleira ("Wrong patch file type (single/all)"). Por
isso este módulo é CODEOWNER explícito e as regras abaixo são contrato.

REGRAS DO FORMATO (aprendidas na prática, validadas no aparelho):

  - a GP-100 distingue export "all" (biblioteca inteira, com `<ppIRInfo>`) do
    arquivo de PATCH ÚNICO; este codec emite o formato SINGLE, réplica do
    export de patch único do GP-100 Edits;
  - preset_info com firmware="2.1" (o 2.0 do export antigo é rejeitado);
  - SEM `<ppIRInfo>` (isso é coisa do export "all");
  - cada preset termina com `<ppCtrl>` e `<ppEXP1>` (3 slots de expressão);
  - atributos do `<Effect>` na ordem: effectModuleName, effectName,
    effectState, effectCode, params_0, x, y, params_1..14;
  - x = posição fixa do módulo na cadeia: PRE=0 DST=1 AMP=2 NR=3 CAB=4 EQ=5
    MOD=6 DLY=7 RVB=8 (`CHAIN_POS`, particular do formato `.prst`);
  - params além dos reais do modelo = 65535; params_12..14 = 0;
  - timestamp determinístico (epoch ms): `GP100_BUILD_TIME` ou o padrão
    1688207360000 — build reprodutível, sem churn em 97+ arquivos.

Fonte dos templates: `data/factory-catalog.json` (export de fábrica drenado
por `analyze_prst`). Somente params declarados no spec sobrescrevem o template.

Camada: infrastructure (o domínio nunca importa daqui). Funções PURAS no
sentido do projeto: nenhum print, nenhum SystemExit — erros previstos são
exceções de domínio; escrever arquivo é da CLI (interfaces).
"""

from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.errors import (
    FormatoPrstInvalido,
    ModeloDesconhecido,
    SpecInvalido,
)

__all__ = [
    'BUILD_TIME_PADRAO',
    'CHAIN_POS',
    'EXPORT_ORDER',
    'EXP_DUMMY_CODE',
    'FACTORY_IR',
    'PARAM_COUNT_OVERRIDES',
    'caminho_catalogo',
    'gerar_xml',
    'is_junk',
    'load_templates',
    'real_param_count',
    'validar_spec',
]

# ---- constantes do formato -------------------------------------------------

# ordem dos módulos nos blocos <Effect> observada no export de fábrica
EXPORT_ORDER: tuple[str, ...] = ('RVB', 'DLY', 'MOD', 'EQ', 'CAB', 'NR', 'AMP', 'DST', 'PRE')

# posição fixa de cada módulo na cadeia do preset (atributo x)
CHAIN_POS: dict[str, int] = {
    'PRE': 0,
    'DST': 1,
    'AMP': 2,
    'NR': 3,
    'CAB': 4,
    'EQ': 5,
    'MOD': 6,
    'DLY': 7,
    'RVB': 8,
}

FACTORY_IR = '27'  # IR padrão dos 99 patches de fábrica
BASE_IR_NUM = 168820736
EXP_DUMMY_CODE = '524295'  # slot de expressão vazio (observado no export single)
BUILD_TIME_PADRAO = '1688207360000'

GENRE_CODES: dict[str, str] = {
    'Metal': '0',
    'World': '1',
    'Indie': '2',
    'Country': '3',
    'Rock': '4',
    'Funk': '5',
    'Pop': '6',
    'Blues': '7',
    'Jazz': '8',
    'Bass': '9',
    'Acoustic': '10',
}

# Contagem de params REAIS por modelo (slots além deste índice viram 65535).
# Fontes: export single real que importou com sucesso no aparelho + manual V1.8.
PARAM_COUNT_OVERRIDES: dict[str, int] = {
    'Plate': 4,
    'M-Echo': 5,
    'A-Chorus': 4,
    'EQ 1': 6,
    'UK-75 4x12': 2,
    'Gate 2': 3,
    'UK 50JP': 7,
    'Green OD': 3,
    'V-Wah': 3,
    # modelos PRE que o export de fábrica zera (sem "junk" para detectar):
    'COMP': 4,
    'COMP4': 4,
    'Boost': 2,
    'AC Sim': 4,
    'T-WAH': 4,
    'A-WAH': 4,
    'C-Wah': 4,
    'OCTA': 2,
}

# Modelos REAIS do fw 2.0 ausentes no export de fábrica (nenhum preset os usava).
# Códigos/params de referência: reference/15-firmware2-effects.md (PRE, linha Saturate).
EXTRA_TEMPLATES: dict[tuple[str, str], dict[str, Any]] = {
    ('PRE', 'Saturate'): {
        'module': 'PRE',
        'name': 'Saturate',
        'code': '16777267',
        'state': '1',
        'params': [
            '50',
            '99',
            '70',
            '30',
            '50',
            '50',
            '1',
            '65535',
            '65535',
            '65535',
            '65535',
            '65535',
            '0',
            '0',
            '0',
        ],
    },
}


def caminho_catalogo() -> Path:
    """`data/factory-catalog.json` a partir da raiz do repositório.

    O pacote é desenvolvido DENTRO do repo (ADR-0001): o catálogo fica em
    `data/` e o caminho sobe quatro níveis (prst → infrastructure →
    gp100_architect → src → raiz). Num pacote instalado isolado o catálogo não
    existe — o projeto não se destina a isso (o TestH roda o sandbox do repo).
    """
    return Path(__file__).resolve().parents[4] / 'data' / 'factory-catalog.json'


def load_templates(catalogo: Path | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    """Carrega o catálogo como `{(módulo, modelo): template}`.

    Cada template traz effectCode e os 15 params_0..14 observados no export de
    fábrica; servem de base para o patch — só os params declarados no spec
    sobrescrevem. Primeira ocorrência de cada (módulo, modelo) vence.
    """
    caminho = catalogo or caminho_catalogo()
    try:
        data = json.loads(caminho.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        msg = (
            f'catálogo do firmware não encontrado: {caminho}\n'
            f'Ele é versionado em data/factory-catalog.json — '
            f'restaurá-lo ou regenerá-lo (reference/15).'
        )
        raise FormatoPrstInvalido(msg) from exc
    templates: dict[tuple[str, str], dict[str, Any]] = {}
    for p in data['patches']:
        for e in p['effects']:
            key = (e['module'], e['name'])
            if key not in templates:
                templates[key] = {
                    'module': e['module'],
                    'name': e['name'],
                    'code': e['code'],
                    'state': e['state'],
                    'params': list(e['params']),
                }
    templates.update(EXTRA_TEMPLATES)
    return templates


def is_junk(v: Any) -> bool:
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


def real_param_count(name: str, tpl_params: list[Any]) -> int:
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


def _validar_campos(preset: dict[str, Any]) -> None:
    """Campos escalares do spec — erros acionáveis em vez de silenciosos."""
    genre = preset.get('type', 'Rock')
    if genre not in GENRE_CODES:
        raise SpecInvalido(
            f"spec.type '{genre}' inválido — use um de: {', '.join(sorted(GENRE_CODES))}"
        )
    ir_slot = preset.get('ir_slot')
    if ir_slot is not None and not 0 <= int(ir_slot) <= 19:
        raise SpecInvalido(f'ir_slot deve ser 0..19 (user IR) ou null — recebi {ir_slot}')
    ir_cab_slot = preset.get('ir_cab_user_slot')
    if ir_cab_slot is not None and not 0 <= int(ir_cab_slot) <= 19:
        raise SpecInvalido(f'ir_cab_user_slot deve ser 0..19 — recebi {ir_cab_slot}')


def validar_spec(spec: dict[str, Any], templates: dict[tuple[str, str], dict[str, Any]]) -> None:
    """Valida o spec contra o contrato do formato (módulos, modelos, campos).

    Antes do primeiro byte ser escrito: módulo fora da cadeia, modelo fora do
    catálogo e campo escalar inválido falham aqui com exceção de domínio — a
    CLI converte em erro acionável (nada de estourar no meio do XML).
    """
    if not isinstance(spec, dict):
        raise SpecInvalido(f'spec deve ser um objeto JSON — recebi {type(spec).__name__}')
    _validar_campos(spec)
    modules = spec.get('modules', {})
    for m in modules:
        if m not in CHAIN:
            raise SpecInvalido(
                f'spec.modules.{m}: módulo desconhecido — a cadeia fixa é '
                f'{", ".join(CHAIN)} (o GP-100 não permite reordenar)'
            )
    for m in EXPORT_ORDER:
        mspec = modules.get(m)
        if mspec is None:
            continue  # neutro resolvido na geração
        nome = str(mspec.get('name'))
        if (m, nome) not in templates:
            raise ModeloDesconhecido(
                f"modelo '{nome}' do módulo {m} não existe no catálogo do firmware 2.0. "
                f'Consulte reference/15-firmware2-effects.md'
            )
    _validar_exp1_spec(spec, modules)


def _validar_exp1_spec(spec: dict[str, Any], modules: dict[str, Any]) -> None:
    """`spec.exp1` (issue #9) — o pedal controla um módulo DECLARADO no spec.

    O domínio valida nomes oficiais e faixa min/max; aqui vale a regra de
    formato: sem módulo-alvo não há `expCode` para amarrar no `<ppEXP1>`.
    """
    exp1 = spec.get('exp1')
    if exp1 is None:
        return
    if not isinstance(exp1, dict) or not exp1.get('módulo'):
        raise SpecInvalido(
            "spec.exp1 deve ser {'módulo', 'param', 'min'?, 'max'?} — 'módulo' é obrigatório"
        )
    alvo = exp1['módulo']
    if alvo not in modules:
        raise SpecInvalido(
            f"spec.exp1.módulo: '{alvo}' não está em spec.modules — declare o módulo "
            f'(name/on); o EXP1 controla um pedal específico da cadeia'
        )
    for campo in ('min', 'max'):
        v = exp1.get(campo)
        if v is None:
            continue
        try:
            int(v)
        except (TypeError, ValueError) as exc:
            raise SpecInvalido(
                f'spec.exp1.{campo}: {v!r} não é número — use o valor do curso do pedal (0–99)'
            ) from exc


def gerar_xml(
    spec: dict[str, Any],
    templates: dict[tuple[str, str], dict[str, Any]],
    build_time: str | None = None,
) -> bytes:
    """Gera o XML single-patch fw 2.1 como bytes (UTF-8, CRLF, sem escrever disco).

    Comportamento idêntico ao gerador original (provado byte-a-byte pelo
    TestH): mesmo cabeçalho, mesmos atributos na mesma ordem, mesmo CRLF.
    """
    validar_spec(spec, templates)

    root = ET.Element('GP-100')
    info = ET.SubElement(root, 'preset_info')
    info.set('software', '1.2.0')
    info.set('firmware', '2.1')  # firmware atual — 2.0 no export antigo rejeita
    info.set('product', 'GP-100')
    info.set('count', '1')
    info.set('platform', 'WINDOWS')
    info.set('time', build_time or os.environ.get('GP100_BUILD_TIME', BUILD_TIME_PADRAO))

    genre = spec.get('type', 'Rock')
    preset = ET.SubElement(root, 'presets')
    preset.set('ppBank', '0')
    preset.set('ppName', str(spec.get('name', 'PATCH'))[:12])
    preset.set('ppVolume', str(spec.get('volume', 50)))
    preset.set('ppID', '0')
    preset.set('ppBPM', str(spec.get('bpm', 120)))
    ir_slot = spec.get('ir_slot')
    preset.set('ppIRNum', FACTORY_IR if ir_slot is None else str(BASE_IR_NUM + int(ir_slot)))
    ir_cab_slot = spec.get('ir_cab_user_slot')
    preset.set('ppType', GENRE_CODES[genre])
    preset.set('ppAuthor', str(spec.get('author', '')))
    preset.set('ppNotes', str(spec.get('notes', '')))
    preset.set('ppTypeName', genre)

    modules = spec.get('modules', {})
    for module in EXPORT_ORDER:
        mspec = modules.get(module)
        if mspec is None:
            neutral = (
                'Sweet'
                if module == 'DLY'
                else 'Hall'
                if module == 'RVB'
                else 'A-Chorus'
                if module == 'MOD'
                else 'EQ 1'
                if module == 'EQ'
                else 'Gate 1'
                if module == 'NR'
                else None
            )
            if neutral and (module, neutral) in templates:
                mspec = {'name': neutral, 'on': False}
            else:
                raise SpecInvalido(
                    f'spec.modules.{module}: não declarado e sem template neutro. '
                    f"Declare 'name' e 'on' (ver reference/15)."
                )
        eff = _build_effect(module, mspec, templates)
        if module == 'CAB' and ir_cab_slot is not None:
            eff.set('effectCode', str(BASE_IR_NUM + int(ir_cab_slot)))
            eff.set('effectName', f'User IR {int(ir_cab_slot) + 1}')
        preset.append(eff)

    _anexar_controle(preset, spec, modules, templates)
    return _serializar(root)


def _build_effect(
    module: str, spec: dict[str, Any], templates: dict[tuple[str, str], dict[str, Any]]
) -> ET.Element:
    """Monta o `<Effect>` de um módulo (contrato: ver docstring do módulo)."""
    name = str(spec['name'])
    tpl = templates[(module, name)]
    raw = list(tpl['params'])
    if len(raw) < 15:
        raw += [None] * (15 - len(raw))
    count = min(15, max(0, real_param_count(name, raw)))

    user = spec.get('params') or {}
    params: dict[int, str] = {}
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


def _anexar_controle(
    preset: ET.Element,
    spec: dict[str, Any],
    modules: dict[str, Any],
    templates: dict[tuple[str, str], dict[str, Any]],
) -> None:
    """`<ppCtrl>` e `<ppEXP1>` — presentes em TODO preset do formato single.

    EXP1 (issue #9): quando `spec.exp1` declara o pedal, o slot 1 do
    `<ppEXP1>` recebe o `expCode` do módulo-alvo e o curso [expMin, expMax].
    O slot 0 permanece do comportamento de fábrica do aparelho (auto-PRE,
    volume do pré) — é a premissa do gerador desde sempre; a confirmação
    empírica no aparelho segue a agenda da #83. Sem `exp1`, os 3 slots saem
    dummy exatamente como sempre (biblioteca existente byte-a-byte).
    """
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
    cfg_exp1 = spec.get('exp1') or {}
    alvo = cfg_exp1.get('módulo') if isinstance(cfg_exp1, dict) else None
    alvo_code: str | None = None
    if alvo in modules:
        nome_alvo = str((modules.get(alvo) or {}).get('name', ''))
        alvo_code = templates.get((alvo, nome_alvo), {}).get('code')
    pre_name = (modules.get('PRE') or {}).get('name')
    pre_code = templates.get(('PRE', pre_name), {}).get('code') if pre_name else None
    for idx in range(3):
        ch = ET.SubElement(exp1, f'ppEXP1_{idx}')
        if idx == 0 and pre_code not in (None, '0'):
            ch.set('expMId', '0')
            ch.set('expCode', str(pre_code))
        elif idx == 1 and alvo_code:
            ch.set('expMId', '65535')
            ch.set('expCode', str(alvo_code))
        else:
            ch.set('expMId', '65535')
            ch.set('expCode', EXP_DUMMY_CODE)
        ch.set('expIndex', '0')
        ch.set('expMin', '0')
        ch.set('expMax', '99')
        if idx == 1 and alvo_code:
            ch.set('expMin', str(int(cfg_exp1.get('min', 0))))
            ch.set('expMax', str(int(cfg_exp1.get('max', 99))))


def _serializar(root: ET.Element) -> bytes:
    """Serializa com o layout byte-a-byte do arquivo validado no aparelho."""
    ET.indent(root, space='  ')
    xml = ET.tostring(root, encoding='unicode')
    linhas = '\r\n'.join(xml.splitlines()) + '\r\n'
    return ('<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n' + linhas).encode('utf-8')
