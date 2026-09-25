# 📚 Reference — base de conhecimento da GP-100

Tudo que os agentes consultam antes de propor um patch. **Fontes na ordem de precedência:**

1. **Catálogo empírico do firmware 2.0/2.1** (`15`) — extraído do export de fábrica do próprio aparelho (dados brutos em `data/factory-catalog.json`; export original removido na limpeza). Os **nomes reais** dos modelos (`Blues OD`, `Dark Twin`, `DarkTW 2x12`, `Spring`…) vêm daqui e **vencem** qualquer outro documento.
2. **Manual impresso V1.8** (`01`–`10`, `14`) — transcrição página a página de `manual.pdf` (páginas renderizadas sob demanda: `gp100 manual-page <impressa>`). Serve para conceito, técnica e sugestões de uso; nomes divergentes perdem para o catálogo.
3. **Biblioteca local de IRs** (`16`) — gerada pelo pipeline (`gp100 build`) a partir de `impulse_responses/`.

## 📄 Documentos

| # | Documento | Conteúdo |
|---|---|---|
| 00 | `00-signal-chain.md` | Visão geral da cadeia de sinal (PRE → DST → AMP → NR → CAB → EQ → MOD → DLY → RVB) |
| 01 | `01-pre.md` | Módulo PRE: COMP/COMP4, Boost, wahs, OCTA — params e uso |
| 02 | `02-dst.md` | Módulo DST: overdrives, distorções e fuzz |
| 03 | `03-amp.md` | Módulo AMP: modelos de amp, ganho e EQ |
| 04 | `04-cab-ir.md` | Módulo CAB: gabinetes de fábrica e User IR |
| 05 | `05-eq.md` | Módulo EQ |
| 06 | `06-mod.md` | Módulo MOD: chorus, tremolo, phaser, vibe… |
| 07 | `07-nr.md` | Módulo NR: gates (regra: ganho ≥ 55) |
| 08 | `08-dly.md` | Módulo DLY: delays |
| 09 | `09-rvb.md` | Módulo RVB: reverbs |
| 10 | `10-globals.md` | Configurações globais (master volume, tuner, etc.) |
| 11 | `11-ir-guide.md` | Guia de Impulse Response na GP-100 (formato, slots, cortes) |
| 12 | `12-workflow.md` | Workflow de criação de patch (do pedido ao `.prst`) |
| 13 | `13-preset-list.md` | Os 99 presets de fábrica |
| 14 | `14-glossario.md` | Glossário de termos de áudio e da pedaleira |
| 15 | `15-firmware2-effects.md` | ⭐ **Catálogo real fw 2.0/2.1** — nomes, effectCodes e contagem de params |
| 16 | `16-ir-library.md` | Catálogo do banco local de IRs (gerado — rode `uv run gp100 build` após baixar packs) |
| 17 | `17-free-ir-packs.md` | Packs de IR gratuitos na internet, por lacuna da biblioteca |
| 18 | `18-project-management.md` | 🗂 Gestão de projetos: Project v2, milestones, taxonomia de labels e fluxo PR-driven (issue → PR → release) |
| 19 | `19-roadmap-v2.md` | 🗺 Roadmap da v2.0: schema v2 do defs, CLI unificada, site estático e meta de 100+ patches |
| 20 | `20-golden-set.md` | 🥇 Golden set: 20 músicas/43 patches canônicos como régua de avaliação dos agentes de pesquisa |
| 21 | `21-code-review.md` | 🔍 Code review do código Python: forças, achados (M/B) e proposta do agente gp100-code-reviewer |
| 22 | `22-dead-code-analysis.md` | 🧹 Análise de código obsoleto/morto: método, achados corrigidos e prevenção |
| 23 | `23-skills-curation.md` | 🧩 Curadoria das skills globais: vereditos, precedência e decisão pytest da 2.0 |
| 24 | `24-import-all.md` | 📦 Import "all" da GP-100: formato `.prst` multi-preset, comando para gerar candidatos e protocolo físico da #83 |

> `16` e `17` foram criados depois do manual; `15` é a ponte entre os nomes do manual V1.8 e os nomes reais do firmware. `18` não é sobre som — é sobre como o repositório se gerencia; `19` é o plano do próximo major.

---

[`📖 README do projeto`](../README.md) · [`🤖 Agentes`](../.agents/README.md) · [`🎸 patches/`](https://lucascantarelli.github.io/gp-100-patch-architect/)
