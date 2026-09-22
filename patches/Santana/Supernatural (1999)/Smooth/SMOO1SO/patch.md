# 🎺 SMOO1SO
### Smooth — Solo
##### Santana · Supernatural (1999)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Solo-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Solo lead: Soldano denso e cantável sobre gabinete Mesa — o sustain infinito que faz a guitarra 'cantar' por cima do vocal do Rob Thomas**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: SELETOR 1 · Volume 10 · Tone 8 — VINTE segundos de solo: frases que começam e não param**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 1 (bridge humbucker) — sustain e mordida |
| **Volume** | 10 |
| **Tone** | 8 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Frases longas com vibrato de dedo largo (não de tremolo)
2. Puxe a escala de Am com bends até a 12ª casa — deixe a nota CHORAR antes de resolver

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U65** (seção 8).
> 3. Toque *solo de Am pentatônica menor com frases longas* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| granulado/áspero | Yellow OD Gain -4 |
| agudo piante | EQ High -2 |
| falta corte | Solo100 LD PRSE +4 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`Mess-D 4x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 🔍 Não há captura melhor no nosso banco para este alvo

O CAB de fábrica `Mess-D 4x12` **já é a representação correta** deste alvo — nenhum gabinete do banco casa melhor (o catálogo local é consultado em `reference/16-ir-library.md`).

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Ambos valem aqui: Modern Boutique 4x12 Medium Mix (User IR 4) para o recorte de mesa de gravação, ou fique no Mess-D de fábrica (o mapa registra as duas rotas).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `COMP` |
| DST | **🔴 ON** | `Yellow OD` |
| AMP | **🔴 ON** | `Solo100 LD` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `Mess-D 4x12` |
| EQ | **🔴 ON** | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | **🔴 ON** | `Sweet` |
| RVB | **🔴 ON** | `Plate` |

### 🎭 Momentos desta música (validados para este patch)

Mude SÓ os módulos indicados — o resto permanece como na tabela acima:

1. **Ponte espessa (dobro)** — **MOD → ON**
   *Quando*: Na ponte, o chorus dá o dobro de estúdio da gravação.
   *Dica*: Religue para o solo seco.

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Solo lead: Soldano denso e cantável sobre gabinete Mesa — o sustain infinito que faz a guitarra 'cantar' por cima do vocal do Rob Thomas.

Santana com Rob Thomas: groove de Am–D, riff festonado sobre o groove de timba e o solo mais radioativo da década — o tom 'gordo e liso' da PRS na Mesa.

**Teste recomendado**: solo de Am pentatônica menor com frases longas · **Drum**: Solo 112 BPM

**Como saber que está certo**:

- ☑️ sustain infinito nas notas presas
- ☑️ midrange cantável (a assinatura Santana)
- ☑️ legato liso, sem granulado

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Guitarra: PRS Santana signature — humbuckers gordos, sustain longo | alta | guitarchalk.com — 'Amp Settings for Smooth' (PRS Santana + Mesa) |
| Amp: Mesa/Boogie — o Mark I é o clássico dele desde Woodstock; gain moderado | alta | guitarchalk.com · tonesmatch.com — Smooth riff tone |
| Groove: riff festonado em Am–D sobre percussão afro (timba/conga) | alta | Supernatural (1999), Arista · Wikipedia |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| **🔴** PRE · COMP | **🔴** DST · Yellow OD | **🔴** AMP · Solo100 LD | **🔴** NR · Gate 1 | **🔴** CAB · Mess-D 4x12 | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | **🔴** DLY · Sweet | **🔴** RVB · Plate |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | COMP | Sens: 25 · Attack: 40 · Sustain: 50 |
| DST | Yellow OD | Gain: 48 · Tone: 83 · Level: 55 |
| AMP | Solo100 LD | Vol: 46 · PRSE: 52 · Master: 62 · Bass: 55 · Middle: 58 · Treble: 62 |
| NR | Gate 1 | Thr: 28 |
| CAB | Mess-D 4x12 | Level: 85 · High Cut: 80 |
| EQ | EQ 1 | Low: 2 · Mid: 3 · High: -1 · Mid Freq: 5 · Presença: 5 · Level: 50 |
| DLY | Sweet | Mix: 20 · Time: 420 ms · Fdbk: 24 |
| RVB | Plate | Mix: 30 · Decay: 40 · H-Damp: 50 · Trail: On |

### Mapeamento rig real → GP-100

- Overdrive amarelo empurrando o amp (o corte do groove) → `Yellow OD`
- Soldano® SLO-100 (lead denso e cantável) → `Solo100 LD`
- Controle de hum (single coils + ganho) → `Gate 1`
- Gabinete Mesa/Boogie® Rectifier 4x12 → `Mess-D 4x12`
- Esculpir o som para fone/PC → `EQ 1`
- Delay com 1 repetição na duração da nota (assinatura do solo de Gilmour) → `Sweet`
- Plate de estúdio ("splash" da faixa) → `Plate`

### Parâmetros módulo a módulo

### PRE — COMP

| Parâmetro | Valor |
|---|---|
| Sens | 25 |
| Attack | 40 |
| Sustain | 50 |

### DST — Yellow OD

| Parâmetro | Valor |
|---|---|
| Gain | 48 |
| Tone | 83 |
| Level | 55 |

### AMP — Solo100 LD

| Parâmetro | Valor |
|---|---|
| Vol | 46 |
| PRSE | 52 |
| Master | 62 |
| Bass | 55 |
| Middle | 58 |
| Treble | 62 |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 28 |

### CAB — Mess-D 4x12

| Parâmetro | Valor |
|---|---|
| Level | 85 |
| High Cut | 80 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | 2 |
| Mid | 3 |
| High | -1 |
| Mid Freq | 5 |
| Presença | 5 |
| Level | 50 |

### DLY — Sweet

| Parâmetro | Valor |
|---|---|
| Mix | 20 |
| Time | 420 ms |
| Fdbk | 24 |

### RVB — Plate

| Parâmetro | Valor |
|---|---|
| Mix | 30 |
| Decay | 40 |
| H-Damp | 50 |
| Trail | On |


### Globais da sessão

| Item | Valor |
|---|---|
| MASTER VOLUME | 65% fixo — não compensar nível por aqui |
| Afinador | A ≈ 442 Hz (discos da época correm acima de A440) |
| USB/Saída | 44,1 kHz · driver ASIO no Windows |
| Fones | saída PHONE (monitores) |

> *RVB (*): valores na escala interna do firmware — o `.prst` carrega o template de fábrica; ajuste fino de reverb é feito no painel conforme o descrito na seção 3.*

---

## 💾 8. Carregar na pedaleira

**Nome no painel**: `SMOO1SO` · **Slot sugerido**: **U65**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U65**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `COMP` (Sens 25 / Attack 40 / Sustain 50) → **DST** `Yellow OD` (Gain 48 / Tone 83 / Level 55) → **AMP** `Solo100 LD` (Vol 46 / PRSE 52 / Master 62 / Bass 55 / Middle 58 / Treble 62) → **NR** `Gate 1` (Thr 28) → **CAB** `Mess-D 4x12` (Level 85 / High Cut 80) → **EQ** `EQ 1` (Low 2 / Mid 3 / High -1 / Mid Freq 5 / Presença 5 / Level 50) → **DLY** `Sweet` (Mix 20 / Time 420 ms / Fdbk 24) → **RVB** `Plate` (ajuste fino no painel — seção 3 📡) → SOBRESSALENTE **MOD** `A-Chorus` (template de fábrica — ajuste por orelha ao ligar)
```

3. **SAVE** no slot → renomeie para `SMOO1SO`.

---

## 🚫 9. Evite com este patch

- ⛔ Delay longo: o eco do solo é curto e discreto
- ⛔ Distorção extra no DST: o sustain já vem do amp + sustain do dedo

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
