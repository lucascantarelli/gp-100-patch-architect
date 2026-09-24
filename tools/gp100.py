#!/usr/bin/env python3
"""gp100.py — shim de compatibilidade da CLI unificada (issues #48/#49).

A CLI oficial agora é a do **pacote**: `uv run gp100 <comando>` (entry point
`gp100_architect.interfaces.cli.main:app`, Typer). Os casos de uso vivem em
`src/gp100_architect/application/` (consulta, setlist, release, changelog) e
as regras, em `domain/`. Este arquivo só repassa os argumentos — existe para
não quebrar quem ainda chama `python tools/gp100.py ...` (agentes, docs,
músculo memória); a remoção é a issue #33, quando o último consumidor migrar.

Comandos (os mesmos, agora com `--json` estável e `--quiet`):

  find <termo>        busca por música/artista/álbum/captador/camada/nome
  show <NOME>         resumo do patch (cadeia, params, momentos, stomps, IR)
  diff <A> <B>        diff legível entre dois patches
  export [--album ID | NOMES...] [--destino D] [--listar]
  build [--quiet]     roda o pipeline completo (ordem do guarda de sincronia)
  verify [--quiet]    roda a suíte de testes (a mesma do CI)
"""
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if _stream.encoding and _stream.encoding.lower() != 'utf-8':
        _stream.reconfigure(encoding='utf-8')  # console Windows (cp1252)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))

from gp100_architect.interfaces.cli.main import app  # noqa: E402

if __name__ == '__main__':
    app(sys.argv[1:])
