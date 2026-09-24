# 🤖 Agentes — configuração do Freebuff

Os 19 agentes deste projeto são carregados automaticamente pelo Freebuff (CLI, Desktop ou Web) ao abrir a pasta — não há chave, registro nem setup além do `npm install -g freebuff`. O modelo padrão é **GLM 5.3 Flash** (`z-ai/glm-5.3-flash`).

## 🧩 Skills (Agent Skills)

O projeto também versiona **11 skills** em [`skills/`](skills/) (formato pasta + `SKILL.md`): 4 do GP-100 (`gp100-criar-patch`, `gp100-por-referencia`, `gp100-ajustar-patch`, `gp100-sugerir-timbres` — a forma executável dos fluxos de `prompts/`) e 7 genéricas curadas (brainstorming, writing-plans, finishing-a-development-branch, github-actions-docs, python-testing-patterns, documentation-writer, frontend-design). Inventário, vereditos e precedência: [`reference/23-skills-curation.md`](../reference/23-skills-curation.md).

## 🏗️ Arquitetura

```
                 ┌──────────────────────────────┐
                 │  gp100-patch-architect       │  ← orquestrador: entrevista, pesquisa
                 │  (agente-mestre)             │    o rig real e distribui o trabalho
                 └──────────────┬───────────────┘
        spawn em paralelo ↓↓↓   (uma skill por bloco da cadeia)
┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
│ pre  │ dst  │ amp  │cab-ir│  eq  │ mod  │  nr  │ dly  │ rvb  │  ← skills de efeito:
│      │      │      │      │      │      │      │      │      │    params, ranges, evite, sugestões
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
                 ↓ apoio (invocadas conforme o fluxo)
┌────────────────┬────────────────┬────────────────┬───────────────────┐
│ tone-research  │  tone-mapper   │ ir-research/   │ patch-validator + │
│ (rig real,     │  (rig → GP-100)│ ir-fit +       │ ab-tester +       │
│ fontes, época) │                │ globals        │ setlist           │
└────────────────┴────────────────┴────────────────┴───────────────────┘
```

## 📄 Arquivos

| Agente | Papel |
|---|---|
| `gp100-patch-architect.ts` | **Orquestrador** — fluxo completo: entrevista → cadeia → skills em paralelo → validação → documentação |
| `gp100-pre.ts` | Bloco PRE: COMP, COMP4, Boost, wahs, OCTA |
| `gp100-dst.ts` | Bloco DST: overdrives, distorções, fuzz do fw 2.0 |
| `gp100-amp.ts` | Bloco AMP: modelos de amp reais do catálogo fw 2.0 |
| `gp100-cab-ir.ts` | Bloco CAB + política de IR (fábrica → banco local → internet → fallback) |
| `gp100-eq.ts` | Bloco EQ |
| `gp100-mod.ts` | Bloco MOD (chorus, tremolo, phaser, vibe…) |
| `gp100-nr.ts` | Bloco NR (gates) — regra de ganho ≥ 55 |
| `gp100-dly.ts` | Bloco DLY (delays) |
| `gp100-rvb.ts` | Bloco RVB (reverbs) |
| `gp100-globals.ts` | Configurações globais da pedaleira (master, tuner, footswitches PATCH/STOMP etc.) |
| `gp100-tone-research.ts` | Pesquisa do rig real do artista/música com fontes |
| `gp100-tone-mapper.ts` | Mapeamento rig real → modelos da GP-100 |
| `gp100-ir-research.ts` | Pesquisa de IRs na internet + catálogo de packs gratuitos |
| `gp100-ir-fit.ts` | Ajuste fino de IR (Low/High Cut, Level) |
| `gp100-manual-reader.ts` | Consulta ao manual V1.8 e ao catálogo fw 2.0 |
| `gp100-patch-validator.ts` | Validação técnica e documental do patch |
| `gp100-ab-tester.ts` | A/B pós-criação: entrevista guiada pelo protocolo universal (doc 12), mudanças mínimas |
| `gp100-setlist.ts` | Cola de palco: ordem de slots do repertório via `gp100 setlist` (CLI do pacote) |

## ➕ Como criar um agente novo

1. Copie um `.ts` existente como modelo — a definição tipada está em [`types/agent-definition.ts`](types/agent-definition.ts) (campos: `id`, `displayName`, `model`, `toolNames`, `spawnableAgents`, `whenToUse`, `systemPrompt`).
2. Declare o novo id no `spawnableAgents` do orquestrador.
3. Valide com `tsc --noEmit` (o `tsconfig.json` da raiz inclui `.agents/**/*.ts`).

> **Regras compartilhadas** (nomenclatura de patches, política de IR, toggle/Modos de atuação, formato dos docs) vivem no [`knowledge.md`](../knowledge.md) — todos os agentes o consultam.

---

[`📖 README do projeto`](../README.md) · [`📚 Reference`](../reference/) · [`🎸 patches/`](../patches/README.md)
