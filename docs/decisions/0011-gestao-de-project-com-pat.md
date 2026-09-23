# ADR-0011 — Gestão de Project v2 com PAT em secret, e permissões verificadas pelo auditor

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: ADR-0006 (zero escrita no repositório), issue #37

## Contexto

O `project-automation.yml` existia desde a v1.1.0 e **nunca rodou um único job**.
Duas causas somadas:

1. O bloco de permissões declarava `repository-project: write` — escopo que não
   existe (o correto é `repository-projects`, plural). Nome inválido no bloco
   `permissions:` invalida o **arquivo inteiro**: o GitHub responde "workflow
   file issue" em todo push, não executa nada — nem os jobs de leitura — e exibe
   o **caminho** do arquivo como nome do workflow no `gh workflow list`. O sinal
   era visível (quatorze execuções vermelhas seguidas), mas ninguém o leu como
   "esta automação não existe".
2. Mesmo com o nome correto, o `GITHUB_TOKEN` **não acessa Project v2 de
   usuário**: `repository-projects` cobre Projects clássicos do repositório, e
   este board pertence ao owner (pessoa). Ou seja: o desenho original não tinha
   como funcionar.

Bônus do mesmo diagnóstico: como nenhum job jamais executou, os comandos `gh`
escritos de memória nunca foram testados — `gh issue edit --ignore-if-missing`,
`gh project item-edit --item-id/--option-id` e `gh project item-list --limit`
não existem na CLI. Três falhas de runtime esperando a primeira execução.

## Decisão

1. **O `GITHUB_TOKEN` continua só lendo.** `permissions: contents: read` é o piso
   de todos os workflows (ADR-0006): nenhum ator automatizado pode empurrar em
   branch, e a proteção do `main` não precisa de exceção para o app
   `github-actions`.
2. **A escrita no board vem de um PAT em secret** (`PROJECT_TOKEN`),
   fine-grained, restrito a este repositório: `Issues: read/write` +
   `Projects: read/write` (owner). Sem `contents: write` — o token da gestão não
   ganha poder de push que o `GITHUB_TOKEN` não tem.
3. **Sem o secret, o workflow avisa e não reprova.** Job de board sem token
   emite `::warning::` (ou `::notice::` em PR de fork, que não recebe segredos)
   com o comando exato, e segue. A automação também não finge que rodou: o job
   `🩺 Diagnóstico do board` (`workflow_dispatch`) confere token, Project e campo
   `Kanban` sob demanda e **aí sim** falha, porque é execução manual de
   diagnóstico.
4. **Jobs que só leem não usam o PAT**: `guardian` (PR) e `milestone` (issues)
   ficam com o `GITHUB_TOKEN` e declaram só o que usam.
5. **Nome e nível de permissão passam a reprovar no auditor** (regra 8 do
   `.github/scripts/audit_workflows.py`), no bloco do topo e no de cada job, com
   teste em `tests/unit/test_audit_workflows.py`. A lista de escopos é fechada de
   propósito: é ela que transforma typo em erro de CI em vez de arquivo morto.
6. **Gatilhos alinhados ao que os jobs declaram**: `synchronize`, `labeled` e
   `edited` entraram em `pull_request.types` — o guardian prometia revalidar a
   cada push e a cada label, mas os eventos nem chegavam.

## Consequências

- ✅ O board passa a receber card automático, e o guardian (label, `Closes #N`,
  milestone) passa a aparecer na lista de checks do PR — inclusive para o
  `setup_repo.sh`, que o exige como check obrigatório do `main`.
- ✅ A falha deixa de ser silenciosa: arquivo inválido agora reprova no CI, e
  token ausente aparece como anotação no job, não como board parado.
- ⚠️ Passa a existir **um segredo de longa duração** no repositório — o único
  até hoje, já que o CI inteiro vive de `GITHUB_TOKEN`. Rotação é manual; o PAT
  deve ser fine-grained e restrito a este repositório para limitar o dano.
- ⚠️ PR de fork não move card (não recebe segredo). É aceitável: fork não tem
  permissão de escrita no board de qualquer forma, e o guardian — a parte que
  importa no PR de fora — não depende de PAT.
- ⚠️ Exceção que exige disciplina: nada de `contents: write` no PAT, mesmo que
  seja conveniente para alguma automação futura (o auditor reprova `permissions`
  amplo no YAML, mas não vê o PAT — a regra vale por escrito, aqui).

## Alternativas descartadas

- **Manter `repository-projects: write` e seguir com o `GITHUB_TOKEN`** — o
  Project é de usuário: o token do Actions continua sem acesso e o board
  continuaria parado. Trocaria um arquivo inválido por um arquivo válido que não
  faz nada.
- **PAT clássico com escopo `repo`** — é o caminho que "simplesmente funciona" e
  é exatamente o que não se quer: dá ao token de gestão poder de push em todos
  os repositórios do mantenedor, contrariando o ADR-0006.
- **GitHub App instalada no repositório** — não se instala em conta de usuário,
  e Projects de usuário não ficam acessíveis por ela; exigiria mover o board para
  uma organização que não existe.
- **Automação local (cron no clone do mantenedor)** — o board deixaria de ser
  consequência do evento e passaria a depender da máquina ligada, sem rastro na
  aba de Actions.
- **Desligar a automação e gerir tudo à mão** — descarta justamente o guardian,
  que é a parte que funciona com `GITHUB_TOKEN` e é exigida pelo
  `setup_repo.sh`.
