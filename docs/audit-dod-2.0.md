# Auditoria do DoD da 2.0 — métrica a métrica, com evidência

- **Data**: 2026-09-24 · **Issue**: #64 (epic #47) · **Base auditada**: `develop` `467920c`
- **Método**: cada métrica do §5 do [roadmap 2.0](roadmap-2.0.md) foi verificada com o
  comando que a prova (reproduzível localmente) ou com o artefato remoto correspondente
  (CI, alertas). Nenhuma linha abaixo é impressão: há comando ou link.
- **Veredito**: **11 das 12 métricas verdes com verificação mecânica hoje** — e o
  conserto de um achado real (onboarding em máquina limpa) entra junto com esta auditoria.
  O que falta de verdade está na seção final: nada técnico bloqueia a 2.0.0.

## 1 · As 12 métricas do DoD, verificadas

| # | Métrica (alvo) | Evidência | Veredito |
|---|---|---|---|
| 1 | **Suíte** 100% verde, pytest, pirâmide declarada | `uv run pytest` → **355 passed in 19,22s**; camadas unit/contract/integration/e2e em `tests/` | ✅ |
| 2 | **Cobertura** ≥ 90% (gate) | `pytest --cov` → **91,52%**; `fail_under = 90.0` no `pyproject.toml` reprova no CI | ✅ |
| 3 | **Lint/formatação** zero violação | `ruff check .` → "All checks passed!"; `ruff format --check .` → 103 files formatted. Fora de escopo declarado no próprio DoD: `.github/scripts` e skills de terceiros | ✅ |
| 4 | **Tipos** `mypy --strict` no pacote | `uv run mypy` → "Success: no issues found in 35 source files" | ✅ |
| 5 | **Agentes** `tsc --noEmit` limpo | `npx -y -p typescript@5.9.2 tsc --noEmit -p tsconfig.json` → exit 0 (20 agentes na auditoria; 21 hoje) | ✅ |
| 6 | **Sincronia** guarda verde | `tests/e2e/test_derivados.py` + `test_sincronia.py`: regenera todos os `.prst` com `GP100_BUILD_TIME` fixo e compara **byte a byte**; reforço: clone limpo **sem** `patches/` tem a suíte verde (achado A1) | ✅ |
| 7 | **CI** ≤ 6 min com cache | Run da `develop` (20:08:53 → veredito 20:09:18): **23 s**, jobs paralelos (Testes/Qualidade/Agentes ~15–17 s cada) | ✅ |
| 8 | **Segurança** 0 alerta aberto | CodeQL scanning alerts: **0**; Dependabot alerts: **0**; `audit_workflows.py` → 5 workflows dentro das regras (21 avisos de pinagem — política "aceito no major", parte 1) | ✅ |
| 9 | **Documentação** consistente (linter #58 + revisão) | O linter de consistência é a **#58 (aberta, v2.0.0)** — a única métrica sem verificação automatizada. Hoje: revisão manual; amostra verificada — as 3 ocorrências restantes de `python tools/` são históricas/migração (proposer, `docs/audit-2.0.md`, ADR-0001), zero instrução viva | ⚠️ revisão OK, automação pendente (#58) |
| 10 | **Releases** changelog dos commits, versão de fonte única, tag | `release.yml` L134–172: `gp100 build --quiet` → `gp100 release` → `gp100 changelog --version` → notas → ZIPs → Release; `VERSION` = `1.0.0` (fonte única), tag `v1.0.0` | ⚠️ mecanismo pronto; a **primeira release do mecanismo é a própria #59** |
| 11 | **Onboarding** `clone && uv sync && pytest` verde | **Estava quebrado** (achado A1) — reproduzido e corrigido nesta auditoria; clone limpo → `uv sync` → `pytest` → **355 passed** | ✅ pós-conserto |
| 12 | **Legado** `tools/` extinta | `ls tools` → inexistente; `git grep "python tools/"` → só contexto histórico (ver métrica 9); pipeline vivo em `gp100 build` (roda no CI e na release) | ✅ |

## 2 · Achados da auditoria

### A1 · Onboarding em máquina limpa falhava (corrigido)

`git clone && uv sync && uv run pytest` reproduzia **falha** — a classe de erro que a
auditoria existia para achar: testes que liam `patches/**` (derivado, fora do git por
ADR-0013) passavam no CI porque o job roda `gp100 build` **antes** do pytest; num clone
limpo ninguém roda o build primeiro.

**Conserto** (mesmo PR desta auditoria):
- `tests/integration/test_release.py`: fixture de módulo **gera** o `.prst` do SMOO1RI
  em `tmp_path_factory` a partir do defs (`biblioteca.gerar` — mesma fonte do build);
  nenhum teste lê derivado do disco do repo.
- `tests/contract/test_cli_producao.py::test_analyze_disseca_export_e_salva_json`: o
  sandbox copia `data/`, roda `pipeline.executar` (a fonte do `gp100 build`) e o export
  aponta para lá — reproduzindo o fluxo real do usuário (build antes de export).

**Prova**: clone limpo em `%TEMP%` → `uv sync` → `uv run pytest` → **355 passed**.

**Nota de ciclo de vida**: o `release.yml` ganhou o passo de build em `c95f627`
("ci(#8): construir os derivados antes da suíte"), **depois** do tag `v1.0.0` — o
workflow taggeado nunca rodou o build antes da suíte: a mesma classe de falha dormia
no corte de release. O conserto acima cobre a suíte em qualquer clone; a release
`2.0.0` será o primeiro corte com o workflow já imune (build antes de empacotar é
passo fixo desde a #33).

### A2 · Exceções conscientes que permanecem

- `.github/scripts/` e skills de terceiros fora dos gates de ruff — decisão explícita
  do DoD (superfície shell/conteúdo externo), registrada aqui como exceção vigiada.
- O auditor de workflows aceita pinagem por major (parte 1 da política de SHA) — 21
  avisos hoje, zero reprovação; a parte 2 (pin por SHA integral) continua no backlog
  de endurecimento.

## 3 · Itens abertos do milestone — o que falta de verdade

| Item | Julgamento da auditoria |
|---|---|
| **#59** (publicar a 2.0.0) | A única pendência **essencial**: o DoD de releases (métrica 10) só se completa com a primeira release publicada. Ritual e agente propositor (#56) prontos; decisão MAJOR×MINOR aguarda o mantenedor |
| **#82** (derivados no corte) | **Trabalho 100% entregue** (PR #25): `patches/**` fora do git (0 arquivos), release builda antes de empacotar, guarda prova determinismo, clone limpo íntegro (A1). Residual burocrático — fechar na revisão do milestone |
| **#12** (álbum novo) | Conteúdo é trajetória, não DoD — 97 patches/6 álbuns não bloqueiam a 2.0.0; risco de agenda apenas |
| **#58** (linter de docs) | A única métrica do DoD sem automação; decidir entre v2.0.0 com revisão manual (recomendado) ou descopar para v2.x |
| **#60/#61** (MkDocs/guias) | Não são DoD — a superfície "navegável" já está no ar (site + `/catalog/`); decisão de escopo |

**Conclusão**: nenhuma incerteza técnica resta no caminho crítico. O que separa a
`develop` da 2.0.0 é **a release em si** e **duas decisões de escopo** (#58, #12).
