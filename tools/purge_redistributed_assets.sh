#!/usr/bin/env bash
#
# purge_redistributed_assets.sh — remove do HISTÓRICO do git os ativos de
# terceiros que foram versionados por engano.
#
# O que sai do histórico (e já está fora do HEAD desde o commit que parou de
# versioná-los):
#   impulse_responses/**            — packs de IR de terceiros (licença alheia)
#   impulse_responses/README.md     — PRESERVADO: é a documentação do fluxo
#   manual.pdf                      — manual oficial da Valeton
#
# POR QUE ESTE SCRIPT EXISTE SEPARADO DO setup_repo.sh
# Reescrita de histórico é irreversível e reescreve TODOS os hashes. Não pode ser
# um passo escondido dentro de um script de configuração — precisa de decisão
# consciente, backup e um push explícito depois. Por isso este script:
#
#   * exige a árvore de trabalho limpa (tudo commitado);
#   * cria um backup (tag + branch) antes de tocar em qualquer coisa;
#   * exige a palavra PURGE digitada;
#   * NÃO faz push — ele imprime os comandos e você decide.
#
# Uso:
#   ./tools/purge_redistributed_assets.sh            # mostra o plano e sai
#   CONFIRMAR=1 ./tools/purge_redistributed_assets.sh  # executa (pede PURGE)
#
# Depois de executar, para publicar (você, manualmente):
#   git remote add origin git@github.com:<owner>/<repo>.git   # o filter-repo remove
#   git push --force-with-lease origin main
#   git push --force origin --tags
#
# ⚠️ Quem já clonou precisa re-clonar. Avise os colaboradores ANTES do push: um
# force-push em história compartilhada faz o clone antigo reenviar os arquivos
# purgados no próximo push daquela pessoa.

set -euo pipefail

ASSETS=(impulse_responses manual.pdf)
PRESERVAR='impulse_responses/README.md'
BACKUP="backup-pre-purge-$(date +%Y%m%d-%H%M%S)"

if [ -t 1 ]; then B=$'\e[1m'; G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; Z=$'\e[0m'
else B=; G=; Y=; R=; Z=; fi
passo() { printf '\n%s▸ %s%s\n' "$B" "$*" "$Z"; }
ok()    { printf '  %s✓%s %s\n' "$G" "$Z" "$*"; }
aviso() { printf '  %s!%s %s\n' "$Y" "$Z" "$*"; }
erro()  { printf '  %s✗%s %s\n' "$R" "$Z" "$*" >&2; }

cd "$(git rev-parse --show-toplevel)"

passo "1 · Pré-checagens"

if [ -n "$(git status --porcelain)" ]; then
  erro "A árvore de trabalho não está limpa — commite (ou stashe) antes de reescrever a história."
  git status --short | head -20
  exit 1
fi
ok "árvore de trabalho limpa"

if ! command -v git-filter-repo >/dev/null; then
  erro "git-filter-repo não encontrado."
  printf '\n  Instale (é o método que o próprio git recomenda em vez de filter-branch):\n'
  printf '    pip install git-filter-repo        # ou: brew install git-filter-repo\n\n'
  printf '  Motivo de não cair para `git filter-branch`: ele é lento, tem armadilhas\n'
  printf '  conhecidas de reescrita de merge e foi desaconselhado pelo time do git.\n'
  exit 1
fi
ok "git-filter-repo disponível"

passo "2 · Tamanho atual e o que sai"
TAM_ANTES=$(du -sh .git 2>/dev/null | cut -f1)
printf '  .git agora: %s\n' "$TAM_ANTES"
for alvo in "${ASSETS[@]}"; do
  n=$(git log --oneline --all -- "$alvo" | wc -l)
  printf '  %-22s presente em %s commit(s)\n' "$alvo" "$n"
done
printf '  %-22s %s\n' "preservado:" "$PRESERVAR"

if [ "${CONFIRMAR:-0}" != "1" ]; then
  passo "Plano (nada foi alterado)"
  cat <<PLANO
  Este script vai:
    1. criar a tag e a branch de backup '$BACKUP'
    2. rodar git filter-repo removendo:
         $(printf '%s ' "${ASSETS[@]}")
       ...exceto $PRESERVAR
    3. NÃO fazer push

  Para executar de verdade:
    CONFIRMAR=1 $0
PLANO
  exit 0
fi

passo "3 · Backup antes de qualquer reescrita"
git tag "$BACKUP"
git branch "$BACKUP" 2>/dev/null || aviso "branch de backup já existia"
ok "backup criado: tag e branch '$BACKUP'"
aviso "para desfazer tudo: git reset --hard $BACKUP"

passo "4 · Confirmação"
printf '  Digite %sPURGE%s para reescrever a história: ' "$B" "$Z"
read -r resposta
[ "$resposta" = "PURGE" ] || { erro "cancelado."; exit 1; }

passo "5 · Reescrita do histórico"
# `--paths-from-file` aceita globs e negação com '!': assim o README do banco
# continua na história, e só o conteúdo de terceiros desaparece.
ARQUIVO=$(mktemp)
{
  printf 'impulse_responses/*\n'
  printf '!%s\n' "$PRESERVAR"      # negação: mantém a documentação
  printf 'manual.pdf\n'
} > "$ARQUIVO"
cat "$ARQUIVO" | sed 's/^/    /'

git filter-repo --paths-from-file "$ARQUIVO" --invert-paths --force
rm -f "$ARQUIVO"

passo "6 · Resultado"
TAM_DEPOIS=$(du -sh .git 2>/dev/null | cut -f1)
ok ".git: $TAM_ANTES → $TAM_DEPOIS"
ok "commits reescritos: $(git rev-list --count HEAD)"
if [ -e manual.pdf ]; then
  aviso "manual.pdf continua no disco (fora do git — que é o esperado)"
fi
# `grep -c` sai com 1 quando não há match, e sob `set -e`/pipefail isso abortaria
# o script justamente no caso de sucesso total (nenhum ativo sobrando).
restantes=$(git ls-files | grep -c '^impulse_responses' || true)
printf '  arquivos em impulse_responses/ versionados agora: %s\n' "$restantes"

passo "7 · Publicar (manual — este script não faz push)"
cat <<FIM
  O git-filter-repo removeu o remote 'origin' de propósito, para você não
  empurrar a história reescrita por acidente. Restaure e publique:

    git remote add origin git@github.com:${REPO:-<owner>/<repo>}.git
    git push --force-with-lease origin main
    git push --force origin --tags

  Antes do push: avise quem tiver clone. Depois do push, o GitHub ainda pode
  servir os objetos antigos por um tempo (cache de commits órfãos) — se isso for
  crítico, abra um chamado no GitHub Support pedindo o gc do repositório.

  Backup local para desfazer: $BACKUP
FIM

printf '\n%sHistórico reescrito localmente. Nada foi publicado.%s\n' "$G" "$Z"
