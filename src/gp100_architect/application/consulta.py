"""Casos de uso de consulta da biblioteca — find, show, diff, export (issue #48).

Migração de `tools/gp100.py`: quem **pensa** sobre a biblioteca (buscar, montar
dossiê, comparar specs, planejar exportação) mora aqui, sem I/O de escrita e
sem impressão — a CLI (`interfaces.cli`) imprime e sai; os agentes consomem o
`--json` da CLI (shapes estáveis).

Fontes únicas: slots vêm de `biblioteca.slots` (a mesma numeração do
MAPA-DO-ALBUM e do `gen_indexes`); nomes oficiais de parâmetro vêm de
`domain.params.PARAM_NAMES` (nunca `pN` na saída); recomendação de IR vem do
`ir_local` do defs — nada duplicado aqui.

Camada: application — funções devolvem dados e erros de domínio; quem copia
arquivo para destino real é `exportar`, com destino explícito.
"""

from __future__ import annotations

import shutil
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gp100_architect.application.biblioteca import slots
from gp100_architect.application.nomes import song_display, song_pasta
from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.errors import EntradaInvalida
from gp100_architect.domain.params import PARAM_NAMES

__all__ = [
    'Achado',
    'Dossie',
    'PlanoExportacao',
    'achar_patch',
    'buscar',
    'diferencas',
    'dossie',
    'linha_cadeia',
    'planejar_exportacao',
    'rotulo_param',
]

# sufixo padrão quando o músico pede a música sem seção: o patch 'tocável'
# (riff/base/ambiente) — explicitável com MUSICA:SUFIXO ou pelo nome completo.
SUFIXOS_PADRAO = frozenset({'RI', 'RI1', 'BA', 'AM'})

# chaves de palheiro do find, na ordem em que aparecem na busca
_CAMPOS_BUSCA = (
    'song',
    'display',
    'banda',
    'album',
    'album_display',
    'nome',
    'camada',
    'seletor',
)


@dataclass(frozen=True)
class Achado:
    """Um resultado do find — o que a listagem e o `--json` expõem."""

    slot: str
    nome: str
    musica: str
    camada: str
    captador: str
    banda: str
    album: str
    pasta: str
    arquivo: str


@dataclass(frozen=True)
class Dossie:
    """O resumo completo de um patch (show) — texto e `--json` saem daqui."""

    nome: str
    slot: str
    musica: str
    banda: str
    ano: int
    camada: str
    captador: str
    receita: str
    cadeia: str
    parametros: list[tuple[str, str, str]]  # (módulo, modelo, 'rotulo=val')
    momentos: list[dict[str, Any]]
    ajustes: list[str]
    stomps: list[dict[str, Any]]
    exp1: dict[str, Any] | None
    ir: str
    pasta: str
    arquivo: str


@dataclass(frozen=True)
class PlanoExportacao:
    """A lista de cópias a fazer — executada só com destino explícito."""

    itens: list[tuple[Path, Path]]  # (origem .prst, destino <slot>-<NOME>.prst)
    destino: Path
    listar: bool


def rotulo_param(mod: str, modelo: str, idx: int) -> str:
    """Nome oficial do parâmetro (PARAM_NAMES) — nunca `pN` na saída."""
    nomes = PARAM_NAMES.get((mod, modelo), [])
    return nomes[idx] if idx < len(nomes) else f'param_{idx}'


def linha_cadeia(spec: dict[str, Any]) -> str:
    """Cadeia em 1 linha — módulos setados, na ordem fixa da GP-100."""
    partes = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m:
            continue
        bola = '●' if m.get('on') else '○'
        partes.append(f'{bola}{mod}:{m["name"]}')
    return ' → '.join(partes)


IterPatch = tuple[str, dict[str, Any], dict[str, Any], dict[str, Any]]


def _iter_patches(defs: dict[str, Any]) -> Iterator[IterPatch]:
    """`(idAlbum, album, song, patch)` na ordem do defs — estável entre SOs."""
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]
        for patch in song['patches']:
            yield song['idAlbum'], album, song, patch


def _pasta_patch(raiz: Path, album: Mapping[str, Any], song: Mapping[str, Any], nome: str) -> Path:
    return raiz / 'patches' / str(album['pasta']) / song_pasta(song) / nome


def achar_patch(
    defs: dict[str, Any], nome: str, *, raiz: Path
) -> tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], Path]:
    """Localiza patch por nome (case-insensitive) e devolve o dossiê de contexto.

    Erro de domínio com dica do `find` — nunca `SystemExit` de biblioteca.
    """
    alvo = nome.strip().upper()
    for idalb, album, song, patch in _iter_patches(defs):
        if patch['nome'].upper() == alvo:
            pasta = _pasta_patch(raiz, album, song, patch['nome'])
            return idalb, album, song, patch, pasta
    sufixos = [p['nome'][:4].lower() for _i, _a, _s, p in _iter_patches(defs)]
    primeiros = list(dict.fromkeys(sufixos))[:3]
    dica = primeiros[0] if primeiros else nome[:4].lower()
    raise EntradaInvalida(f"patch '{nome}' não encontrado — use: gp100 find {dica}")


def buscar(defs: dict[str, Any], termo: str, *, raiz: Path) -> list[Achado]:
    """Busca por música/artista/álbum/captador/camada/nome (case-insensitive)."""
    termo_ = termo.lower().strip()
    mapa = slots(defs)
    achados: list[Achado] = []
    for _idalb, album, song, patch in _iter_patches(defs):
        doc = patch.get('doc', {})
        palheiro = ' '.join(
            [
                song['song'],
                song.get('display', ''),
                album.get('banda', ''),
                album.get('album', ''),
                album.get('display', ''),
                patch['nome'],
                patch.get('camada', ''),
                doc.get('guitarra', {}).get('seletorCurto', ''),
            ]
        ).lower()
        if termo_ not in palheiro:
            continue
        pasta = _pasta_patch(raiz, album, song, patch['nome'])
        achados.append(
            Achado(
                slot=mapa[patch['nome']],
                nome=patch['nome'],
                musica=song_display(song),
                camada=patch.get('camada', ''),
                captador=doc.get('guitarra', {}).get('seletorCurto', '—'),
                banda=album['banda'],
                album=album.get('display') or album['album'],
                pasta=str(pasta),
                arquivo=str(pasta / f'{patch["nome"]}.prst'),
            )
        )
    return achados


def _ir_recomendada(defs: dict[str, Any], patch: dict[str, Any]) -> str:
    """Texto da recomendação de IR a partir do CAB do spec + mapa ir_local."""
    cab = patch['spec']['modules'].get('CAB', {}).get('name', '—')
    local = defs.get('ir_local', {}).get(cab)
    if local:
        return f'fábrica `{cab}` · banco local: {local["captura"]} → {local["slot"]}'
    return f'fábrica `{cab}` (sem captura local)'


def dossie(defs: dict[str, Any], nome: str, *, raiz: Path) -> Dossie:
    """O resumo completo de um patch — a única fonte do `show` (texto e JSON)."""
    _idalb, album, song, patch, pasta = achar_patch(defs, nome, raiz=raiz)
    mapa = slots(defs)
    spec, doc = patch['spec'], patch['doc']
    nome_patch = patch['nome']
    guit = doc.get('guitarra', {})

    parametros: list[tuple[str, str, str]] = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or not m.get('on') or not m.get('params'):
            continue
        pares = ', '.join(
            f'{rotulo_param(mod, m["name"], int(k))}={v}'
            for k, v in sorted(m['params'].items(), key=lambda i: int(i[0]))
        )
        parametros.append((mod, m['name'], pares))

    return Dossie(
        nome=nome_patch,
        slot=mapa[nome_patch],
        musica=song_display(song),
        banda=album['banda'],
        ano=album['ano'],
        camada=patch.get('camada', ''),
        captador=guit.get('seletorCurto', '—'),
        receita=guit.get('receita', '—'),
        cadeia=linha_cadeia(spec),
        parametros=parametros,
        momentos=doc.get('momentos', []),
        ajustes=doc.get('ajustes', []),
        stomps=doc.get('stomps', []),
        exp1=spec.get('exp1'),
        ir=_ir_recomendada(defs, patch),
        pasta=str(pasta),
        arquivo=str(pasta / f'{nome_patch}.prst'),
    )


def diferencas(defs: dict[str, Any], a: str, b: str, *, raiz: Path) -> dict[str, Any]:
    """Diff legível entre dois patches — estrutura pronta para texto e JSON.

    Por nome oficial de parâmetro (nunca `pN`); `±` é a marca de divergência.
    """
    _i, _al, _s, pa, _pasta_a = achar_patch(defs, a, raiz=raiz)
    _i, _al, _s, pb, _pasta_b = achar_patch(defs, b, raiz=raiz)
    sa, sb = pa['spec'], pb['spec']
    linhas: list[str] = []
    json_mods: list[dict[str, Any]] = []

    for k in ('type', 'bpm', 'volume'):
        va, vb = sa.get(k), sb.get(k)
        marca = ' ' if va == vb else '±'
        linhas.append(f'  {marca} {k}: {va} → {vb}')
    linhas.append(f'    ir_slot: {sa.get("ir_slot")} → {sb.get("ir_slot")}')

    for mod in CHAIN:
        ma, mb = sa['modules'].get(mod, {}), sb['modules'].get(mod, {})
        if not ma and not mb:
            continue
        na, nb = ma.get('name'), mb.get('name')
        if na != nb:
            linhas.append(f'  ± {mod}: {na} → {nb}')
            json_mods.append({'modulo': mod, 'modelo_a': na, 'modelo_b': nb, 'difs': []})
            continue
        difs: list[str] = []
        ea, eb = ('ON' if ma.get('on') else 'OFF'), ('ON' if mb.get('on') else 'OFF')
        if ea != eb:
            difs.append(f'estado {ea}→{eb}')
        mp, mbp = ma.get('params', {}), mb.get('params', {})
        chaves = sorted(set(mp) | set(mbp), key=lambda x: int(x) if str(x).isdigit() else 99)
        for k in chaves:
            va, vb = mp.get(k), mbp.get(k)
            if va != vb:
                difs.append(f'{rotulo_param(mod, str(na), int(k))} {va}→{vb}')
        if difs:
            linhas.append(f'    {mod} {na}: ' + ' · '.join(difs))
        if difs or ea != eb:
            json_mods.append({'modulo': mod, 'modelo_a': na, 'modelo_b': nb, 'difs': difs})

    da, db = pa['doc'], pb['doc']
    if da.get('guitarra', {}).get('receita') != db.get('guitarra', {}).get('receita'):
        linhas.append(
            f'  ± guitarra: {da["guitarra"].get("receita")} → {db["guitarra"].get("receita")}'
        )
    return {
        'a': pa['nome'],
        'b': pb['nome'],
        'linhas': linhas,
        'modulos': json_mods,
        'momentos': (len(da.get('momentos', [])), len(db.get('momentos', []))),
        'ajustes': (len(da.get('ajustes', [])), len(db.get('ajustes', []))),
    }


def planejar_exportacao(
    defs: dict[str, Any],
    *,
    raiz: Path,
    nomes_patch: list[str] | None = None,
    album: str | None = None,
    destino: Path | None = None,
    listar: bool = False,
) -> PlanoExportacao:
    """A lista de cópias em ordem de slot — a execução é da CLI/shim.

    Seleção: álbum inteiro (`--album`), nomes explícitos ou a biblioteca toda.
    """
    mapa = slots(defs)
    if album:
        if album not in defs['albums']:
            validos = ', '.join(defs['albums'])
            raise EntradaInvalida(f"álbum '{album}' inválido — válidos: {validos}")
        selecao = [t for t in _iter_patches(defs) if t[0] == album]
    elif nomes_patch:
        selecao = []
        for pedido in nomes_patch:
            idalb, albm, sng, ptch, _pasta = achar_patch(defs, pedido, raiz=raiz)
            selecao.append((idalb, albm, sng, ptch))
    else:
        selecao = list(_iter_patches(defs))

    items: list[tuple[Path, Path]] = []
    alvo = destino or (raiz / 'dist' / 'importacao-gp100')
    for _idalb, albm, sng, ptch in sorted(selecao, key=lambda t: mapa[t[3]['nome']]):
        nome = ptch['nome']
        origem = _pasta_patch(raiz, albm, sng, nome) / f'{nome}.prst'
        items.append((origem, alvo / f'{mapa[nome]}-{nome}.prst'))
    return PlanoExportacao(itens=items, destino=alvo, listar=listar)


def executar_exportacao(plano: PlanoExportacao) -> int:
    """Copia os `.prst` do plano para o destino (o único I/O de escrita aqui)."""
    plano.destino.mkdir(parents=True, exist_ok=True)
    for origem, destino_final in plano.itens:
        shutil.copy2(origem, destino_final)
    return len(plano.itens)
