"""chain.py — a cadeia fixa de módulos da GP-100, em UMA fonte.

Antes esta lista vivia copiada em 4 módulos (build_song_patches, defs_schema,
generate_prst, gp100) — e cópia inline vence a referência em silêncio quando
divergem (lição já documentada no gp100-patch-validator). Se o firmware 2.2
mudar a cadeia, muda AQUI e todos os consumidores seguem.

`EXPORT_ORDER` e `CHAIN_POS` NÃO vêm para cá: são particulares do formato
`.prst` (ordem de export do XML e posição na cadeia do preset) e vivem no
`generate_prst.py`.
"""

# ordem de sinal — é a ordem de exibição/validação em todos os consumidores
CHAIN = ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']
