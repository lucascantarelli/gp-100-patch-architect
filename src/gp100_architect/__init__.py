"""gp100-patch-architect — núcleo da biblioteca de patches da Valeton GP-100.

O import name é `gp100_architect` (e não `gp100`) porque o script legado
`tools/gp100.py`, ainda documentado, sombreia qualquer pacote chamado `gp100`
sempre que `tools/` entra no `sys.path` — ver ADR-0001. Quando o legado sair em
PKG-008, o nome pode ser revisto sem impacto em quem consome a CLI (`gp100`).

Arquitetura em camadas pragmáticas (ADR-0002):

    domain          regras puras — sem I/O, sem dependências externas
    application     casos de uso (orquestram domain + infrastructure)
    infrastructure  I/O: defs JSON, formato .prst, zip de release
    interfaces      entrada: CLI (Typer) hoje, API/UI na 2.1

Importar o pacote não toca o disco: o carregamento do defs acontece
explicitamente em `gp100_architect.infrastructure`, nunca na importação.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version
from pathlib import Path

__all__ = ['__version__']

try:  # pacote instalado (uv sync) — metadado é a fonte quando existe
    __version__ = _version('gp100-patch-architect')
except PackageNotFoundError:  # execução direta do fonte, sem instalar
    _arquivo = Path(__file__).resolve().parents[2] / 'VERSION'
    __version__ = _arquivo.read_text(encoding='utf-8').strip() if _arquivo.exists() else '0.0.0'
