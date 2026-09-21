#!/usr/bin/env python3
"""Analisa arquivos .prst da Valeton GP-100 (XML) e extrai dados oficiais.

Uso:
    python tools/analyze_prst.py <arquivo>.prst            # resumo completo
    python tools/analyze_prst.py <arquivo>.prst --json out # dump JSON

Gera:
- Lista de modelos por módulo (com effectCode)
- Estatísticas empíricas de params_0..14 por modelo (min/max/distintos)
- Catálogo dos patches (nome, gênero, BPM, IR, cadeia)

Nota: foi este script que drenou o export de fábrica do aparelho para
`tools/factory-catalog.json` (99 presets · 891 effects · 117 modelos). O
export original foi removido do repositório na limpeza — exporte a biblioteca
no GP-100 Edits se precisar regenerar o catálogo.
"""
import sys
import json
import xml.etree.ElementTree as ET
from collections import defaultdict, OrderedDict

FILLERS = {65535, 12800, 65280}  # valores de preenchimento observados nos slots não usados

def parse(path):
    """Lê um export .prst (XML) e devolve (info, irs, patches).

    info    — atributos de <preset_info> (software/firmware/product/count).
    irs     — lista de User IRs do bloco <ppIRInfo> (só existe no export "all").
    patches — cada preset com nome, gênero, bpm, volume e a lista de <Effect>
              (módulo, nome normalizado sem espaços, effectCode, estado, x/y e
              params_0..14 com None nos slots ausentes).
    """
    tree = ET.parse(path)
    root = tree.getroot()
    info = root.find('preset_info').attrib
    irs = [ir.attrib for ir in root.find('ppIRInfo')]
    patches = []
    for p in root.findall('presets'):
        effects = []
        for e in p.findall('Effect'):
            attrib = e.attrib
            params = []
            for i in range(15):
                v = attrib.get(f'params_{i}')
                params.append(v if v is not None else None)
            effects.append({
                'module': attrib.get('effectModuleName'),
                # 'COMP  ' vem com espaços no export de fábrica — normaliza
                'name': (attrib.get('effectName') or '').strip(),
                'code': attrib.get('effectCode'),
                'state': attrib.get('effectState'),
                'x': attrib.get('x'),
                'y': attrib.get('y'),
                'params': params,
            })
        patches.append({
            'name': p.attrib.get('ppName'),
            'id': p.attrib.get('ppID'),
            'type': p.attrib.get('ppTypeName'),
            'type_code': p.attrib.get('ppType'),
            'bpm': p.attrib.get('ppBPM'),
            'volume': p.attrib.get('ppVolume'),
            'ir_num': p.attrib.get('ppIRNum'),
            'bank': p.attrib.get('ppBank'),
            'effects': effects,
        })
    return info, irs, patches


def analyze(patches):
    """Agrega estatísticas empíricas dos patches parseados.

    Devolve (models, param_stats):
      models      — {(modulo, modelo): {codes, count, x}} — quantos presets usam
                    o modelo, quais effectCode e posições de cadeia (x) assumiu.
      param_stats — {(modulo, modelo): [{valor: ...} x 15]} — conjunto de valores
                    distintos observados em cada params_i (base dos ranges reais).
    """
    # modelos por módulo
    models = defaultdict(lambda: {'codes': set(), 'count': 0, 'x': set()})
    # params por (modulo, modelo)
    param_stats = defaultdict(lambda: [defaultdict(set) for _ in range(15)])
    for p in patches:
        for e in p['effects']:
            key = (e['module'], e['name'])
            m = models[key]
            m['codes'].add(e['code'])
            m['count'] += 1
            if e['x'] is not None:
                m['x'].add(e['x'])
            vals = e['params']
            for i, v in enumerate(vals):
                if v is None:
                    continue
                param_stats[key][i][v].add(0)
    return models, param_stats


def fmt_stat(sets_by_idx):
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
            try:
                nums.append(float(v))
            except ValueError:
                pass
        if len(vals) == 1:
            lines.append(f'  p{i}: fixo={next(iter(vals))}')
        elif nums:
            lines.append(f'  p{i}: min={min(nums):g} max={max(nums):g} distintos={len(vals)}')
        else:
            lines.append(f'  p{i}: valores={sorted(vals)[:8]}')
    return '\n'.join(lines)


def main():
    """Imprime o relatório completo do .prst e, com --json <arquivo>, salva o dump.

    Seções: preset_info, User IRs, modelos por módulo (com estatísticas de
    params) e catálogo de presets (cadeia completa de cada um).
    """
    path = sys.argv[1]
    info, irs, patches = parse(path)
    models, param_stats = analyze(patches)

    print(f"== preset_info: software={info.get('software')} firmware={info.get('firmware')} product={info.get('product')} count={info.get('count')}")
    print(f"== User IRs: {len(irs)} slots")

    by_module = defaultdict(list)
    for (module, name), data in sorted(models.items()):
        by_module[module].append((name, data))
    for module in ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']:
        print(f"\n=== {module} ({len(by_module[module])} modelos) ===")
        for name, data in by_module[module]:
            codes = ','.join(sorted(data['codes']))
            print(f"  {name:24s} code={codes:12s} usado_em={data['count']:3d} x={sorted(data['x'])}")
            print(fmt_stat(param_stats[(module, name)]))

    print(f"\n=== CATALOGO ({len(patches)} patches) ===")
    for p in patches:
        chain = ' '.join(f"{e['module']}:{e['name']}({e['state']})" for e in p['effects'])
        print(f"  #{int(p['id'])+1:03d} [{p['type']}] {p['name']} bpm={p['bpm']} vol={p['volume']} ir={p['ir_num']}\n      {chain}")

    if '--json' in sys.argv:
        out = {
            'info': info,
            'user_irs': irs,
            'patches': patches,
        }
        outpath = sys.argv[sys.argv.index('--json') + 1]
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"\nJSON salvo em {outpath}")


if __name__ == '__main__':
    main()
