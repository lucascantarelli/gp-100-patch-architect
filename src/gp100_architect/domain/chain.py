"""A cadeia fixa de módulos da GP-100 — fonte única do domínio.

Antes esta lista vivia copiada em quatro módulos (`build_song_patches`,
`defs_schema`, `generate_prst`, `gp100`) e o comentário do validador já
documentava o custo: *cópia inline vence a referência em silêncio quando
divergem*. O review do doc 21 (achado M1) consolidou tudo aqui.

Imutável por decisão: a ordem de sinal é uma regra do firmware, não um estado
de execução — `tuple` impede que um consumidor a mutile por acidente.

`EXPORT_ORDER` e `CHAIN_POS` NÃO vivem aqui: são particulares do formato
`.prst` (ordem de export do XML e índice na cadeia do preset) e pertencem à
camada de infraestrutura.
"""

__all__ = ['CHAIN', 'MODULOS_PROIBIDOS_EM_MOMENTO', 'nomeados', 'posicao', 'valido']

# ordem de sinal — exibição, validação e índice de escrita no .prst
CHAIN: tuple[str, ...] = ('PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB')

# módulos que nunca podem ser alternados ao vivo: ligar/desligar AMP ou CAB
# muda volume e corpo no meio da música (regra do doc 12)
MODULOS_PROIBIDOS_EM_MOMENTO: frozenset[str] = frozenset({'AMP', 'CAB'})


def posicao(modulo: str) -> int:
    """Índice do módulo na cadeia (−1 se não for módulo da GP-100)."""
    try:
        return CHAIN.index(modulo)
    except ValueError:
        return -1


def valido(modulo: str) -> bool:
    """O nome é um dos nove módulos da cadeia?"""
    return modulo in CHAIN


def nomeados(modulos: object) -> str:
    """Lista de módulos separada por vírgula — para mensagens acionáveis."""
    return ', '.join(CHAIN)
