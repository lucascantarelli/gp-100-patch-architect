# 🗂 Gestão de projetos — Project v2, milestones e fluxo PR-driven

> Documento 18 — complementa o [`12-workflow`](12-workflow.md) (que cobre a
> criação de *patches*); este cobre a gestão do **repositório**: como uma ideia
> vira issue, a issue vira PR, e o PR vira release — com rastreio automático no
> Project v2.

## 1 · Filosofia: PR-driven, com a issue como unidade de trabalho

**Regra de ouro:** nenhuma mudança entra sem PR; nenhum PR entra sem issue;
nenhuma issue é fechada à mão.

- A **issue** descreve o trabalho (o "porquê" e o "o quê") e vive no Project.
- O **PR** descreve a mudança (o "como") e carrega a prova (pipeline, suíte,
  typecheck). **Referencia** a issue com `Closes #N`.
- O **guardian** (`project-automation.yml`) reprova PR sem label e sem issue
  vinculada — as regras de gestão valem tanto quanto as regras de dados.
- A **branch do PR morre no merge** (`delete_branch_on_merge` ligado no
  repositório): fechado o PR de trabalho, o que resta é `main` e `develop`.
- **Nenhum job escreve no git.** A automação movimenta Project, labels e
  relatórios — quem commita derivados é o autor (mesma filosofia do
  [`12-workflow`](12-workflow.md)).

## 2 · Ciclo de vida completo

```
Issue (task.yml)          PR                          Milestone
────────────────          ──────────────────────      ────────────
aberta                    opened (draft)   → In Progress
status: needs-triage      ready_for_review → In Review
triagem: type/scope/size  approved → merge → Done      fecha; relatório;
status: ready-for-pr      Closes #N liga a issue       próximo marco
```

| Etapa | Quem faz | Onde | O que acontece de automático |
|---|---|---|---|
| 1. Abrir issue | Autor | `gh issue create --template` | Entra no Project (Backlog) + `status: needs-triage` |
| 2. Triagem | Mantenedor | board + `gh issue edit` | Aplica `type:`/`priority:`/`size:` + `area:`/`scope:`; `status: ready-for-pr` quando pronta |
| 3. Branch | Autor | `git switch -c` | — (nome livre; padrão de facto: `feature/…`) |
| 4. PR | Autor | `gh pr create --base develop` | Entra no Project; `In Progress` (draft) / `In Review` (ready); guardian valida |
| 5. Review | Mantenedor | `gh pr review` | Discussões resolvidas; revalidação a cada push |
| 6. Merge | Mantenedor | `gh pr merge --delete-branch` | Card → `Done`; branch do trabalho removida; issue fechada à mão no `develop` (ver nota) |
| 7. Milestone | Mantenedor | `gh api -X PATCH` | Relatório de fechamento; itens pendentes migram |

**Base de PR:** `develop` (trabalho) — só o PR de release (`develop` → `main`)
vai contra a `main`, e ele é **isento de issue vinculada** (a gestão dele é o
CHANGELOG + milestone da versão).

## 3 · A estrutura instalada

### 3.1 Labels — fonte única: `.github/scripts/bootstrap_project_management.sh`

> **Sem número no título de propósito**: contagem memorizada envelhece (achado A8 da auditoria). A conferência é automática — o bootstrap instala a tabela inteira, e o que existe no repositório tem de estar nela.

| Família | Labels | Regra de uso |
|---|---|---|
| **Type** | `type: bug` `type: feature` `type: refactor` `type: docs` `type: chore` `type: test` `type: ci` `type: security` `type: architecture` | exatamente **uma** por issue/PR (bug reaproveita a label `bug`) |
| **Area** | `area: python` `area: cli` `area: api` `area: ui` `area: ci` `area: security` `area: docs` `area: ai` `area: packaging` | onde a mudança mora; uma ou mais |
| **Epic** | `epic` | marca **issue pai**: só ela agrupa sub-issues (ver §3.2) |
| **Priority** | `priority: p0-critical` `p1-high` `p2-medium` `p3-low` | opcional na issue; p0/p1 definem a fila do milestone |
| **Status** | `status: needs-triage` `status: blocked` `status: ready-for-pr` `status: in-review` | issue: triagem aplica; `in-review`/`Done` são movidos pelo **board** |
| **Scope** | `scope: pipeline` `scope: data` `scope: ir-library` `scope: agents` `scope: docs` | uma ou mais |
| **Size** | `size: XS` `size: S` `size: M` `size: L` `size: XL` | uma; XL é cheiro de dividir a issue |
| **Domínio** | `tone-mismatch` `prst-import` | convivem com `type: bug` (especializam o relato) |
| **Release** | `release` `breaking change` `good first issue` `help wanted` | conforme o caso |

Status vive em **dois lugares por design**: a *label* dá o corte via `gh issue list
--label`; o *campo Kanban* dá o quadro visual. Quem consome via CLI usa a label;
quem consome visual usa o board.

### 3.2 Milestone = release · epic = frente de trabalho · sub-issue = task

Três camadas, e cada uma responde por uma coisa:

| Camada | O que é | Exemplo |
|---|---|---|
| **Milestone** | a **release** — o que sai publicado junto | `v2.0.0 — Formato, site e escala` |
| **Epic** (issue pai, label `epic`) | frente de trabalho com objetivo, escopo e critério de saída próprios | `EPIC · Núcleo, CLI e fim do legado` (#41) |
| **Sub-issue** (task) | entrega de **um** PR | `refactor(domain): camada de domínio pura` (#28) |

Consequências práticas:

- **Um milestone por release.** Fase do plano **não** vira milestone: enquanto a
  release está aberta há um milestone só, e o progresso aparece nas barras dos
  epics (sub-issues fechadas / total).
- **Issue nova nasce como sub-issue de um epic.** Sem epic, ou o epic está
  errado ou a issue não deveria existir.
- **Task nasce quando a frente vai começar** — issue detalhada sobre código que
  ainda vai mudar nasce errada (o que aconteceu com metade da primeira leva da
  2.0: quatro issues pediam um caminho de pacote que já tinha mudado).
- **Todo item fechado por cinco eixos**: exatamente **um** `type:`, **um**
  `priority:`, **um** `size:` e ao menos **um** `area:` ou `scope:`. É o que faz
  o filtro responder "o que é p0 e mexe em python?".
- **Dependência é declarada no item que espera**, com
  `gh issue edit <task> --add-blocked-by <task>` — a relação nativa do GitHub, que
  o board e o card mostram. A label `status: blocked` **acompanha**, não
  substitui: label é rótulo de leitura, a relação é o dado. Dependência vive na
  **task**, não no epic — o epic herda a ordem das filhas.
- **O milestone só fecha com a tag publicada** e com **todas** as sub-issues dos
  epics fechadas: as barras de progresso dos epics são o placar da release.
- **Milestone de release só fecha com a tag publicada.** A 1.1.0 e a 1.2.0 foram
  entregues e não publicadas, e o trabalho da fase seguinte entrou no corte
  delas — a regra existe para isso não repetir.
- Sprints, quando existirem, são o campo `Sprint` do Project — não milestone.

### 3.3 Project v2 "GP-100 Pipeline"

| Visão | Layout | Agrupamento | Uso |
|---|---|---|---|
| **Kanban** | Board | campo `Kanban` | dia a dia: `Backlog → Ready → In Progress → In Review → Done` |
| **Sprint** | Table (filtro `Sprint:*`) | campo `Sprint`, ordenado por `Story Points` | o que cabe na iteração |
| **Roadmap** | Roadmap | por `Milestone` | datas das releases |

**Custom fields:** `Kanban` (SINGLE_SELECT — substitui o Status nativo, que a
CLI não edita), `Story Points` (NUMBER), `Sprint` (TEXT), `Priority`/`Linked PR`
não são campos: leem-se das **labels** e do **timeline da issue** (PR vinculado
aparece lá) — duplicar no Project era redundância exatamente do tipo que este
projeto elimina em outra frente.

> **Nota de design (atualizada em 23/09/2026 — duas premissas antigas caíram):**
> (1) A GraphQL v2 **cria, edita e apaga views** (`createProjectV2View`,
> `updateProjectV2View`, `deleteProjectV2View`): as três visões nascem do
> bootstrap, com layout e filtro; só agrupamento/ordenação segue manual (1
> clique por view — a API não expõe `groupBy`). (2) O subcomando `gh project`
> **mascara PAT válido** como `unknown owner type` (cli/cli#8885, provado aqui
> em 23/09): a automação fala **GraphQL puro** — leitura de campo/opções/
> conteúdo → `addProjectV2ItemById` (idempotente) →
> `updateProjectV2ItemFieldValue`, com `singleSelectOptionId` como `String!`
> (não `ID!`). O campo `Kanban` continua existindo porque o Status nativo segue
> sem edição pela CLI.

## 4 · Instalação e operação

```bash
# Escopo de Project no token local (uma vez):  gh auth refresh -s project
.github/scripts/bootstrap_project_management.sh --check   # diagnóstico (só leitura)
.github/scripts/bootstrap_project_management.sh           # instala tudo (idempotente)
ONLY=labels|.  ONLY=milestones|.  ONLY=project .          # fatias isoladas
DRY_RUN=1 .            # ensaio
```

Instalado e operando: o Project "GP-100 Pipeline" é o **#7** do owner
(`PROJECT_NUMBER: "7"` no `project-automation.yml`). Depois de uma reinstalação,
confira o `PROJECT_NUMBER` no topo de
`.github/workflows/project-automation.yml` e crie as 3 visões conforme o guia
impresso no fim da execução do bootstrap.

### 4.1 O secret `PROJECT_TOKEN` (pré-requisito da automação)

O `GITHUB_TOKEN` **não acessa Project v2 de usuário**: a permissão de workflow
`repository-projects` cobre Projects **clássicos** do repositório, e este board é
do owner (pessoa). Quem move card aqui é um PAT fine-grained guardado no secret
`PROJECT_TOKEN` — com `Projects: read/write` (owner = você) e
`Issues: read/write` (só este repositório). **Sem `contents: write`**: o token da
gestão continua incapaz de empurrar em branch nenhuma (ADR-0006).

```bash
# 1. github.com/settings/personal-access-tokens → fine-grained, só este repo:
#    Issues: read/write  ·  Account permissions → Projects: read/write
# 2. guarde no repositório:
gh secret set PROJECT_TOKEN
# 3. confira que a automação está ligada (sem precisar abrir issue/PR de teste):
gh workflow run project-automation.yml      # job 🩺 Diagnóstico do board
```

Sem o secret, os jobs do board **avisam com este comando e não reprovam** — um
fork ou um clone novo não pode ficar vermelho por falta de configuração local,
e a automação não finge que rodou. O detalhamento (e as alternativas
descartadas) está no [`ADR-0011`](../docs/decisions/0011-gestao-de-project-com-pat.md).

**O que a automação faz sozinha** (project-automation.yml): adiciona issue/PR ao
Project; marca issue nova `needs-triage`; move card — PR: `In Progress`
(draft), `In Review` (ready), `Done` (fechado/merged); issue: `Backlog`
(aberta/reaberta), `Done` (fechada, por qualquer motivo — fim dos cards
zumbis); **guardian** reprova PR sem label ou sem `Closes #N`
(avisa quando falta milestone ou assignee); relatório de fechamento de milestone.
As transições de **issue** executam a versão do workflow que está na branch
padrão (`main`): viram efetivas no PR de release `develop → main`.
**O que é humano:** triagem, arraste `Ready → In Progress`, datas de
release, fechamento do milestone (`gh api -X PATCH …/milestones/N -F state=closed`).

## 5 · Guia de comandos `gh` para o dia a dia

### Triagem (manhã)

```bash
gh issue list --label "status: needs-triage"                  # o que chegou
gh issue edit 12 --add-label "type: feature,scope: data,size: M,priority: p1-high" \
                --remove-label "status: needs-triage" \
                --milestone "v2.0.0 — Formato, site e escala" \
                --parent 46                                   # nasce sob um epic
gh issue edit 12 --add-blocked-by 30                          # se espera outra task
gh issue edit 12 --add-label "status: ready-for-pr"           # pronta para puxar
```

### Trabalhar (uma issue = um PR)

```bash
gh issue list --label "status: ready-for-pr" --state open     # fila pronta
git switch develop && git pull
git switch -c feature/<slug>                                  # branch do trabalho
# ... edits + pipeline + suíte ...
gh pr create --base develop --fill --milestone "v2.0.0 — Formato, site e escala" \
  --label "type: feature" --label "scope: data" --label "size: M" --label "priority: p1-high" \
  --assignee "@me" --body "…Closes #12"
gh pr ready                    # draft → In Review (automação move o card)
gh pr checks                   # guardian + CI
```

### Review e merge

```bash
gh pr view 5 --web
gh pr merge 5 --merge --delete-branch   # card → Done; branch do trabalho removida
```

> **`Closes #N` fecha sozinho apenas no PR contra a `main`** (branch padrão).
> Nos PRs do dia a dia, que entram na `develop`, o GitHub só **referencia** a
> issue — o fechamento é do mantenedor no merge:
> `gh issue close 5 --comment "Fechada pelo PR #12 (merge abc1234)."`
> (o comentário guarda a prova do que fechou a issue).

### Status da sprint / do milestone

```bash
gh api repos/lucascantarelli/gp-100-patch-architect/milestones \
  --jq '.[] | "\(.title): \(.closed_issues)/\(.open_issues + .closed_issues) fechados"'
gh issue list --milestone "v2.0.0 — Formato, site e escala" --state open
gh project item-list 7 --owner lucascantarelli --format json \
  | python -c "import json,sys;[print(i['content']['title']) for i in json.load(sys.stdin)['items']]"
```

> `item-list` não tem `--limit` (nem tem mais, em versão recente do `gh`): ele
> lista o board inteiro. O filtro é `--query`, na sintaxe do próprio Projects.

### Fechamento do milestone

```bash
gh issue list --milestone "v2.0.0 — Formato, site e escala" --state open   # migre o que sobrou
gh api -X PATCH repos/lucascantarelli/gp-100-patch-architect/milestones/3 -F state=closed
# e só DEPOIS da tag publicada (regra que nasceu do caso 1.1.0/1.2.0)
# o workflow publica o relatório; então: PR de release develop → main
```

## 6 · Notas de design

- **Por que o guardian é job de CI e não SLSA/branch rule**: a regra "PR sem
  gestão reprova" precisa aparecer na lista de checks como qualquer veredito —
  e sem custo de checkout (só API).
- **Por que o workflow não cria label**: criação é *bootstrap* (com `--force`,
  idempotente, revisável em diff); criação em runtime duplica a fonte e foge do
  diff. O guardian só **cobra**; o bootstrap **define**.
- **Por que `Closes #N` no corpo e não autodetecção**: a keyword é o contrato
  visível no diff do PR; o guardian valida o corpo. Quem fecha a issue no merge
  para a `develop` é o mantenedor (a keyword só atua na branch padrão).
- **Segurança do workflow**: `permissions` no piso por job (o `GITHUB_TOKEN`
  nunca passa de `contents: read`; a escrita no board é do PAT do secret
  `PROJECT_TOKEN`), runner fixado (`ubuntu-24.04`), zero interpolação de
  contexto não confiável em `run:` — passa no
  `.github/scripts/audit_workflows.py`.
- **Por que o auditor confere NOME de permissão**: a versão anterior deste
  workflow declarava `repository-project: write` (sem o "s"). Escopo inexistente
  invalida o arquivo INTEIRO: o GitHub falhava todo push com "workflow file
  issue" e **nenhum job jamais rodou** — o board nunca recebeu card automático.
  O sinal barato de que isso aconteceu: `gh workflow list` mostra o **caminho**
  do arquivo no lugar do `name:` (regra 8 do auditor, com teste em
  `tests/unit/test_audit_workflows.py`).
- **Consistência dos docs** (issue #58): a pior classe de erro do repo é doc
  divergindo da realidade (issue citada inexistente, estado dito errado, caminho
  que nunca existiu, milestone fantasma, comando inválido). O
  `.github/scripts/audit_docs.py` reprova tudo isso com `arquivo:linha` — no CI
  (job de agentes) e no pre-commit; exceções conscientes ficam na tabela
  `EXCETO` do próprio script, cada uma com por quê
  (testes em `tests/unit/test_audit_docs.py`).

---

[`📖 README do projeto`](../README.md) · [`🌊 12-workflow`](12-workflow.md) · [`📦 CLI de agentes`](../DEVELOPMENT.md)
