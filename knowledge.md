# Valeton GP-100 Patch Agent — Conhecimento do Projeto

## Missão
Este repositório abriga um agente especialista em **criação de patches para a pedaleira Valeton GP-100**, com saída documentada em Markdown e valores 100% oficiais (nomes e ranges extraídos do `manual.pdf`, firmware V1.8).

## Contexto do músico (fixo do projeto)
- **Guitarra**: Squier Stratocaster, 3 single coils, potes 250k, ligada DIRETO na GP-100 (sem pedals no meio).
- **Caminho de áudio**: guitarra → GP-100 → saída para o PC (gravação/análise, USB ou L/R) + fones monitores na saída PHONE.
- Implicações de timbre: som brilhante, dinâmica alta, menos ganho natural que humbuckers, ruído audível com drive alto → sempre considerar NR em ganho alto e Treble moderado.

## Estrutura do repositório
```
knowledge.md           ← este arquivo
manual.pdf             ← manual oficial V1.8 (digitalizado; páginas sob demanda: python tools/render_manual_page.py <impressa>)
reference/             ← BASE DE DADOS OFICIAL (ler antes de criar qualquer patch)
  15-firmware2-effects.md ← CATÁLOGO REAL do firmware 2.0/2.1 (prevalece sobre 01–09 em nomes)
  16-ir-library.md     ← catálogo da biblioteca local de IRs (gerado por tools/ir_library.py)
  17-free-ir-packs.md  ← catálogo de packs gratuitos com links p/ ampliar impulse_responses/
  00-signal-chain.md   ← cadeia, painel, fluxo de edição
  01-pre.md … 09-rvb.md ← estratégia/receitas por módulo (nomes conforme fw 2.0 em 15)
  10-globals.md        ← master, EXP, tuner, looper, USB, save
  11-ir-guide.md       ← estratégia de IRs gratuitas e ajuste
  12-workflow.md       ← metodologia, checklist, troubleshooting
  13-preset-list.md    ← presets de fábrica + 100 drum patterns
  14-glossario.md      ← tradução nome-comum → nome-oficial GP-100
.agents/               ← 17 agentes Freebuff/Codebuff (orchestrador + skills + validador + manual + tone-research/mapper)
tools/                 ← build_song_patches.py (gera patches por música) · generate_prst.py (gera .prst single) · gen_indexes.py (regenera índices) · ir_library.py (indexa IRs) · render_manual_page.py (páginas do manual sob demanda) · analyze_prst.py (disseca exports) · build_release.py (empacota os ZIPs) · gen_changelog.py (gera o CHANGELOG) · migrate_defs_v2.py (migração v1→v2 one-shot) · defs/ (_albums.json + um JSON por álbum = FONTE DOS PATCHES, schema v2)
prompts/               ← templates de pedido do usuário (fonte canônica dos fluxos)
.agents/skills/        ← skills versionadas (4 do GP-100 = versão executável dos fluxos + 7 genéricas)
patches/               ← biblioteca (SAÍDA DE SCRIPT, nunca editar à mão): BANDA/ÁLBUM/MÚSICA/MUSICA-CAMADA com patch.md + .prst
impulse_responses/     ← BIBLIOTECA LOCAL DE IRs (1 pasta por pack; os agentes consultam o catálogo 16)
```

## Regras de ouro (resumo executivo)
0. **Firmware 2.0**: os nomes reais dos efeitos estão em `reference/15-firmware2-effects.md` (catálogo empírico extraído do export de fábrica do próprio aparelho; dados brutos em `tools/factory-catalog.json`). Nomes do manual V1.8 que divergem (ex.: manual `T-S OD` → real `Green OD`; manual `Dark Twin` cab → real `DarkTW 2x12`) NÃO devem ser usados na saída final.
1. **Nomes**: só use os nomes exatos da GP-100 (ver `reference/14-glossario.md` para traduzir pedidos; a saída final usa os nomes do catálogo fw 2.0).
2. **Ranges**: todo valor deve estar dentro do range oficial do parâmetro (ver tabelas em `reference/`).
3. **Cadeia fixa**: PRE→DST→AMP→NR→CAB→EQ→MOD→DLY→RVB — não reordenar (a GP-100 não permite). Modelos PRE válidos: catálogo fw 2.0 (reference/15) — incluindo **`Saturate`** (o equivalente do Tube Driver do Gilmour; template cadastrado em `generate_prst.py` pois não há exemplo no export de fábrica). NUNCA use `Tube Clipper` no PRE (é modelo DST).
4. **Perfis por captador**: bridge = baixar Gain ~5; neck = subir Treble ~5, baixar Bass ~5.
5. **Hi-gain**: NR sempre ON (Thr -38, Rel 50 como startpoint).
6. **Volume equilibrado**: Level de efeitos ≈ bypass; jamais compensar patch com MASTER VOLUME.
7. **Espacial**: um "grande" só (DLY ou RVB dominante).
8. **Documentação e nomenclatura (REGRA CENTRAL)**: patches são por MÚSICA, nunca compartilhados entre faixas — `patches/<Banda>/<Álbum>/<Música>/<MUSICA-CAMADA>/`. **Pedido por ÁLBUM = TODAS as faixas** (padrão desde o Pulse): cada música com suas camadas, num fragmento próprio (`tools/defs/<CHAVE>.json` + a chave em `_albums.json`). Nome no painel = MÚSICA(≤4 letras)+versão(2 dígitos)+CAMADA(2 letras), máx. 12 chars: BA=base, SO=solo, RI=riff, CL=clean, FL=fills, AR=arpejos, AC=acústico, VO=voz-líder (ex.: `STH01BA`, `CT01RIF`, `PMH01SO`). Só há mais de um patch por música quando o timbre muda de verdade entre seções. Fonte única: `tools/defs/` (schema v2) → regenerar com `python tools/build_song_patches.py` e `python tools/gen_indexes.py`. **Nenhum script mantém tabela própria de músicas, álbuns, pastas ou cabs**: `albums` (banda/ano/pasta/título/dossiê), `ir_local` e o `pasta`/`display` de cada música vivem SÓ no defs. Foi a duplicação dessas tabelas que fez o mapa do álbum recomendar "fábrica" enquanto o `patch.md` mandava carregar uma IR do banco nos 38 patches do Pulse. **Nenhum agente nem pessoa escreve arquivos em `patches/**`** (os derivados nem são versionados — ADR-0013): projeta-se o patch no defs e o pipeline publica (patch.md, .prst e índices).
9. **TOGGLE / MODOS DE ATUAÇÃO (obrigatório em todo patch, seção após a IR)**: a GP-100 liga/desliga qualquer módulo em TEMPO REAL — painel slot a slot (ON/OFF) ou footswitches FS-A/FS-B no modo STOMP (SYSTEM → Mode → Stomp) — e desligar NÃO apaga parâmetros (religou, som intacto). Sempre: (1) documente o estado de fábrica dos 9 módulos; (2) defina MOMENTOS da música alternando módulos cujo estado pedido é o INVERSO do atual (ex.: base com DLY OFF → liga o eco no solo; solo com RVB OFF → desliga para seções secas); (3) módulo OFF com modelo escolhido = "pedal sobressalente"; (4) NUNCA toggle de AMP/CAB (volume/corpo); (5) um patch bem feito cobre a música inteira com 1–3 momentos — camada extra só quando o timbre-base também muda; (6) desde a #9, o patch pode declarar **stomps dedicados** (`doc.stomps`: `fs` A/B/A+B, `mods` invertendo o estado de fábrica, `quando` — o validador reprova atribuição que não faria nada em palco) e o **pedal de expressão** (`spec.exp1`: `{'módulo', 'param', 'min'?, 'max'?}` — o `.prst` já nasce com o EXP1 amarrado ao parâmetro, com nome oficial do PARAM_NAMES e curso 0–99).
10. **IRs — POLÍTICA DE 4 PASSOS (obrigatória em todo patch)**: (1) **FÁBRICA**: o `.prst` sempre sai com o CAB de fábrica — funciona imediatamente, sem carregar nada. (2) **BANCO LOCAL**: se `impulse_responses/` tem captura do gabinete REAL do rig, o patch.md recomenda o arquivo exato + slot User IR (confira `reference/16-ir-library.md`; atual = Origin Effects IR-Cab Library V3). (3) **INTERNET**: se nem fábrica nem banco cobrem o alvo, pesquise IRs gratuitas (catálogo `reference/17-free-ir-packs.md`) e indique o link no patch.md — o usuário baixa em `impulse_responses/<Pack>/` e reindexa com `python tools/ir_library.py`. (4) **FALLBACK**: mantenha o CAB de fábrica (o patch foi afinado com ele). Máx. 1 IR por patch; slots no device: **User IR 1–20** (wav 44,1 kHz/24 bits/mono, aparar >1024 samples; use a pasta 44.1 kHz do pack). A DOCUMENTAÇÃO SEMPRE tem uma seção exclusiva de IR (📡, após os ajustes finos) explicando os 4 passos — nunca omita, mesmo quando a resposta é "fábrica já é o alvo". No `.prst`, CAB sai de fábrica; variante `-USERIR` (experimental, `ir_cab_user_slot`) só com teste no device.
11. **Validação**: rodar o patch pelo `gp100-patch-validator` antes de entregar.
12. **Runtime Python 3.14 apenas** — os scripts exigem 3.14 (guarda nos entry points via `defs_schema`; CI fixado em 3.14 nos três workflows). Não abra exceção para versões antigas.
12a. **Testes e dados em sincronia (obrigatório antes de entregar qualquer mudança)**: `python -m unittest discover -s tests -v` — a suíte valida o formato `.prst` single fw 2.1, as 9 seções da doc, os momentos de toggle, a coerência mapa × `patch.md` sobre IR, a cobertura de nomes de parâmetro, o drift dos índices e o **guarda de determinismo**: o `TestH` roda o pipeline inteiro numa cópia temporária do repositório e reprova se o resultado divergir dos derivados existentes (ignorando só o `preset_info/@time`) — num clone limpo (CI) prova que o defs determina a biblioteca inteira (`patches/**` não é commitado, ADR-0013); na sua máquina, pega "editei o defs e esqueci de regenerar" e hand-edit em arquivo gerado. **Dado gerado nunca vai "de mão": se você acrescentou música, camada, patch, efeito, momento de toggle ou pack de IR, rode o pipeline** — `python tools/ir_library.py` → `python tools/build_song_patches.py` → `python tools/gen_indexes.py` (sem seeders desde o schema v2, issue #8: um álbum novo entra como fragmento em `tools/defs/`). O CI (`.github/workflows/ci.yml`) roda a cada push/PR em **dois jobs paralelos** — **`test-suite`** (compile + build dos derivados + suíte, incluindo o guarda de determinismo; nenhum job escreve no repositório) e **`typecheck`** (`tsc --noEmit`) — seguidos do portão **`ci-gate`**, que reprova se qualquer um falhar.
13. **Ordem estável entre sistemas**: nunca ordene `Path` direto (`sorted(rglob(...))`) — `Path` compara com `normcase`, que **minúsculas no Windows** e é identidade no Linux; foi assim que o `ir-library.json` saiu diferente na máquina e no CI. Ordene por chave de **string** (`.relative_to(...).as_posix()`). Teste: `TestI_OrdemEstavel`.

13. **NOMES DE PARÂMETRO E SLOTS INTERNOS (nunca invente um nome)**: a fonte primária é o **manual oficial do firmware V2.0** (valeton.net) — tabela pronta em `reference/15-firmware2-effects.md`: `Saturate` = Gain/Mix/Output/H-Cut · `Red Haze` = Fuzz/VOL · família DLY = **Mix/Time/Fdbk** · RVB começa por **Mix** (`Room`/`Hall`/`Church` = Mix/Pre Delay/Decay/Trail; `Plate` = Mix/Decay/H-Damp/Trail; `Spring` = Mix/Decay) · `Vibe` = Depth/Rate/Sync · `Knights CL` = Gain/VOL/Bass/Middle/Treble · `Flagman` = Gain/PRES/Master/Bass/Middle/Treble. O array `params_0..14` segue a ordem documentada e **depois** traz slots **INTERNOS** que o editor não expõe (≈50 nos presets de fábrica; ex.: `Flagman` 7 slots para 6 knobs, `Knights CL` 6/5, `Vibe` 4/3, `Red Haze` 3/2, `Spring` 4/2+Trail). Slot interno **não é parâmetro do usuário**: não sete no spec e não rotule na doc. **Exceção documentada**: `T-Echo` — `params_1` é o **Time** (415 ms nos presets de fábrica; Fdbk é 0~99), ou seja a linha do manual trocou Fdbk/Time; a família inteira é Mix/Time/Fdbk. A suíte reprova rótulo `pN` (`TestD_Documentacao`) e modelo em uso sem tabela de nomes (`TestF_ParamNames`, allowlist hoje vazia).

## Como o usuário pede patches (fluxo Freebuff/Codebuff)
- Interativo: `@gp100-patch-architect quero um patch de blues com delay pra tocar com backing em casa`
- Por referência de artista/música: `@gp100-patch-architect` + `prompts/pesquisar-referencia.md` — dispara gp100-tone-research (pesquisa web dos equipamentos reais) → gp100-tone-mapper (traduz para modelos GP-100) → patch final
- Direto por categoria: `@gp100-overdrive-distortion sugira drive para indie com Strat`
- Ajuste de patch existente: apontar a pasta em `patches/` e descrever o que sentiu.

## Convenções de resposta ao usuário
- Responder em português (idioma do projeto).
- Sempre mostrar a cadeia em uma linha + tabela de parâmetros por módulo.
- Indicar captador sugerido da Strat e o teste recomendado (riff + o que escutar).
- Arquivos gerados: caminho completo a partir da raiz do projeto.
