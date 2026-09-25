"""Camada de domínio — regras puras da GP-100.

Nada aqui importa `typer`, `rich`, `pathlib` de I/O ou toca arquivos. É a
camada que qualquer interface (CLI, API, UI) pode chamar sem efeito colateral.

Convenção de import: direto do submodule (`from gp100_architect.domain.chain
import CHAIN`) — este `__init__` não reexporta símbolos.
"""
