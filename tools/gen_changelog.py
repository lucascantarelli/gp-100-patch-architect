#!/usr/bin/env python3
"""gen_changelog.py — shim de CLI do changelog (issue #32).

A implementação vive em `src/gp100_architect/application/changelog.py`; este
arquivo fica com a cara de terminal: resolve argv, imprime e traduz erros em
saída acionável. Os nomes públicos (`COMMIT_RE`, `BREAKING_FOOTER`, `SKIP`,
`SECOES`, `VISIVEIS`, `coletar`, `bump_sugerido`, `secao`,
`escrever_no_changelog`) continuam aqui por compatibilidade da suíte legada —
a remoção é a #33.

Uso:
  python tools/gen_changelog.py                       # prévia + bump sugerido
  python tools/gen_changelog.py --version 1.1.0       # seção da versão p/ stdout
  python tools/gen_changelog.py --version 1.1.0 --write   # prepende no CHANGELOG.md
  python tools/gen_changelog.py --version 1.1.0 --out dist/notas.md   # seção em arquivo
  python tools/gen_changelog.py --all                 # inclui chore/ci/test (ruído)
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.application import changelog  # noqa: E402

CHANGELOG = ROOT / 'CHANGELOG.md'

# compatibilidade da suíte legada (os nomes moram na biblioteca agora)
COMMIT_RE = changelog.COMMIT_RE
BREAKING_FOOTER = changelog.BREAKING_FOOTER
SKIP = changelog.SKIP
SECOES = changelog.SECOES
VISIVEIS = changelog.VISIVEIS
bump_sugerido = changelog.bump_sugerido
secao = changelog.secao
coletar_do_log = changelog.coletar_do_log


def coletar(desde: str | None):
    """[(tipo, escopo, desc, breaking_note, breaking)] desde a tag — assinatura legada."""
    return changelog.coletar(desde, raiz=ROOT)


def ler_versao_atual(raiz: Path | None = None) -> str:
    """Versão de VERSION ('0.0.0' se ausente) — raiz default: este repositório."""
    return changelog.ler_versao_atual(raiz or ROOT)


def ultima_tag() -> str | None:
    return changelog.ultima_tag(ROOT)


def git(*args) -> str:
    return changelog.git(*args, raiz=ROOT)


def escrever_no_changelog(bloco: str, version: str):
    """Escreve no CHANGELOG.md do repositório (assinatura legada, caminho resolvido aqui)."""
    changelog.escrever_no_changelog(bloco, version, CHANGELOG)


def main():
    """Monta a seção da versão e imprime, grava em arquivo ou prepende no changelog."""
    incluir_ocultos = '--all' in sys.argv
    itens = coletar(ultima_tag())

    version = None
    if '--version' in sys.argv:
        version = sys.argv[sys.argv.index('--version') + 1]
        import re

        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise SystemExit(f"Versão inválida: '{version}' — use SemVer (ex.: 1.1.0).")
    if version is None:
        version = bump_sugerido(itens, ler_versao_atual())

    bloco = secao(version, itens, incluir_ocultos)

    if '--write' in sys.argv:
        escrever_no_changelog(bloco, version)
        print(
            f'✅ CHANGELOG.md: seção [{version}] prependida '
            f'({len(itens)} commit(s) desde {ultima_tag() or "o início"}).'
        )
    elif '--out' in sys.argv:
        destino = ROOT / sys.argv[sys.argv.index('--out') + 1]
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(bloco, encoding='utf-8')
        print(f'✅ {destino.relative_to(ROOT).as_posix()}')
    else:
        print(bloco)
        print(
            f'--- {len(itens)} commit(s) desde {ultima_tag() or "o início da história"}'
            f' · bump sugerido: v{bump_sugerido(itens, ler_versao_atual())}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
