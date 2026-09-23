#!/usr/bin/env python3
"""migrate_defs_v2.py — migração one-shot do monólito para o schema v2 (issue #8).

    ANTES (v1)                          DEPOIS (v2)
    tools/patches-defs.json      →      tools/defs/_albums.json + <álbum>.json

O que ele faz, nesta ordem:

  1. lê o monólito `tools/patches-defs.json` (fonte da migração);
  2. valida a PRÉ-CONDIÇÃO da equivalência: as músicas têm de estar contíguas
     por álbum, na ordem declarada — senão o split mudaria a numeração dos
     slots U01…Uxx (contrato com o músico) sem mudar dado nenhum;
  3. escreve `tools/defs/_albums.json` + um fragmento por álbum
     (`<banda>-<álbum>.json`, slug determinístico), cada um com
     `{idAlbum, album, ir_local?, meta?, songs[]}`;
  4. PROVA a equivalência: consolida o que acabou de escrever (pelo loader v2)
     e compara com o monólito — `json.dumps` canônico, byte a byte;
  5. determinístico por construção: nada de timestamp, nada de filesystem
     order — rodar 2× produz os mesmos bytes (a suíte prova).

O monólito NÃO é apagado por este script: quem o remove é a migração
commitada (o PR), depois da prova. Idempotente: rodar sobre um repositório já
migrado reescreve os mesmos bytes.

Uso: python tools/migrate_defs_v2.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.infrastructure.defs import MANIFESTO, consolidar  # noqa: E402

MONOLITO = ROOT / 'tools' / 'patches-defs.json'
DEFS_DIR = ROOT / 'tools' / 'defs'

CANONICO = dict(ensure_ascii=False, indent=2, sort_keys=False)  # ordena listas: NUNCA


def pre_condicao(dados: dict) -> None:
    """Músicas contíguas por álbum, na ordem das chaves — senão os slots mudam."""
    seq = [s['idAlbum'] for s in dados['songs']]
    blocos = [seq[0]] + [a for i, a in enumerate(seq[1:], 1) if a != seq[i - 1]]
    ordem = list(dados['albums'])
    if blocos != ordem:
        raise SystemExit(
            'FALHA: as músicas NÃO estão contíguas por álbum na ordem das chaves '
            f'(blocos: {", ".join(blocos)}; chaves: {", ".join(ordem)}). Migrar assim '
            'reordenaria as músicas e mudaria os slots U01…Uxx. Reordene o monólito '
            'ANTES de migrar (a ordem dos slots é contrato com o músico).'
        )


def migrar() -> None:
    if not MONOLITO.is_file():
        raise SystemExit(f'FALHA: {MONOLITO} não existe — nada a migrar.')
    dados = json.loads(MONOLITO.read_text(encoding='utf-8'))
    pre_condicao(dados)

    DEFS_DIR.mkdir(exist_ok=True)
    escritos: list[Path] = []
    for chave, album in dados['albums'].items():
        frag: dict = {'idAlbum': chave, 'album': album, 'songs': []}
        if chave == next(iter(dados['albums'])):
            frag['meta'] = dados.get('meta', {})
        irs = {
            c: par
            for c, par in dados.get('ir_local', {}).items()
            if c
            in {
                p['spec']['modules']['CAB']['name']
                for s in dados['songs']
                if s['idAlbum'] == chave
                for p in s['patches']
            }
        }
        if irs:
            frag['ir_local'] = irs
        frag['songs'] = [s for s in dados['songs'] if s['idAlbum'] == chave]

        # o nome do fragmento é a PRÓPRIA chave do manifesto: `_albums.json` é a
        # única fonte da ordem E do mapeamento chave→arquivo — impossível divergirem.
        alvo = DEFS_DIR / f'{chave}.json'
        alvo.write_text(json.dumps(frag, **CANONICO) + '\n', encoding='utf-8')
        escritos.append(alvo)

    manifesto = DEFS_DIR / MANIFESTO
    manifesto.write_text(json.dumps(list(dados['albums']), **CANONICO) + '\n', encoding='utf-8')

    # ---- prova de equivalência: o loader v2 devolve o monólito, byte a byte ----
    consolidado = consolidar(DEFS_DIR)
    antes = json.dumps(dados, **CANONICO)
    depois = json.dumps(consolidado, **CANONICO)
    if antes != depois:
        import difflib

        diff = '\n'.join(
            list(
                difflib.unified_diff(
                    antes.splitlines(), depois.splitlines(), 'monolito', 'consolidado', lineterm=''
                )
            )[:40]
        )
        raise SystemExit('FALHA: o consolidado DIVERGE do monólito:\n' + diff)

    n_patches = sum(len(s['patches']) for s in consolidado['songs'])
    print(f'✅ {len(escritos)} fragmentos + {MANIFESTO} escritos em tools/defs/')
    for p in escritos:
        print(f'   - {p.name}')
    print(
        f'   equivalência: {len(consolidado["songs"])} músicas · {n_patches} patches '
        f'· {len(consolidado["albums"])} álbuns — idêntico ao monólito (JSON canônico)'
    )
    print('   PRÓXIMO passo do PR: remover tools/patches-defs.json (a prova acima é a licença).')


if __name__ == '__main__':
    migrar()
