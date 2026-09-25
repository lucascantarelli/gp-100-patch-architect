# ADR-0009 — Governança: labels, milestones e templates com uma taxonomia só

- **Status**: aceito — **itens 3 e a alternativa "épicos via issue-mãe" revogados
  por [ADR-0012](0012-epics-com-sub-issues.md)** (a taxonomia de labels segue
  valendo)
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #33, #41–#64

## Contexto

O repositório já tem templates de issue (bug/feature/task), template de PR,
labels e um board Project v2 com automação. O que falta é **taxonomia**: a
classificação de um item não pode depender de quem abriu. Sem isso, o board vira
lista e o filtro deixa de responder "o que está travado?", "o que é breaking?".

## Decisão

1. **Cinco eixos de label**, com prefixo explícito e conjunto fechado:
   `type:` (bug, feature, refactor, docs, test, ci, security, architecture,
   chore), `priority:` (p0-critical…p3-low), `status:` (needs-triage, blocked,
   ready-for-pr, in-review), `area:` (python, cli, api, ui, ci, security, docs,
   ai, packaging) e `scope:` (pipeline, data, ir-library, agents, docs), além
   das transversais (`release`, `breaking change`, `good first issue`,
   `help wanted`, `dependencies`). A fonte única do conjunto é o
   `.github/scripts/bootstrap_project_management.sh`; o significado de cada
   família está no [`reference/18`](../../reference/18-project-management.md) § 3.1.
2. **Um item tem exatamente um `type:`, um `priority:` e um `size:`**; `area:` e
   `scope:` podem ter mais de um.
3. **Milestone é fase, não sprint**: `2.0 · F1 … F5` + `2.0 · Release`. O que não
   entra na 2.0 fica em milestone próprio (2.1) em vez de virar backlog
   solto. ~~Revogado na prática pelo ADR-0012: o milestone passou a ser a
   **release** e a fase virou **epic** — ver o ADR para o porquê.~~
4. **Issue sem contexto executável não é issue**: título, contexto, objetivo,
   escopo, arquivos impactados, dependências, critérios de aceitação, testes,
   documentação, breaking change, riscos. O modelo está no template e as issues
   geradas na auditoria seguem ele.
5. **Dependência entre issues é explícita** (bloqueia/é bloqueada por) — a ordem
   do roadmap é a ordem de execução.
6. **CODEOWNERS reflete o que existe**: caminho citado tem de existir no
   repositório (a auditoria achou caminhos inexistentes na versão anterior).

## Consequências

- ✅ Qualquer pessoa abre issue que um agente ou outro dev consegue executar sem
  reconstruir contexto.
- ✅ O board responde pergunta de gestão (bloqueio, foco, breaking change) por
  filtro, sem curadoria manual.
- ⚠️ Criar label nova exige justificativa: o conjunto é fechado de propósito.
- ⚠️ Toda issue nova precisa nascer com `type:` e `priority:`; sem isso a
  automação do board não classifica e o item fica invisível nos filtros.

## Alternativas descartadas

- **Labels livres por issue** — foi o estado anterior; o custo apareceu como
  filtro que não filtra.
- **Um milestone único "2.0"** — mistura 20 issues de fases diferentes e
  elimina a leitura de progresso por fase. *(Reavaliada no ADR-0012: o problema
  era usar o milestone como fase, não como release; com epics por cima, o
  milestone único passou a ser a leitura correta.)*
- **Épicos via issue-mãe com checklist** — duplica o que o milestone + label de
  área já respondem, e issue-mãe envelhece mal. *(Revogada no ADR-0012: com
  sub-issues e `blocked by` nativos, o epic deixou de ser um checklist em texto
  e virou uma estrutura que o GitHub atualiza sozinho.)*
