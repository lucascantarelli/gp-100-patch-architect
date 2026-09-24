"""Carregamento do defs — a fonte única do projeto (schema v2, issue #8).

O defs vive em **fragmentos por álbum** sob `data/defs/`:

    data/defs/_albums.json          ← manifesto: chaves de álbum, EM ORDEM
    data/defs/<slug-do-álbum>.json  ← { "idAlbum": "AR", "album": {...},
                                        "songs": [ …na ordem da tracklist ] }

`consolidar()` concatena os fragmentos **na ordem de `_albums.json`** e devolve
o MESMO shape do monólito (`meta`, `albums`, `ir_local`, `songs`) — o resto do
pipeline não sabe que passou a haver fragmentos. `_albums.json` é a ÚNICA fonte
da ordem: é dela que sai a numeração U01…Uxx, e a numeração dos slots é
contrato com o músico.

Regras que este módulo impõe (reprovam alto, com caminho do arquivo):

* todo fragmento listado no manifesto tem de existir, e todo fragmento no
  diretório tem de estar no manifesto (arquivo fora do manifesto é dado órfão);
* as músicas de cada álbum têm de ser CONTÍGUAS na sequência consolidada e
  seguir a ordem do manifesto — uma intercalação mudaria os slots sem mudar
  nenhum dado, e slots desalinhados são bug silencioso;
* o `idAlbum` do fragmento tem de casar com a chave declarada no manifesto.

A porta de entrada continua sendo `carregar_e_validar()` (regra do achado M2:
não existe carregar sem validar). O caminho é apontável por `GP100_DEFS` — que
agora aponta para o DIRETÓRIO de fragmentos (ou para um JSON único, que o
loader aceita para testes e diagnóstico).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from gp100_architect.domain.errors import DefsInvalidos
from gp100_architect.domain.validation import validar

__all__ = [
    'DEFS_PADRAO',
    'MANIFESTO',
    'VAR_DEFS',
    'caminho_defs',
    'carregar',
    'carregar_e_validar',
    'consolidar',
    'raiz_do_repo',
]

VAR_DEFS = 'GP100_DEFS'
MANIFESTO = '_albums.json'


def raiz_do_repo() -> Path:
    """Raiz do repositório — onde estão `data/`, `patches/` e `VERSION`."""
    return Path(__file__).resolve().parents[3]


DEFS_PADRAO: Path = raiz_do_repo() / 'data' / 'defs'


def caminho_defs(caminho: Path | None = None) -> Path:
    """Prioridade: argumento → `GP100_DEFS` → `data/defs/`."""
    if caminho is not None:
        return caminho
    do_ambiente = os.environ.get(VAR_DEFS)
    return Path(do_ambiente) if do_ambiente else DEFS_PADRAO


def _ler_json(caminho: Path) -> Any:
    try:
        return json.loads(caminho.read_text(encoding='utf-8'))
    except OSError as e:
        raise DefsInvalidos(f'✗ {caminho}: não pôde ser lido ({e.strerror or e})', 1) from e
    except json.JSONDecodeError as e:
        raise DefsInvalidos(f'✗ {caminho}: JSON inválido — {e}', 1) from e


def consolidar(diretorio: Path) -> dict[str, Any]:
    """Lê `data/defs/` e devolve o defs consolidado, no shape do monólito.

    Levanta `DefsInvalidos` com relatório acionável quando a estrutura fere as
    regras do schema v2 (fragmento fora do manifesto, ordem divergente, música
    intercalada, `idAlbum` trocado).
    """
    if not diretorio.is_dir():
        raise DefsInvalidos(
            f'✗ {diretorio}: diretório do defs não existe — o schema v2 guarda os '
            f'fragmentos em {MANIFESTO} + um JSON por álbum (issue #8)',
            1,
        )

    caminho_manifesto = diretorio / MANIFESTO
    if not caminho_manifesto.is_file():
        raise DefsInvalidos(f'✗ {caminho_manifesto}: manifesto de álbuns ausente', 1)
    manifesto = _ler_json(caminho_manifesto)
    if not isinstance(manifesto, list) or not all(isinstance(a, str) for a in manifesto):
        raise DefsInvalidos(
            f'✗ {caminho_manifesto}: esperado um ARRAY de chaves de álbum EM ORDEM '
            '(ex.: ["AR", "ZP", …]) — é dele que sai a ordem dos slots U01…Uxx',
            1,
        )

    no_disco = {p.name for p in diretorio.glob('*.json')}
    declarados = {f'{a}.json' for a in manifesto}
    problemas: list[str] = []
    for nome in sorted(no_disco - declarados - {MANIFESTO}):
        problemas.append(
            f'✗ {nome}: fragmento FORA do manifesto — ou declare a chave em '
            f'{MANIFESTO} ou mova o arquivo para fora de {diretorio.name}/'
        )
    for chave in manifesto:
        if f'{chave}.json' not in no_disco:
            problemas.append(f'✗ {MANIFESTO}: declara "{chave}" mas {chave}.json não existe')
    if problemas:
        raise DefsInvalidos('\n'.join(problemas), len(problemas))

    meta: dict[str, Any] = {}
    albums: dict[str, Any] = {}
    ir_local: dict[str, Any] = {}
    songs: list[dict[str, Any]] = []
    for chave in manifesto:
        frag = _ler_json(diretorio / f'{chave}.json')
        if not isinstance(frag, dict):
            raise DefsInvalidos(f'✗ {chave}.json: esperado um objeto JSON', 1)
        if frag.get('idAlbum') != chave:
            problemas.append(
                f'✗ {chave}.json: idAlbum "{frag.get("idAlbum")}" diverge da chave '
                f'"{chave}" declarada em {MANIFESTO}'
            )
            continue
        # cada música do fragmento pertence ao SEU álbum: uma song de outro
        # álbum aqui é edição no arquivo errado — e intercalaria os slots
        for song in frag.get('songs') or []:
            if song.get('idAlbum') != chave:
                problemas.append(
                    f'✗ {chave}.json: song "{song.get("id")}" tem idAlbum '
                    f'"{song.get("idAlbum")}" — música de outro álbum no fragmento '
                    f'de {chave}; mova para {song.get("idAlbum")}.json'
                )
        meta.update(frag.get('meta') or {})
        albums[chave] = frag.get('album') or {}
        ir_local.update(frag.get('ir_local') or {})
        songs.extend(frag.get('songs') or [])
    if problemas:
        raise DefsInvalidos('\n'.join(problemas), len(problemas))

    # contiguidade: uma intercalação de álbuns muda a numeração dos slots sem
    # mudar nenhum dado — reprova aqui, onde a causa é visível. A regra vale na
    # sequência CONSOLIDADA: os blocos distintos de `idAlbum`, na ordem em que
    # aparecem, têm de sair na ordem do manifesto (apenas os com músicas). Como
    # cada fragmento só entra sob a SUA chave, o caso [ZP, ZP] com manifesto
    # [AR, ZP] não passa como "contíguo por acidente": o bloco AR está ausente.
    vistos: list[str] = []
    for song in songs:
        chave = song.get('idAlbum')
        if not isinstance(chave, str):
            continue  # song sem idAlbum: o domínio reprova
        if not vistos or vistos[-1] != chave:
            vistos.append(chave)
    declarados_com_musicas = [a for a in manifesto if a in set(vistos)]
    if vistos != declarados_com_musicas:
        raise DefsInvalidos(
            '✗ ordem das músicas: álbuns intercalados ou fora da ordem de '
            f'{MANIFESTO} na sequência consolidada ('
            f'{", ".join(map(str, vistos))} ≠ '
            f'{", ".join(declarados_com_musicas)}). Intercalar muda os slots '
            'U01…Uxx sem mudar dado nenhum.',
            1,
        )

    return {'meta': meta, 'albums': albums, 'ir_local': ir_local, 'songs': songs}


def carregar(caminho: Path | None = None) -> dict[str, Any]:
    """Lê o defs **sem** validar — só para diagnóstico e ferramentas de migração."""
    alvo = caminho_defs(caminho)
    if alvo.is_dir():
        return consolidar(alvo)
    dados = _ler_json(alvo)
    if not isinstance(dados, dict):
        raise DefsInvalidos(f'✗ {alvo}: esperado um objeto JSON', 1)
    return dados


def carregar_e_validar(caminho: Path | None = None) -> dict[str, Any]:
    """Lê o defs validando todas as regras do domínio.

    Levanta `DefsInvalidos` (com relatório acionável) quando o arquivo não passa.
    """
    alvo = caminho_defs(caminho)
    dados = carregar(alvo)
    erros = validar(dados)
    if not erros.ok():
        raise DefsInvalidos(erros.relatorio(), len(erros.itens))
    return dados
