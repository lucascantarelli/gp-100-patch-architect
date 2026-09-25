# ADR-0013 — Modelo de artefatos em escala: o defs é a única fonte versionada

- **Status**: aceito — **implementado** (auditoria #125): schema v2 (#8),
  split por álbum, `.prst`/`patch.md` fora do git gerados no corte (#82) e o
  guard de determinismo provando byte a byte; o import "all" foi investigado
  na #83 (parte de software completa, receita em `reference/24`; veredito
  físico pendente do mantenedor).
- **Data**: 2026-09
- **Decisão relacionada**: pausa planejada das issues #31/#32; implementa-se via #8
  (schema v2), issue nova de build de artefatos no CI e issue de investigação do
  import "all"; funda-se na #29 (codec como biblioteca, fechada) e muda a **origem**
  dos ZIPs da [ADR-0010](0010-release-engineering.md)

## Contexto

A biblioteca hoje materializa **3–4 arquivos por patch** — 97 patches ⇒ 291 arquivos
em `patches/`:

| Artefato | Papel | Commitado? |
|---|---|---|
| `tools/patches-defs.json` (420 KB) | **Fonte única** — dados do patch | Sim |
| `<patch>/<NOME>.prst` | **Produto final** — importável na pedaleira | Sim |
| `<patch>/patch.md` | Documentação prática — **derivada** do defs | Sim |
| `<patch>/spec.json` | Intermediário de build | Não (gitignored) |

Um pedido de patch novo ao agente cria entradas no defs **e** materializa os três
arquivos em `patches/`. Com 97 patches isso é navegável e barato. Projetado para
10.000 patches: **~43 MB de defs monolítico, ~30 mil arquivos, repo > 100 MB** —
conflitos de git competindo pelo mesmo JSON, agentes editando arquivo gigante,
clones e buscas degradados.

A pergunta do mantenedor que disparou este ADR: *"por que sempre criamos diversos
arquivos por patch? Isso está correto? Pode ser melhor?"*

## Decisão

> **`patches-defs.json` é a única fonte versionada. Todo o resto é derivado
> construído, não armazenado.**

| Artefato | Destino |
|---|---|
| `.prst` | **Para de ser commitado.** Nasce no CI no corte da release (build a partir do defs) e vai para os ZIPs do GitHub Release. |
| `patch.md` | **Gerado no build** (ZIPs da release; o site da #43 renderiza navegável a partir do defs). Sai do git no marco da #8/#42, com transição documentada. |
| `spec.json` | **Eliminado do disco** — o codec (biblioteca pura desde a #29) recebe o spec in-memory do defs. Aplicável imediatamente. |
| `defs.json` | **Split por álbum** (`data/defs/PL.json` — Pulse, `data/defs/WM.json` — From the Muddy Banks of the Wishkah, … + índice `_albums.json`) na **#8 (schema v2)**: conflitos isolados por álbum, agentes editam arquivos pequenos, seeders da #31 aposentados naturalmente. |
| Import "all" | **Investigar** (issue dedicada): se a GP-100 aceita o formato all, um único arquivo de biblioteca substitui a importação de N `.prst` — muda a experiência do músico em escala. |

**A prova de que o `.prst` não precisa estar no git já existe em código:** o guarda de
sincronia (TestH) regenera todos os 97 `.prst` a partir do defs e compara
**byte a byte** (CRLF inclusive), com `GP100_BUILD_TIME` fixo. Se os bytes são
deterministicamente reconstruíveis, commitá-los é convenção de leitura, não
necessidade de dado. O custo dessa convenção é O(n) arquivos para sempre; o benefício
(acesso direto pelo navegador do GitHub) é atendível pelos ZIPs da release e pelo site
da #43.

**Por que o split do defs é da #8 e não antes:** o schema v2 redefine o formato do
defs (stomps/EXP1, `-USERIR`); dividir o arquivo antes de redefinir o schema
significaria fazer o trabalho duas vezes — a lição de premissas do ADR-0012. Os
seeders (`add_*_defs.py`) são a implementação atual do "append idempotente de álbum"
que o split per-álbum torna obsoleto.

## Consequências

- ✅ Repo plano a partir do marco #8/#42: +1 entrada de defs por patch, +0 arquivos derivados.
- ✅ Agentes e mantenedor editam dados num lugar só; o pipeline continua provando os derivados.
- ✅ `.prst`/`patch.md` passam a ter consumidor canônico (Release + site) em vez de dois.
- ⚠️ Quem hoje baixa `.prst` direto do repo passa a baixar do GitHub Release (ou do site).
- ⚠️ Janela de transição entre o corte no CI e a remoção do git: derivados podem
  divergir do defs se alguém editar sem rodar o pipeline — o TestH já reprova esse
  estado; a regra "derivado não se edita" passa a ser documentada, não óbvia.
- ⚠️ O formato "all" depende de investigação empírica no aparelho (issue dedicada).
- ⚙️ `build_release.py` muda de "ler `.prst` do repo" para "consumir artefatos gerados
  no job" — mesmo layout de ZIP, mesma validação, outra origem dos bytes.

## Alternativas descartadas

- **Banco de dados (SQLite) no lugar do defs** — mata a identidade "dados vivem no
  git, legíveis por humanos e agentes" (ADR-0001/auditoria 2.0), exige tooling de
  migração e diff sem merge. Custo alto para um problema que o split per-álbum
  resolve com a ferramenta que o projeto já usa.
- **Um único arquivo "all" por álbum desde já** — o formato all existe no firmware,
  mas aceitar import no aparelho/Edits é premissa **não verificada**; decidir por ele
  agora repetiria o erro de projetar sobre premissa vencida (ADR-0012). Vira
  investigação com critério de saída.
- **Manter tudo como está** — funciona em 97 patches, falha em 10k; a própria
  pergunta do mantenedor mostra que a inflação já é sentida. O custo de adiamento é
  O(n) arquivos e uma migração de git ainda maior depois.
