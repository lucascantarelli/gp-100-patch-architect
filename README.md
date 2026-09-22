# 🎸 GP-100 Patch Architect

### *Agente Freebuff que cria patches Valeton GP-100 a partir do rig real de qualquer música*

![Release](https://img.shields.io/badge/release-1.0-e02d2d?style=flat-square) ![Firmware](https://img.shields.io/badge/firmware-2.1%20(confirmado%20no%20device)-2ea44f?style=flat-square) ![Agentes](https://img.shields.io/badge/agentes-17-e02d2d?style=flat-square) ![Patches](https://img.shields.io/badge/patches-62%20·%203%20álbuns-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Python](https://img.shields.io/badge/gerador-Python%203-f3a637?style=flat-square) [![CI](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/ci.yml/badge.svg)](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/ci.yml)

---

> Agente que entrevista o músico, pesquisa o **rig real** do artista/música na internet, mapeia para os modelos reais da GP-100 (catálogo **firmware 2.0/2.1**) e entrega patches **documentados + arquivos `.prst` importáveis**. Roda no [Freebuff](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) — o agente de código gratuito.

## 💜 Freebuff — a plataforma deste agente

Este projeto roda sobre o **[Freebuff](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf)**, o agente de programação gratuito (CLI, Desktop, Web, Cloud e Chat) — sem assinatura, sem créditos e sem chave de API, sustentado por anúncios de texto.

**💜 Apoie o projeto usando meu link de indicação** — cadastros por indicação rendem **sessões extras** para você:

> ### 👉 [https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf)

| Produto | Para quê | Começar |
|---|---|---|
| **Freebuff CLI** | Rodar este agente no terminal, nesta pasta | `npm install -g freebuff` |
| **Freebuff Desktop** | Vários agentes em paralelo, cada um em workspace isolado | [Download](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) |
| **Freebuff Web / Cloud** | Agentes em nuvem, conectados a repositórios GitHub | [Site](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) |
| **Freebuff Chat** | Pesquisa e estudo (ex.: consultar este README em campo) | [Site](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) |

**Modelos:** o catálogo inclui **GLM 5.3 Flash** (padrão, raciocínio profundo), DeepSeek V4.1 Flash (rápido), GPT-5.6 Luna, MiMo 2.5 e outros — a troca é feita no seletor do CLI. Indicações e bounties rendem sessões extras além da franquia diária gratuita.

## 📦 Instalação do Freebuff CLI

Requisito único: **Node.js 18+** (macOS, Windows ou Linux).

```bash
# 1. Instale o CLI (uma vez)
npm install -g freebuff

# 2. Entre na pasta deste projeto (o nome tem espaços — use aspas)
cd "GP-100 Patch Architect"

# 3. Inicie o agente
freebuff
```

É isso — **sem chave de API, sem cartão, sem configuração obrigatória**. Descreva o que quer em português e o Freebuff orquestra os agentes. 💡 Dica: instale pela [página de indicação](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) para ganhar as sessões extras desde o primeiro dia.

## ⚙️ Como este projeto está configurado

O comportamento do agente é 100% definido por arquivos versionados nesta pasta — qualquer Freebuff (CLI ou Desktop) os carrega sozinho ao abrir o projeto:

| Camada | Arquivos | Papel |
|---|---|---|
| **Orquestração** | `.agents/gp100-patch-architect.ts` | Agente-mestre: recebe o pedido, pesquisa o rig real, distribui o trabalho |
| **Skills por efeito** | `.agents/gp100-{pre,dst,amp,cab-ir,eq,mod,nr,dly,rvb,globals}.ts` | Uma skill por bloco da cadeia, com todos os parâmetros, ranges, "o que evitar" e sugestões |
| **Skills de apoio** | `.agents/gp100-{tone-research,tone-mapper,ir-research,ir-fit,manual-reader,patch-validator}.ts` | Pesquisa de referência, mapeamento rig→GP-100, política de IRs, validação |
| **Regras de ouro** | `knowledge.md` | Convenções do projeto (patches por música, nomenclatura, política de IR) |
| **Base técnica** | `reference/00…17` | Manual V1.8 transcrito + catálogo empírico do firmware 2.0/2.1 |
| **Template de doc** | `templates/patch-template.md` | Estrutura fixa de cada `patch.md` |
| **Prompts prontos** | `prompts/*.md` | Fluxos de criação, ajuste, sugestão e pesquisa |

## 🚀 Como usar

Abra o Freebuff nesta pasta e peça um patch:

```
Criar patch GP-100 com referência

Artista/música: <artista ou música>
O que quero extrair: <base, solo, som geral — uma camada por pedido>
Captador que usarei: <bridge / neck / posição 2–4 / decida o melhor e documente>
Contexto: <gravar em casa com fone / ensaio / show>
IR de terceiros: pesquisar IR; caso não encontre, use uma de fábrica
```

> Fluxos prontos em [`prompts/`](prompts/) · Exemplos reais na [biblioteca de patches](patches/README.md): **Pulse** (Pink Floyd — 24 músicas → 38 patches, ordem do álbum em U25–U62), **Abbey Road** (17 músicas → 20 patches), **Uncle Remus** (Zappa) e **Piece of My Heart** (Janis Joplin).

## 📦 Entrega de cada patch

**Regra central: patches são por MÚSICA** — cada faixa tem seu conjunto exclusivo, dividido nas camadas que ela contém (base, solo, riff, clean…). Nome no painel = `MÚSICA+CAMADA` (máx. 12 caracteres): `STH01BA` = Something · base · `CT01RIF` = Come Together · riff · `PMH01SO` = Piece of My Heart · solo.

Cada patch entrega:

| Arquivo | O que é |
|---|---|
| `<NOME>.prst` | **Importável no GP-100 Edits ou direto na pedaleira** (formato single-patch, firmware 2.1) |
| `patch.md` | Doc **prática-primeiro**: 🎸 guitarra (seletor/volume/tone/técnica) → 🔧 ajustes finos → 📡 seção exclusiva de IR → 🔊 objetivo do som → 📚 dossiê do rig real com fontes → 🎛️ parâmetros e receita de digitação |
| `spec.json` | Definição estruturada (fonte do `.prst`) |

> **📡 Política de IR** — a seção exclusiva de cada `patch.md` segue sempre: **1.** o que o `.prst` usa agora (CAB de fábrica, funciona imediatamente) → **2.** captura melhor no banco local `impulse_responses/` (arquivo exato + slot User IR + passo a passo) → **3.** download gratuito na internet quando nem banco nem fábrica cobrem → **4.** fallback garantido no CAB de fábrica.

> Fonte única dos patches: `tools/patches-defs.json` · regenerar com `python tools/build_song_patches.py` + `python tools/gen_indexes.py`.

## 🗂️ Estrutura do projeto

```
├── .agents/            # 17 agentes (orquestrador + 16 skills) — configuração do Freebuff
├── reference/          # base de conhecimento: manual V1.8 + catálogo fw 2.0/2.1 + catálogos de IR
├── prompts/            # fluxos prontos (criar, ajustar, sugerir, pesquisar referência)
├── templates/          # template de documentação de patch
├── tools/              # scripts Python (ver 🔧 Ferramentas abaixo)
├── patches/            # biblioteca: Banda/Álbum/Música/PATCH (.prst + patch.md + spec.json)
├── impulse_responses/  # banco local de IRs (WAV 44.1 kHz) — indexado por ir_library.py
├── tests/              # suíte do pipeline (unittest, sem dependências)
├── .github/workflows/  # CI: pipeline de dados + testes + typecheck dos agentes
├── knowledge.md        # regras de ouro do projeto
├── manual.pdf          # manual oficial (V1.8 impresso)
├── .gitattributes      # .prst fixado em CRLF · WAV/PDF tratados como binários
└── .gitignore          # manual_pages/, caches Python, lixo de SO e estado local
```

## 🔧 Ferramentas

| Script | Uso | O que faz |
|---|---|---|
| `tools/build_song_patches.py` | `python tools/build_song_patches.py` | **Construtor principal** — a partir de `patches-defs.json`, gera `spec.json` + `patch.md` + `.prst` de todos os patches e valida (nome ≤ 12 chars, XML conforme) |
| `tools/generate_prst.py` | `python tools/generate_prst.py spec.json saida.prst` | Gera **um** `.prst` single-patch fw 2.1 — réplica exata do formato single validado no aparelho (sem `<ppIRInfo>`, com `<ppCtrl>`/`<ppEXP1>`, cadeia x=0–8) |
| `tools/render_manual_page.py` | `python tools/render_manual_page.py 21 [22 …] · --all` | Renderiza páginas do `manual.pdf` **sob demanda** (PNG alta + JPG leve em `manual_pages/`, efêmero) — página impressa NN = arquivo NN+2 |
| `tools/gen_indexes.py` | `python tools/gen_indexes.py` | Regenera os `MAPA-DO-ALBUM.md` e o `patches/README.md` — slots U01…Uxx calculados pela ordem dos defs |
| `tools/ir_library.py` | `python tools/ir_library.py` | Indexa `impulse_responses/` (valida mono/24-bit/44.1 kHz) → `tools/ir-library.json` + `reference/16-ir-library.md` |
| `tools/check_data_freshness.py` | `python tools/check_data_freshness.py` | **Guarda do CI** — compara os artefatos gerados no disco com o HEAD (só o `preset_info/@time` é ignorado) e reprova citando o comando de conserto quando algo gerado ficou fora do commit |
| `tools/analyze_prst.py` | `python tools/analyze_prst.py <arquivo>.prst [--json out.json]` | Disseca qualquer export `.prst` (modelos, ranges empíricos de params, catálogo) — é dele que nasceu o catálogo fw 2.0 |
| `tests/test_pipeline.py` | `python -m unittest discover -s tests -v` | **Suíte de validação** do pipeline: defs, formato `.prst`, docs, momentos, nomes de parâmetro, drift dos índices e a ordem estável entre sistemas operacionais (é o que o CI roda) |

**Cadeia típica ao acrescentar um álbum:** edite `tools/patches-defs.json` → `build_song_patches.py` → `gen_indexes.py` → **rode a suíte de testes** e o `check_data_freshness.py`. **Baixou packs de IR?** Extraia em `impulse_responses/<Pack>/` → rode `ir_library.py`. Downloads recomendados: [`reference/17-free-ir-packs.md`](reference/17-free-ir-packs.md).

> **Acrescentou elemento novo?** (música, camada, patch, efeito, momento de toggle, pack de IR) O pipeline inteiro é obrigatório, e o job `dados` do CI reprova o PR que esquecer:
>
> ```bash
> python tools/ir_library.py && python tools/add_pulse_defs.py \
>   && python tools/build_song_patches.py && python tools/gen_indexes.py \
>   && python tools/check_data_freshness.py
> ```

### 📍 Fonte única de dados

Tudo que descreve uma música, um álbum ou uma IR vive **só** em `tools/patches-defs.json` (`albums` → banda/ano/pasta/título/dossiê do rig · `ir_local` → captura recomendada por CAB · cada música → `song`, `pasta`, `display`, patches). Os scripts são renderizadores: nenhum deles tem lista de músicas ou de cabs. Foi a duplicação dessas tabelas que fez o mapa do álbum recomendar "fábrica" enquanto o `patch.md` mandava carregar uma IR do banco nos 38 patches do Pulse — hoje o teste `TestB_FonteUnica_IR` reprova isso.

## ✅ Qualidade — o que o CI garante

Cada push e cada PR rodam o workflow [`pipeline`](.github/workflows/ci.yml), em três jobs:

| Job | O que faz |
|---|---|
| **`dados`** | roda o **pipeline de dados inteiro** (IR → seeders → momentos → construtor → índices). **Em push no `main` (ou execução manual), se o pipeline mexeu em algo, o próprio job commita e envia** (`chore: regenera os dados do pipeline`) — o repositório não fica vermelho por esquecimento de regenerar. Depois `check_data_freshness.py` dá o veredito; **em PR o commit não roda** (fork não tem escrita) e o guarda reprova com o comando exato de conserto |
| **`python`** | compila os scripts e executa a suíte (**28 testes, sem dependências** — `unittest` da stdlib) |
| **`agentes`** | `tsc --noEmit` nos 17 agentes |

Para rodar igual na sua máquina:

```bash
python -m unittest discover -s tests -v
```

A suíte cobre as invariantes que **já quebraram uma vez** neste projeto:

| Classe | O que reprova |
|---|---|
| `TestB_FonteUnica_IR` | mapa do álbum e seção 📡 do `patch.md` discordando sobre a IR (bug dos 38 patches do Pulse) |
| `TestC_Prst` | `.prst` fora do formato **single fw 2.1** (`ppIRInfo`, ordem dos módulos, `x`, 15 params, `ppName` ≠ pasta) |
| `TestD_Documentacao` | doc sem uma das 9 seções, HTML cru no Markdown ou rótulo placeholder (`(pN)`/`pN` solto em ajustes e tabelas) |
| `TestE_Momentos` | momento de toggle inválido (módulo inexistente, estado já ativo, ou tentativa de desligar AMP/CAB) |
| `TestF_ParamNames` | modelo ligado em patch **sem tabela de nomes** fora da allowlist (hoje vazia: o manual oficial do fw V2.0 deu nome a `Saturate`, `Red Haze` e `T-Echo`) ou tabela com placeholder |
| `TestG_Indices` | índice defasado (esqueceu de rodar `gen_indexes.py`) ou numeração de slots divergente entre os dois scripts |
| `TestH_DadosEmSincronia` | normalização do check de frescor: `time` do `.prst` ignorado, CRLF≡LF e mudança de parâmetro **não** mascarada; e toda saída do pipeline coberta pelo check |

## 🎯 Regras de ouro

- Precedência do catálogo **fw 2.0/2.1** (nomes reais: `Blues OD`, `Green OD`, `Dark Twin`, `DarkTW 2x12`, `Spring`...) sobre o manual impresso V1.8 — ver `reference/15-firmware2-effects.md`.
- **Nomes de parâmetro 100% oficiais** (manual do firmware V2.0): `Saturate` = Gain/Mix/Output/H-Cut · `Red Haze` = Fuzz/VOL · família DLY = **Mix/Time/Fdbk** · RVB começa por **Mix** · `Vibe` = Depth/Rate/Sync. Zero rótulo `pN` na documentação: os slots **internos** do firmware (que o editor não expõe) não são setados nem rotulados — tabela completa e a exceção do `T-Echo` em `reference/15-firmware2-effects.md`.
- **Patches por música, nunca compartilhados**; camadas separadas quando o timbre muda de verdade — e **momentos de toggle** documentados: a GP-100 liga/desliga módulos em tempo real (painel ou modo STOMP), então um patch de base com DLY sobressalente vira solo ao ligar o eco, sem trocar de patch.
- NR obrigatório com ganho ≥ 55; um efeito espacial dominante por patch.
- Perfis por captador da Strat single coil (bridge/neck/posições 2–4).
- `.prst` sai sempre no formato **single** com CAB de fábrica; IRs de terceiros são **documentadas**, nunca embutidas.

## 🧪 Histórico de validação

- ✅ `.prst` comparados estruturalmente com o export **single** que importou com sucesso no aparelho (7 checks), formato firmware 2.1 — o formato está registrado no gerador.
- ✅ 62 patches em biblioteca (Abbey Road, Apostrophe (') e Pulse — 42 músicas), XMLs validados, 0 HTML cru e slots U01–U62 mapeados; pipeline **idempotente** (regenerar não muda parâmetros — só o timestamp `preset_info/@time`, igual ao export real).
- ✅ Seções obrigatórias presentes nos 62 docs (guitarra → ajustes finos → IR → modos de atuação → objetivo → dossiê → parâmetros → carga → evite) e 32 momentos de toggle validados contra o spec.
- ✅ **Zero rótulo `pN` nos 62 docs**: os 40 `patch.md` do Pulse e as 28 menções em textos de ajustes/evite passaram a usar os nomes do manual V2.0 (rótulos acima); os slots **internos** do firmware (que o editor não expõe) não são setados nem rotulados — ficam no default de fábrica.
- ✅ **Dossiê de rig de Cheap Thrills** (Big Brother & The Holding Company): duas guitarras em **Gibson SG** (Gurley e Andrew), **Fender Twin Reverb**, Maestro FZ-1 no Gurley — e o achado que fecha o timbre da faixa: **Piece of My Heart sem fuzz** (Gurley limpo, Sam sujo no Twin estourado); o mapa da Janis voltou a ter seção de rig, com fontes.
- ✅ **CI + suíte de testes** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): 28 testes em `tests/` validam defs, formato dos 62 `.prst`, docs, momentos, nomes de parâmetro, drift dos índices e a ordem estável entre OS — stdlib pura (nenhuma dependência para instalar). O job **`dados`** roda o pipeline completo a cada push/PR e, **em push no `main`, commita os dados regenerados sozinho** antes do veredito do `check_data_freshness.py` (só o timestamp `preset_info/@time` é ignorado — o pipeline é reprodutível em 194 artefatos).
- ✅ **Pipeline reprodutível entre sistemas**: a ordem dos artefatos derivados não depende do SO — a comparação de `Path` usa `normcase` (minúsculas no Windows, identidade no Linux) e fazia o manifesto de IRs divergir entre a máquina e o CI; a ordenação agora é por string (ordem de code point), com teste travando a regressão (`TestI_OrdemEstavel`).
- ✅ Typecheck `tsc --noEmit` limpo nos 17 agentes.
- ✅ Manual V1.8 transcrito página a página para `reference/` + catálogo empírico extraído do export de fábrica (`tools/factory-catalog.json`, 99 presets · 117 modelos).
- ✅ Banco local de IRs indexado (291 WAVs — Origin Effects IR-Cab Library V3).
- ✅ Limpeza: export de fábrica, arquivos de exemplo e páginas pré-renderizadas do manual removidos — todo o conhecimento drenado para `reference/` + `tools/`; manual renderizável sob demanda.

## 📚 Toda a documentação

| Documento | Conteúdo |
|---|---|
| [`knowledge.md`](knowledge.md) | Regras de ouro e convenções que os agentes seguem |
| [`.agents/README.md`](.agents/README.md) | Arquitetura dos 17 agentes e como criar um novo |
| [`tools/README.md`](tools/README.md) | Scripts de geração/análise, arquivos de dados e armadilhas do formato |
| [`reference/README.md`](reference/README.md) | Índice da base de conhecimento + ordem de precedência das fontes |
| [`impulse_responses/README.md`](impulse_responses/README.md) | Banco local de IRs: política, formato aceito e fluxo de indexação |
| [`reference/00-signal-chain.md`](reference/00-signal-chain.md) | Visão da cadeia de sinal da GP-100 |
| [`reference/01–10`](reference/) | Módulos bloco a bloco: PRE, DST, AMP, CAB/IR, EQ, MOD, NR, DLY, RVB, globais |
| [`reference/11-ir-guide.md`](reference/11-ir-guide.md) | Guia de Impulse Response na GP-100 |
| [`reference/12-workflow.md`](reference/12-workflow.md) | Workflow de criação de patch |
| [`reference/13-preset-list.md`](reference/13-preset-list.md) | Os 99 presets de fábrica |
| [`reference/14-glossario.md`](reference/14-glossario.md) | Glossário de termos |
| [`reference/15-firmware2-effects.md`](reference/15-firmware2-effects.md) | **Catálogo real fw 2.0/2.1** (fonte da precedência) |
| [`reference/16-ir-library.md`](reference/16-ir-library.md) | Catálogo do banco local de IRs (gerado) |
| [`reference/17-free-ir-packs.md`](reference/17-free-ir-packs.md) | Packs de IR gratuitos para download |
| [`prompts/`](prompts/) | Fluxos prontos de pedido ao agente |
| [`patches/README.md`](patches/README.md) | Biblioteca completa + nomenclatura + mapas |

---

[`🎸 Biblioteca de patches`](patches/README.md) · [`🤖 Agentes`](.agents/) · [`📚 Reference`](reference/) · [`💜 Criar conta no Freebuff`](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf)
