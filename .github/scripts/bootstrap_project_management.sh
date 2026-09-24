#!/usr/bin/env bash
#
# bootstrap_project_management.sh — instala a gestão ágil do repositório no
# GitHub: taxonomia de labels, milestones de release e o Project v2
# "GP-100 Pipeline" (com campos customizados e visões de Kanban/Roadmap/Sprint).
#
# Uso:
#   ./bootstrap_project_management.sh --check   # só leitura (diagnóstico)
#   ./bootstrap_project_management.sh           # aplica tudo (idempotente)
#   ONLY=labels ./bootstrap_project_management.sh      # só labels
#   ONLY=milestones ./bootstrap_project_management.sh  # só milestones
#   ONLY=project ./bootstrap_project_management.sh     # só project
#
# Pré-requisitos: `gh` autenticado com escopo `project` (além de `repo`):
#   gh auth refresh -s project
#
# ─────────────────────────────────────────────────────────────────────────────
# FONTE ÚNICA da taxonomia: `setup_repo.sh` (passo 7) invoca este script no
# bloco de labels — a tabela abaixo não deve ser copiada para outro arquivo.
# Os workflows não criam label nenhum (isso é work de bootstrap, não de runtime).
#
# Paleta: tons por família (vermelho=bug, verde=done, azul=escopo,
# amarelo=atenção, roxo=processo, cinza=trivial) no padrão usado pela
# indústria — família reconhecível pela cor antes de pelo texto.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO="${REPO:-lucascantarelli/gp-100-patch-architect}"
PROJECT_TITLE="GP-100 Pipeline"
ONLY="${ONLY:-all}"

# ── Plomeria (mesmo estilo do setup_repo.sh) ────────────────────────────────
if [ -t 1 ]; then B=$'\e[1m'; G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; Z=$'\e[0m'
else B=; G=; Y=; R=; Z=; fi

passo() { printf '\n%s▸ %s%s\n' "$B" "$*" "$Z"; }
ok()    { printf '  %s✓%s %s\n' "$G" "$Z" "$*"; }
aviso() { printf '  %s!%s %s\n' "$Y" "$Z" "$*"; }
erro()  { printf '  %s✗%s %s\n' "$R" "$Z" "$*" >&2; }

DRY_RUN="${DRY_RUN:-0}"
MODO_CHECK=0
[ "${1:-}" = "--check" ] && MODO_CHECK=1

# ═══════════════════════════ 1 · LABELS ══════════════════════════════════════
instalar_labels() {
passo "1 · Labels — taxonomia tipo/prioridade/status/escopo/tamanho"

# (a) Defaults do GitHub que a taxonomia substitui (existem? apaga).
while IFS= read -r nome; do
  [ -z "$nome" ] && continue
  if gh label list --repo "$REPO" --json name --jq '.[].name' 2>/dev/null | grep -Fxq "$nome"; then
    if [ "$DRY_RUN" = "1" ]; then
      printf '  %s[dry-run]%s gh label delete "%s"\n' "$Y" "$Z" "$nome"
    else
      gh label delete "$nome" --repo "$REPO" --yes >/dev/null 2>&1 \
        && ok "removida (default): $nome" || aviso "não removi $nome"
    fi
  fi
done <<'APAGAR'
enhancement
wontfix
invalid
duplicate
question
APAGAR
ok "defaults substituídos (bug, good first issue e help wanted são reaproveitados)"

# (b) Taxonomia: nome|cor|descrição  (cria; se existe, atualiza via --force)
# O total é CONTADO na tabela abaixo, não escrito à mão: número memorizado
# envelhece a cada label nova (achado A8 da auditoria).
instaladas=0
while IFS='|' read -r nome cor desc; do
  [ -z "$nome" ] && continue
  case "$nome" in \#*) continue ;; esac   # comentário da tabela não é label
  instaladas=$((instaladas + 1))
  if [ "$DRY_RUN" = "1" ]; then
    printf '  %s[dry-run]%s label: %s\n' "$Y" "$Z" "$nome"
  else
    gh label create "$nome" --repo "$REPO" --color "$cor" --description "$desc" --force >/dev/null 2>&1 \
      && ok "$nome" || aviso "não instalei $nome"
  fi
done <<'LABELS'
type: bug|d73a4a|Não funciona como documentado (labels de domínio convivem: tone-mismatch, prst-import)
type: feature|a2eeef|Capability nova: álbum, camada, patch, efeito, momento de toggle
type: refactor|1d76db|Reorganização sem mudar a saída do pipeline
type: docs|0075ca|Só documentação (reference/, README, patch.md)
type: chore|fef2c0|Manutenção: scripts, CI, dependências, release
priority: p0-critical|b60205|Reprovação do CI, dado corrompido ou pipeline quebrado — primeira da fila
priority: p1-high|d93f0b|Impacta a próxima release — entra no milestone atual
priority: p2-medium|fbca04|Importante, sem prazo — backlog do Project
priority: p3-low|ededed|Nice to have — sem data
status: needs-triage|ededed|Aguardando triagem do mantenedor
status: blocked|e99695|Impedida por outra issue, decisão ou recurso externo
status: ready-for-pr|0e8a16|Triada e pronta: qualquer branch/parte pode implementá-la
status: in-review|bfd4f2|Existe PR aberto vinculado (o guardian do project-automation seta)
scope: pipeline|5319e7|tools/, geração de dados e CI
scope: data|0e8a16|Dados gerados: patches, índices, defs, catálogo de IRs
scope: ir-library|c5def5|Packs de IR, slots de User IR e política de IR
scope: agents|bea3dd|Agentes em .agents/ (orquestrador e subagentes)
scope: docs|0075ca|reference/, README, CONTRIBUTING e documentação de patch
scope: api|d4c5f9|API do catálogo: JSON estático/servidor para agentes e site
size: XS|c2e0c6|Troca de uma linha ou ajuste de texto
size: S|bfe5bf|Um arquivo, um seeder pequeno
size: M|d4c5f9|Alguns arquivos ou um patch por música completo
size: L|959af5|Álbum inteiro, efeito novo ou workflow novo
size: XL|6f42c1|Múltiplas frentes — provavelmente deveria ser dividida
bug|d73a4a|Reaproveitada como apelido de type: bug
tone-mismatch|f9d0c4|O patch importa, mas o som não bate com o patch.md
prst-import|1d76db|Falha ao importar .prst na pedaleira ou no GP-100 Edits
release|0e8a16|Preparação de versão (VERSION + CHANGELOG)
breaking change|d93f0b|Mudança incompatível (força bump MAJOR)
good first issue|7057ff|Bom para quem está começando
help wanted|008672|Atenção extra é bem-vinda

# ── Extensões que nasceram com o pacote e com os epics ────────────────
# Toda label do repositório está nesta tabela: ela é a fonte única da
# taxonomia (o bootstrap --check confere, e o `epic` marca issue pai).
type: architecture|5319e7|Arquitetura, camadas e ADRs
type: ci|1d76db|CI/CD, workflows e automações
type: security|b60205|Segurança e supply chain
type: test|0e8a16|Testes automatizados e cobertura
area: ai|fbca04|Agentes, skills e rules de IA
area: api|fbca04|API HTTP (2.1)
area: ci|fbca04|GitHub Actions e pipelines
area: cli|fbca04|Interface de linha de comando
area: docs|fbca04|Documentação técnica
area: packaging|fbca04|Empacotamento, uv e dependências
area: python|fbca04|Código Python (pacote, domínio, aplicação)
area: security|fbca04|Segurança e políticas
area: ui|fbca04|Interface gráfica/web (2.1)
accessibility|f143ab|Barrier affecting people with disabilities
dependencies|c5def5|Atualização de dependências
documentation|0075ca|Improvements or additions to documentation
epic|3E4B9E|Issue pai: agrupa tasks (sub-issues) de um mesmo fluxo da release
LABELS
ok "taxonomia instalada ($instaladas labels; domínio tone-mismatch/prst-import preservados)"
}

# ═══════════════════════ 2 · MILESTONES ══════════════════════════════════════
instalar_milestones() {
passo "2 · Milestones — v1.1.0 (dev), v1.2.0 (fundações) e v2.0.0 (major)"

# Cada linha: título|descrição|data-ISO (ou '-' para sem prazo)
while IFS='|' read -r titulo desc data; do
  [ -z "$titulo" ] && continue
  args=(gh api -X POST "repos/$REPO/milestones" -f title="$titulo" -f description="$desc" -f state=open)
  [ "$data" != "-" ] && args+=(-f due_on="${data}T08:00:00Z")
  if [ "$DRY_RUN" = "1" ]; then
    printf '  %s[dry-run]%s milestone: %s\n' "$Y" "$Z" "$titulo"
  else
  if "${args[@]}" >/dev/null 2>&1; then ok "$titulo"
  else aviso "não criei $titulo (provavelmente já existe — a API recusa duplicado)"
  fi
  fi
done <<'MILESTONES'
v1.1.0 — Álbuns e fluxo PR-driven|Wishkah (17 músicas/31 patches) + automação de Project v2, templates de issue e guardian de gestão.|-
v1.2.0 — Fundações do 2.0|Tudo aditivo rumo ao major: CLI unificada (gp100.py), validação acionável do defs, skills novas (setlist, A/B, golden set) e matriz Python no CI.|-
v2.0.0 — Formato, site e escala|As quebras que justificam o MAJOR: schema v2 do defs (por álbum), stomps/EXP1 formais, variante -USERIR, site estático e ≥ 100 patches / ≥ 10 álbuns. Ver reference/19-roadmap-v2.md.|-
MILESTONES
ok "milestones garantidos (idempotente: existente não é recriado)"
}

# ═══════════════════════ 3 · PROJECT v2 ══════════════════════════════════════
# O `gh project` não edita opções do Status nativo nem cria visões — então:
#   · o board usa um campo SINGLE_SELECT "Kanban" criado aqui (ordem estável);
#   · as visões (Kanban/Roadmap/Sprint) são 3 cliques no painel, guiados no fim.
instalar_project() {
passo "3 · Project v2 '$PROJECT_TITLE'"

OWNER="${OWNER:-@me}"
# `--format json` é aceito por toda a família `gh project`; se um `gh` antigo
# reclamar, o fallback localiza pelo título em `project list`.
# Procura ANTES de criar: o GitHub aceita títulos duplicados de Project, então
# criar primeiro nunca seria idempotente — cada rodada gerava um Project novo.
# Aconteceu de verdade em 23/09/2026: os Projects #8 e #9 nasceram assim
# (vazios) e foram apagados.
PRJ="$(gh project list --owner "$OWNER" --format json | python -c "
import json,sys
for p in json.load(sys.stdin)['projects']:
    if p['title'] == '$PROJECT_TITLE':
        print(p['number']); break")"

if [ -n "${PRJ:-}" ]; then
  ok "já existe — Project #$PRJ (reaproveitado)"
else
  PRJ="$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json --jq '.number')" \
    && ok "criado — Project #$PRJ"
fi

if [ -z "$PRJ" ]; then
  erro "não consegui criar nem localizar o Project — confira 'gh auth status' (escopo project)"
  return 1
fi

# Link ao repositório (mostra o Project na aba Projects do repo).
if [ "$OWNER" = "@me" ]; then
  login="$(gh api user --jq .login)"
else
  login="$OWNER"
fi
if [ "$DRY_RUN" = "1" ]; then
  printf '  %s[dry-run]%s gh project link %s --owner %s --repo %s\n' "$Y" "$Z" "$PRJ" "$login" "${REPO#*/}"
else
  gh project link "$PRJ" --owner "$login" --repo "${REPO#*/}" >/dev/null 2>&1 \
    && ok "linkado ao repositório" || aviso "link falhou (não bloqueia: o workflow usa o owner, não o link)"
fi

# ── Campos customizados ──────────────────────────────────────────────────────
# `gh project field-create` é idempotente-tolerante: falha suave se o nome existe.
if [ "$DRY_RUN" = "1" ]; then
  printf '  %s[dry-run]%s field-create: Story Points (NUMBER)\n' "$Y" "$Z"
  printf '  %s[dry-run]%s field-create: Sprint (TEXT)\n' "$Y" "$Z"
  printf '  %s[dry-run]%s field-create: Kanban (SINGLE_SELECT)\n' "$Y" "$Z"
else
  gh project field-create "$PRJ" --owner "$OWNER" --name "Story Points" --data-type NUMBER >/dev/null 2>&1 \
    && ok "campo: Story Points (NUMBER)" || aviso "Story Points já existe"
  gh project field-create "$PRJ" --owner "$OWNER" --name "Sprint" --data-type TEXT >/dev/null 2>&1 \
    && ok "campo: Sprint (TEXT)" || aviso "Sprint já existe"
  gh project field-create "$PRJ" --owner "$OWNER" --name "Kanban" --data-type SINGLE_SELECT \
    --single-select-options "Backlog,Ready,In Progress,In Review,Done" >/dev/null 2>&1 \
    && ok "campo: Kanban (SINGLE_SELECT — substitui o Status nativo, que o gh não edita)" \
    || aviso "Kanban já existe"
fi

# ── Views do board (Kanban · Sprint · Roadmap) ───────────────────────────────
# A API GraphQL v2 cria e apaga views (createProjectV2View/updateProjectV2View/
# deleteProjectV2View) — a premissa antiga de que "o gh não cria views" caiu
# (provado no Project #7 em 23/09/2026). Ainda não vão pela API: agrupamento e
# ordenação — 1 clique por view, indicado no aviso ao fim.
if [ "$DRY_RUN" = "1" ]; then
  printf '  %s[dry-run]%s views: Kanban (BOARD) · Sprint (TABLE, filtro Sprint:*) · Roadmap (ROADMAP)\n' "$Y" "$Z"
else
  projeto_id="$(gh project view "$PRJ" --owner "$OWNER" --format json --jq .id)"
  views_existentes="$(gh api graphql -f query='query($id: ID!){node(id:$id){... on ProjectV2{views(first:20){nodes{id name}}}}}' -f id="$projeto_id" --jq '[.data.node.views.nodes[].name]')"

  criar_view() {
    # $1 = nome · $2 = layout (BOARD_LAYOUT|TABLE_LAYOUT|ROADMAP_LAYOUT) · $3 = filtro (opcional)
    local nome="$1" layout="$2" filtro="$3"
    if printf '%s' "$views_existentes" | grep -q "\"$nome\""; then
      ok "view: $nome (já existe)"
      return 0
    fi
    local vid
    vid="$(gh api graphql -f query='mutation($p: ID!, $n: String!, $l: ProjectV2ViewLayout!){createProjectV2View(input:{projectId:$p,name:$n,layout:$l}){projectV2View{id}}}' \
      -f p="$projeto_id" -f n="$nome" -f l="$layout" --jq '.data.createProjectV2View.projectV2View.id')" \
      || { aviso "view: $nome — falhou ao criar (crie à mão em projects/$PRJ)"; return 1; }
    if [ -n "$filtro" ]; then
      gh api graphql -f query='mutation($v: ID!, $f: String!){updateProjectV2View(input:{viewId:$v,filter:$f}){projectV2View{id}}}' \
        -f v="$vid" -f f="$filtro" >/dev/null \
        || aviso "view: $nome — filtro '$filtro' não aplicado (1 clique na view resolve)"
    fi
    ok "view: $nome"
  }

  criar_view "Kanban" "BOARD_LAYOUT" ""
  criar_view "Sprint" "TABLE_LAYOUT" "Sprint:*"
  criar_view "Roadmap" "ROADMAP_LAYOUT" ""

  printf '\n'
  aviso "agrupamento/ordenação das views não vão na API — 1 clique por view em https://github.com/users/$login/projects/$PRJ/views:"
  aviso "  Kanban → agrupar por 'Kanban' · Sprint → agrupar por 'Sprint' + ordenar por 'Story Points' · Roadmap → agrupar por 'Milestone'"
fi
}

# ── Execução ─────────────────────────────────────────────────────────────────
passo "Bootstrap de gestão de projetos — $REPO"
command -v gh >/dev/null || { erro "gh não encontrado no PATH."; exit 1; }
gh auth status >/dev/null 2>&1 || { erro "gh não autenticado — rode: gh auth login"; exit 1; }
if [ "$MODO_CHECK" = "1" ]; then
  passo "Estado atual (--check)"
  falar_n=$(gh label list --repo "$REPO" --limit 200 --json name --jq 'length' 2>/dev/null || echo '?')
  ok "labels: $falar_n instaladas"
  ms="$(gh api "repos/$REPO/milestones" --jq 'map(.title) | join(", ")' 2>/dev/null)"
  ok "milestones: ${ms:-(nenhum)}"
  prj="$(gh project list --owner @me --format json 2>/dev/null | python -c "
import json,sys
try:
    ps=json.load(sys.stdin)['projects']
    print(', '.join(p['title'] for p in ps) or '(nenhum)')
except Exception: print('?')")"
  ok "projects do owner: $prj"
  exit 0
fi

[ "$DRY_RUN" = "1" ] && aviso "DRY_RUN=1 — nada será alterado"

case "$ONLY" in
  labels)     instalar_labels ;;
  milestones) instalar_milestones ;;
  project)    instalar_project ;;
  all)        instalar_labels; instalar_milestones; instalar_project ;;
  *) erro "ONLY inválido: $ONLY (use labels | milestones | project | all)"; exit 1 ;;
esac

printf '\n%sConcluído.%s Próximo passo: project-automation.yml assume o movimento de cards (In Review/Done) — os estados intermediários você arrasta no board.\n' "$G" "$Z"
