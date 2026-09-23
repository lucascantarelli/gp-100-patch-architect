# Roadmap 2.0 — fases, issues e critério de pronto

> **Este documento é o plano de execução** (fases, dependências, portões). O
> escopo de produto por versão continua em
> [`reference/19-roadmap-v2.md`](../reference/19-roadmap-v2.md) — pilares e
> ambição. Divergência entre os dois é bug deste arquivo.
>
> **Fonte das issues**: <https://github.com/lucascantarelli/gp-100-patch-architect/issues>
> (milestones `2.0 · F1 … F5` + `2.0 · Release`).

## Fases

| Fase | Milestone (nome exato no GitHub) | Objetivo | Issues |
|---|---|---|---|
| **F1 · Fundação** | `2.0 · F1 — Fundação` | pacote, uv, gates, ADRs, docs de engenharia | #25–#34 (**criadas**; #25, #26, #27 entregues) |
| **F2 · Núcleo e CLI** | `2.0 · F2 — Núcleo e CLI` | domínio, infraestrutura `.prst`, casos de uso, CLI completa, fim do legado, suíte nova | #28–#34 abertas; complementos na abertura da fase |
| **F3 · Automação e CI** | `2.0 · F3 — Automação e CI` | workflows separados, segurança, dependabot, release automation | a criar na abertura da fase |
| **F4 · Documentação** | `2.0 · F4 — Documentação` | site MkDocs, guias por público, FAQ, exemplos | a criar na abertura da fase |
| **F5 · IA e governança** | `2.0 · F5 — IA e governança` | agentes especializados, agente de versionamento, templates, labels, board | a criar na abertura da fase |
| **Release** | `2.0 · Release` | auditoria de consistência, validação final, changelog, tag | a criar no fim de F5 |

As issues são criadas fase a fase **com o contexto da fase anterior já
executado** — issue detalhada sobre código que vai mudar é issue que nasce
errada.

## Dependências

```
F1 (fundação)
 ├── ARCH-001 ADRs + ARCHITECTURE ─┬── PKG-001 pacote/uv ── PKG-002 gates
 │                                │        │
 │                                │        ├── PKG-003 domínio
 │                                │        ├── PKG-004 infraestrutura .prst
 │                                │        ├── PKG-005 application + CLI (consulta)
 │                                │        ├── PKG-006 application + CLI (setlist)
 │                                │        ├── PKG-007 application + CLI (release)
 │                                │        ├── PKG-008 remove legado  ← só depois de 003…007
 │                                │        └── PKG-009 suíte em pirâmide (#23)
 └── governança (labels, milestones, templates) ── F5
```

Regra de sequência: **nada de F2 antes de F1 fechada** (o pacote precisa dos
gates para não regredir) e **PKG-008 é o último** (o legado só sai quando todo
consumidor estiver no pacote).

## Definition of Done da 2.0

| Métrica | Alvo | Onde é verificado |
|---|---|---|
| Suíte | 100% verde, em pytest, com pirâmide declarada | CI (`pytest`) |
| Cobertura do pacote | ≥ 90% (hoje 91%) | CI (`fail_under`) |
| Lint e formatação | zero violação em **todo** o Python do repositório (inclusive `tools/`, que sai das exclusões) | CI (`ruff`) |
| Tipos | `mypy --strict` no pacote; legado fora | CI (`mypy`) |
| Agentes | `tsc --noEmit` limpo | CI (`typecheck`) |
| Sincronia do pipeline | TestH verde (nenhum derivado defasado) | CI |
| CI | tempo total ≤ 6 min, com cache de uv | medido no job |
| Segurança | 0 alerta crítico (CodeQL + dependency review + auditor de workflows) | `security.yml` |
| Documentação | nenhum doc descrevendo arquitetura inexistente; link quebrado reprova | auditoria de consistência (fase final) + revisão |
| Releases | changelog gerado dos commits, versão de fonte única, tag assinada | ADR-0010 |
| Onboarding | `git clone && uv sync && uv run pytest` verde em máquina limpa | README/DEVELOPMENT |
| Legado | `tools/` contém apenas conteúdo/scripts de conteúdo — nenhum código de produto | PKG-008 |

## Fronteira de escopo

**Entra na 2.0**: pacote, uv, camadas, CLI completa, testes em pirâmide, gates,
CI/CD por responsabilidade, segurança, ADRs, documentação de engenharia,
governança (labels/milestones/templates), agentes especializados, fim do legado.

**Fica para 2.1**: API FastAPI, UI, autenticação, TUI (Textual) se houver uso.

**Fica para 3.0**: schema v2 do defs (#8) e a aposentadoria dos seeders, site
público de patches, empacotamento para PyPI.

**Fora de escopo, explicitamente**: aplicar patches na pedaleira por USB/serial
(o formato é gerado, não enviado), app mobile, suporte a firmware V1.8.

## Ritual de release (ADR-0010)

```
suíte verde → build regenerado (idempotente) → changelog → VERSION
  → commit de release → tag → PR develop → main → artefatos anexados
```

Publicação é decisão humana: agente propõe o bump e o changelog, mantenedor
aprova. A dívida atual — `main` em 1.0.0 com v1.1.0 e v1.2.0 entregues — é
justamente o que a 1.2.0 cortada antes da 2.0 resolve.
