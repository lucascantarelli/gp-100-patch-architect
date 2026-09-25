"""Golden set do doc 20 — a região de tabelas de `reference/20-golden-set.md`
é DERIVADA (issue #129/#131): nasce de `data/golden-set.json` (a seleção,
dado editorial versionado) + `data/defs/` (cadeias do `spec.modules`).

O que é editorial e o que é derivado no doc 20:

* **Seleção** (quais músicas/álbuns entram na régua): `data/golden-set.json`
  — mesma natureza do `_albums.json` (dado curado, não tabela de script);
* **Cadeia esperada** de cada patch: defs (`spec.modules`, estado `on`) —
  regenerada pelo pipeline no passo `golden_set`, dentro das marcas
  `gerado:inicio`/`gerado:fim`;
* **Prosa** (regras de pontuação, placar da rodada, fontes, armadilhas):
  editorial — o pipeline NUNCA toca nada fora das marcas.

Assim como o `patch.md` e o `.prst` (ADR-0013), a tabela não se edita à mão:
mudou o defs, `gp100 build` regenera; editou à mão, o guarda de sincronia
(TestH) reprova. A seleção mora em dado versionado — a regra 8 da casa
proíbe tabela de músicas dentro de script.

Camada: application (funções puras; quem lê/grava é o pipeline via
`infrastructure.escrita`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = [
    'ARQUIVO_SELECAO',
    'DOC_ALVO',
    'MARCA_FIM',
    'MARCA_INICIO',
    'ORDEM_BLOCOS',
    'aplicar_no_doc',
    'cadeia_esperada',
    'regiao_derivada',
    'selecao_carregar',
]

ARQUIVO_SELECAO = Path('data') / 'golden-set.json'
DOC_ALVO = Path('reference') / '20-golden-set.md'
MARCA_INICIO = (
    '<!-- gerado:inicio (gp100 build — não editar; fonte: data/golden-set.json + data/defs) -->'
)
MARCA_FIM = '<!-- gerado:fim -->'

# A ordem canônica da cadeia (knowledge.md regra 3) — o doc 20 documenta a
# mesma ordem no cabeçalho.
ORDEM_BLOCOS = ('PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB')


class Gp100GoldenSetError(Exception):
    """Erro previsto da derivação do golden set (mensagem acionável, sem traceback)."""


def selecao_carregar(raiz: Path) -> dict[str, Any]:
    """Lê `data/golden-set.json` com validação mínima de forma."""
    caminho = raiz / ARQUIVO_SELECAO
    try:
        selecao = json.loads(caminho.read_text(encoding='utf-8'))
    except FileNotFoundError as erro:
        raise Gp100GoldenSetError(
            f'{ARQUIVO_SELECAO} não existe — a seleção do golden set é dado '
            'versionado; crie o arquivo (veja data/golden-set.json no repo).'
        ) from erro
    except json.JSONDecodeError as erro:
        raise Gp100GoldenSetError(f'{ARQUIVO_SELECAO} ilegível: {erro}') from erro
    if not isinstance(selecao, dict) or not selecao.get('musicas') or not selecao.get('porAlbum'):
        raise Gp100GoldenSetError(
            f'{ARQUIVO_SELECAO} precisa de "porAlbum" (ordem dos álbuns) e '
            '"musicas" (ids na ordem da régua).'
        )
    return selecao


def cadeia_esperada(spec: dict[str, Any]) -> str:
    """`spec.modules` → 'PRE:Boost+ DST:Red Haze- …' (ordem canônica, 9 blocos).

    `BLOCO:Modelo+` ligado, `BLOCO:Modelo-` presente e desligado — a notação
    do doc 20. Bloco ausente do spec é erro (o defs é schema-validado, mas a
    mensagem precisa apontar o patch, não quebrar com KeyError).
    """
    partes: list[str] = []
    for bloco in ORDEM_BLOCOS:
        modulo = (spec.get('modules') or {}).get(bloco)
        if not modulo or not modulo.get('name'):
            raise Gp100GoldenSetError(f'bloco {bloco} ausente no spec do defs')
        estado = '+' if modulo.get('on') else '-'
        partes.append(f'{bloco}:{modulo["name"]}{estado}')
    return ' '.join(partes)


def _song_por_id(defs: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {song['id']: song for song in defs['songs']}


def regiao_derivada(defs: dict[str, Any], selecao: dict[str, Any]) -> str:
    """O texto completo que vai entre as marcas: uma seção por álbum.

    Ordem dos álbuns = `selecao['porAlbum']`; dentro do álbum, as músicas
    seguem `selecao['musicas']` e os patches a ordem do defs. Heading e
    contagens vêm do defs (regra 8: nada de tabela própria no módulo).
    """
    por_id = _song_por_id(defs)
    desconhecidas = [mid for mid in selecao['musicas'] if mid not in por_id]
    if desconhecidas:
        raise Gp100GoldenSetError(
            'musicas fora do defs: ' + ', '.join(desconhecidas) + ' — '
            'atualize data/golden-set.json ou o defs.'
        )
    unknown_albuns = [a for a in selecao['porAlbum'] if a not in defs['albums']]
    if unknown_albuns:
        raise Gp100GoldenSetError('porAlbum fora do defs: ' + ', '.join(unknown_albuns))

    secoes: list[str] = []
    total = 0
    for chave in selecao['porAlbum']:
        album = defs['albums'][chave]
        songs = [por_id[mid] for mid in selecao['musicas'] if por_id[mid]['idAlbum'] == chave]
        if not songs:
            continue
        linhas: list[str] = []
        for song in songs:
            for patch in song['patches']:
                linhas.append(f'| `{patch["nome"]}` | {cadeia_esperada(patch["spec"])} |')
                total += 1
        heading = f'### {album["banda"]} — {album["display"]}'
        secoes.append(heading + '\n\n| Patch | Cadeia esperada |\n|---|---|\n' + '\n'.join(linhas))
    if not secoes:
        raise Gp100GoldenSetError(
            'nenhuma música da seleção pertence aos álbuns de porAlbum — '
            'confira data/golden-set.json.'
        )
    return (
        f'> {len(selecao["musicas"])} músicas · {total} patches · '
        f'{len(secoes)} álbum(ns) — derivado do defs pelo `gp100 build`.\n\n' + '\n\n'.join(secoes)
    )


def aplicar_no_doc(doc_atual: str, regiao: str) -> str:
    """Substitui SÓ o trecho entre as marcas; prosa fora delas é intocada."""
    ini = doc_atual.find(MARCA_INICIO)
    fim = doc_atual.find(MARCA_FIM)
    if ini == -1 or fim == -1 or fim < ini:
        raise Gp100GoldenSetError(
            f'{DOC_ALVO} sem as marcas {MARCA_INICIO!r} … {MARCA_FIM!r} — '
            'a região derivada do doc 20 precisa delas para ser regenerada.'
        )
    fim_fim = fim + len(MARCA_FIM)
    sufixo = doc_atual[fim_fim:].lstrip('\n')  # normaliza linhas em branco pós-região
    return doc_atual[:ini] + MARCA_INICIO + '\n\n' + regiao + '\n\n' + MARCA_FIM + '\n\n' + sufixo
