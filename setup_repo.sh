#!/usr/bin/env bash
#
# setup_repo.sh — aplica no GitHub, via `gh`, a configuração que o repositório
# descreve em texto (SECURITY.md, CONTRIBUTING.md, .github/*). Idempotente: rodar
# duas vezes não quebra nada, e rodar de novo é como você reaplica o estado.
#
# Uso:
#   ./setup_repo.sh                    # aplica tudo
#   DRY_RUN=1 ./setup_repo.sh          # só mostra o que faria (recomendado na 1ª vez)
#   ./setup_repo.sh --check            # só lê o estado atual e imprime o diagnóstico
#
# Pré-requisitos: `gh` autenticado com escopo `repo` e permissão de admin no
# repositório (branch protection e security features exigem admin).
#
# ─────────────────────────────────────────────────────────────────────────────
# ⚠️ DUAS DECISÕES QUE VOCÊ PRECISA CONHECER ANTES DE RODAR
#
# 1. O bot do GitHub Actions precisa furar o branch protection.
#    Dois workflows ESCREVEM no `main`: o `data-pipeline` do ci.yml (que commita
#    os dados regenerados) e o `release.yml` (que commita VERSION + CHANGELOG).
#    Se o protection exigir PR sem liberar ninguém, os dois pushes são
#    REJEITADOS e o CI passa a falhar de um jeito confuso. Por isso o app
#    `github-actions` entra em `bypass_pull_request_allowances`.
#
# 2. NÃO habilitamos `sha_pinning_required` nas Actions.
#    Os workflows existentes usam tags (`actions/checkout@v4`). Exigir SHA fixo
#    tornaria todos eles inválidos de uma vez. O caminho certo é o que este repo
#    já tem: o `audit_workflows.py` avisa a cada execução e o Dependabot
#    (`.github/dependabot.yml`) mantém as Actions atualizadas, o que torna a
#    fixação por SHA sustentável — migração gradual, workflow por workflow.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuração (sobrescreva por variável de ambiente) ──────────────────────
REPO="${REPO:-lucascantarelli/gp-100-patch-architect}"
BRANCH="${BRANCH:-main}"

# Nº de aprovações exigidas. 0 = revisão obrigatória de PR mas sem terceiro
# aprovador, que é o único arranjo que funciona com um mantenedor só (o GitHub
# não permite aprovar o próprio PR). Suba para 1 quando houver mais gente — o
# mantenedor é colocado automaticamente na lista de bypass para não travar.
REQUIRED_APPROVALS="${REQUIRED_APPROVALS:-0}"

# O check que vale como veredito. Precisa bater EXATAMENTE com o `name:` do job
# no ci.yml — confira em Actions → CI → o nome do check na aba de checks.
CI_CHECK="${CI_CHECK:-🚦 Veredito do CI}"

# Exigir branch atualizada antes do merge. Fica `false` de propósito: o
# auto-commit de dados mexe no main sozinho, e `true` forçaria rebase a cada
# auto-commit — churn sem ganho real neste projeto.
STRICT_CHECKS="${STRICT_CHECKS:-false}"

# Aplicar as regras também a admins. `false` mantém a saída de emergência do
# mantenedor; `true` é o mais rígido e depende do bypass do bot estar correto.
ENFORCE_ADMINS="${ENFORCE_ADMINS:-false}"

DRY_RUN="${DRY_RUN:-0}"
MODO_CHECK=0
[ "${1:-}" = "--check" ] && MODO_CHECK=1

DESCRIPTION="Agente que cria patches Valeton GP-100 a partir do rig real de cada música — 62 patches documentados + .prst importáveis"
TOPICS=(valeton gp-100 guitar-pedal impulse-response guitar-tones patch-library
        freebuff python data-pipeline conventional-commits codeql band-patches)

# ── Plomería ─────────────────────────────────────────────────────────────────
if [ -t 1 ]; then B=$'\e[1m'; G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; Z=$'\e[0m'
else B=; G=; Y=; R=; Z=; fi

falar()  { printf '%s\n' "$*"; }
passo()  { printf '\n%s▸ %s%s\n' "$B" "$*" "$Z"; }
ok()     { printf '  %s✓%s %s\n' "$G" "$Z" "$*"; }
aviso()  { printf '  %s!%s %s\n' "$Y" "$Z" "$*"; }
erro()   { printf '  %s✗%s %s\n' "$R" "$Z" "$*" >&2; }

# Executa (respeitando DRY_RUN) e mostra o comando.
fazer() {
  if [ "$DRY_RUN" = "1" ]; then
    printf '  %s[dry-run]%s %s\n' "$Y" "$Z" "$*"
  else
    "$@" >/dev/null
  fi
}

# ── Pré-checagens ────────────────────────────────────────────────────────────
passo "Pré-checagens"
command -v gh >/dev/null || { erro "gh não encontrado no PATH."; exit 1; }
ok "gh instalado ($(gh --version | head -1 | cut -d' ' -f3))"

gh auth status >/dev/null 2>&1 || { erro "gh não autenticado — rode: gh auth login"; exit 1; }
ok "gh autenticado"

if ! gh api "repos/$REPO" >/dev/null 2>&1; then
  erro "Sem acesso a $REPO (verifique o nome e o escopo do token)."; exit 1
fi
ok "repositório acessível: $REPO"

DONO="${REPO%%/*}"
ADMIN_OK=0
if [ "$(gh api "repos/$REPO" --jq '.permissions.admin' 2>/dev/null)" = "true" ]; then
  ADMIN_OK=1; ok "você é admin deste repositório"
else
  aviso "você NÃO é admin — branch protection e security features vão falhar"
fi

if [ "$MODO_CHECK" = "1" ]; then
  passo "Estado atual (--check)"
  gh api "repos/$REPO" --jq '"descrição: \(.description // "(vazia)")\ntópicos:   \(.topics | if length == 0 then "(nenhum)" else join(", ") end)\nlicença:   \(.license.spdx_id // "(nenhuma)")\nmerge:     squash=\(.allow_squash_merge) merge=\(.allow_merge_commit) rebase=\(.allow_rebase_merge) del-branch=\(.delete_branch_on_merge)"'
  falar ""
  falar "proteção de $BRANCH: $(gh api "repos/$REPO/branches/$BRANCH/protection" --jq '.required_pull_request_reviews.required_approving_review_count' 2>/dev/null || echo 'NÃO PROTEGIDA')"
  falar "health score:       $(gh api "repos/$REPO/community/profile" --jq '.health_percentage')%"
  falar "CodeQL:             $(gh api "repos/$REPO/code-scanning/default-setup" --jq '.state' 2>/dev/null)"
  exit 0
fi

[ "$DRY_RUN" = "1" ] && aviso "DRY_RUN=1 — nada será alterado"

# ── 1 · Metadados ────────────────────────────────────────────────────────────
passo "1 · Metadados (descrição e tópicos)"
fazer gh repo edit "$REPO" --description "$DESCRIPTION" --enable-discussions
ok "descrição definida"

args=()
for t in "${TOPICS[@]}"; do args+=(--add-topic "$t"); done
fazer gh repo edit "$REPO" "${args[@]}"
ok "${#TOPICS[@]} tópicos aplicados"

# ── 2 · Segurança ────────────────────────────────────────────────────────────
passo "2 · Recursos de segurança"
fazer gh api -X PUT "repos/$REPO/vulnerability-alerts"
ok "alertas de vulnerabilidade (Dependabot) ligados"

fazer gh api -X PUT "repos/$REPO/automated-security-fixes"
ok "security updates automáticos ligados"

fazer gh api -X PUT "repos/$REPO/private-vulnerability-reporting"
ok "divulgação privada de vulnerabilidades ligada (canal do SECURITY.md)"

# Push protection já vem ligado em repositório público novo; reforçamos aqui as
# duas checagens opcionais, que são as que costumam faltar.
fazer gh api -X PATCH "repos/$REPO" \
  -F 'security_and_analysis[secret_scanning][status]=enabled' \
  -F 'security_and_analysis[secret_scanning_push_protection][status]=enabled' \
  -F 'security_and_analysis[secret_scanning_validity_checks][status]=enabled' \
  -F 'security_and_analysis[secret_scanning_non_provider_patterns][status]=enabled'
ok "secret scanning, push protection e checagens de validade ligados"

aviso "CodeQL: configurado por workflow (security.yml), NÃO pelo default setup —"
aviso "não ligue o default setup no painel, os dois juntos se anulam."

# ── 3 · Fluxo de merge ───────────────────────────────────────────────────────
passo "3 · Fluxo de merge (squash-only, branch limpa, auto-merge)"
fazer gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_auto_merge=true \
  -F allow_update_branch=true
ok "squash é o único merge; branch apagada após o merge"

# ── 4 · Permissões das Actions ───────────────────────────────────────────────
passo "4 · Permissões das Actions"
fazer gh api -X PUT "repos/$REPO/actions/permissions" \
  -f enabled=true -f allowed_actions=all
ok "Actions habilitadas (allowlist ampla de propósito — ver o aviso no topo)"

fazer gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=false
ok "token default dos workflows é SOMENTE LEITURA (cada job eleva o que precisa)"

# ── 5 · Branch protection ────────────────────────────────────────────────────
passo "5 · Proteção de $BRANCH"

if [ "$REQUIRED_APPROVALS" -gt 0 ]; then
  code_owners=true
  aviso "exigindo $REQUIRED_APPROVALS aprovação(ões) — '$DONO' entra no bypass para poder mergear o próprio PR"
else
  code_owners=false
  ok "exigindo PR, mas sem aprovador terceiro (mantenedor único não pode aprovar o próprio PR)"
fi

PROTECAO=$(cat <<JSON
{
  "required_status_checks": {
    "strict": $STRICT_CHECKS,
    "contexts": ["$CI_CHECK"]
  },
  "enforce_admins": $ENFORCE_ADMINS,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": $code_owners,
    "required_approving_review_count": $REQUIRED_APPROVALS,
    "bypass_pull_request_allowances": {
      "users": ["$DONO"],
      "teams": [],
      "apps": ["github-actions"]
    }
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON
)

if [ "$DRY_RUN" = "1" ]; then
  printf '  %s[dry-run]%s PUT branches/%s/protection <<<\n%s\n' "$Y" "$Z" "$BRANCH" "$PROTECAO"
else
  if printf '%s' "$PROTECAO" | gh api -X PUT "repos/$REPO/branches/$BRANCH/protection" \
      --input - >/dev/null 2>&1; then
    ok "proteção aplicada (PR + check '$CI_CHECK' + bypass do bot)"
  else
    erro "falhou — se a mensagem falar de check inexistente, rode o CI uma vez e"
    erro "ajuste CI_CHECK para o nome exato do check: CI_CHECK='...' ./setup_repo.sh"
  fi
fi

# ── 6 · Labels ───────────────────────────────────────────────────────────────
passo "6 · Labels padronizadas"
# `--force` atualiza descrição/cor de label existente (idempotente).
while IFS='|' read -r nome cor desc; do
  [ -z "$nome" ] && continue
  if [ "$DRY_RUN" = "1" ]; then
    printf '  %s[dry-run]%s label: %s\n' "$Y" "$Z" "$nome"
  else
    gh label create "$nome" --color "$cor" --description "$desc" --force >/dev/null 2>&1 \
      && ok "$nome" || aviso "não criei $nome"
  fi
done <<'LABELS'
bug|d73a4a|Algo não funciona como documentado
data|0e8a16|Dados gerados pelo pipeline (patches, índices, catálogo de IRs)
documentation|0075ca|Melhoria ou correção em documentação
prst-import|1d76db|Falha ao importar .prst na pedaleira ou no GP-100 Edits
tone-mismatch|fbca04|O patch importa, mas o som não bate com o patch.md
pipeline|5319e7|Scripts de tools/, geração de dados e CI
ir-library|c5def5|Packs de Impulse Response, slots de User IR e política de IR
security|b60205|Superfície de segurança, dependências e workflows
good first issue|7057ff|Bom para quem está começando
help wanted|008672|Atenção extra é bem-vinda
needs triage|ededed|Aguardando triagem do mantenedor
breaking change|d93f0b|Mudança incompatível (força bump MAJOR)
LABELS

# ── 7 · Verificação ──────────────────────────────────────────────────────────
passo "7 · Verificação final"
if [ "$DRY_RUN" = "1" ]; then
  aviso "dry-run: nada a verificar (rode sem DRY_RUN para aplicar)"
else
  HEALTH=$(gh api "repos/$REPO/community/profile" --jq '.health_percentage')
  falar "  health score: ${HEALTH}%"
  falar "  proteção:     $(gh api "repos/$REPO/branches/$BRANCH/protection" --jq '"PR=\(.required_pull_request_reviews != null) checks=\(.required_status_checks.contexts | join(","))"' 2>/dev/null || echo 'AUSENTE')"
  falar "  tópicos:      $(gh api "repos/$REPO" --jq '.topics | join(", ")')"
  falar ""
  falar "Próximo passo: faça um push no main e confira os 3 workflows em"
  falar "  https://github.com/$REPO/actions"
fi

printf '\n%sConcluído.%s\n' "$G" "$Z"
