# Desenvolvimento

Guia de quem vai **mexer no código**. Se o seu objetivo é usar a biblioteca na
pedaleira, comece pelo [README](README.md); se quer entender as decisões,
[ARCHITECTURE.md](ARCHITECTURE.md) e [`docs/decisions/`](docs/decisions/README.md).

## Setup (2 minutos)

```bash
git clone https://github.com/lucascantarelli/gp-100-patch-architect.git
cd gp-100-patch-architect
uv sync                 # cria .venv e instala o lockfile inteiro
uv run pytest -q        # suíte completa (inclui o guarda de sincronia)
```

Requisitos: **Python 3.14** (política do projeto — o CI trava nisso) e
[uv](https://docs.astral.sh/uv/) (`pip install uv` ou o instalador oficial).

Não é preciso instalar nada além disso: `uv sync` traz as dependências de
desenvolvimento e instala o pacote em modo editável — `uv run gp100 --version`
funciona logo depois do clone.

## Comandos do dia a dia

```bash
uv run gp100 validate              # valida o defs (data/defs/, fonte única)
uv run gp100 build                 # regenera a biblioteca (IRs → patches → índices)
uv run gp100 site                  # gera o site estático em dist/site (issue #11)
uv run pytest -q                   # suíte completa
uv run pytest tests/unit -q        # só os testes do pacote (milissegundos)
uv run pytest -q -m unit           # fatia por marcador da pirâmide
uv run pytest -q --cov --cov-report=term-missing   # cobertura do pacote

uv run ruff check .                # lint
uv run ruff format --check .       # formatação (use sem --check para aplicar)
uv run mypy                        # tipos (strict, no pacote)

uv run pre-commit install          # hooks locais (uma vez por clone)
uv run pre-commit run --all-files  # roda os hooks em tudo
```

O pipeline de dados (patches → `.prst` → docs) roda pelo pacote
(`gp100 build`, in-process desde a #33) — e o guarda de sincronia reprova se
você editar o defs e esquecer de regenerar.

## Onde mexer

| Vou fazer… | Onde |
|---|---|
| regra de validação, cadeia, catálogo de params | `src/gp100_architect/domain/` |
| ler/escrever arquivo, defs, `.prst`, zip | `src/gp100_architect/infrastructure/` |
| caso de uso (montar setlist, exportar, publicar) | `src/gp100_architect/application/` |
| comando de terminal, help, saída | `src/gp100_architect/interfaces/cli/` |
| dado versionado do pipeline | `data/` (defs, catálogo, manifesto de IRs) |
| conteúdo de domínio (timbre, IR, álbum) | `reference/` |
| decidir arquitetura | `docs/decisions/` — ADR novo **com** o PR |

## Regras que o CI cobra

1. **`tests/` não escreve no repositório.** Use `tmp_path`; para apontar o defs,
   use a variável `GP100_DEFS`.
2. **Teste novo nasce em `tests/unit/`** (pytest), com o marcador da pirâmide
   (`@pytest.mark.unit`…). Os testes históricos migram em #23.
3. **Domínio não importa I/O.** Se a regra precisa de arquivo, ela pertence à
   infraestrutura e o caso de uso orquestra.
4. **A CLI não contém regra** — ela chama caso de uso e traduz o resultado
   (código de saída: `0` ok, `1` entrada inválida, `2` erro de uso).
5. **Conventional Commits** — o changelog e o bump de versão saem daí (ADR-0010).
6. **Formato de `.prst` é contrato byte a byte** (CRLF inclusive): nada de hook
   de higiene em `patches/**`, e o TestH confere.

## Fluxo de contribuição

```
branch a partir de develop  →  commits convencionais  →  PR para develop
   →  CI verde (testes, qualidade, agentes)  →  review  →  merge
   →  release (develop → main)  quando o milestone fecha (ADR-0010)
```

Detalhes de branch, review e release: [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Problemas comuns

| Sintoma | Causa provável | Saída |
|---|---|---|
| `python: command not found` ou versão ≠ 3.14 | runtime fora da política | instale 3.14; o CI e os scripts recusam outra versão de propósito |
| `uv: command not found` | uv não instalado | `pip install uv` |
| TestH acusa derivado defasado | editou o defs e não regenerou | o teste imprime o comando exato de conserto |
| `mypy` reclama em outro lugar | o gate cobre só o pacote | rode `uv run mypy` (sem argumento) — ele usa a config |
| Suíte completa lenta (~1 min) | TestH roda o pipeline numa cópia | use `uv run pytest tests/unit -q` enquanto itera |
