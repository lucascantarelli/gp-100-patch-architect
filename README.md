# 🎸 GP-100 Patch Architect

### *Agente Freebuff que cria patches Valeton GP-100 a partir do rig real de qualquer música*

![Release](https://img.shields.io/badge/release-1.0-e02d2d?style=flat-square) ![Firmware](https://img.shields.io/badge/firmware-2.1%20(confirmado%20no%20device)-2ea44f?style=flat-square) ![Agentes](https://img.shields.io/badge/agentes-19-e02d2d?style=flat-square) ![Skills](https://img.shields.io/badge/skills-11-e02d2d?style=flat-square) ![Patches](https://img.shields.io/badge/patches-97%20·%206%20álbuns-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Python](https://img.shields.io/badge/gerador-Python%203.14-f3a637?style=flat-square) ![Testes](https://img.shields.io/badge/333%20testes%20·%20cobertura%2090%2C81%25-2ea44f?style=flat-square) [![Site](https://img.shields.io/badge/📚%20biblioteca%20online-lucascantarelli.github.io-2f6fdd?style=flat-square)](https://lucascantarelli.github.io/gp-100-patch-architect/) [![CI](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/ci.yml/badge.svg)](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/ci.yml) [![Security](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/security.yml/badge.svg)](https://github.com/lucascantarelli/gp-100-patch-architect/actions/workflows/security.yml) [![CodeQL](https://img.shields.io/badge/CodeQL-Python%20·%20TypeScript-2f6fdd?style=flat-square)](https://github.com/lucascantarelli/gp-100-patch-architect/security/code-scanning) [![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE) [![PRs welcome](https://img.shields.io/badge/PRs-welcome-e02d2d?style=flat-square)](CONTRIBUTING.md)

---

> Agente que entrevista o músico, pesquisa o **rig real** do artista/música na internet, mapeia para os modelos reais da GP-100 (catálogo **firmware 2.0/2.1**) e entrega patches **documentados + arquivos `.prst` importáveis**. 📚 **[Navegue pela biblioteca](https://lucascantarelli.github.io/gp-100-patch-architect/)** — busca client-side e página por patch, publicada direto do defs. Roda no [Freebuff](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf) — o agente de código gratuito.

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
| **Persistência** | `data/defs/` (fragmentos por álbum, schema v2) | Fonte única do patch: `_albums.json` + um JSON por álbum; o pipeline (`gp100 build`) gera `patch.md` e `.prst` a partir deles |
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

> Fluxos prontos em [`prompts/`](prompts/) · Exemplos reais na [biblioteca de patches](patches/README.md): **Pulse** (Pink Floyd — 24 músicas → 38 patches, ordem do álbum em U25–U62), **Wishkah** (Nirvana — 17 músicas → 31 patches, U63–U93), **Abbey Road** (14 músicas → 20 patches), **Uncle Remus** (Zappa), **Piece of My Heart** (Janis Joplin) e **Smooth** (Santana — 4 patches com stomps, U94–U97).

## 📦 Entrega de cada patch

**Regra central: patches são por MÚSICA** — cada faixa tem seu conjunto exclusivo, dividido nas camadas que ela contém (base, solo, riff, clean…). Nome no painel = `MÚSICA+CAMADA` (máx. 12 caracteres): `STH01BA` = Something · base · `CT01RIF` = Come Together · riff · `PMH01SO` = Piece of My Heart · solo.

Cada patch entrega:

| Arquivo | O que é |
|---|---|
| `<NOME>.prst` | **Importável no GP-100 Edits ou direto na pedaleira** (formato single-patch, firmware 2.1) |
| `patch.md` | Doc **prática-primeiro**: 🎸 guitarra (seletor/volume/tone/técnica) → 🔧 ajustes finos → 📡 seção exclusiva de IR → 🔊 objetivo do som → 📚 dossiê do rig real com fontes → 🎛️ parâmetros e receita de digitação |

> **📡 Política de IR** — a seção exclusiva de cada `patch.md` segue sempre: **1.** o que o `.prst` usa agora (CAB de fábrica, funciona imediatamente) → **2.** captura melhor no banco local `impulse_responses/` (arquivo exato + slot User IR + passo a passo) → **3.** download gratuito na internet quando nem banco nem fábrica cobrem → **4.** fallback garantido no CAB de fábrica.

> Fonte única dos patches: `data/defs/` (schema v2) · regenerar com `uv run gp100 build`.

## 🗂️ Estrutura do projeto

```
├── src/gp100_architect/ # PACOTE Python (domain · application · infrastructure · interfaces)
├── docs/               # ADRs (docs/decisions/) — documentação de engenharia
├── .agents/            # 19 agentes + 11 skills (agents/skills/) — configuração do Freebuff
├── reference/          # base de conhecimento: manual V1.8 + catálogo fw 2.0/2.1 + catálogos de IR
├── prompts/            # fluxos prontos (criar, ajustar, sugerir, pesquisar referência)
├── data/               # dados do pipeline: defs/, factory-catalog.json, ir-library.json
├── patches/            # biblioteca (saída de script): Banda/Álbum/Música/PATCH (.prst + patch.md)
├── impulse_responses/  # banco local de IRs (WAV 44.1 kHz) — indexado por gp100 build
│                       # ⚠️ os WAV NÃO são versionados (licença de terceiro)
├── tests/              # suíte (unit/ em pytest + testes históricos do pipeline)
├── .github/            # CI · segurança (CodeQL) · release · templates de issue/PR · CODEOWNERS
├── pyproject.toml      # pacote: metadados, deps, entry point `gp100` e config dos gates
├── uv.lock             # resolução travada — o CI instala com `uv sync --frozen`
├── ARCHITECTURE.md     # arquitetura em 1 página (resumo; a decisão vive nos ADRs)
├── DEVELOPMENT.md      # setup, comandos do dia a dia, regras que o CI cobra
├── knowledge.md        # regras de ouro do projeto
├── CONTRIBUTING.md     # ambiente, pipeline obrigatório, Conventional Commits, fluxo develop → main
├── SECURITY.md         # escopo de segurança, prazos e canal de divulgação privada
├── CODE_OF_CONDUCT.md  # Contributor Covenant 2.1
├── CHANGELOG.md        # gerado pelo comando gp100 changelog a partir dos commits
├── VERSION             # fonte única da versão (SemVer) — lida pelo CI de release
├── manual.pdf          # manual oficial (V1.8) — NÃO versionado: obtenha no site do fabricante
├── .editorconfig       # indentação e fim de linha (CRLF em .prst e docs de patch)
├── .gitattributes      # .prst fixado em CRLF · WAV/PDF tratados como binários
└── .gitignore          # banco de IRs e manual.pdf fora do git · caches · estado local
```

> **📡 O banco de IRs e o `manual.pdf` não vivem no repositório.** As licenças são de
> terceiros — a IR-Cab Library V3 é gratuita com cadastro no site da Origin Effects,
> mas não concede redistribuição. O que **é** versionado é o catálogo derivado
> (`data/ir-library.json` + `reference/16-ir-library.md`), porque é ele que diz a cada
> `patch.md` qual arquivo exato do banco usar. Detalhes: [`impulse_responses/README.md`](impulse_responses/README.md).

## 🔧 Ferramentas

| Comando / caminho | Uso | O que faz |
|---|---|---|
| `gp100` | `uv run gp100 <comando>` | **CLI oficial** (Typer + Rich) — consulta: `find` · `show` · `diff` · `export`; produção: `build` · `verify` · `setlist` · `release`; utilidades: `validate` · `analyze` · `manual-page` · `changelog` · `site` · `version`. Saídas `--json` estáveis para agentes |
| `gp100 build` | `uv run gp100 build [--with-user-ir]` | **O pipeline completo** in-process (`application/pipeline.py`) — indexa `impulse_responses/` → `data/ir-library.json` + `reference/16-ir-library.md`, gera `patch.md` + `.prst` via codec in-memory (ADR-0013) e regenera os `MAPA-DO-ALBUM.md` + `patches/README.md`. Com `--with-user-ir` (issue #10), escreve também as variantes experimentais `-USERIR` |
| `gp100 analyze` | `uv run gp100 analyze <arquivo>.prst [--json out.json]` | Disseca qualquer export `.prst` (modelos, ranges empíricos de params, catálogo) — é dele que nasceu o catálogo fw 2.0 (`data/factory-catalog.json`) |
| `gp100 manual-page` | `uv run gp100 manual-page 21 [22 …] · --all` | Renderiza páginas do `manual.pdf` **sob demanda** (requer pymupdf; PNG alta + JPG leve em `manual_pages/`, efêmero) — página impressa NN = arquivo NN+2 |
| `gp100 changelog` | `uv run gp100 changelog [--version X.Y.Z] [--write]` | **Changelog derivado dos commits** (Conventional Commits): agrupa por tipo, isola breaking changes e sugere o bump SemVer |
| `gp100 site` | `uv run gp100 site [--destino dist/site] [--base-url /gp-100-patch-architect/]` | **Site estático da biblioteca** (issue #11): página por álbum e por patch + busca client-side sobre `busca.json` minúsculo — derivado do defs, sem backend. **Publicado no GitHub Pages a cada push na `develop`**: [lucascantarelli.github.io/gp-100-patch-architect](https://lucascantarelli.github.io/gp-100-patch-architect/) |
| `tests/` | `uv run pytest` | **Suíte em pirâmide** (issue #34): `unit` (regras puras) → `integration` (defs real) → `contract` (formato `.prst` e CLI `gp100`) → `e2e` (derivados e guardas, incluindo a sincronia do pipeline). Fatias: `uv run pytest -m unit`, `-m "not slow"` |
| `data/` | — | **Dados versionados do pipeline**: `defs/` (fonte única, schema v2), `factory-catalog.json` (catálogo empírico do firmware) e `ir-library.json` (manifesto do banco local de IRs, gerado) |
| `scripts/purge_redistributed_assets.sh` | `CONFIRMAR=1 bash scripts/purge_redistributed_assets.sh` | Ferramenta de manutenção: plano/execução de remoção de ativos redistribuíveis (licença) |
| `.github/scripts/audit_workflows.py` | `python .github/scripts/audit_workflows.py` | **Guarda dos workflows** — reprova permissões ausentes ou ACIMA DO TETO declarado por arquivo, job sem `timeout`, injeção em `run:` e `pull_request_target`; avisa sobre Action não fixada por SHA |
| `.github/scripts/audit_agents.py` | `python .github/scripts/audit_agents.py` | **Guarda da camada de IA** (issue #63) — reprova caminho citado por agente inexistente no git, contrato ADR-0008 incompleto e skill fora da curadoria (doc 23); avisa sobre skill sem consumidor |

**Cadeia típica ao acrescentar um álbum:** crie `data/defs/<CHAVE>.json` (e declare a chave em `_albums.json`) → `uv run gp100 build` → **rode a suíte de testes** (ela inclui o guarda de determinismo). **Baixou packs de IR?** Extraia em `impulse_responses/<Pack>/` → `uv run gp100 build`. Downloads recomendados: [`reference/17-free-ir-packs.md`](reference/17-free-ir-packs.md).

> **Acrescentou elemento novo?** (música, camada, patch, efeito, momento de toggle, pack de IR) O pipeline é obrigatório, e o guarda de determinismo da suíte reprova o PR que esquecer de regenerar:
>
> ```bash
> uv run gp100 build
> ```

### 📍 Fonte única de dados

Tudo que descreve uma música, um álbum ou uma IR vive **só** em `data/defs/` (`albums` → banda/ano/pasta/título/dossiê do rig · `ir_local` → captura recomendada por CAB · cada música → `song`, `pasta`, `display`, patches). O pacote é o renderizador: nenhum módulo tem lista de músicas ou de cabs. Foi a duplicação dessas tabelas que fez o mapa do álbum recomendar "fábrica" enquanto o `patch.md` mandava carregar uma IR do banco nos 38 patches do Pulse — hoje o teste `TestB_FonteUnica_IR` reprova isso.

## ✅ Qualidade — o que o CI garante

Cada PR (e cada push em `main` e `develop`) roda o workflow [`CI`](.github/workflows/ci.yml): **três jobs em paralelo** (fase 1) e um **portão de veredito único** (fase 2) — é o check exigido pelas regras de proteção das duas branches:

| Job | O que faz |
|---|---|
| **🚦 `ci-gate`** | **Portão do CI** — reprova se qualquer job da fase 1 falhou e publica o resumo dos resultados |
| **🧪 `test-suite`** | instala o ambiente do lockfile (`uv sync --frozen`), verifica o runtime (**trava Python 3.14.* como primeiro passo**) e executa a suíte (**337 testes**) com pytest e **cobertura do pacote com piso de 90%** (hoje 90,81%), incluindo o **guarda de determinismo**: o pipeline roda numa cópia temporária e tem de reproduzir exatamente o que o defs determina (em clone limpo, a biblioteca inteira — `patches/**` não é commitado). **Nada é escrito no repositório:** o workflow roda com `contents: read`, então nenhum ator automatizado pode empurrar no `main` e a branch protection não precisa de exceção para o bot |
| **🧹 `quality`** | `ruff check` + `ruff format --check` + `mypy --strict` — no pacote `src/gp100_architect` e em toda a suíte `tests/` |
| **🔍 `typecheck`** | `tsc --noEmit` nos 19 agentes, com cache do TypeScript |

Todos os jobs têm `timeout` e o resultado da sincronia dos dados é publicado no **resumo da execução** (Step Summary) do GitHub.

Para rodar igual na sua máquina:

```bash
uv run pytest              # pirâmide completa (unit, integration, contract, e2e)
uv run pytest -m unit     # só a fatia rápida, quando estiver iterando
```

A suíte cobre as invariantes que **já quebraram uma vez** neste projeto:

| Camada / guarda | O que reprova |
|---|---|
| `e2e · fonte única de IR` | mapa do álbum e seção 📡 do `patch.md` discordando sobre a IR (bug dos 38 patches do Pulse) |
| `e2e · .prst` | `.prst` fora do formato **single fw 2.1** (`ppIRInfo`, ordem dos módulos, `x`, 15 params, `ppName` ≠ pasta) |
| `e2e · patch.md` | doc sem uma das 9 seções, HTML cru no Markdown ou rótulo placeholder (`(pN)`/`pN` solto em ajustes e tabelas) |
| `e2e · momentos` | momento de toggle inválido (módulo inexistente, estado já ativo, ou tentativa de desligar AMP/CAB) |
| `e2e · guardas` | modelo ligado em patch **sem tabela de nomes** (allowlist consciente) ou tabela com placeholder; índice defasado (esqueceu de rodar `gen_indexes.py`); ordem de artefato dependente de SO |
| `e2e · sincronia (TestH)` | **guarda de determinismo**: o pipeline rodado numa cópia limpa do repo tem de reproduzir os derivados byte a byte — prova que o defs determina a biblioteca e pega hand-edit em arquivo gerado; `time` do `.prst` ignorado, CRLF≡LF e mudança de parâmetro **não** mascarada |
| `unit` + `integration` | regras puras e casos de uso sobre o defs real — validação com caminho JSON, resolução de pedidos, empacotamento e changelog |

## 🎯 Regras de ouro

- Precedência do catálogo **fw 2.0/2.1** (nomes reais: `Blues OD`, `Green OD`, `Dark Twin`, `DarkTW 2x12`, `Spring`...) sobre o manual impresso V1.8 — ver `reference/15-firmware2-effects.md`.
- **Nomes de parâmetro 100% oficiais** (manual do firmware V2.0): `Saturate` = Gain/Mix/Output/H-Cut · `Red Haze` = Fuzz/VOL · família DLY = **Mix/Time/Fdbk** · RVB começa por **Mix** · `Vibe` = Depth/Rate/Sync. Zero rótulo `pN` na documentação: os slots **internos** do firmware (que o editor não expõe) não são setados nem rotulados — tabela completa e a exceção do `T-Echo` em `reference/15-firmware2-effects.md`.
- **Patches por música, nunca compartilhados**; camadas separadas quando o timbre muda de verdade — e **momentos de toggle** documentados: a GP-100 liga/desliga módulos em tempo real (painel ou modo STOMP), então um patch de base com DLY sobressalente vira solo ao ligar o eco, sem trocar de patch.
- NR obrigatório com ganho ≥ 55; um efeito espacial dominante por patch.
- Perfis por captador da Strat single coil (bridge/neck/posições 2–4).
- `.prst` sai sempre no formato **single** com CAB de fábrica; IRs de terceiros são **documentadas**, nunca embutidas.

## 🧪 Histórico de validação

- ✅ `.prst` comparados estruturalmente com o export **single** que importou com sucesso no aparelho (7 checks), formato firmware 2.1 — o formato está registrado no gerador.
- ✅ 97 patches em biblioteca (Abbey Road, Apostrophe ('), Cheap Thrills, Pulse, From the Muddy Banks of the Wishkah e Supernatural — 58 músicas), XMLs validados, 0 HTML cru e slots U01–U97 mapeados; pipeline **idempotente e reprodutível** (regenerar não muda nada — o timestamp `preset_info/@time` é determinístico).
- ✅ Seções obrigatórias presentes nos 97 docs (guitarra → ajustes finos → IR → modos de atuação → objetivo → dossiê → parâmetros → carga → evite) e 67 momentos de toggle validados contra o spec.
- ✅ **Zero rótulo `pN` nos 97 docs**: os 40 `patch.md` do Pulse e as 28 menções em textos de ajustes/evite passaram a usar os nomes do manual V2.0 (rótulos acima); os slots **internos** do firmware (que o editor não expõe) não são setados nem rotulados — ficam no default de fábrica.
- ✅ **Dossiê de rig de Cheap Thrills** (Big Brother & The Holding Company): duas guitarras em **Gibson SG** (Gurley e Andrew), **Fender Twin Reverb**, Maestro FZ-1 no Gurley — e o achado que fecha o timbre da faixa: **Piece of My Heart sem fuzz** (Gurley limpo, Sam sujo no Twin estourado); o mapa da Janis voltou a ter seção de rig, com fontes.
- ✅ **CI + suíte de testes** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)): **321 testes** em pirâmide pytest (`tests/`) validam defs, formato dos 97 `.prst`, docs, momentos, nomes de parâmetro, drift dos índices, a ordem estável entre OS e o **determinismo dos derivados** — o guarda de sincronia (TestH) roda o pipeline completo numa cópia temporária e compara com o que o defs produz (em clone limpo, a biblioteca inteira; só o timestamp `preset_info/@time` é ignorado); **nenhum job escreve no repositório** (auditoria `--guarda-repo`), e o portão **`ci-gate`** concentra o veredito final.
- ✅ **Pipeline reprodutível entre sistemas**: a ordem dos artefatos derivados não depende do SO — a comparação de `Path` usa `normcase` (minúsculas no Windows, identidade no Linux) e fazia o manifesto de IRs divergir entre a máquina e o CI; a ordenação agora é por string (ordem de code point), com teste travando a regressão (`TestI_OrdemEstavel`).
- ✅ Typecheck `tsc --noEmit` limpo nos 19 agentes.
- ✅ Manual V1.8 transcrito página a página para `reference/` + catálogo empírico extraído do export de fábrica (`data/factory-catalog.json`, 99 presets · 117 modelos).
- ✅ Banco local de IRs indexado (291 WAVs — Origin Effects IR-Cab Library V3).
- ✅ Limpeza: export de fábrica, arquivos de exemplo e páginas pré-renderizadas do manual removidos — todo o conhecimento drenado para `reference/` e o pacote; manual renderizável sob demanda.

## ❓ FAQ

**Preciso instalar ou baixar alguma coisa para usar os patches?**
Não. O `.prst` sai com **CAB de fábrica** e funciona ao importar. IR de terceiro é
uma camada **opcional** de refinamento — a seção 📡 do `patch.md` explica qual usar.

**O patch não importou na pedaleira. Por onde começo?**
Confira três coisas, nesta ordem: (1) o firmware é **2.1** (o formato é single fw 2.1);
(2) o arquivo veio de `patches/**` sem edição manual — os `.prst` são gerados e validados
pelo pipeline; (3) você está importando em **SYSTEM → USB → Import**, com o GP-100 Edits
atualizado. Se ainda falhar, abra uma issue com o template de bug ([`bug_report.yml`](.github/ISSUE_TEMPLATE/bug_report.yml))
informando o nome do patch e a versão de firmware.

**O som não ficou igual ao disco. O patch está errado?**
Provavelmente não — e a diferença costuma ter causa identificável. Compare o
**captador** (cada patch documenta o perfil: bridge, neck, posições 2–4), o **volume e
o tone da guitarra**, a **técnica** (palhetada, posição da mão) e o **monitor**: fone e
monitor de estúdio mostram um som bem mais aberto que um amp real acima do volume de
ensaio. Só depois disso a diferença é do patch.

**Onde estão os arquivos `.prst`?**
Em `patches/<Banda>/<Álbum>/<Música>/<PATCH>/`. Para achar rápido pela música, use o
mapa por álbum (`MAPA-DO-ALBUM.md`) ou a [biblioteca completa](patches/README.md), que
lista os 97 patches com nome, captador, IR recomendada e slot.

**Os patches servem para outra pedaleira?**
Não. O formato é o XML single da GP-100, com os modelos e ranges do firmware **2.0/2.1**.
A documentação (`patch.md`) é útil como receita de timbre em qualquer plataforma, mas o
`.prst` só importa na GP-100.

**Preciso do banco de IRs que você indexou?**
Não é obrigatório — e ele **não está no repositório**, por licença. Os catálogos
(`data/ir-library.json` e `reference/16-ir-library.md`) ficam versionados e continuam
dizendo qual arquivo exato usar. O fluxo de download está em
[`impulse_responses/README.md`](impulse_responses/README.md).

**Por que os patches são por música e não compartilhados?**
Porque o ponto do projeto é o timbre **daquela faixa**: divisões de amplificador,
pedais e captadores mudam de música para música, e até entre camadas da mesma música.
Um patch "genérico de Pink Floyd" não tem a informação que faz a diferença.

**O que é "momento de toggle"?**
É a instrução de ligar/desligar um módulo **em tempo real** (painel ou modo STOMP)
durante a música — por exemplo, um patch de base com DLY sobressalente vira solo ao
ligar o eco, sem trocar de patch. Os momentos vivem em `doc.momentos` no
`data/defs/` e são validados pela camada e2e da suíte (momentos).

**O projeto tem dependências?**
Não. Os scripts usam só a biblioteca padrão do Python; o TypeScript dos agentes é baixado
sob demanda pelo `npx` no typecheck. Isso é uma decisão consciente — e é também por isso
que as Actions são praticamente o único item que o Dependabot vigia.

**Posso usar os patches em show/gravação comercial?**
O código e a documentação são MIT (ver [`LICENSE`](LICENSE)). Nomes de artista, título de
música, marca e modelo são citados de forma **nominativa e descritiva**, e nada aqui é
afiliado ou endossado pelos fabricantes. Se você redistribuir os packs de IR, a licença
deles é que manda.

## 📚 Toda a documentação

| Documento | Conteúdo |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitetura em 1 página: camadas, estrutura, portões de qualidade |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | Setup com uv, comandos do dia a dia e as regras que o CI cobra |
| [`docs/decisions/`](docs/decisions/README.md) | **ADRs** 0001–0010: pacote/uv, camadas, CLI, UI, qualidade, CI, docs, agentes, governança, release |
| [`knowledge.md`](knowledge.md) | Regras de ouro e convenções que os agentes seguem |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Ambiente, pipeline obrigatório, Conventional Commits e o fluxo develop → main |
| [`SECURITY.md`](SECURITY.md) | Escopo de segurança, prazos de resposta e canal privado |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Contributor Covenant 2.1 |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de versões (gerado dos commits) |
| [`LICENSE`](LICENSE) | MIT (texto canônico, para detecção automática) |
| [`NOTICE.md`](NOTICE.md) | Escopo da licença: o que **não** é coberto (marcas, títulos, manual, packs de IR) |
| [`.agents/README.md`](.agents/README.md) | Arquitetura dos 19 agentes e como criar um novo |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Camadas do pacote e fluxo de dados do pipeline |
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
| [`reference/19-roadmap-v2.md`](reference/19-roadmap-v2.md) | Roadmap da v2.0: schema v2 do defs, CLI unificada, site estático e meta de 100+ patches |
| [`prompts/`](prompts/) | Fluxos prontos de pedido ao agente |
| [`patches/README.md`](patches/README.md) | Biblioteca completa + nomenclatura + mapas |

## 🤝 Contribuindo

Contribuições são bem-vindas — conteúdo (patch novo, música, álbum) e código
(scripts, agentes, docs). O ponto de partida é o [`CONTRIBUTING.md`](CONTRIBUTING.md),
e ele tem uma regra que muda tudo: **`patches/**` é saída de script**.

```bash
# Antes de abrir um PR, rode o que o CI roda:
uv run pytest

# Se você mexeu em dados, o pipeline (a suíte cuida do guarda de determinismo):
uv run gp100 build
```

Fluxo: **desenvolve na `develop`** (push direto, CI a cada push, Conventional Commit
que alimenta o [`CHANGELOG.md`](CHANGELOG.md)) e **release aprovada alimenta a
`main`** via PR `develop` → `main` (merge commit) com o portão
`🚦 Veredito do CI` verde. Nada de editar à mão arquivo gerado — a
[`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) traz o
checklist completo das invariantes do projeto.

Participando, você aceita o [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## 🔐 Segurança

**Não abra issue pública para vulnerabilidade.** Use o
[Security Advisory privado](https://github.com/lucascantarelli/gp-100-patch-architect/security/advisories/new)
— escopo, prazos e controles ativos estão no [`SECURITY.md`](SECURITY.md).

O que o repositório roda sozinho, a cada push, PR e semanalmente:

| Workflow | O que garante |
|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | Dados em sincronia + 256 testes + typecheck dos agentes (Python 3.14 fixado e travado no job) |
| [`security.yml`](.github/workflows/security.yml) | CodeQL (Python e TypeScript), revisão de dependências em PR e auditoria de permissões dos próprios workflows |
| [`release.yml`](.github/workflows/release.yml) | Release **automática no merge para a `main`**: tag SemVer a partir do `VERSION` e ZIPs publicados |

Além disso: secret scanning com **push protection**, alertas e correções
automáticas do Dependabot, e branch protection na `main` (aplicável com
[`setup_repo.sh`](setup_repo.sh)).

## 📄 Licença

[MIT](LICENSE) — código, scripts, agentes, documentação e os `.prst` gerados por
este projeto. **Não** são cobertos: marcas e modelos de equipamento, nomes de
artistas e títulos de músicas (citados de forma nominativa e descritiva), o manual
da Valeton e os packs de IR de terceiros — que por isso **não** são versionados
aqui. Nada neste repositório é afiliado ou endossado pelos fabricantes citados.
O detalhamento de cada caso está em [`NOTICE.md`](NOTICE.md).

---

[`🎸 Biblioteca de patches`](patches/README.md) · [`🤖 Agentes`](.agents/) · [`📚 Reference`](reference/) · [`💜 Criar conta no Freebuff`](https://freebuff.com/?ref=ref-58064aca-e945-42d4-a383-e5f26ce7beaf)
