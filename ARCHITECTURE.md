# Arquitetura

> **Este documento é um resumo.** Cada decisão tem um ADR com contexto, custo e
> alternativas descartadas em [`docs/decisions/`](docs/decisions/README.md) — o
> ADR é a fonte; divergência entre os dois é bug deste arquivo.

## O que é o sistema

Uma biblioteca de **conteúdo** para a pedaleira Valeton GP-100, com um pipeline
reprodutível:

```
tools/patches-defs.json        ← FONTE ÚNICA (música, cadeia, params, doc)
        │
        ├─→ patches/**/*.prst   arquivo que a pedaleira lê (byte a byte)
        └─→ patches/**/patch.md doc prática-primeiro + MAPA-DO-ALBUM.md
```

Duas garantias sustentam tudo: **o defs é a fonte única** (arquivo gerado nunca
é editado à mão) e **o pipeline é reprodutível** (rodá-lo do zero reproduz
exatamente o que está commitado — é isso que o guarda de sincronia, TestH,
verifica a cada PR).

## Camadas (ADR-0002)

```
interfaces/      CLI (Typer + Rich) — e a API na 2.1 (ADR-0004)
      │          nenhuma regra aqui: traduz caso de uso em texto/exit code
application/     casos de uso que orquestram domínio e infraestrutura
      │
domain/          regras puras: cadeia, catálogo de params, modelo, validação
      ▲
infrastructure/  defs JSON, formato .prst, empacotamento de release
```

Regra de dependência em uma direção: `infrastructure` e `application` importam
`domain`; `domain` não importa ninguém. Importar o pacote **não toca o disco** —
o defs é carregado explicitamente, sempre validado
(`infrastructure.defs.carregar_e_validar`).

```python
from gp100_architect.domain.chain import CHAIN
from gp100_architect.infrastructure.defs import carregar_e_validar
```

## Estrutura de diretórios

| Caminho | O que é |
|---|---|
| `src/gp100_architect/` | o pacote (domain/application/infrastructure/interfaces) |
| `tools/` | scripts do pipeline — **em migração** para o pacote (PKG-003…008) |
| `patches/` | produto: `.prst` + `patch.md` por patch (gerado) |
| `tests/` | suíte (histórica em `tests/`, nova em `tests/unit/`) |
| `reference/` | 24 documentos de **domínio** (timbre, catálogo, dossiês, histórico) |
| `docs/` | documentação de **engenharia** (ADRs e, na F4, guias) |
| `.agents/` | 19 agentes + 11 skills do Freebuff — contrato, não se move (ADR-0008) |
| `.github/` | workflows, templates, labels, automação do board |

## Ferramentas e portões (ADR-0005, ADR-0006)

| Portão | Comando | Onde |
|---|---|---|
| lint + formatação | `uv run ruff check .` · `uv run ruff format --check .` | pre-commit + CI |
| tipos | `uv run mypy` (strict, no pacote) | pre-commit + CI |
| testes + cobertura | `uv run pytest -q --cov` (piso 90% no pacote) | CI |
| agentes | `npx -p typescript@5.9.2 tsc --noEmit` | CI |
| sincronia do pipeline | TestH (dentro do pytest) | CI |
| hardening de workflow | `python .github/scripts/audit_workflows.py` | CI (security) |

Runtime: **Python 3.14 apenas** (ADR-0001). Ambiente e comandos: **uv**.

## Evolução

- **2.0** — fundação (ADR-0001…0012), migração dos scripts para o pacote, CLI
  completa, suíte em pirâmide, docs de engenharia **e as quebras de formato**
  (schema v2 do defs, stomps/EXP1, `-USERIR`): é a release que aposenta os
  seeders e formaliza o formato.
- **2.1** — API FastAPI + UI, sobre os mesmos casos de uso (ADR-0004).

O escopo por versão está em [`reference/19-roadmap-v2.md`](reference/19-roadmap-v2.md),
a execução em [`docs/roadmap-2.0.md`](docs/roadmap-2.0.md) e a estrutura de
issues (epic × task, ADR-0012) nos [epics do GitHub](https://github.com/lucascantarelli/gp-100-patch-architect/labels/epic).
