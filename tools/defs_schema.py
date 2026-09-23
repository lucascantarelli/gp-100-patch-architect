#!/usr/bin/env python3
"""defs_schema.py — validação acionável do patches-defs.json ANTES do build.

Roda embutida no `build_song_patches` (valida ao carregar) e isolada via
CLI para diagnóstico:

    python tools/defs_schema.py            # valida e sai 0/1 com relatório

Cada erro aponta o CAMINHO JSON exato e COMO corrigir — fim do KeyError no
meio do build. Stdlib pura; não escreve nada.

Também define a política de runtime do projeto: **Python 3.14 apenas**.
O `exigir_python_314()` é chamado nos entry points e o CI roda em 3.14
(setup-python em ci/security/release.yml).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFS = ROOT / 'tools' / 'patches-defs.json'

PY_OK = (3, 14)
if sys.version_info[:2] < PY_OK:
    raise SystemExit(
        f"Este projeto exige Python {'.'.join(map(str, PY_OK))} — "
        f"encontrado {sys.version.split()[0]}. Atualize o interpretador "
        f"(o CI roda em 3.14; veja .github/workflows/ci.yml).")

# nomes oficiais de parâmetro — fonte única em param_names.py (sem ciclo:
# build_song_patches também importa daqui/da mesma fonte)
sys.path.insert(0, str(Path(__file__).parent))
from param_names import PARAM_NAMES  # noqa: E402

CAMS = {'BA', 'SO', 'RI', 'CL', 'FL', 'AR', 'AC', 'VO', 'SL', 'AM', 'EC', 'JM', 'FZ', 'IN', 'S2', 'VOX'}  # documental

# fonte única da cadeia fixa (review doc 21, M1)
from chain import CHAIN  # noqa: E402,F401


class Erros:
    """Coletor de erros com caminho JSON e correção sugerida."""

    def __init__(self):
        self.itens: list[str] = []

    def add(self, caminho: str, problema: str, correcao: str):
        self.itens.append(f"  ✗ {caminho}: {problema}\n    → {correcao}")

    def ok(self) -> bool:
        return not self.itens

    def relatorio(self) -> str:
        return (f"\n❌ {len(self.itens)} problema(s) no patches-defs.json "
                f"(fonte única — corrija nele, nunca no arquivo gerado):\n\n"
                + "\n".join(self.itens) + "\n")


def _e_num(e):
    return isinstance(e, (int, float)) and not isinstance(e, bool)


def validar(defs: dict) -> Erros:
    er = Erros()
    albums = defs.get('albums')

    # ── topo ────────────────────────────────────────────────────────────
    if not isinstance(albums, dict) or not albums:
        er.add('albums', 'ausente ou não é objeto',
               "declare albums: {'AR': {banda, album, ano, display, pasta, rig}}")
    if not isinstance(defs.get('songs'), list) or not defs['songs']:
        er.add('songs', 'ausente ou não é lista', 'declare songs: [{id, song, idAlbum, bpm, resumo, referencias, patches}]')
    if not isinstance(defs.get('ir_local'), dict):
        er.add('ir_local', 'ausente ou não é objeto',
               "declare ir_local: {'<CAB>': {captura, slot}} — mesmo sem capturas, use {}")

    # ── albums ──────────────────────────────────────────────────────────
    if isinstance(albums, dict):
        for idalb, alb in albums.items():
            base = f'albums.{idalb}'
            for campo in ('banda', 'album', 'ano', 'pasta', 'rig'):
                if campo not in alb:
                    er.add(f'{base}.{campo}', 'campo obrigatório ausente',
                           f'acrescente "{campo}" ao álbum (rig = dossiê com fontes)')
            ano = alb.get('ano')
            if ano is not None and not isinstance(ano, int):
                er.add(f'{base}.ano', f'deve ser int, veio {type(ano).__name__}', 'use o ano do lançamento')

    # ── songs / patches ─────────────────────────────────────────────────
    ids_songs, nomes = set(), set()
    for i, song in enumerate(defs.get('songs', [])):
        base = f'songs[{i}]'
        sid, nome_song = song.get('id'), song.get('song')
        if not sid:
            er.add(f'{base}.id', 'obrigatório', 'use o padrão AAZZNN (ex.: SMOO1)')
        elif sid in ids_songs:
            er.add(f'{base}.id', f"duplicado ('{sid}')", 'ids de música têm de ser únicos')
        ids_songs.add(sid)

        if song.get('idAlbum') not in (albums or {}):
            er.add(f'{base}.idAlbum', f"'{song.get('idAlbum')}' não existe em albums",
                   f"ids válidos: {', '.join(albums or {})}")
        bpm = song.get('bpm')
        if not _e_num(bpm) or not 30 <= bpm <= 300:
            er.add(f'{base}.bpm', f'fora do range 30–300 ({bpm})', 'confira o BPM real da faixa')

        patches = song.get('patches', [])
        if not patches:
            er.add(f'{base}.patches', 'música sem patch nenhum',
                   'toda música do defs precisa de ao menos 1 patch (ou saia do defs)')
        for j, patch in enumerate(patches):
            pb = f'{base}.patches[{j}]'
            nome = patch.get('nome')
            if not nome:
                er.add(f'{pb}.nome', 'obrigatório', 'MUSICA(≤4)+NN+CAMADA(2), ex.: SMOO1SO')
                continue
            if nome in nomes:
                er.add(f'{pb}.nome', f"duplicado ('{nome}')", 'nomes de painel têm de ser únicos')
            nomes.add(nome)
            if len(nome) > 12:
                er.add(f'{pb}.nome', f"'{nome}' tem {len(nome)} chars",
                       'máx. 12 (limite do painel da GP-100) — renomeie')
            if not patch.get('camada'):
                er.add(f'{pb}.camada', 'obrigatória (aparece na doc e nos índices)',
                       'ex.: "Base", "Solo", "Riff"')
            if not isinstance(patch.get('spec'), dict):
                er.add(f'{pb}.spec', 'obrigatório', 'estrutura documentada no docstring de generate_prst.py')
                continue
            _validar_spec(patch['spec'], f'{pb}.spec', er)
            if not isinstance(patch.get('doc'), dict):
                er.add(f'{pb}.doc', 'obrigatório', 'guitarra/comoTocar/teste/ajustes/evite/irNota')
                continue
            _validar_doc(patch['doc'], f'{pb}.doc', er)

    # ── ir_local ↔ CAB usado ────────────────────────────────────────────
    cabs = {p['spec']['modules'].get('CAB', {}).get('name')
            for s in defs.get('songs', []) for p in s.get('patches', [])
            if isinstance(p.get('spec'), dict)}
    for cab in defs.get('ir_local', {}):
        if cab not in cabs:
            er.add(f'ir_local.{cab}', 'nenhum patch usa este CAB',
                   'remova a entrada (ou o CAB saiu do defs e a captura ficou órfã)')
    return er


def _validar_spec(spec: dict, base: str, er: Erros):
    nome = spec.get('name')
    if not nome:
        er.add(f'{base}.name', 'obrigatório', 'deve ser igual ao nome do patch')
    if spec.get('type') not in {'Metal', 'World', 'Indie', 'Country', 'Rock',
                                'Funk', 'Pop', 'Blues', 'Jazz', 'Bass', 'Acoustic'}:
        er.add(f'{base}.type', f"'{spec.get('type')}' não é gênero válido",
               'use um de: Metal World Indie Country Rock Funk Pop Blues Jazz Bass Acoustic')
    modules = spec.get('modules')
    if not isinstance(modules, dict):
        er.add(f'{base}.modules', 'obrigatório', 'os 9 módulos da cadeia (ou os usados + neutros no gerador)')
        return
    for mod, m in modules.items():
        if mod not in CHAIN:
            er.add(f'{base}.modules.{mod}', 'módulo fora da cadeia fixa',
                   f'use apenas: {", ".join(CHAIN)}')
            continue
        if not m.get('name'):
            er.add(f'{base}.modules.{mod}.name', 'obrigatório',
                   'nome EXATO do catálogo fw 2.0 (reference/15) — nunca o do manual V1.8')
        nomes = PARAM_NAMES.get((mod, m.get('name')), [])
        for k, v in (m.get('params') or {}).items():
            if not str(k).isdigit() or not 0 <= int(k) <= 14:
                er.add(f'{base}.modules.{mod}.params.{k}', 'índice inválido',
                       'params_0..14 — slots internos do firmware não se setam')
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                er.add(f'{base}.modules.{mod}.params.{k}', f'valor não numérico ({v!r})',
                       'params do .prst são numéricos')
                continue
            # limite por RÓTULO oficial: Time/Pre Delay são ms; o resto é 0–100
            # (EQ admite corte negativo) — range fino por modelo em reference/15
            rotulo = nomes[int(k)] if int(k) < len(nomes) else ''
            if rotulo in ('Time', 'Pre Delay'):
                if not 0 <= v <= 1000:
                    er.add(f'{base}.modules.{mod}.params.{k}',
                           f'{rotulo}={v} ms fora de 0–1000',
                           'confira o tempo em ms (export de fábrica usa 160–620)')
            elif v < -15 or v > 100:
                er.add(f'{base}.modules.{mod}.params.{k}',
                       f'{rotulo or f"param_{k}"}={v} fora do range esperado',
                       'confira o range oficial do modelo em reference/15')
    if 'CAB' not in modules:
        er.add(f'{base}.modules.CAB', 'ausente', 'todo patch single fw 2.1 declara CAB (fábrica na política de IR)')


def _validar_doc(doc: dict, base: str, er: Erros):
    for campo in ('guitarra', 'teste', 'irNota'):
        if not doc.get(campo):
            er.add(f'{base}.{campo}', 'obrigatório', 'a doc prática-primeiro exige guitarra, teste e seção de IR')
    for k in ('ajustes', 'evite'):
        if not isinstance(doc.get(k), list):
            er.add(f'{base}.{k}', 'deve ser lista de strings', 'ex.: ["lamacento → CAB High Cut -5"]')
    for i, mom in enumerate(doc.get('momentos', [])):
        for campo in ('nome', 'mods', 'quando'):
            if campo not in mom:
                er.add(f'{base}.momentos[{i}].{campo}', 'obrigatório no momento de toggle',
                       "{'nome', 'mods': [['MOD','ON']], 'quando', 'dica?'}")
        for mod, estado in mom.get('mods', []):
            if mod not in CHAIN:
                er.add(f'{base}.momentos[{i}].mods', f'módulo {mod} fora da cadeia',
                       f'use: {", ".join(CHAIN)}')
            if estado not in ('ON', 'OFF'):
                er.add(f'{base}.momentos[{i}].mods', f"estado '{estado}' inválido", 'use ON ou OFF')
            if mod in ('AMP', 'CAB'):
                er.add(f'{base}.momentos[{i}].mods', 'toggle de AMP/CAB é proibido',
                       'nunca ligue/desligue volume e corpo em tempo real')


def carregar_e_validar(caminho: Path = DEFS) -> dict:
    """Carrega o defs validando — para usar no lugar de json.loads nos scripts.

    Levanta SystemExit com o relatório acionável se houver problema.
    """
    data = json.loads(caminho.read_text(encoding='utf-8'))
    er = validar(data)
    if not er.ok():
        raise SystemExit(er.relatorio())
    return data


def main() -> int:
    data = json.loads(DEFS.read_text(encoding='utf-8'))
    er = validar(data)
    if er.ok():
        n = len(data.get('songs', []))
        np = sum(len(s.get('patches', [])) for s in data['songs'])
        print(f"✅ patches-defs.json válido — {n} músicas, {np} patches, "
              f"{len(data.get('albums', {}))} álbuns")
        return 0
    print(er.relatorio())
    return 1


if __name__ == '__main__':
    sys.exit(main())
