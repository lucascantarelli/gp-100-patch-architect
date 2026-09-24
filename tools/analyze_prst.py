#!/usr/bin/env python3
"""analyze_prst.py — shim de CLI do leitor `.prst` (issue #29).

O parse e as estatísticas vivem em
`src/gp100_architect/infrastructure/prst/reader.py` (biblioteca pura, parse
defensivo com `FormatoPrstInvalido`); aqui fica só a cara de terminal:
resolver argumentos, imprimir o relatório e, com `--json`, salvar o dump.

Uso:
    python tools/analyze_prst.py <arquivo>.prst            # resumo completo
    python tools/analyze_prst.py <arquivo>.prst --json out # dump JSON
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.domain.errors import Gp100Error  # noqa: E402
from gp100_architect.infrastructure.prst.reader import analyze, fmt_stat, parse  # noqa: E402

ORDEM_CADEIA = ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']


def main() -> None:
    """Imprime o relatório completo do .prst e, com --json <arquivo>, salva o dump."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    info, irs, patches = parse(path)
    models, param_stats = analyze(patches)

    print(f"== preset_info: software={info.get('software')} firmware={info.get('firmware')} "
          f"product={info.get('product')} count={info.get('count')}")
    print(f'== User IRs: {len(irs)} slots')

    by_module: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for (module, name), data in sorted(models.items()):
        by_module[module].append((name, data))
    for module in ORDEM_CADEIA:
        print(f'\n=== {module} ({len(by_module[module])} modelos) ===')
        for name, data in by_module[module]:
            codes = ','.join(sorted(data['codes']))
            print(f'  {name:24s} code={codes:12s} usado_em={data["count"]:3d} '
                  f'x={sorted(data["x"])}')
            print(fmt_stat(param_stats[(module, name)]))

    print(f'\n=== CATALOGO ({len(patches)} patches) ===')
    for p in patches:
        chain = ' '.join(f"{e['module']}:{e['name']}({e['state']})" for e in p['effects'])
        print(f'  #{int(p["id"]) + 1:03d} [{p["type"]}] {p["name"]} bpm={p["bpm"]} '
              f'vol={p["volume"]} ir={p["ir_num"]}\n      {chain}')

    if '--json' in sys.argv:
        out = {
            'info': info,
            'user_irs': irs,
            'patches': patches,
        }
        outpath = sys.argv[sys.argv.index('--json') + 1]
        with Path(outpath).open('w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f'\nJSON salvo em {outpath}')


if __name__ == '__main__':
    try:
        main()
    except Gp100Error as e:
        print(f'ERRO: {e}', file=sys.stderr)
        sys.exit(1)
