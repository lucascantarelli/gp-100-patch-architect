---
name: gp100-por-referencia
description: "Use quando o usuário quiser um patch GP-100 baseado em artista/música real (ex.: Pink Floyd — 'Time'). Dispara o fluxo gp100-tone-research (pesquisa web dos equipamentos reais) → gp100-tone-mapper (tradução para modelos da GP-100) → gp100-patch-architect (montagem, validação e persistência)."
---

# Criar patch GP-100 com referência (artista/música)

Para que o agente pesquise os equipamentos reais e transforme em patch GP-100:

```
Criar patch GP-100 com referência

Artista/música: {ex.: Pink Floyd — "Time" (solo) · The Strokes — timbre geral do Is This It}
O que quero extrair: {o riff / o solo / o timbre geral / só o delay}
Captador que usarei: {bridge / middle / neck}
Contexto: {gravar em casa com fone / banda / prática}
Liberdade de adaptação: {fiel ao máximo / pode adaptar para a Strat}
IR de terceiros: {quero IR / CAB de fábrica}
```

O agente então:
1. `gp100-tone-research` — pesquisa na internet guitarra, amps, cabines e pedais usados naquela música/era (com fontes e nível de confiança).
2. `gp100-tone-mapper` — traduz cada equipamento real para os modelos reais da GP-100 (fw 2.0), com similaridade e parâmetros.
3. `gp100-patch-architect` — monta, valida e **persiste o patch em `tools/defs/`** (fragmento do álbum); o `patch.md` e o `.prst` saem do pipeline.

Exemplo preenchido:
```
Criar patch GP-100 com referência
Artista/música: John Mayer — "Slow Dancing in a Burning Room" (ao vivo, Where the Light Is)
O que quero extrair: timbre do solo (clean quente com leve breakup)
Captador: neck
Contexto: gravar em casa com fone
Liberdade: pode adaptar para Strat single coil
IR: CAB de fábrica
```

**Dica**: quanto mais específica a referência (música + era/álbum/ao vivo), melhor a pesquisa. "Queen em geral" é vago; "Queen — Bohemian Rhapsody, solo de ópera-rock, 1975, studio" gera dossiê preciso.

> **Precedência**: dentro do projeto GP-100 Patch Architect, `knowledge.md` e
> `reference/` vencem esta skill. Fonte canônica do fluxo:
> `prompts/pesquisar-referencia.md` no repositório. Régua de qualidade das
> cadeias esperadas: `reference/20-golden-set.md`.
