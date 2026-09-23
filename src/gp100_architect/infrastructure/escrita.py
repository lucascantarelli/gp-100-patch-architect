"""Escrita de artefatos — o único lugar que toca o disco para gerar saída.

Os casos de uso da camada de aplicação devolvem conteúdo **em memória** (texto
ou bytes); quem grava é este módulo. A separação é o que permite testar a
geração inteira sem tmpdir e o que evitou, na migração da issue #30, que cada
shim tivesse a sua própria forma de escrever (e de errar o fim de linha).

Regras do formato que a escrita preserva:

* `.prst` — bytes exatos do codec (CRLF inclusive): nunca passar por
  `write_text`, que traduziria o fim de linha;
* documentos `.md` da biblioteca — CRLF (`crlf=True`), o que o GitHub renderiza
  igual e o que já está commitado;
* manifestos `.json` — LF, sem `crlf`.

Camada: infrastructure.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ['escrever_bytes', 'escrever_texto']


def escrever_bytes(caminho: Path, dados: bytes) -> None:
    """Grava bytes crus, criando as pastas que faltarem."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(dados)


def escrever_texto(caminho: Path, texto: str, *, crlf: bool = False) -> None:
    """Grava texto UTF-8, criando as pastas que faltarem.

    `crlf=True` escreve fim de linha do Windows (o padrão dos documentos da
    biblioteca, que são commitados assim).
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding='utf-8', newline='\r\n' if crlf else '\n')
