# ADR-0009 — Governança: labels, milestones e templates com uma taxonomia só

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #33

## Contexto

O repositório já tem templates de issue (bug/feature/task), template de PR,
labels e um board Project v2 com automação. O que falta é **taxonomia**: a
classificação de um item não pode depender de quem abriu. Sem isso, o board vira
lista e o filtro deixa de responder "o que está travado?", "o que é breaking?".

## Decisão

1. **Cinco eixos de label**, com prefixo explícito e conjunto fechado:
   `type:` (bug, feature, refactor, docs, test, ci, security, architecture,
   chore), `priority:` (critical…low), `status:` (planned, ready, in-progress,
   blocked, review), `area:` (python, cli, api, ui, data, ci, docs, security,
   ai), além das transversais (`good-first-issue`, `help-wanted`,
   `breaking-change`, `dependencies`).
2. **Um item tem exatamente um `type:` e um `priority:`**; `area:` pode ter mais
   de um.
3. **Milestone é fase, não sprint**: `2.0 · F1 … F5` + `2.0 · Release`. O que não
   entra na 2.0 fica em milestone próprio (2.1/3.0) em vez de virar backlog
   solto.
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
  elimina a leitura de progresso por fase.
- **Épicos via issue-mãe com checklist** — duplica o que o milestone + label de
  área já respondem, e issue-mãe envelhece mal.
