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
| [#41](../../issues/41) | **Núcleo, CLI e fim do legado** | o produto sai de `tools/` para `src/gp100_architect` | #25–#30 (entregues), ~~#31~~ (obsoleta: seeders aposentados na #8), #32–#34, #48, #49 (entregues, PR #94) |
| [#42](../../issues/42) | **Formato e dados** | as quebras que justificam o MAJOR: schema v2, stomps/EXP1, `-USERIR` | #8 (→ #50–#53), #9, #10 |
| [#43](../../issues/43) | **Site e documentação** | biblioteca navegável + doc por público | #11, #60, #61 + **#90 fase 1** (JSON do catálogo, com o site) |
| [#44](../../issues/44) | **CI, automação e segurança** | o que vigia o repositório | #37 (entregue), #54, #55, #62 |
| [#45](../../issues/45) | **IA e governança** | agentes com contrato e board como fonte de verdade | #39 (entregue), #56, #57, #63, **#91** (agentes consomem a CLI) |
| [#46](../../issues/46) | **Conteúdo (pilar D)** | primeiro álbum novo e a meta de escala | #12 |
| [#47](../../issues/47) | **Release 2.0.0** | auditoria de consistência e publicação | #58, #64, #59 |

> **Cada linha desta tabela é a mesma coisa que a barra de progresso do epic no
> GitHub**: a tabela é o resumo legível, o epic é o dado. Divergência é bug —
> quem edita um confere o outro (§ 5 do `reference/18`).

## 3 · Ordem de execução

```
#41 Núcleo, CLI e fim do legado          ← começa aqui: é o que destrava o resto
  #28 domínio ──┬── #29 codec .prst ── #30 aplicação ──┬── #48, #49 ✅ (CLI, PR #94)
                ├── #32 release ✅ ────────────────────┘
                ├── #34 suíte em pirâmide
                └── #91 agentes consomem a CLI
                                   #33 limpa tools/ (o último de todos)

#42 Formato e dados    ← depois do #30: o gerador precisa estar no pacote, senão
                          a mudança de formato é feita duas vezes
#43 Site               ← depois do #30 (consome dado gerado)
#44 CI e segurança     ← independente (roda em paralelo)
#45 IA e governança    ← independente
#46 Conteúdo           ← independente (conteúdo não bloqueia engenharia)
#47 Release 2.0.0      ← último: auditoria e publicação
```

Regra de sequência: **#33 é o último** (o legado só sai quando todo consumidor
estiver no pacote) e **#42 só começa depois do #30** — as duas decisões existem
para não fazer o mesmo trabalho em dois lugares.

O diagrama acima não é a única cópia da ordem: **cada seta está declarada no
GitHub** como relação `blocked by`, visível no card e no board. Quem abre a
issue vê do que ela depende sem consultar este arquivo.

```
#29 #32 ✅ #34   ← #28         #11 #60 #61 ← #30
#30 ✅           ← #29         #8  #9 #10  ← #30 ✅
#48 #49 ✅       ← #30, #32    #59 ← #64
#91              ← #48, #49    #90 (fase 1) ← #11
#33              ← #29, #32, #34, #91   (o último de todos)
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
| Cobertura do pacote | ≥ 90% (gate do `pyproject.toml`; 91% hoje) | CI (`fail_under`) |
| Lint e formatação | zero violação em **todo** o Python do repositório — as exclusões atuais (`tools/`, `.github/scripts`, testes históricos) saem junto com cada migração | CI (`ruff`) |
| Tipos | `mypy --strict` no pacote | CI (`mypy`) |
| Agentes | `tsc --noEmit` limpo | CI (`typecheck`) |
| Sincronia do pipeline | guarda verde (nenhum derivado defasado) | CI |
| CI | tempo total ≤ 6 min, com cache de uv | medido no job |
| Segurança | 0 alerta aberto (CodeQL + dependency review + auditor de workflows) | `security.yml` |
| Documentação | nenhum doc descrevendo arquitetura inexistente; issue/caminho/link/milestone citados existem | **linter de consistência (#58)** + revisão |
| Releases | changelog gerado dos commits, versão de fonte única, tag | ADR-0010 |
| Onboarding | `git clone && uv sync && uv run pytest` verde em máquina limpa | README/DEVELOPMENT |
| Legado | `tools/` contém apenas conteúdo — nenhum código de produto | #33 |

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
