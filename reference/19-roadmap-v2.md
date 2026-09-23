# 🗺 Roadmap v2.0 — formato, ferramentas, site e conteúdo

> Documento 19 — consolida o brainstorm da versão 2.0. Define **o que justifica o
> bump MAJOR**, o que entra antes (1.x) e a sequência de releases. Complementa o
> [`18-project-management`](18-project-management.md) (que cobre o *como* de
> gestão) e o [`12-workflow`](12-workflow.md) (que cobre a criação de patches).

## 1 · Onde estamos (baseline de set/2026)

| Dimensão | Estado |
|---|---|
| Biblioteca | **66 patches / 41 músicas / 5 álbuns** (Abbey Road 20 · Pulse 38 · Supernatural 4 · Apostrophe 2 · Cheap Thrills 2) |
| Pipeline | Reprodutível e guardado pela suíte (43 testes, incluindo o `TestH` de sincronia) · CLI unificada `gp100.py` |
| Em voo | **Wishkah (Nirvana)**: 17 músicas / 31 patches prontos em branch própria, aguardando merge |
| Em voo | **Smooth (Santana)**: 4 patches com stomps, à frente da `develop` |
| Gestão | Taxonomia, milestones, Project v2 e guardian definidos no repo (doc 18) — **bootstrap ainda não rodado contra o GitHub** |
| Formato | `patches-defs.json` monolítico (~1 arquivo, 41 músicas); stomps ad-hoc no defs; `<ppEXP1>` ainda não explorado |

> ⚠️ O README ainda anuncia 62 patches — atualizar junto com o próximo merge de álbum (é saída de texto do próprio README, não de script).

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
tools/
  defs/
    _albums.json        ← albums + meta (o que é hoje albums/meta)
    abbey-road.json     ← só as músicas do álbum (AR)
    pulse.json          ← PL
    cheap-thrills.json  ← PMH
    apostrophe.json     ← ZP
    supernatural.json   ← SN
  patches-defs.json     ← LEGADO: loader continua lendo (ou migrado por script)
```

- **Loader único**: um `tools/defs_loader.py` concatena os fragmentos na ordem
  declarada em `_albums.json` — a ordem dos slots U01…Uxx continua
  determinística (regra de estável entre SOs, `TestI_OrdemEstavel`, se aplica).
- **Fonte única preservada**: nenhum script passa a manter tabela própria; o
  que muda é só a *granularidade física* do defs.
- **Guarda de sincronia**: o `TestH` passa a comparar o resultado do pipeline
  sobre os fragmentos com o commitado — a mesma garantia, novo formato.
- **Migração**: script one-shot `tools/migrate_defs_v2.py` escreve os
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
Proposta: um `tools/defs_schema.py` (stdlib pura) que valida o defs **antes** de
qualquer script tocar nele — campos obrigatórios, tipos, ranges de nome
(`≤ 12 chars`), unicidade de ids, referências cruzadas (`ir_local` ↔ CAB usado).
Mensagem aponta o caminho JSON exato e o que fazer.

### A4. Variante `-USERIR` gerável

Hoje `ir_cab_user_slot` é experimental e só com teste no device. Proposta:
flag de build (`--with-user-ir`) que gera a variante ao lado do `.prst` canônico,
marcada como experimental na doc — quem valida no device empacota a variante
com confiança de que o canônico não mudou.

## 4 · Pilar B — CLI unificada

**`python tools/gp100.py`** — um ponto de entrada que compõe os scripts
existentes (eles continuam funcionando sozinhos):

| Comando | O que faz |
|---|---|
| `gp100.py find <termo>` | Busca por música/artista/álbum/captador → caminho, slot, IR recomendada |
| `gp100.py show <NOME>` | Resumo do patch: cadeia em 1 linha, ajustes finos, momentos, stomps |
| `gp100.py diff <A> <B>` | Diff **legível** de spec (módulo a módulo, nome de parâmetro oficial) — hoje comparar dois `.prst` é ler JSON à mão |
| `gp100.py export [--album X] [--destino D]` | Copia a seleção de `.prst` para a pasta de importação USB, na ordem dos slots |
| `gp100.py build` | Encadeia o pipeline inteiro (o mesmo comando do guarda de sincronia) |
| `gp100.py verify` | Suíte + guarda, resumo curto |

Zero dependências (stdlib), padrão dos scripts existentes (stdout UTF-8,
ordenação estável). Reaproveita `patches-defs` + catálogos; nada de rede.

## 5 · Pilar C — Site estático da biblioteca

**`tools/gen_site.py`** → GitHub Pages, gerado dos mesmos dados do `gen_indexes`:

- **Página por álbum** e **página por patch**: cadeia, tabela de parâmetros
  (nomes oficiais), ajustes finos, seção 📡 de IR, momentos/stomps, badges.
- **Busca client-side** (índice JSON minúsculo: música, artista, álbum,
  captador, camada) — sem backend, sem dependência.
- Regra herdada do projeto: **o site é saída de script** (o guarda de sincronia
  passa a cobrir `site/**` se ele for versionado; alternativa: gerar no workflow
  de release e publicar via Pages sem commitar — decidir na issue).

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
   palco — **entregue**: cálculo em `tools/gp100_setlist.py` (vizinho mais
   próximo sobre a assinatura PRE→RVB; slots do `slot_map`), agente
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

- ~~Matriz Python 3.10–3.13 no CI~~ **Reorientado (decisão do mantenedor): Python 3.14 APENAS** — travado em código: guarda de runtime nos entry points (`tools/defs_schema.py`), suíte inteira recusa outro runtime e verificação `3.14.*` como primeiro passo do job `test-suite` no CI.
- Testes para os scripts hoje fora da suíte: `analyze_prst`, `build_release`,
  `gen_changelog` — **entregues** (24 testes em `tests/test_scripts.py`).
- `dependabot` já vigia Actions; manter.

## 9 · Sequência de releases

```
v1.1.0 — Álbuns e fluxo PR-driven
  □ bootstrap da gestão rodado contra o GitHub (labels + milestones; Project pende escopo `project`) ✓
  □ camada de gestão commitada (doc 18, bootstrap, guardian) → PR → merge — issue #4
  □ merge de Smooth (Santana) — 4 patches com stomps — issue #5
  □ merge do Wishkah (Nirvana) — 17 músicas / 31 patches — issue #6
  □ README atualizado (contagens por álbum pós-merges) — issue #7

v1.2.0 — Fundações do 2.0 (tudo aditivo; issues a abrir)
  □ CLI gp100.py (find/show/diff/export/build/verify) — issue #13 ✅
  □ defs_schema.py (validação acionável) — issue #14 ✅
  □ skills gp100-setlist + A/B + golden set dos agentes — issue #15 ✅
  □ trava Python 3.14 no CI + testes dos scripts soltos — issue #16 ✅
  □ 1º álbum novo do pilar D (SRV ou Mayer)

v2.0.0 — Formato, site e escala (as quebras)
  □ schema v2: defs por álbum + migrate_defs_v2.py + guarda atualizado — issue #8
  □ stomps/EXP1 formais no schema, com validação e seções novas na doc — issue #9
  □ variante -USERIR gerável — issue #10
  □ gen_site.py + GitHub Pages (busca + página por patch) — issue #11
  □ ≥ 100 patches / ≥ 10 álbuns (1º álbum: SRV / Hendrix / Mayer) — issue #12
```

Regras herdadas valem para tudo acima: nenhum job escreve no git; patches/** é
saída de script; todo PR fecha issue com `Closes #N`; suíte verde antes do
merge (doc 18).

## 10 · Itens para decidir nas issues (não aqui)

- Pilar A1: manter `patches-defs.json` como alias de leitura por um ciclo ou removê-lo no mesmo PR?
- Pilar A2: `doc.stomps` vazio é válido ou o validador passa a exigir o campo?
- Pilar C: site versionado (com guarda de sincronia) ou gerado no release e publicado sem commitar?
- Pilar D: ordem dos álbuns e se "álbuns parciais" (2–3 faixas, como ZP/PMH hoje) contam para a meta de 10.

---

[`📖 README do projeto`](../README.md) · [`🗂 18-project-management`](18-project-management.md) · [`🌊 12-workflow`](12-workflow.md) · [`🔧 tools/`](../tools/README.md)
