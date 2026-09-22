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
# O FLUXO (detalhado em CONTRIBUTING.md)
#
#   develop     →  onde se trabalha: push direto liberado, CI a cada push
#        ↓  PR de release (quando a release for aprovada)
#   main        →  publicada; protegida, e o merge aqui dispara a Release
#
# POR QUE ESTE SCRIPT EXISTE — E POR QUE ELE É LOCAL
#
# Branch protection, permissão default do token e secret scanning não são
# versionáveis: vivem no servidor, não no git. E nenhum workflow pode
# configurá-los — `GITHUB_TOKEN` não fura branch protection por definição (se
# furasse, a proteção não valeria nada: qualquer action comprometida no pipeline
# poderia desligar a regra). Logo quem aplica é um humano com `admin`, e a única
# forma de isso ser reprodutível em vez de uma lista em prosa é um script.
#
# O repositório NÃO precisa de exceção para o bot, porque nenhum workflow escreve
# em branch: o `ci.yml` roda inteiro com `contents: read` e o `release.yml` só
# cria TAG (proteção de branch não governa tag). Se algum dia um job voltar a
# commitar, o push será rejeitado — e é esse o comportamento correto.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuração (sobrescreva por variável de ambiente) ──────────────────────
REPO="${REPO:-lucascantarelli/gp-100-patch-architect}"

# Branches do fluxo. `develop` é criada a partir de `main` se ainda não existir.
# Só a `main` recebe proteção (PR de release + ci-gate): a `develop` é onde se
# trabalha, com push direto liberado.
BRANCHES=(main develop)
BRANCHES_PROTEGIDAS=(main)
BASE_BRANCH="${BASE_BRANCH:-main}"

# Nº de aprovações exigidas nos PRs.
#
# Hoje: 0 — não porque revisão não importa, mas porque **o GitHub não permite
# aprovar o próprio PR** e existe um único mantenedor. Com 1, nenhum PR seu
# poderia ser mergeado. No dia em que houver segundo revisor, rode:
#     REQUIRED_APPROVALS=1 ./setup_repo.sh
# (aí `require_code_owner_reviews` liga sozinho, e os PRs de quem não é o
# mantenedor passam a exigir aprovação dele).
REQUIRED_APPROVALS="${REQUIRED_APPROVALS:-0}"

# Aplicar as regras também a admins. `true` é o que faz a proteção valer alguma
# coisa: como nenhum workflow escreve em branch, ninguém precisa de exceção.
ENFORCE_ADMINS="${ENFORCE_ADMINS:-true}"

# O check que vale como veredito. Precisa bater EXATAMENTE com o `name:` do job
# no ci.yml — confira em Actions → CI → o nome do check na aba de checks.
CI_CHECK="${CI_CHECK:-🚦 Veredito do CI}"

# Exigir a branch atualizada antes do merge. Fica `false` de propósito: o check
# do PR já roda sobre o merge ref (base + PR), então exigir rebase antes de
# mergear não soma verificação — só churn.
STRICT_CHECKS="${STRICT_CHECKS:-false}"

DRY_RUN="${DRY_RUN:-0}"
MODO_CHECK=0
[ "${1:-}" = "--check" ] && MODO_CHECK=1

DESCRIPTION="Agente que cria patches Valeton GP-100 a partir do rig real de cada música — 62 patches documentados + .prst importáveis"
TOPICS=(valeton gp-100 guitar-pedal impulse-response guitar-tones patch-library
        freebuff python patch-pipeline conventional-commits codeql band-patches)

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

# Proteção da branch de release (`main`): PR obrigatório + ci-gate verde.
proteger() {
  local b="$1" code_owners="$2" protecao
  # Sem `bypass_pull_request_allowances`: ninguém precisa furar nada. O bot não
  # escreve em branch (ver o cabeçalho) e o mantenedor passa por PR como qualquer
  # pessoa. Force-push e deleção ficam bloqueados para todos, inclusive admins.
  #
  # `required_linear_history: false` é obrigatório aqui: o release vai de `develop`
  # para `main` como merge commit (ver o passo 4), e histórico linear proibiria
  # exatamente esse merge.
  protecao=$(cat <<JSON
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
      "users": [],
      "teams": [],
      "apps": []
    }
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON
)
  if [ "$DRY_RUN" = "1" ]; then
    printf '  %s[dry-run]%s PUT branches/%s/protection <<<\n%s\n' "$Y" "$Z" "$b" "$protecao"
    return 0
  fi
  if printf '%s' "$protecao" | gh api -X PUT "repos/$REPO/branches/$b/protection" \
      --input - >/dev/null 2>&1; then
    ok "$b protegida (PR + check '$CI_CHECK', force-push e deleção bloqueados)"
  else
    erro "falhou ao proteger $b — se a mensagem falar de check inexistente, rode o"
    erro "CI uma vez e ajuste CI_CHECK para o nome exato: CI_CHECK='...' ./setup_repo.sh"
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

if [ "$(gh api "repos/$REPO" --jq '.permissions.admin' 2>/dev/null)" = "true" ]; then
  ok "você é admin deste repositório"
else
  aviso "você NÃO é admin — branch protection e security features vão falhar"
fi

# ── Modo --check: só leitura ─────────────────────────────────────────────────
if [ "$MODO_CHECK" = "1" ]; then
  passo "Estado atual (--check)"
  gh api "repos/$REPO" --jq '"descrição: \(.description // "(vazia)")\ntópicos:   \(.topics | if length == 0 then "(nenhum)" else join(", ") end)\nlicença:   \(.license.spdx_id // "(nenhuma)")\nmerge:     squash=\(.allow_squash_merge) merge=\(.allow_merge_commit) rebase=\(.allow_rebase_merge) del-branch=\(.delete_branch_on_merge)"'
  falar ""
  for b in "${BRANCHES[@]}"; do
    if gh api "repos/$REPO/branches/$b" >/dev/null 2>&1; then
      estado="$(gh api "repos/$REPO/branches/$b/protection" \
        --jq '"PR=\(.required_pull_request_reviews != null) aprovações=\(.required_pull_request_reviews.required_approving_review_count // 0) admins=\(.enforce_admins.enabled) checks=\(.required_status_checks.contexts | join(","))"' \
        2>/dev/null || echo 'SEM PROTEÇÃO')"
      falar "  $b: existe · $estado"
    else
      falar "  $b: NÃO EXISTE"
    fi
  done
  falar ""
  falar "  health score: $(gh api "repos/$REPO/community/profile" --jq '.health_percentage')%"
  falar "  CodeQL:       $(gh api "repos/$REPO/code-scanning/default-setup" --jq '.state' 2>/dev/null)"
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

# ── 2 · Branches ─────────────────────────────────────────────────────────────
passo "2 · Branches do fluxo"
for b in "${BRANCHES[@]}"; do
  if gh api "repos/$REPO/branches/$b" >/dev/null 2>&1; then
    ok "$b já existe"
  elif [ "$b" = "$BASE_BRANCH" ]; then
    erro "$BASE_BRANCH não existe — crie a branch padrão antes de rodar isto."; exit 1
  else
    sha="$(gh api "repos/$REPO/git/ref/heads/$BASE_BRANCH" --jq '.object.sha')"
    fazer gh api -X POST "repos/$REPO/git/refs" -f ref="refs/heads/$b" -f sha="$sha"
    ok "$b criada a partir de $BASE_BRANCH (${sha:0:7})"
  fi
done
aviso "develop não recebe regra nenhuma de propósito: é onde se trabalha, com push direto."

# ── 3 · Segurança ────────────────────────────────────────────────────────────
passo "3 · Recursos de segurança"
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

# ── 4 · Fluxo de merge ───────────────────────────────────────────────────────
passo "4 · Fluxo de merge"
# `allow_merge_commit` fica LIGADO de propósito, e isso não é descuido: o PR que
# leva `develop` → `main` precisa de merge commit. Se ele fosse squash, a `main`
# receberia um único commit com tudo — e o CHANGELOG (que é derivado dos commits)
# sairia vazio, porque as features que alimentam o changelog viveriam só na
# `develop`. Com merge commit a `main` contém a história da `develop`, e a
# `develop` continua ancestral da `main` (nada de sync para trás).
#
# Convenção de uso: `--merge` em `develop` → `main`; squash só em PR externo
# contra a `develop`, se houver.
fazer gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true \
  -F allow_merge_commit=true \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true \
  -F allow_auto_merge=true \
  -F allow_update_branch=true
ok "merge commit para o release; rebase desligado (squash só em PR externo, se houver)"

# ── 5 · Permissões das Actions ───────────────────────────────────────────────
passo "5 · Permissões das Actions"
fazer gh api -X PUT "repos/$REPO/actions/permissions" \
  -f enabled=true -f allowed_actions=all
ok "Actions habilitadas"

fazer gh api -X PUT "repos/$REPO/actions/permissions/workflow" \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=false
ok "token default dos workflows é SOMENTE LEITURA (cada job eleva o que precisa)"

# ── 6 · Branch protection ────────────────────────────────────────────────────
passo "6 · Proteção da branch de release (main)"

if [ "$REQUIRED_APPROVALS" -gt 0 ]; then
  code_owners=true
  ok "exigindo $REQUIRED_APPROVALS aprovação(ões) + revisão de CODEOWNERS"
else
  code_owners=false
  aviso "PR obrigatória sem aprovador terceiro (mantenedor único não aprova o próprio PR)"
  aviso "quando houver segundo revisor: REQUIRED_APPROVALS=1 ./setup_repo.sh"
fi

if [ "$ENFORCE_ADMINS" = "true" ]; then
  ok "as regras valem para você também (nenhuma exceção de bypass)"
else
  aviso "ENFORCE_ADMINS=false — você (admin) fura as regras; só os demais ficam presos"
fi

for b in "${BRANCHES_PROTEGIDAS[@]}"; do
  proteger "$b" "$code_owners"
done

# ── 7 · Labels ───────────────────────────────────────────────────────────────
passo "7 · Labels padronizadas"
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
release|0e8a16|Preparação de versão (VERSION + CHANGELOG)
good first issue|7057ff|Bom para quem está começando
help wanted|008672|Atenção extra é bem-vinda
needs triage|ededed|Aguardando triagem do mantenedor
breaking change|d93f0b|Mudança incompatível (força bump MAJOR)
LABELS

# ── 8 · Verificação ──────────────────────────────────────────────────────────
passo "8 · Verificação final"
if [ "$DRY_RUN" = "1" ]; then
  aviso "dry-run: nada a verificar (rode sem DRY_RUN para aplicar)"
else
  falar "  health score: $(gh api "repos/$REPO/community/profile" --jq '.health_percentage')%"
  for b in "${BRANCHES[@]}"; do
    falar "  $b: $(gh api "repos/$REPO/branches/$b/protection" \
      --jq '"PR=\(.required_pull_request_reviews != null) admins=\(.enforce_admins.enabled) checks=\(.required_status_checks.contexts | join(","))"' \
      2>/dev/null || echo 'SEM PROTEÇÃO')"
  done
  falar "  tópicos:      $(gh api "repos/$REPO" --jq '.topics | join(", ")')"
fi

passo "Como fica o dia a dia"
falar "  Push direto na develop. A main só recebe release aprovada:"
falar ""
falar "    git switch develop && git pull"
falar "    # ... trabalho: edite os defs, rode o pipeline e a suíte ..."
falar "    git commit -m 'feat(...)' && git push"
falar ""
falar "  Para lançar uma versão (a Release dispara sozinha no merge para a main):"
falar "    python tools/gen_changelog.py --version X.Y.Z --write"
falar "    printf '%s\\n' X.Y.Z > VERSION"
falar "    git commit -am 'chore(release): vX.Y.Z' && git push"
falar "    gh pr create --base main --head develop --title 'chore(release): vX.Y.Z'"
falar "    gh pr merge --merge"
falar ""
falar "  develop → main é MERGE COMMIT (sem --delete-branch, que apagaria a develop —"
falar "  o squash apagaria a história da develop na main e o CHANGELOG sairia vazio)"
falar ""
falar "  O CI roda a cada push na $BASE_BRANCH/develop e em todo PR (o de release):"
falar "    https://github.com/$REPO/actions"

printf '\n%sConcluído.%s\n' "$G" "$Z"
