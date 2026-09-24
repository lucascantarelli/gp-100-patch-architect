# Roadmap 2.0 — epics, ordem de execução e critério de pronto

> **Este documento é o plano de execução.** O escopo de produto vive em
> [`reference/19-roadmap-v2.md`](../reference/19-roadmap-v2.md) — pilares e
> ambição. Divergência entre os dois é bug deste arquivo.
>
> **Tudo o que está aqui entra na release 2.0.0 — uma só.** A execução se organiza
> em **epics** (issues pai, label `epic`) com **sub-issues** (tasks); o milestone
> é a **release**, não a fase.

## 1 · Como o board se organiza

| Camada | O que é | Onde vive |
|---|---|---|
| **Release** | o que sai publicado junto | milestone `v2.0.0 — Formato, site e escala` |
| **Stream (epic)** | frente com objetivo, escopo e critério de saída próprios | issue pai com a label `epic` |
| **Task** | entrega de **um** PR | sub-issue do epic |
| **Triagem** | `status: needs-triage` · `blocked` · `ready-for-pr` · `in-review` | label (o quadro visual é o campo `Kanban` do Project) |

As três visões do Project #7 — **Kanban** (Board), **Sprint** (Tabela, filtro
`Sprint:*`) e **Roadmap** (Roadmap) — nascem do bootstrap por GraphQL
(`createProjectV2View`); só agrupamento/ordenação é manual, pois a API não
expõe `groupBy` (premissa vencida registrada em `reference/18` § 3.3 e
ADR-0012).

Duas regras que mantêm isso coerente:

1. **Issue nova nasce como sub-issue de um epic.** Se não tem epic, ou o epic
   está errado ou a issue não deveria existir.
2. **Task nasce quando a stream vai começar**, não antes: issue detalhada sobre
   código que ainda vai mudar nasce errada (foi o que aconteceu com metade da
   primeira leva — ver § 5).

## 2 · Streams (epics)

| EPIC | Stream | Objetivo | Tasks |
|---|---|---|---|
| [#41](../../issues/41) | **Núcleo, CLI e fim do legado** ✅ **encerrado** | o produto sai de `tools/` para `src/gp100_architect` — feito (dados em `data/`, pipeline in-process, CLI `gp100`) | #25–#34, #48, #49 (entregues: PRs #35, #81, #86, #93–#96), ~~#31~~ (obsoleta: seeders aposentados na #8) |
| [#42](../../issues/42) | **Formato e dados** ✅ **encerrado** | as quebras que justificam o MAJOR: schema v2, stomps/EXP1, `-USERIR` | #8 (com #50–#53; PRs #87, #89), #9, #10 — todas entregues |
| [#43](../../issues/43) | **Site e documentação** | biblioteca navegável + doc por público | #11, #60, #61 + **#90 fase 1** (JSON do catálogo, com o site) |
| [#44](../../issues/44) | **CI, automação e segurança** | o que vigia o repositório | #37 (entregue), #54, #55, #62 |
| [#45](../../issues/45) | **IA e governança** | agentes com contrato e board como fonte de verdade | #39 (entregue), **#91** ✅ (PR #97), #56, #57, #63 |
| [#46](../../issues/46) | **Conteúdo (pilar D)** | primeiro álbum novo e a meta de escala | #12 |
| [#47](../../issues/47) | **Release 2.0.0** | auditoria de consistência e publicação | #58, #64, #59 |

> **Cada linha desta tabela é a mesma coisa que a barra de progresso do epic no
> GitHub**: a tabela é o resumo legível, o epic é o dado. Divergência é bug —
> quem edita um confere o outro (§ 5 do `reference/18`).

## 3 · Ordem de execução

```
#41 Núcleo, CLI e fim do legado ✅ ENCERRADO (PRs #35, #81, #86, #93–#96)
  #28 domínio ──┬── #29 codec .prst ── #30 aplicação ──┬── #48, #49 ✅ (CLI, PR #94)
                ├── #32 release ✅ (PR #93) ───────────┘
                ├── #34 suíte em pirâmide ✅ (PR #95)
                └── #33 fim do legado ✅ (PR #96, o último de todos)

#42 Formato e dados ✅ ENCERRADO (PRs #87 e #89 — schema v2, stomps, -USERIR)
#43 Site               ← CAMINHO CRÍTICO: #11 (gerador no pacote) → #90 fase 1
#44 CI e segurança     ← independente (roda em paralelo): #54, #55, #62
#45 IA e governança    ← independente: #91 ✅ (PR #97), #56, #57, #63
#46 Conteúdo           ← independente (conteúdo não bloqueia engenharia): #12
#47 Release 2.0.0      ← último: #58 (linter), #64 (auditoria DoD) → #59 (publicar)
```

Regra de sequência que regia as streams fechadas: **#33 era o último** (o legado
só saiu quando todo consumidor estava no pacote) e **#42 só começou depois do
#30** — as duas decisões evitaram fazer o mesmo trabalho em dois lugares. Com
#41 e #42 encerrados, o caminho crítico restante é o **site (#11 → #90 fase 1)**
e #59 (publicar a 2.0.0) fica atrás da auditoria de DoD (#64).

A ordem também vive no GitHub: as dependências de execução são registradas por
**labels** (`status: blocked` ↔ `status: ready-for-pr`) e sub-issue — a API do
GitHub não expõe mutação para `blocked-by` (auditoria do grafo, 24/09/2026),
então este diagrama e a tabela §3 de cada epic são a fonte documentada do grafo.

```
#29 ✅ #32 ✅ #34 ✅ ← #28      #11 #60 #61 ← #30 ✅
#30 ✅              ← #29       #8 ✅ #9 ✅ #10 ✅ ← #30 ✅
#48 #49 ✅          ← #30, #32  #59 ← #64
#91 ✅ (PR #97)      ← #48, #49  #90 (fase 1) ← #11
#33 ✅              ← #29, #32, #34, #91   (o último de todos)
```

## 4 · Fronteira de escopo

**Entra na 2.0.0**: os sete streams acima — pacote, CLI, fim do legado, formato e
dados, site, documentação, CI/segurança, IA/governança, conteúdo e a publicação.

**Fica para 2.1**: API FastAPI, UI, autenticação, TUI (Textual) se houver uso.

**Não existe 3.0.** O escopo de produto que em algum momento foi escrito como
"3.0" (schema v2, site público, escala) é **2.0** — é o que
o [`reference/19-roadmap-v2.md`](../reference/19-roadmap-v2.md) §9 sempre disse,
e o que dá ao MAJOR a razão de existir. Menção a 3.0 no repositório é resíduo.

**Fora de escopo, explicitamente**: aplicar patches na pedaleira por USB/serial
(o formato é gerado, não enviado), app mobile, suporte a firmware V1.8.

## 5 · Definition of Done da 2.0

| Métrica | Alvo | Onde é verificado |
|---|---|---|
| Suíte | 100% verde, em pytest, com pirâmide declarada | CI (`pytest`) |
| Cobertura do pacote | ≥ 90% (gate do `pyproject.toml`; 90,81% hoje) | CI (`fail_under`) |
| Lint e formatação | zero violação em **todo** o Python do repositório — `src/` e a suíte inteira já estão nos gates; `.github/scripts` e skills de terceiros ficam fora (superfície shell/conteúdo externo) | CI (`ruff`) |
| Tipos | `mypy --strict` no pacote | CI (`mypy`) |
| Agentes | `tsc --noEmit` limpo | CI (`typecheck`) |
| Sincronia do pipeline | guarda verde (nenhum derivado defasado) | CI |
| CI | tempo total ≤ 6 min, com cache de uv | medido no job |
| Segurança | 0 alerta aberto (CodeQL + dependency review + auditor de workflows) | `security.yml` |
| Documentação | nenhum doc descrevendo arquitetura inexistente; issue/caminho/link/milestone citados existem | **linter de consistência (#58)** + revisão |
| Releases | changelog gerado dos commits, versão de fonte única, tag | ADR-0010 |
| Onboarding | `git clone && uv sync && uv run pytest` verde em máquina limpa | README/DEVELOPMENT |
| Legado | `tools/` extinta — dados em `data/`, pipeline no pacote (`gp100 build`) | #33 ✅ |

## 6 · Ritual de release (ADR-0010)

```
suíte verde → build regenerado (idempotente) → changelog → VERSION
  → commit de release → tag → PR develop → main → artefatos anexados
```

Publicação é decisão humana: o agente propõe o bump e o changelog, o mantenedor
aprova.

**A 2.0.0 é a próxima release.** `VERSION` está em `1.0.0` na `develop` e na
`main`, e a única tag publicada é a `v1.0.0`: os milestones `v1.1.0` e `v1.2.0`
foram **entregues e não publicados**, e o conteúdo deles entra na 2.0.0. A regra
que nasce deste caso: **milestone de release só fecha com a tag publicada** — sem
ela, o trabalho da fase seguinte entra no corte da anterior.

## 7 · Issues

Fonte: <https://github.com/lucascantarelli/gp-100-patch-architect/issues> — os
epics (#41–#47) são o índice vivo. Não repetir contagem de issues aqui: número
memorizado envelhece (é o achado A8 da auditoria).
