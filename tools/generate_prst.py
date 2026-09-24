#!/usr/bin/env python3
"""generate_prst.py — shim de CLI do codec `.prst` (issue #29).

O codec vive em `src/gp100_architect/infrastructure/prst/codec.py` (biblioteca
tipada, sem SystemExit, reusável pela CLI `gp100` e pela UI futura); este
arquivo fica só com a cara de terminal: ler argumentos, escrever o arquivo e
imprimir. O formato single fw 2.1 e as regras do XML são contrato do codec —
o docstring completo da migração está lá.

Uso:
    python tools/generate_prst.py patch.json saida.prst
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.domain.errors import Gp100Error  # noqa: E402
from gp100_architect.infrastructure.prst.codec import (  # noqa: E402
    BASE_IR_NUM,
    BUILD_TIME_PADRAO,
    CHAIN_POS,
    EXPORT_ORDER,
    EXP_DUMMY_CODE,
    FACTORY_IR,
    gerar_xml,
    is_junk,
    load_templates,
    real_param_count,
)

# reexports do pacote para consumidores que ainda importam por `tools/` —
# a remoção é a #33 (a suíte já consome o pacote: issue #34)
__all__ = ['CHAIN_POS', 'EXPORT_ORDER', 'EXP_DUMMY_CODE', 'FACTORY_IR',
           'gerar_xml', 'is_junk', 'load_templates', 'real_param_count']


def main() -> None:
    """Lê spec+saida, gera via codec e escreve o arquivo (único I/O aqui)."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_path = Path(sys.argv[2])
    spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    templates = load_templates()

    build_time = os.environ.get('GP100_BUILD_TIME', BUILD_TIME_PADRAO)
    xml = gerar_xml(spec, templates, build_time=build_time)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(xml)

    print(f'OK: {out_path}')
    print('Formato single-patch (firmware 2.1). Importe no GP-100 Edits ou direto na pedaleira.')
    ir_cab_slot = spec.get('ir_cab_user_slot')
    if ir_cab_slot is not None:
        print(f'EXPERIMENTAL: CAB = User IR slot {int(ir_cab_slot) + 1} '
              f'(code {BASE_IR_NUM + int(ir_cab_slot)}).')
        print('Carregue o .wav no slot antes de importar e teste na pedaleira.')


if __name__ == '__main__':
    try:
        main()
    except Gp100Error as e:
        # erro previsto: acionável, sem traceback cru (regra do projeto)
        print(f'ERRO: {e}', file=sys.stderr)
        sys.exit(1)
