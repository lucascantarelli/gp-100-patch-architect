# 🌍 Packs de IR gratuitos — links de download para ampliar a biblioteca

> **Mantido por** `gp100-ir-research` · Última varredura: 2026-09-19.
> **Regra**: baixar em `impulse_responses/<Nome do Pack>/` e reindexar com `python tools/ir_library.py`.
> **Formato-alvo GP-100**: wav mono · 24 bits · 44,1 kHz · ≤ 1024 samples (converta se necessário).
> **Prioridade**: preencher o que a biblioteca atual **não tem** (ver lacunas ao final).

## 🎸 Cabes de guitarra (gaps da biblioteca atual)

| Pack | O que traz | Formato | Licença | Link |
|---|---|---|---|---|
| **Celestion — Cenzo Townshend IR Mix** | V30 em 1x12 fechado + blend Royer/SM57 + room Neumann — polido, mix-ready | ZIP multi-formato (escolher mono) | Gratuita (cadastro) | [celestionplus.com/free-download](https://www.celestionplus.com/free-download/) |
| **Bogren Digital — Free IR Pack** | 6 IRs Mix-finished™ de coleções Jens Bogren/Tue Madsen — metal moderno/downtuned | WAV multi-taxa | Gratuita (e-mail) | [bogrendigital.com/pages/free-ir-pack](https://bogrendigital.com/pages/free-ir-pack) |
| **ML Sound Lab — Free Premium IR** | Mesa Traditional 4x12, SM57 + R121 — V30 agressivo | 48 kHz/24-bit/200 ms → converter p/ 44.1 | Gratuita | [ml-sound-lab.com/pages/free-premium-ir](https://ml-sound-lab.com/pages/free-premium-ir) |
| **PreSonus — 25 Analog Cab IRs (Craig Anderton)** | 25 cabes "analógicos" (EQ-based) dos cabes do Ampire — caráter gordo, responde bem a EQ | **1024 samples exatos** ✓ · 48 kHz/24-bit/mono → só resamplear | Gratuita | [presonus.com/blogs/home/free-download-25-analog-cab-irs](https://www.presonus.com/blogs/home/free-download-25-analog-cab-irs) |
| **Zach Weeks — TL806 & Basement 1960B** | 4x12 clássicos (TL806 e 1960B) gravados de forma independente | WAV (bandcamp nome-seu-preço/0) | Gratuita | [zachweeks.bandcamp.com](https://zachweeks.bandcamp.com/album/tl806-and-basement-1960b-guitar-cab-impulse-responses) |
| **Henry Olonga — Amps Bundle Community Edition** | Coleção ampla de amp+cab em alta resolução | ZIP WAV | Gratuita | [nebulapresets.com](http://www.nebulapresets.com/Henry_Olonga_ULTRA_HiRes_Amp_Models_VOL_1.zip) |
| **Tone Junkie — Free IR Pack** | Seleção de cabes da loja (usado na cena Helix; conferir se inclui WAV) | variável | Gratuita (e-mail) | [tonejunkiestore.com/tone-junkie-ir-free-pack](https://tonejunkiestore.com/tone-junkie-ir-free-pack) |
| **Studio Nord Bremen — Amps** | IRs de amps/cabes vintage (grgr.de) | WAV | Gratuita | [grgr.de/IR](http://www.grgr.de/IR/) |

## 🔊 Baixo (nenhum na biblioteca ainda)

| Pack | O que traz | Formato | Licença | Link |
|---|---|---|---|---|
| **Shift Line — Bass HD IR Pack** | 80 IRs (20 cabes de baixo × 4 variantes) | WAV | Gratuita | [shift-line.com/basshdirpack](https://shift-line.com/basshdirpack) |

## 🛠️ Utilitários (converter/aparar IRs p/ GP-100)

| Ferramenta | Para quê | Link |
|---|---|---|
| **IR Workshop** (Windows, grátis) | mixar, **truncar ≤1024 samples**, converter taxa/mono, EQ de IR | [github.com/ValdemarOrn/IRWorkshop](https://github.com/ValdemarOrn/IRWorkshop) |
| **Darwin's Cat — Cabinet IR Utility** | editor/conversor **no navegador**, sem cadastro | [darwinscat.com/sound-utils/cabinet-ir-utility](https://darwinscat.com/sound-utils/cabinet-ir-utility) |

## 🚫 Categoria fora de escopo (não usar como CAB)

- IRs de **salas/reverbs** (OpenAIR, Echothief, Fokke van Saane, PastToFuture…) — a GP-100 usa o RVB interno e o CAB espera IR de gabinete curta; IR de sala soaria como reverb embolado no bloco CAB.

## 📌 Lacunas da biblioteca atual (Origin Effects V3 = vintage americano/inglês)

1. **Metal moderno / V30 4x12 agressivo** → resolver com Bogren ou ML Sound Lab.
2. **V30 polido 1x12 mix-ready** → Celestion Cenzo.
3. **Cabes de baixo** → Shift Line.
4. **Variações "analógicas"** → PreSonus (extremamente fácil: já tem 1024 samples).
5. **Hiwatt/WEM 4x12 (Fane)** — o gabinete real do Pink Floyd (Gilmour): packs **pagos** de referência são Dr. Bonkers (Hiwatt SE4123 Fane) e York Audio WEM Starfinder; **grátis**, teste o **Tone Junkie free pack** e o **Shift Line Guitar HD IR Pack 1** (10 gabinetes britânicos, grátis). Enquanto não houver captura local, os patches do Pulse usam o CAB de fábrica `UK-LD 4x12` (Marshall 4x12 — parente mais próximo no device) ou a IR `British Straight 4x12` do banco Origin (User IR 4).

## 📥 Fluxo de atualização

1. Baixar o pack → extrair dentro de `impulse_responses/<Nome do Pack>/` (manter a pasta 44.1 kHz como fonte preferida).
2. `python tools/ir_library.py` → reindexa e atualiza `reference/16-ir-library.md` + `tools/ir-library.json`.
3. Se algum WAV vier 48/96 kHz ou estéreo → converter (IR Workshop / Darwin's Cat) para 44,1 kHz/24-bit/mono antes de carregar no device.
4. Carregar no **User IR 1–20** via GP-100 Edits e anotar o slot no patch que usar.
