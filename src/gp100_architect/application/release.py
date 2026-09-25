"""Empacotamento da release — biblioteca da aplicação (issue #32).

Migração de `tools/build_release.py`: a biblioteca **não imprime** e **não
estoura `SystemExit`** — devolve dados (`{Path: bytes/texto}`) e levanta
`ReleaseInvalida` com mensagem acionável; quem imprime e sai é a CLI
(`gp100 release`). É o contrato que a #49 consome.

O que vai em cada ZIP: apenas o que o músico precisa — `<NOME>.prst` e
`patch.md`, na estrutura `<Banda>/<Álbum>/<Música>/`. Os `.prst` são
validados antes de entrar no pacote (formato single fw 2.1, nome conforme).

A versão é sempre SemVer (`MAIOR.MENOR.PATCH`); `VERSION` é a fonte única
usada pelo CI (job release) e por quem empacota localmente.

Camada: application — lê o defs e os `.prst` da biblioteca (leitura de
entradas do pipeline); gravação apenas em `destino` explícito.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

from gp100_architect.domain.errors import ReleaseInvalida

__all__ = [
    'SEMVER_RE',
    'bump',
    'collect_patches',
    'ler_versao',
    'notas_markdown',
    'package',
    'validar_versao',
]

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')


def validar_versao(version: str) -> str:
    """Versão SemVer validada — erro acionável em vez de regex espalhada."""
    if not SEMVER_RE.match(version):
        raise ReleaseInvalida(f"Versão inválida: '{version}' — use SemVer (ex.: 1.2.3).")
    return version


def ler_versao(raiz: Path) -> str:
    """Lê VERSION (fonte única) e devolve a versão validada."""
    arquivo = raiz / 'VERSION'
    if not arquivo.exists():
        raise ReleaseInvalida(
            'VERSION não existe — crie com a versão atual (ex.: 1.0.0) ou passe a '
            'versão como argumento.'
        )
    return validar_versao(arquivo.read_text(encoding='utf-8').strip())


def bump(version: str, part: str) -> str:
    """Sobe um componente do SemVer (major/minor/patch)."""
    validar_versao(version)
    if part not in ('major', 'minor', 'patch'):
        raise ReleaseInvalida(f"parte '{part}' inválida — use major, minor ou patch")
    major, minor, patch = (int(n) for n in version.split('.'))
    return {
        'major': f'{major + 1}.0.0',
        'minor': f'{major}.{minor + 1}.0',
        'patch': f'{major}.{minor}.{patch + 1}',
    }[part]


def collect_patches(defs: dict[str, Any], patches_dir: Path) -> list[tuple[Path, str]]:
    """Todos os patches da biblioteca: [(caminho_da_pasta, nome_do_patch)].

    A lista vem do defs, não do disco: quem define a pasta de cada patch é ele
    (`albums[].pasta` + `songs[].pasta|song` + `patch.nome`). Num clone limpo
    (o job de release não roda o pipeline) um rglob sairia VAZIO.
    """
    items = []
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]['pasta']
        musica = song.get('pasta') or song['song']
        for patch in song['patches']:
            pasta = patches_dir / album / musica / patch['nome']
            items.append((pasta, patch['nome']))
    return items


def assert_valid_prst(path: Path, nome: str) -> None:
    """Confere o mínimo do formato single fw 2.1 antes de entrar no pacote.

    O `ppName` é atributo do elemento `<presets>` (não existe elemento
    `<ppName>`): confere por regex com fronteira, para não pegar `ppNameXYZ`.
    """
    text = path.read_text(encoding='utf-8', errors='replace')
    if not re.search(rf'ppName="{re.escape(nome)}"', text):
        raise ReleaseInvalida(
            f'{path}: ppName não confere com o nome do defs ({nome}) — regenere o '
            'pipeline antes de empacotar.'
        )
    if 'firmware="2.1"' not in text:
        raise ReleaseInvalida(
            f'{path}: formato inesperado (esperado firmware 2.1) — regenere o pipeline.'
        )


MIGRACAO: dict[str, list[str]] = {
    # Notas de migração por versão breaking (issue #59). A chave é a versão;
    # `notas_markdown` inclui a seção quando a versão tem entrada — o texto é
    # PARTE DO PACOTE (deriva do código), não editado à mão por release.
    '2.0.0': [
        '`python tools/*.py` **deixa de existir** — o pipeline inteiro agora é '
        'o pacote: `uv run gp100 …` (substitua cada script pelo comando equivalente: '
        '`gp100.py` → `gp100 build`/`show`/`diff`/`export`; `build_release.py` → '
        '`gp100 release`; `gen_changelog.py` → `gp100 changelog`).',
        '`patches/patches-defs.json` (v1) **não existe mais** — o defs é '
        '`data/defs/<ÁLBUM>.json` (schema v2, índice em `_albums.json`).',
        '`patches/**` **saiu do git** (ADR-0013): os `.prst`/`patch.md` se baixam '
        'desta Release (ou do site) e/ou nascem com `uv run gp100 build`.',
        'Firmware **2.1** obrigatório — o formato single fw 2.0 do export antigo '
        'é rejeitado pelo validador e pela pedaleira.',
    ],
}


def notas_markdown(version: str, total: int, n_songs: int, albums: dict[str, int]) -> str:
    """RELEASE-NOTES-v<versão>.md — o texto pronto para `gh release create`."""
    linhas = [
        f'# GP-100 Patches v{version}',
        '',
        f'**{total} patches · {n_songs} músicas · {len(albums)} álbuns** — formato single, '
        'firmware 2.1, prontos para importar no aparelho (SYSTEM → USB → Import).',
        '',
    ]
    if version in MIGRACAO:
        linhas += [
            '## ⚠️ Migração da 1.x — o que quebra e para onde foi',
            '',
            *(f'- {item}' for item in MIGRACAO[version]),
            '',
        ]
    linhas += [
        '## 📦 Downloads',
        f'- [`gp100-patches-v{version}.zip`] — biblioteca completa',
    ]
    for album in sorted(albums):
        slug = _slug(album)
        linhas.append(f'- [`gp100-patches-v{version}-{slug}.zip`] — {album}')
    linhas += [
        '',
        '## 📖 Como usar',
        '',
        '- Cada pasta traz `<NOME>.prst` (importar no aparelho) e `patch.md` '
        '(captador, ajustes finos, IR e modos de atuação).',
        '- Guia por álbum: `MAPA-DO-ALBUM.md` dentro de cada álbum do '
        '[repositório](../../blob/main/patches/README.md).',
        '',
    ]
    return '\n'.join(linhas)


def _slug(album: str) -> str:
    return re.sub(r'[^A-Za-z0-9._-]+', '_', album).strip('_')


def package(
    version: str,
    *,
    defs: dict[str, Any],
    patches_dir: Path,
    destino: Path,
) -> dict[str, Any]:
    """Gera os ZIPs (completo + por álbum) e as notas em `destino`.

    Devolve um relatório imprimível pela CLI (`{'completo': Path, 'zips': [...],
    'notas': Path, 'total': int, 'albums': {slug: n}}`); nenhuma impressão aqui.
    """
    validar_versao(version)
    destino.mkdir(parents=True, exist_ok=True)
    items = collect_patches(defs, patches_dir)
    if not items:
        raise ReleaseInvalida('Nenhum patch definido no defs — nada a empacotar.')

    albums: dict[str, list[tuple[Path, str]]] = {}
    for pasta, nome in items:
        rel = pasta.relative_to(patches_dir)
        album_dir = rel.parts[0] if len(rel.parts) > 1 else '(raiz)'
        albums.setdefault(album_dir, []).append((pasta, nome))

    # ---- pacote completo (valida cada .prst antes de entrar) ----
    completo = destino / f'gp100-patches-v{version}.zip'
    n = 0
    with zipfile.ZipFile(completo, 'w', zipfile.ZIP_DEFLATED) as z:
        for pasta, nome in items:
            assert_valid_prst(pasta / f'{nome}.prst', nome)
            arc = pasta.relative_to(patches_dir)
            z.write(pasta / f'{nome}.prst', arc / f'{nome}.prst')
            if (pasta / 'patch.md').exists():
                z.write(pasta / 'patch.md', arc / 'patch.md')
            n += 1

    # ---- um ZIP por álbum ----
    zips: list[tuple[Path, int]] = []
    for album, patches in sorted(albums.items()):
        alvo = destino / f'gp100-patches-v{version}-{_slug(album)}.zip'
        with zipfile.ZipFile(alvo, 'w', zipfile.ZIP_DEFLATED) as z:
            for pasta, nome in patches:
                assert_valid_prst(pasta / f'{nome}.prst', nome)
                arc = pasta.relative_to(patches_dir)
                z.write(pasta / f'{nome}.prst', arc / f'{nome}.prst')
                if (pasta / 'patch.md').exists():
                    z.write(pasta / 'patch.md', arc / 'patch.md')
        zips.append((alvo, len(patches)))

    # ---- notas da release ----
    n_songs = len(defs.get('songs', []))
    notas = destino / f'RELEASE-NOTES-v{version}.md'
    notas.write_text(
        notas_markdown(version, n, n_songs, {a: len(p) for a, p in albums.items()}),
        encoding='utf-8',
    )

    return {
        'completo': completo,
        'zips': zips,
        'notas': notas,
        'total': n,
        'albums': {a: len(p) for a, p in albums.items()},
    }
