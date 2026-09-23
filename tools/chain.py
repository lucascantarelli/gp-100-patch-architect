"""chain.py — SHIM de compatibilidade. A cadeia agora vive no pacote.

A implementação real é `gp100_architect.domain.chain` (fonte única, imutável). Este
arquivo existe só para os consumidores legados de `tools/`, que ainda importam
`from chain import CHAIN` e serão migrados para `gp100` em PKG-008 — quando o
último sair, este shim é removido junto com os demais.

Ele insere `src/` no `sys.path` para que `python tools/x.py` continue rodando
sem instalar o pacote: desenvolvimento dentro do repositório não deve exigir
`uv sync` só para executar um script.

Histórico: antes de PKG-001 esta lista estava copiada em quatro módulos; o
review do doc 21 (achado M1) consolidou a verdade, e agora ela mora onde o
domínio mora.
"""
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / 'src'
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from gp100_architect.domain.chain import CHAIN  # noqa: E402,F401
