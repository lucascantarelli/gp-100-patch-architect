# 🌪️ OEOD01SL
### One of These Days — Slide/Ruído
##### Pink Floyd · Pulse (live) (1995)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Slide/Ruído-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Abertura instrumental: slide com delay longo + tempestade de ruído**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: SELETOR 1 · Volume 9 · Tone 8**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 1 (bridge) |
| **Volume** | 9 |
| **Tone** | 8 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Slide na 4ª/5ª corda com o delay fazendo o padrão
2. Deixe o delay criar o ciclo

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U42** (seção 8).
> 3. Toque *slide e tempestade de ruído* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| delay embolando | Fdbk -8 |
| tempestade forte | RVB mix -8 |

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
| PRE | ⚪ OFF | `Boost` |
| DST | ⚪ OFF | `Blues OD` |
| AMP | **🔴 ON** | `Knights CL` |
| NR | ⚪ OFF | `Gate 1` |
| CAB | **🔴 ON** | `UK-LD 4x12` |
| EQ | ⚪ OFF | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | **🔴 ON** | `T-Echo` |
| RVB | **🔴 ON** | `Hall` |

### 🎭 Momentos desta música

Este patch foi afinado para **um** papel — use os sobressalentes da tabela acima para variar na hora (ex.: desligar o DLY para uma seção seca). Momentos dedicados estão nos patches irmãos da mesma música (veja o mapa do álbum).

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Abertura instrumental: slide com delay longo + tempestade de ruído.

Abertura instrumental: slide com delay longo e a tempestade de ruído.

**Teste recomendado**: slide e tempestade de ruído · **Drum**: Instrumental 110 BPM

**Como saber que está certo**:

- ☑️ slide flutuando no delay
- ☑️ tempestade controlada

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Slide com delay + tempestade de ruído (não há base de acordes) | alta | Pulse (1995) · gilmourish.com |
| Rig 1994: Hiwatt DR103 + Alembic F-2B + WEM/Marshall 4x12 + pedalboard completo | alta | gilmourish.com — Division Bell Tour |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| ~~⚪~~ PRE | ~~⚪~~ DST | **🔴** AMP · Knights CL | ~~⚪~~ NR | **🔴** CAB · UK-LD 4x12 | ~~⚪~~ EQ | ~~⚪~~ MOD | **🔴** DLY · T-Echo | **🔴** RVB · Hall |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| AMP | Knights CL | Gain: 42 · Vol: 62 · Bass: 62 · Middle: 48 · Treble: 52 · p5: 58 |
| CAB | UK-LD 4x12 | Level: 78 · High Cut: 62 |
| DLY | T-Echo | p0: 30 · p1: 480 · p2: 20 |
| RVB | Hall | Decay*: 55 · Pre-D*: 50 · Damp*: 50 · Mix*: 1 |

### Mapeamento rig real → GP-100

- Hiwatt® DR103 + Alembic F-2B (limpo, aberto, dinâmico) → `Knights CL`
- Pilha 4x12 Marshall da turnê (Greenbacks; papel do WEM/Fane) → `UK-LD 4x12`
- O efeito Binson Echorec das jams espaciais → `T-Echo`
- Hall etéreo das seções lentas → `Hall`

### Parâmetros módulo a módulo

### AMP — Knights CL

| Parâmetro | Valor |
|---|---|
| Gain | 42 |
| Vol | 62 |
| Bass | 62 |
| Middle | 48 |
| Treble | 52 |
| p5 | 58 |

### CAB — UK-LD 4x12

| Parâmetro | Valor |
|---|---|
| Level | 78 |
| High Cut | 62 |

### DLY — T-Echo

| Parâmetro | Valor |
|---|---|
| p0 | 30 |
| p1 | 480 |
| p2 | 20 |

### RVB — Hall

| Parâmetro | Valor |
|---|---|
| Decay* | 55 |
| Pre-D* | 50 |
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

**Nome no painel**: `OEOD01SL` · **Slot sugerido**: **U42**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U42**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**AMP** `Knights CL` (Gain 42 / Vol 62 / Bass 62 / Middle 48 / Treble 52 / p5 58) → **CAB** `UK-LD 4x12` (Level 78 / High Cut 62) → **DLY** `T-Echo` (p0 30 / p1 480 / p2 20) → **RVB** `Hall` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `OEOD01SL`.

---

## 🚫 9. Evite com este patch

- ⛔ Tocar riffs de acordes: a música é slide e ambiente

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
