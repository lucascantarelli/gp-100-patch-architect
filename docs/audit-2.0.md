# Auditoria técnica 2.0 — estado atual, arquitetura alvo e plano de migração

- **Data**: 2026-09
- **Escopo**: ~6.300 linhas de Python (`tools/`, `tests/`, `.github/scripts/`),
  19 agentes + 11 skills, 24 docs de domínio, 6 workflows, governança do GitHub.
- **Método**: leitura integral dos módulos núcleo, inventário com referência
  cruzada, scanners AST (imports e símbolos sem uso) e comparação do pipeline
  documentado com o executado. Cada achado abaixo tem arquivo/linha ou comando
  que o reproduz — **nenhum item é impressão**.

> Complementa (não substitui) a análise de código morto de `reference/22`: lá o
> foco foi linha e símbolo; aqui o foco é **arquitetura, processo e governança**.

## 1. O que já está certo (e não pode ser perdido na 2.0)

| Ativo | Por que é decisivo |
|---|---|
| **Fonte única** — `tools/patches-defs.json` | Nenhum script tem lista de música, álbum ou IR dentro do código. É a razão do projeto ser confiável. |
| **Guarda de sincronia (TestH)** | Roda o pipeline numa cópia e compara com o commitado: pega "editei o defs e esqueci de regenerar" **e** "editei arquivo gerado à mão". Poucos projetos têm isso. |
| **Formato validado no device** | `.prst` single fw 2.1 verificado byte a byte (CRLF inclusive), com teste de contrato. |
| **CI sem escrita no repositório** | `contents: read` em todos os workflows: a proteção do `main` não precisa de exceção para bot. |
| **Política de segurança real** | `SECURITY.md` com escopo, prazos e canal privado; CodeQL + dependency review + auditor de workflows. |
| **Erro acionável** | O validador diz caminho JSON **e** correção; o build não vaza traceback. |
| **Base de domínio** | 24 documentos de catálogo, workflow e dossiês — ativo raro, e a razão de os agentes funcionarem. |

## 2. Achados por severidade

### 🔴 Crítico (impede evolução)

| # | Achado | Evidência | Consequência |
|---|---|---|---|
| C1 | **Nenhum `pyproject.toml`** — o projeto não era instalável, importável nem verificável | `ls *.toml` vazio antes de PKG-001 | Sem lint, sem tipos, sem cobertura, onboarding manual, import cruzado por `sys.path` |
| C2 | **Colisão de nomes `gp100`** — o script `tools/gp100.py` sombreia qualquer pacote homônimo | `tests/test_gp100_cli.py` faz `import gp100` e recebe o *script* | Bloqueava criar o pacote; resolvido pelo import name `gp100_architect` (ADR-0001) |
| C3 | **Validação em uma porta só** — só o build validava o defs | `gen_indexes`, `gp100`, `build_release` liam JSON cru | Defs quebrado explodia longe da causa; corrigido no PR #21 (M2) e institucionalizado em `infrastructure.defs` (pacote `gp100_architect`, ADR-0001) |
| C4 | **Versão em dois lugares** | `VERSION` + versão escrita em metadados/docs | Risco de release inconsistente; tratado no ADR-0010 (o `pyproject` lê `VERSION`) |

### 🟠 Alto (tratar na 2.0)

| # | Achado | Evidência | Plano |
|---|---|---|---|
| A1 | **Scripts monolíticos** — `build_song_patches.py` mistura geração de doc, `.prst` e validação | `tools/` | #29–#32 separam por caso de uso no pacote (EPIC #41) |
| A2 | **Sem CLI única** — seis `argparse`/`sys.argv` divergentes | `tools/*.py` | #48/#49 portam os comandos para a CLI do pacote (ADR-0003) |
| A3 | **Suíte em `unittest`**, sem pirâmide | `tests/` | #34 (fecha #23): pytest + `tests/{unit,integration,contract,e2e,fixtures}` |
| A4 | **Sem lint/type check de Python** | CI antes de PKG-002 | ruff + mypy strict + pre-commit (ADR-0005) |
| A5 | **Sem cobertura medida** | CI antes de PKG-002 | piso 90% no pacote (91% hoje) |
| A6 | **Docs de engenharia inexistentes** | só `reference/` (domínio) | `ARCHITECTURE.md`, `DEVELOPMENT.md`, `docs/decisions/`, Fase F4 |
| A7 | **CODEOWNERS apontava arquivos inexistentes** (`check_data_freshness.py`) | `.github/CODEOWNERS` | Ajustado + regra no ADR-0009 (caminho citado tem de existir) |
| A8 | **Contagens desatualizadas em docs** ("17 agentes", "43 testes", "56 testes") | README, `knowledge.md`, `tools/README.md` | Corrigido nesta passagem; a regra é derivar, não memorizar |

### 🟡 Médio

| # | Achado | Plano |
|---|---|---|
| M1 | Seeders `add_*.py` são fonte executável da história do defs, não código morto — mas serão aposentados pelo schema v2 | #8 (EPIC #42) → schema v2 é **2.0**, não 3.0 |
| M2 | `tools/param_names.py` duplicava `domain/params.py` | **resolvido no delta da #28**: o arquivo foi removido (decisão do mantenedor: sem re-export, sem cópia) e o build importa o domínio |
| M3 | Cinco test files históricos fora dos gates de estilo | #34 |
| M4 | Documentação sem site/publicação | EPIC **Site e documentação** (#43): #11 (site da biblioteca) e #60 (site de docs, MkDocs Material) |
| M5 | Sem dependabot para dependências Python (só para Actions) | EPIC **CI, automação e segurança** (#44) — #54 |

### 🟢 Baixo

| # | Achado | Plano |
|---|---|---|
| B1 | Sem `AGENTS.md`/guia único de convenções de IA (substituído por `.agents/README.md`) | EPIC **IA e governança** (#45) |
| B2 | Sem issue de bootstrap para o board v2 | concluído (hub de projeto) |
| B3 | FAQ disperso entre README e docs | EPIC **Site e documentação** (#43) |

## 3. Arquitetura alvo

Resumo em [`ARCHITECTURE.md`](../ARCHITECTURE.md); decisões com contexto, custo e
alternativas em [`docs/decisions/`](decisions/README.md).

```
src/gp100_architect/
├── domain/          regras puras (cadeia, params, modelo, validação, erros)
├── application/     casos de uso (validação, setlist, consulta, build, release)
├── infrastructure/  defs JSON, formato .prst, empacotamento
└── interfaces/
    └── cli/         Typer + Rich  (a api/ entra na 2.1)
```

Estrutura de diretórios definitiva (o que ainda falta, com o epic responsável):

```
├── src/gp100_architect/{domain,application,infrastructure,interfaces}   #28–#32 · EPIC #41
├── tests/{unit,integration,contract,e2e,fixtures}                       #34 · EPIC #41
├── docs/{decisions,architecture,development,guides,reference,contributing,operations}  EPIC #43
├── .agents/{,skills,types}                                             mantido (ADR-0008)
├── tools/                                                              esvaziado por #33 · EPIC #41
├── patches/ · impulse_responses/ · reference/                           conteúdo (inalterado)
├── .github/{workflows,ISSUE_TEMPLATE,scripts}                           EPIC #44
└── pyproject.toml · uv.lock · ARCHITECTURE.md · DEVELOPMENT.md · README.md …
```

## 4. Plano de migração (sem big bang)

Regra que torna a migração segura: **nenhum passo deixa a suíte vermelha**.

| Passo | O que muda | Como o legado continua funcionando |
|---|---|---|
| 1 | Pacote + uv + gates (PKG-001/002) | `tools/` roda com stdlib pura; `python tools/x.py` não exige instalação |
| 2 | Domínio no pacote (#28) | shims em `tools/` reexportam (`chain.py`, `defs_schema.py`) e inserem `src/` no `sys.path` |
| 3 | Infraestrutura do `.prst` (#29) | `generate_prst.py`/`analyze_prst.py` viram wrappers do pacote |
| 4 | Casos de uso + CLI (#30, #32, #48, #49) | cada família de comando migra com teste de contrato |
| 5 | Legado sai (#33) | remoção dos shims e scripts; docs e agentes atualizados no mesmo PR |
| 6 | Suíte nova (#34, fecha #23) | `tests/` históricos migram para `tests/unit|integration|contract|e2e` |

Cada passo entra por PR próprio, com Conventional Commit, gates verdes e merge
na `develop`. A ordem é a das dependências em
[`docs/roadmap-2.0.md`](roadmap-2.0.md).

## 5. Riscos identificados

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Migração alterar byte do `.prst` | baixa | teste de contrato (TestC) roda a cada PR; nenhum passo toca no gerador sem ele |
| `tools/` e pacote divergirem durante a transição | média | shim é a única ponte (`tools/chain.py`, removido no #33); a cópia do `param_names` já saiu |
| Adoção de pytest quebrar os testes históricos | baixa | pytest roda `unittest` nativamente — comprovado: a suíte inteira roda sob pytest (`uv run pytest -q` é a contagem, não uma promessa) |
| Escopo da 2.0 crescer sem controle | média | **um milestone (a release) + epics** com critério de saída (#41–#47) e o DoD em `docs/roadmap-2.0.md`; o que não é 2.0 vai para 2.1 |
| Dependência nova sem justificativa | baixa | ADR obrigatório para dependência de runtime (ADR-0001/0003/0005 registram typer, rich, uv, pytest) |
| Documentação passar a descrever algo inexistente | média | linter de consistência (#58) como portão de release — foi ele que faltava quando este próprio audit citou números de issue errados |
