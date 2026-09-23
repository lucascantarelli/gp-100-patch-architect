#!/usr/bin/env python3
"""gp100.py — CLI unificada da biblioteca de patches GP-100.

Comandos:
  find <termo>        busca por música/artista/álbum/captador/camada/nome
  show <NOME>         resumo do patch (cadeia, params, momentos, IR, ajustes)
  diff <A> <B>        diff legível entre dois patches (spec módulo a módulo)
  export [--album ID | NOMES...] [--destino D] [--listar]
                      copia .prst para pasta de importação USB, em ordem de slot
  build               roda o pipeline completo (ordem do guarda de sincronia)
  verify              roda a suíte de testes (a mesma do CI)

Sem dependências além da stdlib. Padrões do projeto: stdout UTF-8 e
ordenação por string (regra da ordem estável entre SOs — TestI).

Exemplos:
  python tools/gp100.py find money
  python tools/gp100.py show SMOO1SO
  python tools/gp100.py diff STH01BA STH01SO
  python tools/gp100.py export --album SN --destino C:/temp/gp100
  python tools/gp100.py build
  python tools/gp100.py verify
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if _stream.encoding and _stream.encoding.lower() != 'utf-8':
        _stream.reconfigure(encoding='utf-8')  # console Windows (cp1252)

ROOT = Path(__file__).resolve().parent.parent
DEFS = ROOT / 'tools' / 'patches-defs.json'
PATCHES = ROOT / 'patches'

# cadeia fixa da GP-100 — mesma ordem do gerador (x=0..8)
# fonte única da cadeia fixa (review doc 21, M1)
from chain import CHAIN  # noqa: E402,F401

# ordem do guarda de sincronia (TestH) — os seeders re-appendam seu álbum
PIPELINE = (
    'tools/ir_library.py',
    'tools/add_pulse_defs.py',
    'tools/add_wishkah_defs.py',
    'tools/add_santana_defs.py',
    'tools/add_momentos.py',
    'tools/build_song_patches.py',
    'tools/gen_indexes.py',
)

# nomes oficiais de parâmetro — reaproveitados do construtor (sem duplicar fonte)
try:
    sys.path.insert(0, str(ROOT / 'tools'))
    from build_song_patches import PARAM_NAMES  # noqa: E402
except Exception:  # pragma: no cover — fallback: a CLI ainda funciona sem rótulos
    PARAM_NAMES = {}


# ---------------------------------------------------------------- dados ----

def carregar_defs():
    """Lê o defs via validação acionável — a CLI não exibe dados de defs quebrado
    (review doc 21, M2); o erro sai com caminho JSON e correção sugerida."""
    from defs_schema import carregar_e_validar
    return carregar_e_validar(DEFS)


def song_pasta(song):
    return song.get('pasta') or song['song']


def song_display(song):
    return song.get('display') or song['song']


def slots(defs):
    """{'NOME': 'U01'} — mesma passada de gen_indexes.slot_map (ordem do defs)."""
    mapa, n = {}, 0
    for song in defs['songs']:
        for patch in song['patches']:
            n += 1
            mapa[patch['nome']] = f"U{n:02d}"
    return mapa


def iter_patches(defs):
    """(idAlbum, album, song, patch) na ordem do defs — estável entre SOs."""
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]
        for patch in song['patches']:
            yield song['idAlbum'], album, song, patch


def pasta_patch(album, song, patch):
    return PATCHES / album['pasta'] / song_pasta(song) / patch['nome']


def achar_patch(defs, nome):
    """Localiza patch por nome (case-insensitive); erro acionável se ausente."""
    alvo = nome.strip().upper()
    for idalb, album, song, patch in iter_patches(defs):
        if patch['nome'].upper() == alvo:
            return idalb, album, song, patch
    raise SystemExit(f"patch '{nome}' não encontrado — use: python tools/gp100.py find {nome[:4].lower()}")


def ir_recomendada(defs, patch):
    """Texto da recomendação de IR a partir do CAB do spec + mapa ir_local."""
    cab = patch['spec']['modules'].get('CAB', {}).get('name', '—')
    local = defs.get('ir_local', {}).get(cab)
    if local:
        return f"fábrica `{cab}` · banco local: {local['captura']} → {local['slot']}"
    return f"fábrica `{cab}` (sem captura local)"


def rotulo_param(mod, modelo, idx):
    nomes = PARAM_NAMES.get((mod, modelo), [])
    return nomes[idx] if idx < len(nomes) else f"param_{idx}"


def linha_cadeia(spec):
    partes = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m:
            continue
        bola = '🔴' if m.get('on') else '⚪'
        partes.append(f"{bola}{mod}:{m['name']}")
    return ' → '.join(partes)


# --------------------------------------------------------------- find -----

def cmd_find(args, defs):
    termo = args.termo.lower()
    smap = slots(defs)
    atual, achados = None, 0
    for idalb, album, song, patch in iter_patches(defs):
        doc = patch.get('doc', {})
        palheiro = ' '.join([
            song['song'], song.get('display', ''),
            album.get('banda', ''), album.get('album', ''), album.get('display', ''),
            patch['nome'], patch.get('camada', ''),
            doc.get('guitarra', {}).get('seletorCurto', ''),
        ]).lower()
        if termo not in palheiro:
            continue
        if idalb != atual:
            atual = idalb
            print(f"\n{album['banda']} — {album.get('display') or album['album']}")
        captador = doc.get('guitarra', {}).get('seletorCurto', '—')
        print(f"  {smap[patch['nome']]}  {patch['nome']:<9} {song_display(song):<40} "
              f"{patch.get('camada', ''):<22} captador: {captador}")
        print(f"           {pasta_patch(album, song, patch).with_suffix('.prst')}")
        achados += 1
    print(f"\n{achados} patch(es) para '{args.termo}'" if achados
          else f"nada encontrado para '{args.termo}' — tente música, banda, álbum, captador (bridge/neck) ou nome")
    return 0 if achados else 1


# ---------------------------------------------------------------- show ----

def cmd_show(args, defs):
    idalb, album, song, patch = achar_patch(defs, args.nome)
    smap = slots(defs)
    spec, doc = patch['spec'], patch['doc']
    nome = patch['nome']

    print(f"\n🎛️  {nome} ({smap[nome]}) — {song_display(song)} · "
          f"{album['banda']} ({album['ano']})")
    print(f"   {patch.get('camada', '')}")
    guit = doc.get('guitarra', {})
    print(f"   🎸 Captador: {guit.get('seletorCurto', '—')} · "
          f"Receita: {guit.get('receita', '—')}")
    print(f"\n   Cadeia: {linha_cadeia(spec)}")

    print("\n   Parâmetros (módulos ligados):")
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or not m.get('on') or not m.get('params'):
            continue
        pares = ', '.join(
            f"{rotulo_param(mod, m['name'], int(k))}={v}"
            for k, v in sorted(m['params'].items(), key=lambda i: int(i[0])))
        print(f"     {mod:<4} {m['name']}: {pares}")

    momentos = doc.get('momentos', [])
    if momentos:
        print(f"\n   Momentos de toggle ({len(momentos)}):")
        for mom in momentos:
            mods = ', '.join(f"{a}→{b}" for a, b in mom.get('mods', []))
            print(f"     • {mom['nome']} [{mods}]: {mom['quando']}")

    ajustes = doc.get('ajustes', [])
    if ajustes:
        print("\n   Ajustes finos deste patch:")
        for a in ajustes:
            print(f"     • {a}")

    print(f"\n   📡 IR: {ir_recomendada(defs, patch)}")
    pasta = pasta_patch(album, song, patch)
    print(f"   📁 {pasta / nome}.prst")
    print(f"   📄 {pasta / 'patch.md'}")
    return 0


# ---------------------------------------------------------------- diff ----

def cmd_diff(args, defs):
    _, _, _, pa = achar_patch(defs, args.a)
    _, _, _, pb = achar_patch(defs, args.b)
    sa, sb = pa['spec'], pb['spec']

    print(f"\ndiff {pa['nome']} → {pb['nome']}\n")
    for k in ('type', 'bpm', 'volume'):
        va, vb = sa.get(k), sb.get(k)
        marca = ' ' if va == vb else '±'
        print(f"  {marca} {k}: {va} → {vb}")
    print(f"    ir_slot: {sa.get('ir_slot')} → {sb.get('ir_slot')}")

    for mod in CHAIN:
        ma, mb = sa['modules'].get(mod, {}), sb['modules'].get(mod, {})
        if not ma and not mb:
            continue
        na, nb = ma.get('name'), mb.get('name')
        if na != nb:
            print(f"  ± {mod}: {na} → {nb}")
            continue
        difs = []
        ea, eb = ('ON' if ma.get('on') else 'OFF'), ('ON' if mb.get('on') else 'OFF')
        if ea != eb:
            difs.append(f"estado {ea}→{eb}")
        mp, mbp = ma.get('params', {}), mb.get('params', {})
        chaves = sorted(set(mp) | set(mbp),
                        key=lambda x: int(x) if str(x).isdigit() else 99)
        for k in chaves:
            va, vb = mp.get(k), mbp.get(k)
            if va != vb:
                difs.append(f"{rotulo_param(mod, na, int(k))} {va}→{vb}")
        if difs:
            print(f"    {mod} {na}: " + ' · '.join(difs))

    da, db = pa['doc'], pb['doc']
    if da.get('guitarra', {}).get('receita') != db.get('guitarra', {}).get('receita'):
        print(f"  ± guitarra: {da['guitarra'].get('receita')} → {db['guitarra'].get('receita')}")
    print(f"\n  momentos: {len(da.get('momentos', []))} → {len(db.get('momentos', []))} · "
          f"ajustes: {len(da.get('ajustes', []))} → {len(db.get('ajustes', []))}")
    return 0


# -------------------------------------------------------------- export ----

def cmd_export(args, defs):
    smap = slots(defs)
    if args.album:
        if args.album not in defs['albums']:
            validos = ', '.join(defs['albums'])
            raise SystemExit(f"álbum '{args.album}' inválido — válidos: {validos}")
        selecao = [(i, a, s, p) for i, a, s, p in iter_patches(defs) if i == args.album]
    elif args.nomes:
        selecao = [achar_patch(defs, n) for n in args.nomes]
    else:
        selecao = list(iter_patches(defs))
    selecao.sort(key=lambda t: smap[t[3]['nome']])  # ordem de slot (string)

    destino = Path(args.destino) if args.destino else ROOT / 'dist' / 'importacao-gp100'
    if args.listar:
        for idalb, album, song, patch in selecao:
            print(f"  {smap[patch['nome']]}  {patch['nome']:<9} {song_display(song)}")
        print(f"\n{len(selecao)} arquivo(s) — destino seria: {destino}")
        return 0
    destino.mkdir(parents=True, exist_ok=True)
    for idalb, album, song, patch in selecao:
        src = pasta_patch(album, song, patch).with_suffix('.prst')
        dst = destino / f"{smap[patch['nome']]}-{patch['nome']}.prst"
        shutil.copy2(src, dst)
    print(f"✅ {len(selecao)} .prst copiado(s) para {destino} (prefixo = slot, "
          f"ordem pronta para importar)")
    return 0


# -------------------------------------------------------- build/verify ----

def _rodar(passos, titulo):
    print(f"\n▶ {titulo}")
    for passo in passos:
        print(f"  $ python {passo}")
        r = subprocess.run([sys.executable, str(ROOT / passo)], cwd=ROOT)
        if r.returncode != 0:
            print(f"\n✗ falhou em {passo} — corrija e rode de novo")
            return r.returncode
    print(f"\n✅ {titulo} concluído")
    return 0


def cmd_build(args, defs):
    return _rodar(PIPELINE, 'pipeline completo (ordem do guarda de sincronia)')


def cmd_verify(args, defs):
    print("\n▶ suíte de testes (a mesma do CI)")
    r = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests'],
                       cwd=ROOT)
    return r.returncode


# ---------------------------------------------------------------- main ----

def main(argv=None):
    p = argparse.ArgumentParser(prog='gp100.py',
                                description='CLI da biblioteca de patches GP-100')
    sub = p.add_subparsers(dest='cmd', required=True)

    f = sub.add_parser('find', help='busca patch por música/artista/álbum/captador')
    f.add_argument('termo')
    f.set_defaults(func=cmd_find)

    s = sub.add_parser('show', help='resumo completo de um patch')
    s.add_argument('nome')
    s.set_defaults(func=cmd_show)

    d = sub.add_parser('diff', help='diff legível entre dois patches')
    d.add_argument('a')
    d.add_argument('b')
    d.set_defaults(func=cmd_diff)

    e = sub.add_parser('export', help='copia .prst para pasta de importação USB')
    e.add_argument('nomes', nargs='*', help='nomes de patch (opcional)')
    e.add_argument('--album', help='exporta um álbum inteiro (id: AR/ZP/PMH/PL/WM/SN)')
    e.add_argument('--destino', help='pasta destino (default: dist/importacao-gp100)')
    e.add_argument('--listar', action='store_true', help='só lista, não copia')
    e.set_defaults(func=cmd_export)

    b = sub.add_parser('build', help='roda o pipeline completo')
    b.set_defaults(func=cmd_build)

    v = sub.add_parser('verify', help='roda a suíte de testes')
    v.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    defs = carregar_defs()
    return args.func(args, defs)


if __name__ == '__main__':
    sys.exit(main())
