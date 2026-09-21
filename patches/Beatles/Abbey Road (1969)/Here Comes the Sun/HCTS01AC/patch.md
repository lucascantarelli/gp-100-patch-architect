# ☀️ HCTS01AC
### Here Comes the Sun — Acústico (dedilhado)
##### The Beatles · Abbey Road (1969)

![Genero](https://img.shields.io/badge/Genero-Acoustic-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Acústico-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-posição%204-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Violão simulado: AC Sim (Body 45, Top 68) + cab Dreadnought + Hall suave**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: Capotraste 7ª casa · Seletor 4 · Volume 9 · Tone 9**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 4 — middle+neck |
| **Volume** | 9 |
| **Tone** | 9 (aberto) |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. CAPOTRASTE na 7ª casa — toque as formas de A (é assim que a gravação funciona)
2. Dedilhado alternado com dinâmica uniforme; deixe as cordas rangendo levemente

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U11** (seção 8).
> 3. Toque *intro completa + refrão* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| mais nylon | AC Sim Mode 1 (Jumbo) ou 2 |
| mais brilho | Top +3 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`D`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 🔍 Não há captura melhor no nosso banco para este alvo

O CAB de fábrica `D` **já é a representação correta** deste alvo — nenhum gabinete do banco casa melhor (o catálogo local é consultado em `reference/16-ir-library.md`).

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Alvo = corpo de violão dreadnought — nenhuma IR de gabinete do banco casa; mantenha o CAB de fábrica.


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `AC Sim` |
| DST | ⚪ OFF | `Blues OD` |
| AMP | ⚪ OFF | `Dark Twin` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `D` |
| EQ | **🔴 ON** | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | ⚪ OFF | `Sweet` |
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

**O que este patch é**: Violão simulado: AC Sim (Body 45, Top 68) + cab Dreadnought + Hall suave.

George no Martin D-28 com capotraste na 7ª casa, gravado limpo. O AC Sim + cab Dreadnought reproduz exatamente essa cor.

**Teste recomendado**: intro completa + refrão · **Drum**: nenhum

**Como saber que está certo**:

- ☑️ ataque de dedilhado claro
- ☑️ corpo de dreadnought no acorde

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| George: Martin D-28, capotraste 7 | alta | Guitar World — Abbey Road gear guide |
| Sem amp — captação de violão | alta | Guitar World |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| **🔴** PRE · AC Sim | ~~⚪~~ DST | ~~⚪~~ AMP | **🔴** NR · Gate 1 | **🔴** CAB · D | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Hall |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | AC Sim | Body: 45 · Top: 68 · Vol: 99 · Mode: STD |
| NR | Gate 1 | Thr: 20 |
| CAB | D | Level: 75 · High Cut: 50 |
| EQ | EQ 1 | Low: -1 · Mid: 0 · High: 1 · Level: 50 |
| RVB | Hall | Decay*: 50 · Pre-D*: 50 · Damp*: 50 · Mix*: 1 |

### Mapeamento rig real → GP-100

- Violão real da gravação → `AC Sim` + CAB `D`
- Controle de hum (single coils + ganho) → `Gate 1`
- Corpo dreadnought → `D`
- Esculpir o som para fone/PC → `EQ 1`
- Hall etéreo das seções lentas → `Hall`

### Parâmetros módulo a módulo

### PRE — AC Sim

| Parâmetro | Valor |
|---|---|
| Body | 45 |
| Top | 68 |
| Vol | 99 |
| Mode | STD |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 20 |

### CAB — D

| Parâmetro | Valor |
|---|---|
| Level | 75 |
| High Cut | 50 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | -1 |
| Mid | 0 |
| High | 1 |
| Level | 50 |

### RVB — Hall

| Parâmetro | Valor |
|---|---|
| Decay* | 50 |
| Pre-D* | 50 |
| Damp* | 50 |
| Mix* | 1 |


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

**Nome no painel**: `HCTS01AC` · **Slot sugerido**: **U11**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U11**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `AC Sim` (Body 45 / Top 68 / Vol 99 / Mode STD) → **NR** `Gate 1` (Thr 20) → **CAB** `D` (Level 75 / High Cut 50) → **EQ** `EQ 1` (Low -1 / Mid 0 / High 1 / Level 50) → **RVB** `Hall` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `HCTS01AC`.

---

## 🚫 9. Evite com este patch

- ⛔ Drive/DST: mata o efeito violão
- ⛔ RVB com Decay alto — o violão real tem cauda curta

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
