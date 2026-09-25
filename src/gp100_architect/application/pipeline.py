"""O pipeline de dados — caso de uso de produção da biblioteca (issue #33).

Sucessor dos shims `tools/ir_library.py`, `tools/build_song_patches.py` e
`tools/gen_indexes.py`: a MESMA sequência, na MESMA ordem, agora in-process —
sem subprocess, sem `sys.path` manual, sem dois lugares para o mesmo código.

Ordem do guarda de determinismo (TestH, `tests/e2e/test_sincronia.py`):

    1. ir_library    — indexa `impulse_responses/` → `data/ir-library.json`
                       + `reference/16-ir-library.md`;
    2. patches       — gera `patch.md` + `.prst` de cada patch (spec in-memory,
                       ADR-0013) em `patches/`;
    3. indices       — `MAPA-DO-ALBUM.md` de cada álbum + `patches/README.md`.

Contratos preservados: cada passo imprime um resumo acionável (o mesmo texto
dos shims, com o comando novo), erro previsto sai com mensagem limpa (sem
traceback) e código != 0; `GP100_BUILD_TIME` fixa o `@time` do `.prst`
(reprodutibilidade); o banco de IRs ausente não zera os catálogos commitados.

Camada: application — orquestra os casos de uso e grava via
`infrastructure.escrita`; quem imprime e decide exit code é a CLI.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from gp100_architect.application import biblioteca, golden_set, indices, ir_library, variantes
from gp100_architect.infrastructure.escrita import escrever_bytes, escrever_texto
from gp100_architect.infrastructure.ir_catalog import carregar as carregar_catalogo
from gp100_architect.infrastructure.ir_catalog import indice_por_cab
from gp100_architect.infrastructure.prst.codec import BUILD_TIME_PADRAO, load_templates
from gp100_architect.infrastructure.wav import inspecionar as wav_info

__all__ = ['PIPELINE_PASSOS', 'executar']

# Ordem canônica, citada pelo nome nos relatórios e no guarda de sincronia.
PIPELINE_PASSOS = ('ir_library', 'patches', 'indices', 'golden_set')


def _indice_de_irs(raiz: Path) -> dict[str, list[str]]:
    """Índice `{gabinete: [arquivos]}` do catálogo local (ou {} se ilegível)."""
    manifesto = carregar_catalogo(raiz / 'data' / 'ir-library.json')
    return indice_por_cab(manifesto) if manifesto else {}


# ── passo 1 · ir_library ────────────────────────────────────────────────────


def _passo_ir_library(raiz: Path, out: Any, _com_variante: bool) -> int:
    """Indexa `impulse_responses/` → `data/ir-library.json` + o catálogo MD.

    Banco ausente/vazio → NÃO sobrescreve os catálogos commitados com um
    manifesto vazio: avisa e segue (o caso do clone limpo, o CI).
    """
    ir_dir = raiz / 'impulse_responses'
    out_json = raiz / 'data' / 'ir-library.json'
    out_md = raiz / 'reference' / '16-ir-library.md'
    wavs = (
        sorted(ir_dir.rglob('*.wav'), key=lambda p: ir_library.wav_order(p, ir_dir))
        if (ir_dir.exists())
        else []
    )
    if not wavs:
        out.write(
            'ℹ️  Banco local de IRs ausente ou vazio — nada a indexar.\n'
            '   Os catálogos commitados (data/ir-library.json e\n'
            '   reference/16-ir-library.md) ficam como estão, com a última\n'
            '   indexação conhecida — os agentes continuam consultando-os.\n'
            '   Para indexar: baixe o pack e extraia em impulse_responses/<Nome do Pack>/.\n'
        )
        return 0

    registros = [
        {
            'file': ir_library.wav_order(wav, ir_dir),
            'size_kb': round(wav.stat().st_size / 1024),
            **wav_info(wav),
        }
        for wav in wavs
    ]
    manifesto = ir_library.montar_manifesto(registros)

    antigo: dict[str, Any] | None = None
    if out_json.exists():
        try:
            antigo = json.loads(out_json.read_text(encoding='utf-8'))
        except Exception:
            antigo = None  # catálogo ilegível: não bloqueia a rodada
    problemas = ir_library.encolhimento(antigo or {}, manifesto)
    if problemas:
        out.write('❌ Esta rodada ENCOLHERIA o catálogo commitado de IRs:\n')
        for p in problemas:
            out.write(f'   - {p}\n')
        out.write('\n' + ir_library.PROBLEMAS_DE_FORMATO + '\n')
        return 1

    escrever_texto(out_json, json.dumps(manifesto, ensure_ascii=False, indent=1))
    escrever_texto(out_md, ir_library.catalogo_md(manifesto))

    total = sum(m['wavs'] for m in manifesto['packs'].values())
    out.write(f'✅ {total} WAVs em {len(manifesto["packs"])} pack(s) indexados.\n')
    for pack, mp in manifesto['packs'].items():
        out.write(
            f'  - {pack}: {mp["wavs"]} WAVs · cabs: {", ".join(mp["cabs"])} · '
            f'compatível: {mp["all_compatible"]}\n'
        )
    return 0


# ── passo 2 · patches ───────────────────────────────────────────────────────


def _passo_patches(raiz: Path, out: Any, com_variante: bool) -> int:
    """Gera `patch.md` + `.prst` de todos os patches do defs (in-memory → disco)."""
    from gp100_architect.domain.errors import Gp100Error
    from gp100_architect.infrastructure.defs import carregar_e_validar

    try:
        defs = carregar_e_validar()
    except Gp100Error as erro:
        out.write(f'FALHA {erro}\n')
        return 1
    templates = load_templates()
    build_time = os.environ.get('GP100_BUILD_TIME', BUILD_TIME_PADRAO)
    try:
        gerados = biblioteca.gerar(
            defs,
            raiz=raiz,
            ir_index=_indice_de_irs(raiz),
            templates=templates,
            build_time=build_time,
            com_variantes=com_variante,
        )
    except Gp100Error as erro:
        out.write(f'FALHA {erro}\n')
        return 1

    for patch in gerados:
        if patch.nome.endswith(variantes.SUFIXO):
            # variante -USERIR (issue #10): doc e .prst ao lado do canônico;
            # fora do guarda de determinismo (o sincronia ignora o sufixo)
            escrever_texto(patch.pasta / f'{patch.nome}.md', patch.documentacao, crlf=True)
        else:
            escrever_texto(patch.pasta / 'patch.md', patch.documentacao, crlf=True)
        escrever_bytes(patch.pasta / f'{patch.nome}.prst', patch.prst)

    rotulo = 'patches + variantes -USERIR' if com_variante else 'patches'
    out.write(f'✅ {len(gerados)} {rotulo} gerados e validados:\n\n')
    for patch in gerados:
        out.write(f'  {patch.musica:45s} → {patch.nome:9s} ({patch.camada})\n')
    return 0


# ── passo 3 · indices ───────────────────────────────────────────────────────


def _passo_indices(raiz: Path, out: Any, _com_variante: bool) -> int:
    """Regenera os `MAPA-DO-ALBUM.md` de cada álbum + o `patches/README.md`."""
    from gp100_architect.infrastructure.defs import carregar_e_validar

    defs = carregar_e_validar()
    saidas, total = indices.build_all(defs, raiz=raiz, ir_index=_indice_de_irs(raiz))
    for caminho, texto in saidas.items():
        escrever_texto(caminho, texto, crlf=True)
    out.write(
        f'✅ {len(defs["albums"])} mapas + patches/README.md regenerados '
        f'({total} patches, slots U01–U{total:02d}).\n'
    )
    return 0


# ── passo 4 · golden_set ──────────────────────────────────────────────────


def _passo_golden_set(raiz: Path, out: Any, _com_variante: bool) -> int:
    """Regenera a região marcada das tabelas do golden set (doc 20) do defs.

    A seleção (quais músicas formam a régua) é dado editorial versionado em
    `data/golden-set.json`; as cadeias são derivadas do `spec.modules`. Só o
    trecho entre as marcas é tocado — prosa (regras, placar, fontes) é
    intocada. Doc sem as marcas = erro acionável.
    """
    from gp100_architect.infrastructure.defs import carregar_e_validar

    defs = carregar_e_validar()
    doc_caminho = raiz / golden_set.DOC_ALVO
    if not doc_caminho.exists():
        out.write(f'❌ {golden_set.DOC_ALVO} não existe — nada a regenerar.\n')
        return 1
    try:
        selecao = golden_set.selecao_carregar(raiz)
        regiao = golden_set.regiao_derivada(defs, selecao)
        novo_doc = golden_set.aplicar_no_doc(
            doc_caminho.read_text(encoding='utf-8'), regiao
        )
    except golden_set.Gp100GoldenSetError as erro:
        out.write(f'❌ {erro}\n')
        return 1
    escrever_texto(doc_caminho, novo_doc, crlf=True)
    n_patches = regiao.count('\n| `')
    out.write(
        f'✅ golden set regenerado: {len(selecao["musicas"])} músicas · '
        f'{n_patches} patches em {golden_set.DOC_ALVO}\n'
    )
    return 0


_PASSOS = {
    'ir_library': _passo_ir_library,
    'patches': _passo_patches,
    'indices': _passo_indices,
    'golden_set': _passo_golden_set,
}


def executar(
    raiz: Path,
    *,
    passos: tuple[str, ...] = PIPELINE_PASSOS,
    com_variante: bool = False,
    out: Any = None,
) -> int:
    """Roda o pipeline na ordem do guarda; devolve 0 ou o código do passo falho.

    `raiz` é o repositório (leitura do defs e do banco de IRs; escrita em
    `data/`, `reference/` e `patches/`). `out` recebe o relatório (default:
    `sys.stdout`) — a CLI injeta um console Rich; o TestH sandbox usa o stdout
    do subprocess. Para no primeiro passo que falhar.
    """
    stream = out if out is not None else sys.stdout
    write = stream.write
    for passo in passos:
        if passo not in _PASSOS:
            write(f'passo desconhecido: {passo} (válidos: {", ".join(PIPELINE_PASSOS)})\n')
            return 2
        codigo = _PASSOS[passo](raiz, stream, com_variante)
        if codigo != 0:
            return codigo
    return 0
