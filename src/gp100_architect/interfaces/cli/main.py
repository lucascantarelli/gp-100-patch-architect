"""CLI oficial — a porta de entrada única do projeto.

Regra do adaptador: **nenhuma regra vive aqui**. O comando monta o caminho,
chama o caso de uso e traduz o resultado em texto, código de saída e cor. É o
que permite a API da 2.1 expor exatamente o mesmo comportamento.

Códigos de saída (contrato para automação, como hoje em `tools/`):
    0  sucesso
    1  entrada inválida (defs quebrado, argumento errado)
    2  erro de uso da CLI (o próprio Typer emite)
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TextIO

import typer
from rich.console import Console

from gp100_architect import __version__
from gp100_architect.domain.errors import Gp100Error
from gp100_architect.infrastructure.defs import DEFS_PADRAO, carregar_e_validar

app = typer.Typer(
    name='gp100',
    help='Biblioteca de patches da Valeton GP-100: validação, índices e release.',
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode='rich',
)
console = Console()
err_console = Console(stderr=True)


def _tolerante_a_encoding(stream: TextIO) -> None:
    """Um caractere que o console não escreve não pode virar traceback.

    No console legado do Windows (cp1252) um emoji de relatório derruba o
    comando com `UnicodeEncodeError` — e o usuário vê stack trace em vez de
    diagnóstico. Aqui a codificação falha para 'replace': acento (que o cp1252
    escreve) continua legível e o ideograma vira '?'. O CI e os testes usam
    stream de texto puro, que não tem `reconfigure` — por isso o getattr.
    """
    reconfigure = getattr(stream, 'reconfigure', None)
    if callable(reconfigure):
        reconfigure(errors='replace')


_tolerante_a_encoding(sys.stdout)
_tolerante_a_encoding(sys.stderr)


def _versao(valor: bool) -> None:
    """`--version` responde e sai antes de qualquer outro trabalho."""
    if valor:
        console.print(f'gp100-patch-architect {__version__}')
        raise typer.Exit()


@app.callback()
def principal(
    version: bool = typer.Option(
        False,
        '--version',
        '-V',
        callback=_versao,
        is_eager=True,
        help='Mostra a versão instalada e sai.',
    ),
) -> None:
    """Ferramentas oficiais da biblioteca GP-100."""


@app.command()
def version() -> None:
    """Mostra a versão instalada."""
    console.print(__version__)


@app.command()
def validate(
    defs: Path | None = typer.Argument(
        None,
        help='Caminho do patches-defs.json (padrão: tools/patches-defs.json).',
    ),
) -> None:
    """Valida o patches-defs.json e sai com 0 (válido) ou 1 (problemas)."""
    try:
        dados = carregar_e_validar(defs)
    except Gp100Error as erro:
        err_console.print(str(erro))
        raise typer.Exit(code=1) from erro
    songs = dados.get('songs') or []
    patches = sum(len(s.get('patches') or []) for s in songs)
    # Texto sem ideograma de propósito: a saída da CLI tem de ser escrevível em
    # qualquer console que o projeto suporta (há teste para isso).
    console.print(
        f'[green]{(defs or DEFS_PADRAO).name} válido[/green] — '
        f'{len(songs)} músicas, {patches} patches, {len(dados.get("albums") or {})} álbuns'
    )


if __name__ == '__main__':  # python -m gp100_architect.interfaces.cli.main
    app()
