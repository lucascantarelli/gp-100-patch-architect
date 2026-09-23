#!/usr/bin/env python3
"""ir_library.py — shim de CLI da indexação de IRs (issue #30).

A implementação vive em `src/gp100_architect/application/ir_library.py`
(manifesto, catálogo legível e guarda de encolhimento) + `infrastructure.wav`
(leitura do cabeçalho) + `infrastructure.escrita`. Este arquivo varre
`impulse_responses/`, avisa/reprova e grava as duas saídas.

Uso:  python tools/ir_library.py            # regenera tools/ir-library.json + reference/16-ir-library.md
      python tools/ir_library.py --force    # aceita encolher o catálogo (pack removido de propósito)

O banco em si (`impulse_responses/**`) NÃO é versionado — as licenças dos packs
são de terceiros. Só o `impulse_responses/README.md` e os dois catálogos gerados
entram no git. Sem o banco este script avisa e sai com 0, sem zerar os catálogos.

Por que este script existe mesmo com o banco fora do git: o catálogo que ele gera
é INSUMO da documentação — `build_song_patches` cita o arquivo exato do banco
na seção 📡 de cada `patch.md` e `gen_indexes` marca 📁 no mapa do álbum.
Versionar o banco é problema de licença; gerar o catálogo é o que mantém as docs
corretas.

Compatibilidade GP-100 (por WAV): mono, 24 bits, 44.1 kHz → OK direto; qualquer
desvio → CONVERTER. Limite do device: 1024 samples (~23 ms @ 44.1 kHz).

Reexporta `wav_order`/`wav_info`/`cab_of`/`encolhimento_do_catalogo` para a
suíte legada até a migração (issue #34).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.application import ir_library as app  # noqa: E402
from gp100_architect.infrastructure.escrita import escrever_texto  # noqa: E402
from gp100_architect.infrastructure.wav import inspecionar as wav_info  # noqa: E402

IR_DIR = ROOT / 'impulse_responses'
OUT_JSON = ROOT / 'tools' / 'ir-library.json'
OUT_MD = ROOT / 'reference' / '16-ir-library.md'

# reexportados para a suíte legada (nomes históricos)
cab_of = app.cab_of                    # noqa: F401
encolhimento_do_catalogo = app.encolhimento  # noqa: F401


def wav_order(path: Path) -> str:
    """Compatibilidade da suíte legada (a raiz do banco vem do módulo)."""
    return app.wav_order(path, IR_DIR)


def main() -> int:
    """Varre impulse_responses/, indexa os packs e regenera as duas saídas.

    Banco ausente ou vazio (o caso do CI: só `impulse_responses/README.md` é
    versionado) → **não** sobrescreve os catálogos commitados com um manifesto
    vazio, apenas avisa e sai com 0. É o que mantém o job de dados verde em um
    clone limpo, sem transformar "não baixei o pack" em build vermelho.

    Banco incompleto → reprova, a menos que venha `--force` (guarda de
    encolhimento na aplicação).
    """
    wavs = sorted(IR_DIR.rglob('*.wav'), key=wav_order) if IR_DIR.exists() else []
    if not wavs:
        print('ℹ️  Banco local de IRs ausente ou vazio — nada a indexar.')
        print('   Os catálogos commitados (tools/ir-library.json e')
        print('   reference/16-ir-library.md) ficam como estão, com a última')
        print('   indexação conhecida — os agentes continuam consultando-os.')
        print('   Para indexar: baixe o pack e extraia em impulse_responses/<Nome do Pack>/.')
        return 0

    registros = [
        {'file': app.wav_order(wav, IR_DIR), 'size_kb': round(wav.stat().st_size / 1024),
         **wav_info(wav)}
        for wav in wavs
    ]
    manifesto = app.montar_manifesto(registros)

    antigo = None
    if OUT_JSON.exists():
        try:
            antigo = json.loads(OUT_JSON.read_text(encoding='utf-8'))
        except Exception:
            antigo = None                      # catálogo ilegível: não bloqueia a rodada
    problemas = app.encolhimento(antigo or {}, manifesto)
    if problemas and '--force' not in sys.argv:
        print('❌ Esta rodada ENCOLHERIA o catálogo commitado de IRs:', file=sys.stderr)
        for p in problemas:
            print(f'   - {p}', file=sys.stderr)
        print('\n' + app.PROBLEMAS_DE_FORMATO, file=sys.stderr)
        return 1

    escrever_texto(OUT_JSON, json.dumps(manifesto, ensure_ascii=False, indent=1))
    escrever_texto(OUT_MD, app.catalogo_md(manifesto))

    total = sum(m['wavs'] for m in manifesto['packs'].values())
    print(f'✅ {total} WAVs em {len(manifesto["packs"])} pack(s) indexados.')
    for pack, mp in manifesto['packs'].items():
        print(f"  - {pack}: {mp['wavs']} WAVs · cabs: {', '.join(mp['cabs'])} · "
              f"compatível: {mp['all_compatible']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
