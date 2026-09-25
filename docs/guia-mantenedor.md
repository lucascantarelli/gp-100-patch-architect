# Guia do mantenedor — release, triagem e board

**Leia isto se** você **corta release, tria issue e gere o board** — a parte
que só existe com responsabilidade de escrita. Tudo aqui pressupõe o setup do
[guia do contribuidor](guia-contribuidor.md) já verde.

## 1 · Cortar a release (ritual ADR-0010)

```
suíte verde → build regenerado (idempotente) → changelog → VERSION
  → commit de release → tag → PR develop → main → artefatos anexados
```

Passo a passo real:

1. **Proposta, não decisão**: peça ao agente `gp100-release-proposer` — ele roda
   `uv run gp100 changelog` (fonte única), cruza com `git log <tag>..HEAD`,
   propõe o bump **com evidência por commit** e **nunca decide** (o caso
   `BREAKING CHANGE` fica marcado `confirmado: false` até você responder)
2. **Bump**: edite `VERSION` (fonte única — o `pyproject.toml` o lê)
3. **Tag e push**: o `release.yml` roda `gp100 build --quiet` → `gp100 release`
   → ZIPs + notas do changelog → GitHub Release automaticamente
4. **`develop` → `main`**: PR (a `main` só recebe release aprovada; os checks
   obrigatórios valem inclusive para admin)

## 2 · Triagem de issue (o board é a fonte de verdade)

1. Toda issue nova recebe `type:`, `size:`, `scope:` e milestone — o Guardian
   cobra o mesmo de PR (taxonomia no
   `bootstrap_project_management.sh`)
2. Pronta para implementação? `status: ready-for-pr` (fila dos contribuidores)
3. O card entra no Project #7 sozinho (workflow `Entra no Project`); o estado
   Kanban acompanha a issue por automação — **divergência é bug** (doc 18)

## 3 · Ler review sem engolir ruído

O caso fundador da governança foi um **PR mergeado com review não lido**
(doc 21). Rotina mínima:

- Review com veredito: leia **antes** do merge; comentário sem veredito não
  bloqueia
- O `ci-gate` (Veredito do CI) é obrigatório por branch protection — nunca
  mergeie com `UNSTABLE`
- CodeQL/Dependabot com alerta aberto = merge bloqueado na prática (critério
  do DoD: **0 alertas**)

## 4 · Status do projeto em dois comandos

```bash
uv run gp100 verify        # derivados em frescor com o defs?
gh issue list --milestone "v2.0.0 — Formato, site e escala" --state open
```

Auditorias de referência: `docs/audit-2.0.md` (técnica) e
`docs/audit-dod-2.0.md` (DoD métrica a métrica — 11/12 verdes).

---

**Próximo passo**: para cortar a **2.0.0**, peça a proposta ao
`gp100-release-proposer` e siga o §1. Para entender **por que** o fluxo é
assim, o índice dos ADRs está em [docs/decisions](decisions/README.md).
