# ADR-0012 — Milestone é a release; a fase é um epic com sub-issues

- **Status**: aceito — revoga os itens 3 e a alternativa "issue-mãe" do
  [ADR-0009](0009-governanca-open-source.md)
- **Data**: 2026-09
- **Decisão relacionada**: issues #41–#64, #23 (fechada), #39 (fechada)

## Contexto

O ADR-0009 decidiu que **milestone era fase**: `2.0 · F1 … F5` + `2.0 · Release`.
A execução mostrou o custo, com sintoma observável, não teórico:

1. **A fase virou identidade do trabalho.** Issues da F1 pediam `src/gp100/…`
   quando o pacote já era `gp100_architect` (ADR-0001): o texto envelheceu dentro
   do próprio milestone, e ninguém releu as sete issues antes de planejar em
   cima delas.
2. **Não havia progresso legível.** Cinco milestones de fases não dizem "quanto
   falta para a release"; e a 1.1.0/1.2.0 ficaram **entregues e não publicadas**
   justamente porque fechar fase não é publicar release.
3. **A última análise errou por causa do modelo.** Propus um milestone `3.0` a
   partir de um texto que eu mesmo tinha escrito — o modelo anterior não tinha
   lugar para "isto pertence à 2.0, já está no backlog e ainda não começou".
4. **Sem grafo de dependência.** `blocked by` era prosa ("depende de #28"),
   invisível no card e no board.

## Decisão

Três camadas, cada uma respondendo por uma coisa:

| Camada | O que é | Como se cria |
|---|---|---|
| **Milestone** | a **release** — o que sai publicado junto (hoje: só `v2.0.0`) | `gh api …/milestones` |
| **Epic** — issue pai com a label `epic` | frente de trabalho com objetivo, escopo e critério de saída | `gh issue create --label epic` |
| **Task** — sub-issue do epic | entrega de **um** PR | `gh issue create --parent <epic>` |

1. **Um milestone por release.** Fase **não** vira milestone: o progresso aparece
   na barra de sub-issues do epic.
2. **Toda issue nasce como sub-issue de um epic.** Sem epic, ou o epic está
   errado ou a issue não deveria existir.
3. **Dependência é relação nativa**: `gh issue edit <task> --add-blocked-by <task>`.
   A label `status: blocked` acompanha, não substitui.
4. **Todo item tem um `type:`, um `priority:`, um `size:` e ao menos um
   `area:`/`scope:`** (herda a taxonomia do ADR-0009, que segue valendo).
5. **Task nasce quando a frente vai começar** — o epic declara as tasks
   previstas, o número só existe quando a frente abre. Sem isso, o texto
   descreve código que vai mudar antes de alguém lê-lo (foi o caso das quatro
   issues com caminho errado).
6. **Milestone só fecha com a tag publicada e com todas as sub-issues dos epics
   fechadas.**

## Consequências

- ✅ O placar da release é uma barra, não uma soma de milestones.
- ✅ "Do que isto depende?" é dado do GitHub, não parágrafo de doc.
- ✅ Issue nova num epic existente não precisa de épico-guarda-chuva novo.
- ✅ **Registro de premissa vencida (23/09/2026):** a automação do board opera
  por GraphQL puro — `gh project` mascara PAT válido como `unknown owner type`
  (cli/cli#8885) — e o bootstrap cria as três visões via API
  (`createProjectV2View`); só agrupamento/ordenação segue manual (a API não
  expõe `groupBy`). Fonte: `reference/18` § 3.3, nota de design atualizada.
- ⚠️ O epic é mais uma coisa para manter coerente com o roadmap — o resumo
  legível (`docs/roadmap-2.0.md` § 2) e o dado (a issue pai) podem divergir.
  Mitigação: o linter de consistência de docs (#58) confere os `#N` citados.
- ⚠️ Sub-issue não é obrigatória para o GitHub: quem abre issue fora de um epic
  não é bloqueado por nada, só cobrado no review.

## Alternativas descartadas

- **Manter milestone = fase** (ADR-0009) — foi o estado anterior; o custo está
  no contexto acima.
- **Um epic por fase do plano** — mesmos problemas, mais burocracia: a fase não
  tem critério de saída próprio, o epic tem.
- **Checklist em issue-mãe** (sem sub-issues) — não tem estado por item, não tem
  `blocked by`, e a caixa marcada não fecha issue nenhuma.
- **Sem epics, só milestone** — foi o estado real do repositório por semanas: 40
  issues soltas, e a leitura de "o que falta" dependia de memória.
