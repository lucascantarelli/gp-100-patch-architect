# 📚 Reference — base de conhecimento da GP-100

Tudo que os agentes consultam antes de propor um patch. **Fontes na ordem de precedência:**

1. **Catálogo empírico do firmware 2.0/2.1** (`15`) — extraído do export de fábrica do próprio aparelho (dados brutos em `tools/factory-catalog.json`; export original removido na limpeza). Os **nomes reais** dos modelos (`Blues OD`, `Dark Twin`, `DarkTW 2x12`, `Spring`…) vêm daqui e **vencem** qualquer outro documento.
2. **Manual impresso V1.8** (`01`–`10`, `14`) — transcrição página a página de `manual.pdf` (páginas renderizadas sob demanda: `python tools/render_manual_page.py <impressa>`). Serve para conceito, técnica e sugestões de uso; nomes divergentes perdem para o catálogo.
3. **Biblioteca local de IRs** (`16`) — gerada por `tools/ir_library.py` a partir de `impulse_responses/`.

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
| 16 | `16-ir-library.md` | Catálogo do banco local de IRs (gerado — rode `tools/ir_library.py` após baixar packs) |
| 17 | `17-free-ir-packs.md` | Packs de IR gratuitos na internet, por lacuna da biblioteca |

> `16` e `17` foram criados depois do manual; `15` é a ponte entre os nomes do manual V1.8 e os nomes reais do firmware.

---

[`📖 README do projeto`](../README.md) · [`🤖 Agentes`](../.agents/README.md) · [`🎸 patches/`](../patches/README.md)
