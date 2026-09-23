"""Validação do `patches-defs.json` — regras puras, sem I/O.

Cada erro aponta o **caminho JSON exato** e **como corrigir**: o objetivo é que
um defs errado falhe aqui, com uma instrução, em vez de estourar um `KeyError`
no meio do build.

O defs é a fonte única do projeto (patch, doc e índice saem dele), então esta
validação roda em toda porta de entrada: build, CLI, índices e release
(documentado no review do doc 21, achado M2).
"""

from __future__ import annotations

from typing import Any

from gp100_architect.domain.chain import CHAIN, MODULOS_PROIBIDOS_EM_MOMENTO
from gp100_architect.domain.params import ROTULOS_EM_MS, rotulo

__all__ = ['CAMS', 'Erros', 'validar']

# catálogo de camadas (sufixo do nome do painel). `VOX` é allowance histórica:
# nenhum patch atual usa, mas nomes antigos de painel seguem válidos.
CAMS: frozenset[str] = frozenset(
    {
        'BA',
        'SO',
        'RI',
        'CL',
        'FL',
        'AR',
        'AC',
        'VO',
        'SL',
        'AM',
        'EC',
        'JM',
        'FZ',
        'IN',
        'S2',
        'VOX',
    }
)

TIPOS_VALIDOS: frozenset[str] = frozenset(
    {
        'Metal',
        'World',
        'Indie',
        'Country',
        'Rock',
        'Funk',
        'Pop',
        'Blues',
        'Jazz',
        'Bass',
        'Acoustic',
    }
)

_CAMPOS_MODULO_AUSENTE = ('guitarra', 'teste', 'irNota')


class Erros:
    """Coletor de erros com caminho JSON e correção sugerida."""

    def __init__(self) -> None:
        self.itens: list[str] = []

    def add(self, caminho: str, problema: str, correcao: str) -> None:
        self.itens.append(f'  ✗ {caminho}: {problema}\n    → {correcao}')

    def ok(self) -> bool:
        """Nenhum problema encontrado."""
        return not self.itens

    def relatorio(self) -> str:
        """Relatório legível — usado pela CLI e pelo build."""
        return (
            f'\n❌ {len(self.itens)} problema(s) no patches-defs.json '
            f'(fonte única — corrija nele, nunca no arquivo gerado):\n\n'
            + '\n'.join(self.itens)
            + '\n'
        )


def _e_num(valor: object) -> bool:
    """Número de verdade — `bool` é `int` em Python e não vale como parâmetro."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def validar(defs: dict[str, Any]) -> Erros:
    """Valida o defs inteiro e devolve o coletor de erros (nunca levanta)."""
    er = Erros()
    bruto = defs.get('albums')
    albums: dict[str, Any] | None = bruto if isinstance(bruto, dict) else None

    _validar_topo(defs, albums, er)
    if albums is not None:
        _validar_albums(albums, er)
    _validar_songs(defs, albums, er)
    _validar_ir_local(defs, er)
    return er


def _validar_topo(defs: dict[str, Any], albums: dict[str, Any] | None, er: Erros) -> None:
    if not isinstance(albums, dict) or not albums:
        er.add(
            'albums',
            'ausente ou não é objeto',
            "declare albums: {'AR': {banda, album, ano, display, pasta, rig}}",
        )
    songs = defs.get('songs')
    if not isinstance(songs, list) or not songs:
        er.add(
            'songs',
            'ausente ou não é lista',
            'declare songs: [{id, song, idAlbum, bpm, resumo, referencias, patches}]',
        )
    if not isinstance(defs.get('ir_local'), dict):
        er.add(
            'ir_local',
            'ausente ou não é objeto',
            "declare ir_local: {'<CAB>': {captura, slot}} — mesmo sem capturas, use {}",
        )


def _validar_albums(albums: dict[str, Any], er: Erros) -> None:
    for idalb, alb in albums.items():
        base = f'albums.{idalb}'
        for campo in ('banda', 'album', 'ano', 'pasta', 'rig'):
            if campo not in alb:
                er.add(
                    f'{base}.{campo}',
                    'campo obrigatório ausente',
                    f'acrescente "{campo}" ao álbum (rig = dossiê com fontes)',
                )
        ano = alb.get('ano')
        if ano is not None and not isinstance(ano, int):
            er.add(
                f'{base}.ano',
                f'deve ser int, veio {type(ano).__name__}',
                'use o ano do lançamento',
            )


def _validar_songs(defs: dict[str, Any], albums: dict[str, Any] | None, er: Erros) -> None:
    ids_songs: set[str] = set()
    nomes: set[str] = set()
    for i, song in enumerate(defs.get('songs', [])):
        base = f'songs[{i}]'
        sid = song.get('id')
        if not sid:
            er.add(f'{base}.id', 'obrigatório', 'use o padrão AAZZNN (ex.: SMOO1)')
        elif sid in ids_songs:
            er.add(f'{base}.id', f"duplicado ('{sid}')", 'ids de música têm de ser únicos')
        ids_songs.add(sid)

        if song.get('idAlbum') not in (albums or {}):
            er.add(
                f'{base}.idAlbum',
                f"'{song.get('idAlbum')}' não existe em albums",
                f'ids válidos: {", ".join(albums or {})}',
            )
        bpm = song.get('bpm')
        if not _e_num(bpm) or not 30 <= bpm <= 300:
            er.add(f'{base}.bpm', f'fora do range 30–300 ({bpm})', 'confira o BPM real da faixa')

        patches = song.get('patches', [])
        if not patches:
            er.add(
                f'{base}.patches',
                'música sem patch nenhum',
                'toda música do defs precisa de ao menos 1 patch (ou saia do defs)',
            )
        for j, patch in enumerate(patches):
            _validar_patch(patch, f'{base}.patches[{j}]', nomes, er)


def _validar_patch(patch: dict[str, Any], pb: str, nomes: set[str], er: Erros) -> None:
    nome = patch.get('nome')
    if not nome:
        er.add(f'{pb}.nome', 'obrigatório', 'MUSICA(≤4)+NN+CAMADA(2), ex.: SMOO1SO')
        return
    if nome in nomes:
        er.add(f'{pb}.nome', f"duplicado ('{nome}')", 'nomes de painel têm de ser únicos')
    nomes.add(nome)
    if len(nome) > 12:
        er.add(
            f'{pb}.nome',
            f"'{nome}' tem {len(nome)} chars",
            'máx. 12 (limite do painel da GP-100) — renomeie',
        )

    sufixo = patch.get('sufixo')
    if sufixo not in CAMS:
        er.add(
            f'{pb}.sufixo',
            f"'{sufixo}' não é uma camada conhecida",
            f'use um de: {", ".join(sorted(CAMS))}',
        )
    if not patch.get('camada'):
        er.add(
            f'{pb}.camada',
            'obrigatória (aparece na doc e nos índices)',
            'ex.: "Base", "Solo", "Riff"',
        )

    spec = patch.get('spec')
    if not isinstance(spec, dict):
        er.add(
            f'{pb}.spec', 'obrigatório', 'estrutura documentada no docstring de generate_prst.py'
        )
        return
    _validar_spec(spec, f'{pb}.spec', er)

    doc = patch.get('doc')
    if not isinstance(doc, dict):
        er.add(f'{pb}.doc', 'obrigatório', 'guitarra/comoTocar/teste/ajustes/evite/irNota')
        return
    _validar_doc(doc, f'{pb}.doc', er)


def _validar_spec(spec: dict[str, Any], base: str, er: Erros) -> None:
    if not spec.get('name'):
        er.add(f'{base}.name', 'obrigatório', 'deve ser igual ao nome do patch')
    if spec.get('type') not in TIPOS_VALIDOS:
        er.add(
            f'{base}.type',
            f"'{spec.get('type')}' não é gênero válido",
            f'use um de: {" ".join(sorted(TIPOS_VALIDOS))}',
        )

    modules = spec.get('modules')
    if not isinstance(modules, dict):
        er.add(
            f'{base}.modules',
            'obrigatório',
            'os 9 módulos da cadeia (ou os usados + neutros no gerador)',
        )
        return
    for mod, m in modules.items():
        if mod not in CHAIN:
            er.add(
                f'{base}.modules.{mod}',
                'módulo fora da cadeia fixa',
                f'use apenas: {", ".join(CHAIN)}',
            )
            continue
        if not m.get('name'):
            er.add(
                f'{base}.modules.{mod}.name',
                'obrigatório',
                'nome EXATO do catálogo fw 2.0 (reference/15) — nunca o do manual V1.8',
            )
        _validar_params(m, mod, f'{base}.modules.{mod}', er)
    if 'CAB' not in modules:
        er.add(
            f'{base}.modules.CAB',
            'ausente',
            'todo patch single fw 2.1 declara CAB (fábrica na política de IR)',
        )


def _validar_params(modulo: dict[str, Any], mod: str, base: str, er: Erros) -> None:
    """Índice e faixa de cada parâmetro — faixa fina por modelo em reference/15."""
    bruto = modulo.get('name')
    modelo = bruto if isinstance(bruto, str) else ''
    for k, v in (modulo.get('params') or {}).items():
        if not str(k).isdigit() or not 0 <= int(k) <= 14:
            er.add(
                f'{base}.params.{k}',
                'índice inválido',
                'params_0..14 — slots internos do firmware não se setam',
            )
            continue
        if not _e_num(v):
            er.add(
                f'{base}.params.{k}', f'valor não numérico ({v!r})', 'params do .prst são numéricos'
            )
            continue
        etiqueta = rotulo(mod, modelo, int(k)) or ''
        if etiqueta in ROTULOS_EM_MS:
            if not 0 <= v <= 1000:
                er.add(
                    f'{base}.params.{k}',
                    f'{etiqueta}={v} ms fora de 0–1000',
                    'confira o tempo em ms (export de fábrica usa 160–620)',
                )
        elif v < -15 or v > 100:
            er.add(
                f'{base}.params.{k}',
                f'{etiqueta or f"param_{k}"}={v} fora do range esperado',
                'confira o range oficial do modelo em reference/15',
            )


def _validar_doc(doc: dict[str, Any], base: str, er: Erros) -> None:
    for campo in _CAMPOS_MODULO_AUSENTE:
        if not doc.get(campo):
            er.add(
                f'{base}.{campo}',
                'obrigatório',
                'a doc prática-primeiro exige guitarra, teste e seção de IR',
            )
    for k in ('ajustes', 'evite'):
        if not isinstance(doc.get(k), list):
            er.add(
                f'{base}.{k}', 'deve ser lista de strings', 'ex.: ["lamacento → CAB High Cut -5"]'
            )
    for i, mom in enumerate(doc.get('momentos', [])):
        for campo in ('nome', 'mods', 'quando'):
            if campo not in mom:
                er.add(
                    f'{base}.momentos[{i}].{campo}',
                    'obrigatório no momento de toggle',
                    "{'nome', 'mods': [['MOD','ON']], 'quando', 'dica?'}",
                )
        for mod, estado in mom.get('mods', []):
            if mod not in CHAIN:
                er.add(
                    f'{base}.momentos[{i}].mods',
                    f'módulo {mod} fora da cadeia',
                    f'use: {", ".join(CHAIN)}',
                )
            if estado not in ('ON', 'OFF'):
                er.add(f'{base}.momentos[{i}].mods', f"estado '{estado}' inválido", 'use ON ou OFF')
            if mod in MODULOS_PROIBIDOS_EM_MOMENTO:
                er.add(
                    f'{base}.momentos[{i}].mods',
                    'toggle de AMP/CAB é proibido',
                    'nunca ligue/desligue volume e corpo em tempo real',
                )


def _validar_ir_local(defs: dict[str, Any], er: Erros) -> None:
    """Captura de IR órfã: entrada em ir_local que nenhum CAB usa."""
    cabs = {
        p['spec']['modules'].get('CAB', {}).get('name')
        for s in defs.get('songs', [])
        for p in s.get('patches', [])
        if isinstance(p.get('spec'), dict)
    }
    for cab in defs.get('ir_local', {}):
        if cab not in cabs:
            er.add(
                f'ir_local.{cab}',
                'nenhum patch usa este CAB',
                'remova a entrada (ou o CAB saiu do defs e a captura ficou órfã)',
            )
