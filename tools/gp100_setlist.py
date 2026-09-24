#!/usr/bin/env python3
"""gp100_setlist.py — cola de palco: ordem de slots que minimiza trocas.

Dado um repertório, devolve o plano de palco: em qual slot (U01…U99) está
cada patch, em que ordem pisar e o que muda na cadeia de uma música para
a outra. A ordem sugerida usa vizinho mais próximo (a menor distância de
cadeia a partir da primeira música); `--keep-order` respeita a ordem dada.

Uso:
  python tools/gp100_setlist.py "Come Together" "Something" "Money"
  python tools/gp100_setlist.py Smooth "Come Together:RIF"     # seção à parte
  python tools/gp100_setlist.py --list                          # catálogo
  python tools/gp100_setlist.py ... --json                      # saída máquina
  python tools/gp100_setlist.py ... --out cola.md               # grava arquivo

Fontes (nenhuma duplicada aqui):
  tools/defs/             — fragmentos por álbum (schema v2, issue #8)
  tools/gen_indexes.py    — slot_map (numeração U01… contínua, a mesma do
                            MAPA-DO-ALBUM e dos índices; nunca recalcular)
  gp100_architect.domain.setlist — assinatura, distância, otimizador e dif
                            (issue #28): as REGRAS moram no domínio
  gp100_architect.application.setlist — resolução de pedidos, catálogo e
                            relatórios (issue #49): a camada de aplicação é
                            o consumidor; a CLI oficial é `gp100 setlist`

Este arquivo vira shim: os comandos da CLI do pacote (gp100 setlist --list,
--json, --out) fazem o mesmo via `uv run gp100 setlist ...`. Aqui fica a via
argparse para compatibilidade da suíte legada até a #34; a remoção é a #33.
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
DEFS_FILE = ROOT / 'tools' / 'defs'     # schema v2 (issue #8): diretório de fragmentos
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'src'))

from defs_schema import carregar_e_validar  # noqa: E402  (põe src/ no sys.path)
from gp100_architect.domain.setlist import (  # noqa: E402
    assinatura as chave,
    dif_cadeia,
    otimizar,
    trocas_totais,
)
from gen_indexes import slot_map  # noqa: E402

# regras vivem no domínio (issue #28); o script é consumidor. O alias `chave`
# preserva a via argparse até a remoção do shim (#33) — a suíte já consome o
# pacote (tests/integration/test_setlist.py, issue #34).


class Biblioteca:
    """Índices de consulta do defs: por id de música, nome e patch."""

    def __init__(self, defs):
        self.defs = defs
        self.slots = slot_map(defs)
        self.por_id = {s['id'].upper(): s for s in defs['songs']}
        self.por_nome = {s['song'].upper(): s for s in defs['songs']}
        self.por_patch = {
            p['nome'].upper(): (s, p)
            for s in defs['songs'] for p in s['patches']
        }
        # sufixo padrão quando o músico pede a música sem seção: o patch de
        # riff/base (o 'tocável' do show) — explicitável com MUSICA:SUFIXO.
        self.padrao = {'RI', 'RI1', 'BA', 'AM'}

    def resolver(self, pedido):
        """'SMOO1' | 'smooth' | 'SMOO1SO' | 'SMOO1:SO' | 'CT01VOX' → (song, patch).

        Música sem seção usa o sufixo padrão (RI/BA/AM); se não houver, o
        primeiro patch do defs. Erros saem em SystemExit com sugestões.
        """
        p = pedido.strip()
        if not p:
            self._erro('pedido vazio')
        if ':' in p:
            base, sufixo = (x.strip() for x in p.split(':', 1))
        else:
            base, sufixo = p, None
        musica = self.por_id.get(base.upper()) or self.por_nome.get(base.upper())
        if musica is None:
            # não é música: pode ser o patch inteiro (CT01VOX)
            hit = self.por_patch.get(p.upper())
            if hit:
                return hit
            self._erro(f'"{pedido}" não é música nem patch conhecido')
        if sufixo:
            alvo = sufixo.upper()
            for patch in musica['patches']:
                if patch['sufixo'].upper() == alvo or patch['nome'].upper() == alvo:
                    return musica, patch
            self._erro(f'{musica["id"]} não tem seção "{sufixo}" '
                       f'(há: {", ".join(x["sufixo"] for x in musica["patches"])})')
        for patch in musica['patches']:
            if patch['sufixo'].upper() in self.padrao:
                return musica, patch
        return musica, musica['patches'][0]

    def _erro(self, msg):
        dicas = ', '.join(sorted(self.por_id)[:8])
        raise SystemExit(f'{msg}. Músicas disponíveis (ex.): {dicas}… '
                         f'use --list para o catálogo completo.')

    def catalogo(self):
        """Linhas do --list: (id, música, álbum, patches com sufixo)."""
        albums = self.defs['albums']
        linhas = []
        for s in self.defs['songs']:
            a = albums[s['idAlbum']]
            rotulo = a['album'] if isinstance(a, dict) else a
            patches = ', '.join(f"{p['nome']} ({p['sufixo']})" for p in s['patches'])
            linhas.append((s['id'], s['song'], rotulo, patches))
        return linhas


# ── relatórios (formatação é do script; as regras, do domínio) ─────────────

def plano_json(plano, total_trocas, slots):
    itens = []
    for pos, (musica, patch) in enumerate(plano):
        anterior = plano[pos - 1][1] if pos else None
        itens.append({
            'ordem': pos + 1,
            'slot': slots[patch['nome']],
            'musica': musica['song'],
            'patch': patch['nome'],
            'trocas': [] if anterior is None else dif_cadeia(anterior, patch),
        })
    return {'trocas_totais': total_trocas, 'itens': itens}


def plano_markdown(plano, total_trocas, slots, titulo='Cola de palco'):
    linhas = [
        f'# 🎤 {titulo}', '',
        f'**{len(plano)} músicas · {total_trocas} troca(s) de módulo no total** — '
        'slots da numeração da biblioteca (U01…), a mesma do MAPA-DO-ALBUM.', '',
        '| # | Slot | Música | Patch | Trocas ao entrar |',
        '|---|---|---|---|---|',
    ]
    for pos, (musica, patch) in enumerate(plano):
        anterior = plano[pos - 1][1] if pos else None
        slot = slots[patch['nome']]
        emoji = patch.get('emoji', '') or ''
        trocas = '— (primeira)' if anterior is None else (
            ', '.join(dif_cadeia(anterior, patch)) or 'nenhuma')
        linhas.append(
            f'| {pos + 1} | **{slot}** | {emoji} {musica["song"]} '
            f'| `{patch["nome"]}` | {trocas} |')
    linhas += ['', '> Gerado por `tools/gp100_setlist.py` — reordene e rode de novo '
               'se a sequência do show mandar mais que a economia de trocas.', '']
    return '\n'.join(linhas)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    ap = argparse.ArgumentParser(
        description='Cola de palco GP-100: ordem de slots que minimiza trocas.')
    ap.add_argument('musicas', nargs='*',
                    help='Músicas (nome ou id) e/ou seções (MUSICA:SUFIXO ou nome do patch)')
    ap.add_argument('--patch', action='append', default=[],
                    help='Força o patch de uma música (repita a flag; aceita SMOO1:SO)')
    ap.add_argument('--keep-order', action='store_true',
                    help='Respeita a ordem dada (não otimiza por trocas)')
    ap.add_argument('--title', default='Cola de palco', help='Título do relatório')
    ap.add_argument('--list', action='store_true', help='Lista músicas e patches')
    ap.add_argument('--json', action='store_true', help='Saída em JSON')
    ap.add_argument('--out', metavar='ARQUIVO', help='Grava o relatório em arquivo')
    args = ap.parse_args(argv)

    defs = carregar_e_validar(DEFS_FILE)
    lib = Biblioteca(defs)

    if args.list:
        for sid, musica, album, patches in lib.catalogo():
            print(f'{sid:9} | {musica:38} | {album:32} | {patches}')
        return 0
    if not args.musicas:
        ap.error('informe o repertório (ex.: "Come Together" "Money") ou --list')

    # resolve pedidos; --patch MUSICA:SUFIXO sobrescreve a seção da música
    forcar = {}
    for p in args.patch:
        musica, patch = lib.resolver(p)
        forcar[musica['id'].upper()] = patch
    itens = []
    vistos = set()
    for pedido in args.musicas:
        musica, patch = lib.resolver(pedido)
        chave_m = musica['id'].upper()
        if chave_m in forcar:
            patch = forcar.pop(chave_m)
        if chave_m in vistos:
            raise SystemExit(f'música repetida no repertório: {musica["song"]}')
        vistos.add(chave_m)
        itens.append((musica, patch))
    if forcar:
        raise SystemExit('--patch para música fora do repertório: '
                         + ', '.join(sorted(forcar)))

    plano = itens if args.keep_order else otimizar(itens)
    total = trocas_totais(plano)

    if args.json:
        saida = json.dumps(plano_json(plano, total, lib.slots),
                           ensure_ascii=False, indent=1)
    else:
        saida = plano_markdown(plano, total, lib.slots, args.title)

    if args.out:
        destino = Path(args.out)
        destino.write_text(saida + '\n', encoding='utf-8')
        print(f'✅ {destino}')
    else:
        print(saida)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
