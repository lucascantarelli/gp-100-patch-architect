"""Prepara a árvore de build do site de docs (issue #60).

O MkDocs exige `docs_dir` FORA da raiz, mas a doc CRUZA pastas (`reference/` ↔
`docs/` ↔ md de topo). Este script monta `docs/_site/` com a MESMA organização
de caminhos do repositório — por CÓPIA, regenerada do zero a cada build:

  * a origem única é o repositório (ADR-0007) — o `_site` é artefato de build
    descartável, gitignored, e no CI nasce do checkout fresco a cada deploy;
    não há cópia VIVA para divergir (o risco que a #58 caça é duplicação
    editável, não cópia efêmera regenerada);
  * junções/symlinks não bastam: o descobridor de arquivos do MkDocs não as
    segue no Windows.

Uso:  uv run python scripts/prep_docs.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ALVO = RAIZ / 'docs' / '_site'
MD_TOPO = [
    'README.md',
    'ARCHITECTURE.md',
    'DEVELOPMENT.md',
    'CONTRIBUTING.md',
    'SECURITY.md',
    'CODE_OF_CONDUCT.md',
    'NOTICE.md',
    'CHANGELOG.md',
    'knowledge.md',
    'master_prompt.md',
]


def main() -> int:
    if ALVO.exists():
        shutil.rmtree(ALVO)
    ALVO.mkdir(parents=True)

    # pastas inteiras na MESMA posição relativa do repo — os links cruzados
    # dos md resolvem sem reescrever nada
    shutil.copytree(RAIZ / 'reference', ALVO / 'reference')
    docs = ALVO / 'docs'
    docs.mkdir()
    shutil.copytree(RAIZ / 'docs' / 'decisions', docs / 'decisions')

    # md soltos de docs/ (roadmap, auditorias)
    for f in (RAIZ / 'docs').glob('*.md'):
        shutil.copy2(f, docs / f.name)

    # md de topo (entrada da doc)
    for nome in MD_TOPO:
        if (RAIZ / nome).exists():
            shutil.copy2(RAIZ / nome, ALVO / nome)

    total = sum(1 for _ in ALVO.rglob('*.md'))
    print(f'docs/_site pronto — {total} páginas copiadas do fonte')
    return 0


if __name__ == '__main__':
    sys.exit(main())
