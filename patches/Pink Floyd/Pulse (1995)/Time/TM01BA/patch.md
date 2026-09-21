# ⏳ TM01BA
### Time — Base
##### Pink Floyd · Pulse (live) (1995)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Base-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-middle+bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Base do DSOTM: acordes com crunch suave — o relógio no fundo**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: SELETOR 2 · Volume 10 · Tone 9**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 2 (middle+bridge) |
| **Volume** | 10 |
| **Tone** | 9 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Acordes F#m7/A com palhetada marcada
2. Sincronize com os acordes do piano

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U46** (seção 8).
> 3. Toque *acordes dos versos e refrão* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| lamacento | CAB High Cut -5 |
| seco | RVB mix +5 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`UK-LD 4x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta

O banco local tem a captura **British Straight 4x12** — casamento direto com o gabinete real deste patch:

1. No **GP-100 Edits** → IR Manager, carregue no **User IR 4** o arquivo:
   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/British Straight 4x12/British Straight 4x12 Medium Mix.wav`
2. No patch: bloco CAB → troque `UK-LD 4x12` por **User IR 4**.
3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), **Level** comece em 0 e compare com o bypass.
   Alternativas do mesmo gabinete no banco: `British Straight 4x12 Bright Mix.wav`, `British Straight 4x12 Dark Mix.wav`, `British Straight 4x12 Bright 160.wav`, `British Straight 4x12 Bright 57.wav`, `British Straight 4x12 Dark 160.wav`, `British Straight 4x12 Dark 421.wav`, `British Straight 4x12 Dark 87.wav`, `British Straight 4x12 Medium 160.wav`, `British Straight 4x12 Medium 421.wav`.

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Recomendada: British Straight 4x12 Medium Mix (User IR 4) — o 4x12 britânico da pilha de 1994 (Low Cut 4 · High Cut 8500 · Level 0).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `Saturate` |
| DST | ⚪ OFF | `Blues OD` |
| AMP | **🔴 ON** | `Flagman` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `UK-LD 4x12` |
| EQ | ⚪ OFF | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | ⚪ OFF | `Sweet` |
| RVB | **🔴 ON** | `Plate` |

### 🎭 Momentos desta música (validados para este patch)

Mude SÓ os módulos indicados — o resto permanece como na tabela acima:

1. **Solo (eco curto)** — **DLY → ON**
   *Quando*: Para puxar frases do solo de Time na base, com o eco curto certo.

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Base do DSOTM: acordes com crunch suave — o relógio no fundo.

Solo de 'Time': TD + delay curto, bend de 1 tom e agressividade controlada — icônico.

**Teste recomendado**: acordes dos versos e refrão · **Drum**: DSOTM 121 BPM

**Como saber que está certo**:

- ☑️ crunch suave
- ☑️ boa definição nos graves

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Solo: Tube Driver + delay curto, bend 1 tom, vibrato largo | alta | Pulse (1995) · gilmourish.com |
| Rig 1994: Hiwatt DR103 + Alembic F-2B + WEM/Marshall 4x12 + pedalboard completo | alta | gilmourish.com — Division Bell Tour |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| **🔴** PRE · Saturate | ~~⚪~~ DST | **🔴** AMP · Flagman | **🔴** NR · Gate 1 | **🔴** CAB · UK-LD 4x12 | ~~⚪~~ EQ | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Plate |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | Saturate | p0: 32 · p1: 55 · p2: 60 |
| AMP | Flagman | Gain: 44 · PRSE: 55 · Master: 62 · Bass: 50 · Middle: 55 · Treble: 58 |
| NR | Gate 1 | Thr: 26 |
| CAB | UK-LD 4x12 | Level: 78 · High Cut: 62 |
| RVB | Plate | Decay*: 30 · Pre-D*: 40 · Damp*: 50 · Mix*: 1 |

### Mapeamento rig real → GP-100

- Hiwatt® DR103 da turnê de 1994 (clean potente com headroom) → `Flagman`
- Controle de hum (single coils + ganho) → `Gate 1`
- Pilha 4x12 Marshall da turnê (Greenbacks; papel do WEM/Fane) → `UK-LD 4x12`
- Plate de estúdio ("splash" da faixa) → `Plate`

### Parâmetros módulo a módulo

### PRE — Saturate

| Parâmetro | Valor |
|---|---|
| p0 | 32 |
| p1 | 55 |
| p2 | 60 |

### AMP — Flagman

| Parâmetro | Valor |
|---|---|
| Gain | 44 |
| PRSE | 55 |
| Master | 62 |
| Bass | 50 |
| Middle | 55 |
| Treble | 58 |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 26 |

### CAB — UK-LD 4x12

| Parâmetro | Valor |
|---|---|
| Level | 78 |
| High Cut | 62 |

### RVB — Plate

| Parâmetro | Valor |
|---|---|
| Decay* | 30 |
| Pre-D* | 40 |
| Damp* | 50 |
| Mix* | 1 |

> ℹ️ **`pN`** = slot de parâmetro deste modelo **sem nome oficial documentado** (o manual V1.8 só cobre os modelos antigos) — ajuste por orelha, comparando com o bypass; os demais nomes seguem o manual da GP-100.


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

**Nome no painel**: `TM01BA` · **Slot sugerido**: **U46**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U46**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `Saturate` (p0 32 / p1 55 / p2 60) → **AMP** `Flagman` (Gain 44 / PRSE 55 / Master 62 / Bass 50 / Middle 55 / Treble 58) → **NR** `Gate 1` (Thr 26) → **CAB** `UK-LD 4x12` (Level 78 / High Cut 62) → **RVB** `Plate` (ajuste fino no painel — seção 3 📡) → SOBRESSALENTE **DLY** `Sweet` (Fdbk 18 / Delay ms 380 / High Cut 24)
```

3. **SAVE** no slot → renomeie para `TM01BA`.

---

## 🚫 9. Evite com este patch

- ⛔ Crunch pesado no verso — leve e aberto

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
