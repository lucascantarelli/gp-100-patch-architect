# 🐊 CT01VOX
### Come Together — Voz-líder (solo/final)
##### The Beatles · Abbey Road (1969)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Voz-líder-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-neck-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Fraseados da guitarra do John respondendo a cada verso: mesma mesa derrapada, brilho e sustain um pouco maiores**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: Seletor 5 (neck) · Volume 8 · Tone 4–5**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 5 — neck (captador do braço) |
| **Volume** | 8 |
| **Tone** | 4–5 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Frases curtas respondendo o vocal — deixe silêncio entre elas
2. Nas notas longas, alivie o ataque para o sustain morrer junto com a frase

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U02** (seção 8).
> 3. Toque *'Come toge-ther, right now' + licks finais* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| sustain fraco | Boost p0 +5 |
| muito agudo | CAB High Cut 55 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`J-120 2x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 🔍 Não há captura melhor no nosso banco para este alvo

O CAB de fábrica `J-120 2x12` **já é a representação correta** deste alvo — nenhum gabinete do banco casa melhor (o catálogo local é consultado em `reference/16-ir-library.md`).

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Alvo = mesma mesa derrapada (sem cabine real) — mantenha o CAB de fábrica.


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `Boost` |
| DST | **🔴 ON** | `La Charger` |
| AMP | ⚪ OFF | `Dark Twin` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `J-120 2x12` |
| EQ | **🔴 ON** | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | ⚪ OFF | `Sweet` |
| RVB | **🔴 ON** | `Room` |

### 🎭 Momentos desta música

Este patch foi afinado para **um** papel — use os sobressalentes da tabela acima para variar na hora (ex.: desligar o DLY para uma seção seca). Momentos dedicados estão nos patches irmãos da mesma música (veja o mapa do álbum).

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Fraseados da guitarra do John respondendo a cada verso: mesma mesa derrapada, brilho e sustain um pouco maiores.

Riff de abertura do álbum: baixo de Paul e guitarra ríspida de John (Casino) gravada direto no canal da mesa, sem amp — o 'clipping de mesa' é o timbre.

**Teste recomendado**: 'Come toge-ther, right now' + licks finais · **Drum**: Rock 104 BPM

**Como saber que está certo**:

- ☑️ frase corta na altura do vocal
- ☑️ sustain curto mas presente

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Guitarra: Epiphone Casino (P90) de John, direto na mesa | alta | Guitar World — Abbey Road gear guide (Emerick) |
| Sem amplificador na guitarra do riff | alta | Guitar World / Emerick |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| **🔴** PRE · Boost | **🔴** DST · La Charger | ~~⚪~~ AMP | **🔴** NR · Gate 1 | **🔴** CAB · J-120 2x12 | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Room |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | Boost | Ganho: 22 · Boost: 1 |
| DST | La Charger | Gain: 32 · Tone: 52 · Volume: 62 |
| NR | Gate 1 | Thr: 28 |
| CAB | J-120 2x12 | Level: 75 · High Cut: 50 |
| EQ | EQ 1 | Low: -1 · Mid: 3 · High: -1 · Level: 50 |
| RVB | Room | Decay*: 20 · Pre-D*: 19 · Damp*: 31 · Mix*: 0 |

### Mapeamento rig real → GP-100

- Boost transparente na frente do amp (papel do "volume extra" do rig real) → `Boost`
- Clipping áspero de mesa (RAT-style) → `La Charger`
- Controle de hum (single coils + ganho) → `Gate 1`
- Cabine neutra de JBL (faz o papel da "mesa" da gravação) → `J-120 2x12`
- Esculpir o som para fone/PC → `EQ 1`
- Sala curta da Abbey Road → `Room`

### Parâmetros módulo a módulo

### PRE — Boost

| Parâmetro | Valor |
|---|---|
| Ganho | 22 |
| Boost | 1 |

### DST — La Charger

| Parâmetro | Valor |
|---|---|
| Gain | 32 |
| Tone | 52 |
| Volume | 62 |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 28 |

### CAB — J-120 2x12

| Parâmetro | Valor |
|---|---|
| Level | 75 |
| High Cut | 50 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | -1 |
| Mid | 3 |
| High | -1 |
| Level | 50 |

### RVB — Room

| Parâmetro | Valor |
|---|---|
| Decay* | 20 |
| Pre-D* | 19 |
| Damp* | 31 |
| Mix* | 0 |


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

**Nome no painel**: `CT01VOX` · **Slot sugerido**: **U02**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U02**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `Boost` (Ganho 22 / Boost 1) → **DST** `La Charger` (Gain 32 / Tone 52 / Volume 62) → **NR** `Gate 1` (Thr 28) → **CAB** `J-120 2x12` (Level 75 / High Cut 50) → **EQ** `EQ 1` (Low -1 / Mid 3 / High -1 / Level 50) → **RVB** `Room` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `CT01VOX`.

---

## 🚫 9. Evite com este patch

- ⛔ Delay/reverb longos — a mesa da Abbey Road era seca

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
