# 🪘 SMOO1FL
### Smooth — Camada
##### Santana · Supernatural (1999)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Camada-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-middle+bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Camada percussiva/fills: clean crocante para dobrar o groove em outra passagem na gravação de casa**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: VOLUME 6-7 · Seletor 2 · Tone 7 — grava essa passagem como CAMADA, não como base**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 2 (middle+bridge) |
| **Volume** | 6-7 |
| **Tone** | 7 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Mute com a mão esquerda entre os fills (o 'trabalho' percussivo)
2. Dobre o riff do patch SMOO1RI com 2 compassos de diferença

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U97** (seção 8).
> 3. Toque *fills curtos e percussivos sobre o groove* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| sumir na mixagem | L-Star CL Vol +3 |
| crocante demais | L-Star CL Vol -3 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`L-Star 2x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta

O banco local tem a captura **Magma Vintage 1x12** — casamento direto com o gabinete real deste patch:

1. No **GP-100 Edits** → IR Manager, carregue no **User IR 6** o arquivo:
   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/Magma Vintage 1x12/Magma Vintage 1x12 Medium Mix.wav`
2. No patch: bloco CAB → troque `L-Star 2x12` por **User IR 6**.
3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), **Level** comece em 0 e compare com o bypass.
   Alternativas do mesmo gabinete no banco: `Magma Vintage 1x12 Bright Mix.wav`, `Magma Vintage 1x12 Dark Mix.wav`, `Magma Vintage 1x12 Bright 160.wav`, `Magma Vintage 1x12 Bright 421.wav`, `Magma Vintage 1x12 Bright 87.wav`, `Magma Vintage 1x12 Dark 160.wav`, `Magma Vintage 1x12 Dark 421.wav`, `Magma Vintage 1x12 Dark 87.wav`, `Magma Vintage 1x12 Medium 160.wav`, `Magma Vintage 1x12 Medium 421.wav`, `Magma Vintage 1x12 Medium 87.wav`.

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Recomendada: Magma Vintage 1x12 (User IR 6) — a alma vintage 1x12 do combo do Santana (Low Cut 5 · High Cut 8500 · Level 0).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `COMP` |
| DST | ⚪ OFF | `Blues OD` |
| AMP | **🔴 ON** | `L-Star CL` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `L-Star 2x12` |
| EQ | ⚪ OFF | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | **🔴 ON** | `Sweet` |
| RVB | **🔴 ON** | `Room` |

### 🎭 Momentos desta música (validados para este patch)

Mude SÓ os módulos indicados — o resto permanece como na tabela acima:

1. **Solo (lead herdado)** — **DST → ON**
   *Quando*: Religue o drive e o patch sobe para o território do solo.
   *Dica*: A camada religa o drive só em breaks.

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Camada percussiva/fills: clean crocante para dobrar o groove em outra passagem na gravação de casa.

Santana com Rob Thomas: groove de Am–D, riff festonado sobre o groove de timba e o solo mais radioativo da década — o tom 'gordo e liso' da PRS na Mesa.

**Teste recomendado**: fills curtos e percussivos sobre o groove · **Drum**: Camada 112 BPM

**Como saber que está certo**:

- ☑️ crocante e curto — preenche sem ocupar o lugar da base
- ☑️ ataque seco que 'bate' com a conga

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
| **🔴** PRE · COMP | ~~⚪~~ DST | **🔴** AMP · L-Star CL | **🔴** NR · Gate 1 | **🔴** CAB · L-Star 2x12 | ~~⚪~~ EQ | ~~⚪~~ MOD | **🔴** DLY · Sweet | **🔴** RVB · Room |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | COMP | Sens: 30 · Attack: 40 · Sustain: 50 |
| AMP | L-Star CL | Vol: 36 · PRSE: 50 · Master: 60 · Bass: 52 · Middle: 54 · Treble: 58 |
| NR | Gate 1 | Thr: 28 |
| CAB | L-Star 2x12 | Level: 62 · High Cut: 55 |
| DLY | Sweet | Mix: 15 · Time: 240 ms · Fdbk: 15 |
| RVB | Room | Mix: 22 · Pre Delay: 19 ms · Decay: 31 · Trail: Off |

### Mapeamento rig real → GP-100

- Mesa/Boogie® Lone Star™ — o "gordo e liso" do Santana → `L-Star CL`
- Controle de hum (single coils + ganho) → `Gate 1`
- Combo vintage 1x12 do Lone Star → `L-Star 2x12`
- Delay com 1 repetição na duração da nota (eco do solo) → `Sweet`
- Sala curta e seca — corpo curto que sustenta sem lambear → `Room`

### Parâmetros módulo a módulo

### PRE — COMP

| Parâmetro | Valor |
|---|---|
| Sens | 30 |
| Attack | 40 |
| Sustain | 50 |

### AMP — L-Star CL

| Parâmetro | Valor |
|---|---|
| Vol | 36 |
| PRSE | 50 |
| Master | 60 |
| Bass | 52 |
| Middle | 54 |
| Treble | 58 |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 28 |

### CAB — L-Star 2x12

| Parâmetro | Valor |
|---|---|
| Level | 62 |
| High Cut | 55 |

### DLY — Sweet

| Parâmetro | Valor |
|---|---|
| Mix | 15 |
| Time | 240 ms |
| Fdbk | 15 |

### RVB — Room

| Parâmetro | Valor |
|---|---|
| Mix | 22 |
| Pre Delay | 19 ms |
| Decay | 31 |
| Trail | Off |


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

**Nome no painel**: `SMOO1FL` · **Slot sugerido**: **U97**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U97**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `COMP` (Sens 30 / Attack 40 / Sustain 50) → **AMP** `L-Star CL` (Vol 36 / PRSE 50 / Master 60 / Bass 52 / Middle 54 / Treble 58) → **NR** `Gate 1` (Thr 28) → **CAB** `L-Star 2x12` (Level 62 / High Cut 55) → **DLY** `Sweet` (Mix 15 / Time 240 ms / Fdbk 15) → **RVB** `Room` (ajuste fino no painel — seção 3 📡) → SOBRESSALENTE **DST** `Blues OD` (Gain 55 / Tone 92 / Level 73)
```

3. **SAVE** no slot → renomeie para `SMOO1FL`.

---

## 🚫 9. Evite com este patch

- ⛔ Fills longos: esta camada é percussiva — frases de 1 ou 2 compassos

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
