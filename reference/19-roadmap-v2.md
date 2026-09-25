# 🗺 Roadmap v2.0 — formato, ferramentas, site e conteúdo

> Documento 19 — consolida o brainstorm da versão 2.0. Define **o que justifica o
> bump MAJOR**, o que entra antes (1.x) e a sequência de releases. Complementa o
> [`18-project-management`](18-project-management.md) (que cobre o *como* de
> gestão) e o [`12-workflow`](12-workflow.md) (que cobre a criação de patches).

## 1 · Onde estamos (baseline de set/2026)

| Dimensão | Estado |
|---|---|
| Biblioteca | **103 patches / 61 músicas / 7 álbuns** — derivado, não memorizado: `gp100 validate` (fragmentos em `data/defs/`, schema v2 — o detalhe por álbum está no [README](../README.md)) |
| Pipeline | Reprodutível e guardado pela suíte — **321 testes** em pirâmide pytest (`uv run pytest`): unit → integration → contract → e2e, com markers e auditoria de escrita no repo (`--guarda-repo`; issue #34), `TestH` de determinismo (derivados fora do git, ADR-0013) · CLI única do pacote `gp100` (`--json`; pipeline in-process desde a #33) |
| Em voo | **nada**: `main` + `develop`, zero branch de trabalho — próximo do caminho crítico: **#90 fase 1** (JSON do catálogo) · Pages pendente de ativação (Settings → Source: GitHub Actions) |
| Concluído | **Smooth (Santana)** (#5) e **Wishkah (Nirvana)** (17 músicas / 31 patches, #6) · **epic #41 encerrado** (pacote, CLI, pirâmide pytest, `tools/` extinta — PRs #35, #81, #86, #93–#96) e **epic #42 concluído** (schema v2, stomps, `-USERIR`) — `1.1.0`/`1.2.0` entregues e não publicadas (entram na 2.0.0) |
| Gestão | Taxonomia, milestones, **epics com sub-issues** (ADR-0012) e guardian vivos no GitHub (doc 18) — board com escopo `project` ativo, automação end-to-end (ADR-0011) |
| Formato | **Schema v2** (fragmentos por álbum em `data/defs/`); `doc.stomps` + `spec.exp1` formais (#9); variante `-USERIR` gerável com `--with-user-ir` (#10) — **epic #42 concluído** |

> **Zero número escrito à mão neste arquivo sem o comando que o deriva** — foi o
> que apodreceu a versão anterior (66 patches, 43 testes, "Wishkah em voo").
> Caminho do produto e da execução: [`docs/roadmap-2.0.md`](../docs/roadmap-2.0.md).

## 2 · Filosofia do major

O **2.0 é um salto de propósito** (os milestones da doc 18 tratam 1.x como
degraus). Um bump MAJOR exige *breaking changes* — e as escolhas abaixo são as
que pagam esse preço com ganho real:

1. **Schema v2 do `patches-defs.json`** — quebra o formato do arquivo de dados, mas só para quem edita o defs diretamente (a saída `patches/**` continua idêntica).
2. **Stomps e EXP como cidadãos de primeira classe** — formaliza o que o Smooth já faz ad-hoc.
3. **CLI unificada** — nova superfície de comando; nada existente é quebrado, mas ela passa a ser o caminho recomendado.

Tudo o mais (site, álbuns novos, skills novas, CI) é **aditivo** e entra nos 1.x
sem dor.

## 3 · Pilar A — Formato e pipeline (o coração do major)

### A1. Schema v2: defs dividido por álbum

**Problema hoje:** um único JSON com 41 músicas (≈100 patches no horizonte do
2.0) torna o diff de PR gigante e o review cego.

**Proposta:**

```
data/
  defs/
    _albums.json        ← albums + meta (o que é hoje albums/meta)
    abbey-road.json     ← só as músicas do álbum (AR)
    pulse.json          ← PL
    cheap-thrills.json  ← PMH
    apostrophe.json     ← ZP
    supernatural.json   ← SN
```

- **Loader único**: `infrastructure.defs` concatena os fragmentos na ordem
  declarada em `_albums.json` — a ordem dos slots U01…Uxx continua
  determinística (regra de estável entre SOs, `TestI_OrdemEstavel`, se aplica).
- **Fonte única preservada**: nenhum script passa a manter tabela própria; o
  que muda é só a *granularidade física* do defs.
- **Guarda de sincronia**: o `TestH` passa a comparar o resultado do pipeline
  sobre os fragmentos com o commitado — a mesma garantia, novo formato.
- **Migração**: script one-shot (`tools/migrate_defs_v2.py` na época) escreveu os
  fragmentos a partir do monolito; o monolito sai do repo no mesmo PR (ou fica
  como alias de leitura por um ciclo, se decidirmos suavizar).

**Breaking:** qualquer ferramenta externa que leia `patches-defs.json` direto.

### A2. Stomps e pedal de expressão formais no schema

**Problema hoje:** o Smooth usa stomps (`ppCtrl`) de forma ad-hoc dentro do
`spec`; a seção "Modos de atuação" descreve toggles, mas FS-A/FS-B não têm
campo declarativo; `<ppEXP1>` existe no formato e nunca foi usado.

**Proposta:**

- `doc.stomps`: `[{"fs": "A", "modulo": "DST", "acao": "on", "momento": "refrão"}, …]`
  — validado contra o spec (o módulo existe, o estado inicial é inverso, AMP/CAB
  nunca) e renderizado na doc como tabela própria.
- `spec.exp1`: `{ "modulo": "DLY", "param": "Time", "min": 0, "max": 100 }`
  — o gerador emite `<ppEXP1>` e a doc ganha seção "🎚 Pedal de expressão".
- Testes novos no espírito do `TestE_Momentos`: stomps válidos, EXP1 dentro do
  range do parâmetro, nunca EXP em AMP/CAB.

**Breaking:** patches antigos sem `doc.stomps` ganham a seção vazia (ou o
validador passa a *exigir* o campo — decidir na issue).

### A3. Validação de dados com mensagem acionável

Hoje um erro de edição no defs estoura como `KeyError` no meio do build.
Proposta: um validador (stdlib pura) que valida o defs **antes** de
qualquer script tocar nele — campos obrigatórios, tipos, ranges de nome
(`≤ 12 chars`), unicidade de ids, referências cruzadas (`ir_local` ↔ CAB usado).
Mensagem aponta o caminho JSON exato e o que fazer.

### A4. Variante `-USERIR` gerável

Hoje `ir_cab_user_slot` é experimental e só com teste no device. Proposta:
flag de build (`--with-user-ir`) que gera a variante ao lado do `.prst` canônico,
marcada como experimental na doc — quem valida no device empacota a variante
com confiança de que o canônico não mudou.

## 4 · Pilar B — CLI unificada

**`gp100`** — entry point do pacote (`src/gp100_architect/interfaces/cli`); a
CLI única do projeto desde a #33 (o pipeline roda in-process, sem scripts):

| Comando | O que faz |
|---|---|
| `gp100 find <termo>` | Busca por música/artista/álbum/captador → caminho, slot, IR recomendada |
| `gp100 show <NOME>` | Resumo do patch: cadeia em 1 linha, ajustes finos, momentos, stomps — `--json` para agentes |
| `gp100 diff <A> <B>` | Diff **legível** de spec (módulo a módulo, nome de parâmetro oficial) |
| `gp100 export [--album X] [--destino D] [--listar]` | Copia a seleção de `.prst` para a pasta de importação USB, na ordem dos slots |
| `gp100 build [--with-user-ir]` | Encadeia o pipeline inteiro (o mesmo comando do guarda de sincronia) |
| `gp100 verify` | Suíte + guarda, resumo curto |
| `gp100 setlist <música…>` | Cola de palco: ordena por vizinho mais próximo, trocas ao entrar — `--json` para agentes |
| `gp100 release` | Empacota a release (delega a `application/release`) |

Zero dependências (stdlib), padrão dos scripts existentes (stdout UTF-8,
ordenação estável). Reaproveita `patches-defs` + catálogos; nada de rede.

## 5 · Pilar C — Site estático da biblioteca

Um gerador (`gp100 site`, epics #43) → GitHub Pages, dos mesmos dados do índice:

- **Página por álbum** e **página por patch**: cadeia, tabela de parâmetros
  (nomes oficiais), ajustes finos, seção 📡 de IR, momentos/stomps, badges.
- **Busca client-side** (índice JSON minúsculo: música, artista, álbum,
  captador, camada) — sem backend, sem dependência.
- Regra herdada do projeto: **o site é saída de script** (o guarda de sincronia
  passa a cobrir `site/**` se ele for versionado; alternativa: gerar no workflow
  de release e publicar via Pages sem commitar — decidir na issue).
- **API do catálogo** (issue #90): os mesmos dados ganham `/catalog/*.json` —
  JSON estático na 2.0 (fase 1, nasce com o site) e servidor read-only no 2.x
  (fase 2). Contrato dos shapes é o insumo dos agentes e do site.

## 6 · Pilar D — Conteúdo: rumo aos 100+ patches

Candidatos alinhados ao instrumento fixo do projeto (Strat single coil, 250k)
e ao catálogo fw 2.0/2.1 — três escolas de Strat inteiras e dois gênios de
distorção:

| Álbum candidato | Por quê | Desafio conhecido |
|---|---|---|
| **Stevie Ray Vaughan — Texas Flood** | A escola Strat de bridge + drive; comp/amp/DST do catálogo cobre bem | Strings heavy + dinâmica: doc de técnica pesada |
| **Jimi Hendrix — Are You Experienced** | Fuzz + uni-vibe: o `Red Haze` (fuzz) e `Vibe` (MOD) existem no catálogo | Fuzz é sensível a captador; seções de técnica críticas |
| **John Mayer — Continuum** | Strat neck + cleans com DLY/RVB; usa bem o banco de IRs local | Fender-style fino no catálogo: escolher amp/IR com cuidado |
| **Rage Against the Machine — RATM** | Hi-gain sem amp exótico; NR obrigatório (regra do ganho ≥ 55) | Morello usa efeitos exóticos (kill switch) — vai na técnica |
| **Radiohead — OK Computer** | Amplitude: cleans espaciais a distortions; bom teste de momentos | Ed usa fuzz duplo e capos; camadas por seção |

Meta declarada do 2.0: **≥ 100 patches / ≥ 10 álbuns**, cada álbum via PR com
dossiê do rig real (o fluxo de hoje já cobra isso).

## 7 · Pilar E — Agentes (aditivo, entra em 1.x/2.x)

1. **Skill `gp100-setlist`**: dado um repertório, monta a ordem de slots
   (minimizando trocas de patch entre músicas consecutivas) e imprime a cola de
   palco — **entregue**: cálculo em `application/setlist`
   (vizinho mais próximo sobre a assinatura PRE→RVB; slots de `biblioteca.slots`),
   exposto via `gp100 setlist` (issue #49); agente
   `gp100-setlist` conduz a conversa e roda a CLI.
2. **Skill de A/B pós-criação**: automatiza o "protocolo universal" de ajustes
   (está lamacento? → CAB High Cut −5 …) como entrevista guiada em vez de texto
   fixo na doc — **entregue**: agente `gp100-ab-tester` (fonte única: tabela de
   troubleshooting do doc 12; uma pergunta concreta por vez; mudanças mínimas).
3. **Golden set para tone-research/tone-mapper**: ~20 músicas canônicas com
   cadeia esperada, para avaliar a *qualidade* dos agentes de pesquisa — hoje os
   testes só cobrem o pipeline — **entregue**: `reference/20-golden-set.md`
   (20 músicas / 43 patches extraídos do defs, ponderação por bloco e critério
   de aprovação).

## 8 · Pilar F — Qualidade e CI (aditivo, entra em 1.x)

- ~~Matriz Python 3.10–3.13 no CI~~ **Reorientado (decisão do mantenedor): Python 3.14 APENAS** — travado em código: guarda de runtime na suíte e na CLI do pacote, suíte inteira recusa outro runtime e verificação `3.14.*` como primeiro passo do job `test-suite` no CI.
- Testes para os scripts hoje fora da suíte: `analyze_prst`, `build_release`,
  `gen_changelog` — **entregues** e migrados para o pacote com a pirâmide (issue #34:
  `tests/integration/test_release.py`).
- `dependabot` já vigia Actions; manter.
- **Migração da suíte para pytest** (decisão do mantenedor, set/2026) — **entregue na
  pirâmide (issue #34)**: unit → integration → contract → e2e em
  `tests/{unit,integration,contract,e2e}`, factories em `tests/fixtures/`, markers
  (`unit · integration · contract · e2e · slow`) e auditoria de escrita no repo
  (`--guarda-repo`, ativa no CI). A skill global `python-testing-patterns` vale como
  convenção de teste.

## 9 · Sequência de releases

```
v1.1.0 — Álbuns e fluxo PR-driven
  □ bootstrap da gestão rodado contra o GitHub (labels + milestones ✓; Project #7 criado ✓, pendente o secret `PROJECT_TOKEN` — ADR-0011)
  □ camada de gestão commitada (doc 18, bootstrap, guardian) → PR → merge — issue #4
  □ merge de Smooth (Santana) — 4 patches com stomps — issue #5
  □ merge do Wishkah (Nirvana) — 17 músicas / 31 patches — issue #6
  □ README atualizado (contagens por álbum pós-merges) — issue #7

v1.2.0 — Fundações do 2.0 (tudo aditivo)
  □ CLI gp100.py (find/show/diff/export/build/verify) — issue #13 ✅
  □ defs_schema.py (validação acionável) — issue #14 ✅
  □ skills gp100-setlist + A/B + golden set dos agentes — issue #15 ✅
  □ trava Python 3.14 no CI + testes dos scripts soltos — issue #16 ✅

v2.0.0 — Formato, site e escala (as quebras + a fundação de engenharia)
  □ schema v2: defs por álbum + guarda atualizado — issue #8 ✅ (PR #87)
  □ stomps/EXP1 formais no schema, com validação e seções novas na doc — issue #9 ✅ (PR #89)
  □ variante -USERIR gerável — issue #10 ✅
  □ gerador do site (Pilar C) + GitHub Pages (busca + página por patch) — issue #11 ✅ (PR #99; `gp100 site` + workflow; Pages pendente de ativação)
  □ ≥ 100 patches / ≥ 10 álbuns (1º álbum: ✅ **Hendrix — Are You Experienced**, PR da #12 — 103 patches/7 álbuns; seguem SRV e Mayer) — issue #12
  □ o programa de engenharia que a 2.0 exige (pacote, CLI, docs, CI) — epics #41–#47 — **#41 e #42 encerrados**
```

> **Este quadro é escopo de produto, não plano de execução.** A divisão em tasks,
> a ordem e as dependências vivem nos **epics** (#41–#47) e no
> [`docs/roadmap-2.0.md`](../docs/roadmap-2.0.md) § 2–3 — repetir a lista aqui foi
> o que deixou cinco números vencidos na versão anterior (achado A8).

**Estado das releases (23/09/2026).** A `v1.1.0` e a `v1.2.0` foram **entregues
na `develop` e não publicadas**: o `VERSION` e a única tag do repositório são
`1.0.0`. O conteúdo das duas entra na **2.0.0**, que é a próxima release — e a
regra que nasce daí é: *milestone de release só fecha com a tag publicada*.

**Caminho crítico restante (24/09/2026).** Epics **#41** (núcleo/CLI/fim do
legado) e **#42** (formato) **encerrados**; **#91 fechada** (PR #97); **site
entregue** — #11 (PR #99), com o Pages pendente de ativação. Depois: **#90**
(fase 1, JSON do catálogo), conteúdo **#12**, auditoria de DoD **#64** →
publicar **#59**.

Regras herdadas valem para tudo acima: nenhum job escreve no git; patches/** é
saída de script; o PR referencia a issue com `Closes #N` (no fluxo para a
`develop`, quem fecha é o mantenedor no merge); suíte verde antes do merge
(doc 18).

## 10 · Itens para decidir nas issues (não aqui)

- ~~Pilar A1: manter `patches-defs.json` como alias de leitura por um ciclo ou removê-lo no mesmo PR?~~ → **resolvido no PR #87 (issue #8)**: fragmentos por álbum + loader único, sem alias; o monólito saiu do repositório
- ~~Pilar A2: `doc.stomps` vazio é válido ou o validador passa a exigir o campo?~~ → **resolvido no PR #89 (issue #9)**: campo opcional — patch mono-comportamento simplesmente omite `doc.stomps`
- ~~Pilar C: site versionado (com guarda de sincronia) ou gerado no release e publicado sem commitar?~~ → **resolvido na #11 (PR do site)**: gerado no deploy (`gp100 site` deriva tudo do `data/defs/` no workflow `pages.yml`) e publicado no Pages **sem commitar** — nada de derivado no git, o guarda de sincronia do TestH não precisa cobrir mais nada. Um push na `develop` = redeploy
- ~~Pilar D: ordem dos álbuns e se "álbuns parciais" (2–3 faixas, como ZP/PMH hoje) contam para a meta de 10.~~ → **resolvido no epic #46 (fechamento da #12)**: álbums parciais **contam** — o que vale é o patch documentado com dossiê, não a integralidade do disco; a meta ≥ 100 patches / ≥ 10 álbuns segue como trajetória pública da 2.x (estado: 103/61/7)

---

[`📖 README do projeto`](../README.md) · [`🗂 18-project-management`](18-project-management.md) · [`🌊 12-workflow`](12-workflow.md) · [`📦 DEVELOPMENT`](../DEVELOPMENT.md)
