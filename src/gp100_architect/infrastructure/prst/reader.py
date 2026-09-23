"""Codec de leitura do `.prst` — parse e estatísticas (issue #29).

Migração de `tools/analyze_prst.py`: a leitura do XML vira biblioteca
(`parse`/`analyze`/`fmt_stat` puras), e a CLI de relatório continua no shim
de `tools/` — que agora só resolve argumentos e imprime.

Parse defensivo (novo no #29): XML malformado ou sem a estrutura esperada
reprova com `FormatoPrstInvalido` e mensagem acionável em vez de estourar
`AttributeError`/`ParseError` cru — a regra do projeto é erro que diz onde e
como corrigir.

Foi o script original que drenou o export de fábrica do aparelho para
`tools/factory-catalog.json` (99 presets · 891 effects · 117 modelos). O
export original foi removido do repositório na limpeza — exporte a biblioteca
no GP-100 Edits e rode o shim de `tools/` se precisar regenerar o catálogo.

Camada: infrastructure (o domínio nunca importa daqui).
"""

from __future__ import annotations

import contextlib
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any

from gp100_architect.domain.errors import FormatoPrstInvalido

__all__ = ['analyze', 'fmt_stat', 'parse']


def parse(path: str | Path) -> tuple[dict[str, str], list[dict[str, str]], list[dict[str, Any]]]:
    """Lê um export `.prst` (XML) e devolve (info, irs, patches).

    info    — atributos de `<preset_info>` (software/firmware/product/count).
    irs     — lista de User IRs do bloco `<ppIRInfo>` (só existe no export "all").
    patches — cada preset com nome, gênero, bpm, volume e a lista de `<Effect>`
              (módulo, nome normalizado sem espaços, effectCode, estado, x/y e
              params_0..14 com None nos slots ausentes).
    """
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise FormatoPrstInvalido(
            f'{path}: XML malformado ({exc}) — o arquivo é um export da GP-100 '
            f'(GP-100 Edits: export single ou "all")?'
        ) from exc
    except OSError as exc:
        raise FormatoPrstInvalido(f'{path}: não foi possível ler ({exc})') from exc

    info_node = root.find('preset_info')
    if info_node is None:
        raise FormatoPrstInvalido(
            f'{path}: sem <preset_info> — não é um `.prst` da GP-100 '
            f'(esperado XML do formato single ou "all").'
        )
    info = dict(info_node.attrib)
    # <ppIRInfo> existe só no export "all" — o formato single fw 2.1 (o que este
    # projeto gera) não o tem. Sem o guarda, `for ir in None` estourava TypeError
    # nos patches da própria biblioteca.
    ir_node = root.find('ppIRInfo')
    irs = [dict(ir.attrib) for ir in ir_node] if ir_node is not None else []
    patches: list[dict[str, Any]] = []
    for p in root.findall('presets'):
        effects: list[dict[str, Any]] = []
        for e in p.findall('Effect'):
            attrib = e.attrib
            params: list[str | None] = []
            for i in range(15):
                v = attrib.get(f'params_{i}')
                params.append(v if v is not None else None)
            effects.append(
                {
                    'module': attrib.get('effectModuleName'),
                    # 'COMP  ' vem com espaços no export de fábrica — normaliza
                    'name': (attrib.get('effectName') or '').strip(),
                    'code': attrib.get('effectCode'),
                    'state': attrib.get('effectState'),
                    'x': attrib.get('x'),
                    'y': attrib.get('y'),
                    'params': params,
                }
            )
        patches.append(
            {
                'name': p.attrib.get('ppName'),
                'id': p.attrib.get('ppID'),
                'type': p.attrib.get('ppTypeName'),
                'type_code': p.attrib.get('ppType'),
                'bpm': p.attrib.get('ppBPM'),
                'volume': p.attrib.get('ppVolume'),
                'ir_num': p.attrib.get('ppIRNum'),
                'bank': p.attrib.get('ppBank'),
                'effects': effects,
            }
        )
    return info, irs, patches


def analyze(
    patches: list[dict[str, Any]],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[tuple[str, str], list[dict[str, set[int]]]]]:
    """Agrega estatísticas empíricas dos patches parseados.

    Devolve (models, param_stats):
      models      — {(modulo, modelo): {codes, count, x}} — quantos presets usam
                    o modelo, quais effectCode e posições de cadeia (x) assumiu.
      param_stats — {(modulo, modelo): [{valor: ...} x 15]} — conjunto de valores
                    distintos observados em cada params_i (base dos ranges reais).
    """
    models: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {'codes': set(), 'count': 0, 'x': set()}
    )
    param_stats: dict[tuple[str, str], list[dict[str, set[int]]]] = defaultdict(
        lambda: [defaultdict(set) for _ in range(15)]
    )
    for p in patches:
        for e in p['effects']:
            key = (e['module'], e['name'])
            m = models[key]
            m['codes'].add(e['code'])
            m['count'] += 1
            if e['x'] is not None:
                m['x'].add(e['x'])
            for i, v in enumerate(e['params']):
                if v is None:
                    continue
                valores = param_stats[key][i]
                valores.setdefault(str(v), set()).add(0)
    return dict(models), dict(param_stats)


def fmt_stat(sets_by_idx: list[dict[str, set[int]]]) -> str:
    """Formata as estatísticas de params de um modelo (saída de analyze).

    Para cada params_i observado imprime uma linha: valor fixo, faixa min/max
    com contagem de valores distintos, ou a lista de valores quando não numéricos.
    """
    lines = []
    for i in range(15):
        vals = set(sets_by_idx[i].keys())
        if not vals:
            continue
        nums = []
        for v in vals:
            # Valor não numérico (ex.: 'Sync', 'OFF') não é erro: o parâmetro
            # aceita não-números e eles ficam fora do min/max.
            with contextlib.suppress(ValueError):
                nums.append(float(v))
        if len(vals) == 1:
            lines.append(f'  p{i}: fixo={next(iter(vals))}')
        elif nums:
            lines.append(f'  p{i}: min={min(nums):g} max={max(nums):g} distintos={len(vals)}')
        else:
            lines.append(f'  p{i}: valores={sorted(vals)[:8]}')
    return '\n'.join(lines)
