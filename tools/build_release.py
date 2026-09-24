"""
build_release.py — shim de CLI do empacotamento (issue #32).

A implementação vive em `src/gp100_architect/application/release.py` (biblioteca
sem `print`/`SystemExit`, com `ReleaseInvalida`); este arquivo fica com a cara
de terminal: resolve raiz, imprime e traduz erros de domínio em saída acionável
(código 1). Os nomes públicos (`read_version`, `bump`, `collect_patches`,
`assert_valid_prst`, `package`) continuam aqui por compatibilidade da suíte
legada e dos consumidores — a remoção é a #33.

Uso:
  python tools/build_release.py                # lê a versão de VERSION e empacota em dist/
  python tools/build_release.py 1.2.3          # valida a versão e empacota (sem tocar em VERSION)
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.application import release  # noqa: E402
from gp100_architect.domain.errors import Gp100Error  # noqa: E402
from gp100_architect.infrastructure.defs import carregar_e_validar  # noqa: E402

VERSION_FILE = ROOT / 'VERSION'  # única fonte da versão (compatibilidade)
DIST_DIR = ROOT / 'dist'  # saída do empacotamento (não vai pro git)
PATCHES_DIR = ROOT / 'patches'
DEFS_FILE = ROOT / 'tools' / 'defs'


def read_version() -> str:
    """Lê VERSION (fonte única) e devolve a versão validada (ReleaseInvalida → SystemExit).

    Lê o global `VERSION_FILE` na chamada (compatibilidade da suíte legada, que
    o substitui por um caminho falso para testar a rejeição de não-SemVer).
    """
    if not VERSION_FILE.exists():
        raise SystemExit('VERSION não existe — crie com a versão atual (ex.: 1.0.0).')
    try:
        return release.validar_versao(VERSION_FILE.read_text(encoding='utf-8').strip())
    except Gp100Error as erro:
        raise SystemExit(str(erro)) from erro


def bump(version: str, part: str) -> str:
    """Sobe um componente do SemVer (major/minor/patch)."""
    return release.bump(version, part)


def collect_patches():
    """Todos os patches da biblioteca: [(pasta, nome)] — defs validado primeiro."""
    defs = carregar_e_validar(DEFS_FILE)
    return release.collect_patches(defs, PATCHES_DIR)


def assert_valid_prst(path: Path, nome: str):
    """Confere o formato single fw 2.1 (ReleaseInvalida → SystemExit)."""
    try:
        release.assert_valid_prst(path, nome)
    except Gp100Error as erro:
        raise SystemExit(str(erro)) from erro


def package(version: str):
    """Gera os ZIPs e as notas em dist/ (imprime o relatório da biblioteca)."""
    try:
        defs = carregar_e_validar(DEFS_FILE)
        relatorio = release.package(version, defs=defs, patches_dir=PATCHES_DIR, destino=DIST_DIR)
    except Gp100Error as erro:
        raise SystemExit(str(erro)) from erro
    print(f'  📦 {relatorio["completo"].name}: {relatorio["total"]} patches (com patch.md)')
    for alvo, n in relatorio['zips']:
        print(f'  📦 {alvo.name}: {n} patches')
    print(f'  📝 {relatorio["notas"].name}')


def main():
    """Valida a versão (arg ou VERSION) e empacota tudo em dist/."""
    if len(sys.argv) > 1:
        try:
            version = release.validar_versao(sys.argv[1])
        except Gp100Error as erro:
            raise SystemExit(str(erro)) from erro
    else:
        version = read_version()
    print(f'🚀 Empacotando v{version}:')
    package(version)
    print('✅ Pacotes em dist/ (não versionar — o CI publica na Release).')


if __name__ == '__main__':
    main()
