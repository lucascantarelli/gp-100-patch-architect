"""
build_release.py — Empacota a biblioteca para a Release do GitHub.

Uso:
  python tools/build_release.py                # lê a versão de VERSION e empacota em dist/
  python tools/build_release.py 1.2.3          # valida a versão e empacota (sem tocar em VERSION)

Saídas (dist/):
  gp100-patches-v<versão>.zip          — TODOS os .prst prontos para importar (por álbum/pasta)
  gp100-patches-v<versão>-<album>.zip  — um ZIP por álbum (nome da pasta sem espaços)
  RELEASE-NOTES-v<versão>.md           — notas prontas para `gh release create --notes-file`

O que vai em cada ZIP: apenas os arquivos que o músico precisa — `<NOME>.prst` e
`patch.md` de cada patch, na estrutura `<Banda>/<Álbum>/<Música>/`. O `spec.json`
intermediário nem é empacotado nem versionado. Os `.prst` são validados antes de entrar
no pacote (formato single, firmware 2.1 — o mesmo check da suíte).

A versão é sempre validada como SemVer (`MAIOR.MENOR.PATCH`); `VERSION` é a
fonte única usada pelo CI (job release) e por quem empacota localmente.
"""
import re
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
VERSION_FILE = ROOT / 'VERSION'          # única fonte da versão (ex.: 1.0.0)
DEFS_FILE = ROOT / 'tools' / 'patches-defs.json'   # única fonte da BIBLIOTECA
DIST_DIR = ROOT / 'dist'                 # saída do empacotamento (não vai pro git)
PATCHES_DIR = ROOT / 'patches'

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')


def read_version() -> str:
    """Lê VERSION (fonte única) e devolve a versão validada."""
    if not VERSION_FILE.exists():
        raise SystemExit('VERSION não existe — crie com a versão atual (ex.: 1.0.0).')
    version = VERSION_FILE.read_text(encoding='utf-8').strip()
    if not SEMVER_RE.match(version):
        raise SystemExit(f"VERSION inválida: '{version}' — use SemVer (ex.: 1.0.0).")
    return version


def bump(version: str, part: str) -> str:
    """Sobe um componente do SemVer (major/minor/patch)."""
    major, minor, patch = (int(n) for n in version.split('.'))
    return {
        'major': f'{major + 1}.0.0',
        'minor': f'{major}.{minor + 1}.0',
        'patch': f'{major}.{minor}.{patch + 1}',
    }[part]


def collect_patches():
    """Todos os patches da biblioteca: [(caminho_da_pasta, nome_do_patch)].

    A lista vem do DEFS, não do disco: quem define a pasta de cada patch é ele
    (`albums[].pasta` + `songs[].pasta|song` + `patch.nome`). A versão anterior
    usava `rglob('spec.json')` — e como o `spec.json` é intermediário gerado pelo
    pipeline, num clone limpo (é o que o job de release tem, já que ele não roda o
    pipeline) a lista sairia VAZIA e a release não empacotaria nada.
    """
    # validação acionável também no empacotamento (review doc 21, M2): a
    # release não pode sair de um defs quebrado
    from defs_schema import carregar_e_validar
    defs = carregar_e_validar(DEFS_FILE)
    items = []
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]['pasta']
        musica = song.get('pasta') or song['song']
        for patch in song['patches']:
            pasta = PATCHES_DIR / album / musica / patch['nome']
            items.append((pasta, patch['nome']))
    return items


def assert_valid_prst(path: Path, nome: str):
    """Confere o mínimo do formato single fw 2.1 antes de entrar no pacote.

    O `ppName` é atributo do elemento `<presets>` (não tem elemento `<ppName>`):
    confere por regex com fronteira, para não pegar `ppNameXYZ`.
    """
    text = path.read_text(encoding='utf-8', errors='replace')
    if not re.search(rf'ppName="{re.escape(nome)}"', text):
        raise SystemExit(f'{path}: ppName não confere com a pasta ({nome}).')
    if 'firmware="2.1"' not in text:
        raise SystemExit(f'{path}: formato inesperado (esperado firmware 2.1).')


def package(version: str):
    """Gera os ZIPs (completo + por álbum) e as notas da release em dist/."""
    DIST_DIR.mkdir(exist_ok=True)
    items = collect_patches()
    if not items:
        raise SystemExit('Nenhum patch encontrado — rode o pipeline antes de empacotar.')

    albums = {}
    for pasta, nome in items:
        rel = pasta.relative_to(PATCHES_DIR)
        album_dir = rel.parts[0] if len(rel.parts) > 1 else '(raiz)'
        albums.setdefault(album_dir, []).append((pasta, nome))

    # ---- pacote completo ----
    completo = DIST_DIR / f'gp100-patches-v{version}.zip'
    with zipfile.ZipFile(completo, 'w', zipfile.ZIP_DEFLATED) as z:
        n = 0
        for pasta, nome in items:
            assert_valid_prst(pasta / f'{nome}.prst', nome)
            arc = pasta.relative_to(PATCHES_DIR)
            z.write(pasta / f'{nome}.prst', arc / f'{nome}.prst')
            if (pasta / 'patch.md').exists():
                z.write(pasta / 'patch.md', arc / 'patch.md')
            n += 1
    print(f'  📦 {completo.name}: {n} patches (com patch.md)')

    # ---- um ZIP por álbum ----
    for album, patches in sorted(albums.items()):
        slug = re.sub(r'[^A-Za-z0-9._-]+', '_', album).strip('_')
        alvo = DIST_DIR / f'gp100-patches-v{version}-{slug}.zip'
        with zipfile.ZipFile(alvo, 'w', zipfile.ZIP_DEFLATED) as z:
            for pasta, nome in patches:
                assert_valid_prst(pasta / f'{nome}.prst', nome)
                arc = pasta.relative_to(PATCHES_DIR)
                z.write(pasta / f'{nome}.prst', arc / f'{nome}.prst')
                if (pasta / 'patch.md').exists():
                    z.write(pasta / 'patch.md', arc / 'patch.md')
        print(f'  📦 {alvo.name}: {len(patches)} patches')

    # ---- notas da release ----
    from defs_schema import carregar_e_validar
    defs = carregar_e_validar(DEFS_FILE)
    n_songs = len(defs.get('songs', []))
    linhas = [
        f'# GP-100 Patches v{version}', '',
        f'**{n} patches · {n_songs} músicas · {len(albums)} álbuns** — formato single, '
        'firmware 2.1, prontos para importar no aparelho (SYSTEM → USB → Import).', '',
        '## 📦 Downloads',
        f'- [`gp100-patches-v{version}.zip`] — biblioteca completa',
    ]
    for album in sorted(albums):
        slug = re.sub(r'[^A-Za-z0-9._-]+', '_', album).strip('_')
        linhas.append(f'- [`gp100-patches-v{version}-{slug}.zip`] — {album}')
    linhas += ['', '## 📖 Como usar', '',
               '- Cada pasta traz `<NOME>.prst` (importar no aparelho) e `patch.md` '
               '(captador, ajustes finos, IR e modos de atuação).',
               '- Guia por álbum: `MAPA-DO-ALBUM.md` dentro de cada álbum do '
               '[repositório](../../blob/main/patches/README.md).', '']
    notas = DIST_DIR / f'RELEASE-NOTES-v{version}.md'
    notas.write_text('\n'.join(linhas), encoding='utf-8')
    print(f'  📝 {notas.name}')


def main():
    """Valida a versão (arg ou VERSION) e empacota tudo em dist/."""
    if len(sys.argv) > 1:
        version = sys.argv[1]
        if not SEMVER_RE.match(version):
            raise SystemExit(f"Versão inválida: '{version}' — use SemVer (ex.: 1.2.3).")
    else:
        version = read_version()
    print(f'🚀 Empacotando v{version}:')
    package(version)
    print('✅ Pacotes em dist/ (não versionar — o CI publica na Release).')


if __name__ == '__main__':
    main()
