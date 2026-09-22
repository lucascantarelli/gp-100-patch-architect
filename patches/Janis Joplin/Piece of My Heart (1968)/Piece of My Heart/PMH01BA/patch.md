# 💔 PMH01BA
### Piece of My Heart — Base
##### Janis Joplin (Big Brother & The Holding Company) · Cheap Thrills (1968)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Base-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-posição%204-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **SG + Twin estufado adaptado para Strat: Blues OD empurrando Dark Twin no talo, spring curto**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: Seletor 4 (middle+neck) · Volume 7–8 · Tone 8–9 · abra a 10 no ataque**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 4 — middle+neck (o 'chop' da base) |
| **Volume** | 7–8 |
| **Tone** | 8–9 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Acordes D–A curtidos no contratempo com palhetada forte
2. Abra o Volume a 10 no ataque para 'acordar' o OD — é a dinâmica da música

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U23** (seção 8).
> 3. Toque *groove completo da base* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| acorde embolado | EQ Low -2 |
| hum audível | NR Thr 32 |
| ataque seco | DST Gain +3 |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`DarkTW 2x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta

O banco local tem a captura **American Twin 2x12** — casamento direto com o gabinete real deste patch:

1. No **GP-100 Edits** → IR Manager, carregue no **User IR 1** o arquivo:
   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/American Twin 2x12/American Twin 2x12 Medium Mix.wav`
2. No patch: bloco CAB → troque `DarkTW 2x12` por **User IR 1**.
3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), **Level** comece em 0 e compare com o bypass.
   Alternativas do mesmo gabinete no banco: `American Twin 2x12 Bright Mix.wav`, `American Twin 2x12 Dark Mix.wav`, `American Twin 2x12 Bright 160.wav`, `American Twin 2x12 Bright 87.wav`, `American Twin 2x12 Dark 160.wav`, `American Twin 2x12 Dark 87.wav`, `American Twin 2x12 Medium 160.wav`, `American Twin 2x12 Medium 87.wav`.

### 🌍 Procurar na internet (só se quiser experimentar algo diferente)

O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:

```
impulse_responses/<Nome do Pack>/   ← extraia aqui
python tools/ir_library.py          ← reindexa e valida os WAVs
```

**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).

### ✅ Fallback garantido

Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.

**Nota específica deste patch**: Recomendada: American Twin 2x12 Medium Mix (User IR 1) — o JBL D120F do Twin de Sam Andrew (Low Cut 5 · High Cut 8000 · Level 0).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | ⚪ OFF | `COMP` |
| DST | **🔴 ON** | `Blues OD` |
| AMP | **🔴 ON** | `Dark Twin` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `DarkTW 2x12` |
| EQ | **🔴 ON** | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | ⚪ OFF | `Sweet` |
| RVB | **🔴 ON** | `Spring` |

### 🎭 Momentos desta música

Este patch foi afinado para **um** papel — use os sobressalentes da tabela acima para variar na hora (ex.: desligar o DLY para uma seção seca). Momentos dedicados estão nos patches irmãos da mesma música (veja o mapa do álbum).

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: SG + Twin estufado adaptado para Strat: Blues OD empurrando Dark Twin no talo, spring curto.

Sam Andrew (SG + Twin estufado) na base quebrada; James Gurley no solo com sustain e feedback. Zero pedais — tudo é amp.

**Teste recomendado**: groove completo da base · **Drum**: Rock 90-100 BPM (a música anda ~128)

**Como saber que está certo**:

- ☑️ ataque quebra sem embolar
- ☑️ hum de single coil ausente

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Sam Andrew: Gibson SG | alta | MusicRadar — Sam Andrew interview |
| Fender Twin Reverb estufado | alta | MusicRadar 2012 |
| Zero efeitos | alta | MusicRadar 2012 |
| Solo: James Gurley (mesmo rig, mais ganho/feedback) | média | The Gear Page 2022 |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| ~~⚪~~ PRE | **🔴** DST · Blues OD | **🔴** AMP · Dark Twin | **🔴** NR · Gate 1 | **🔴** CAB · DarkTW 2x12 | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Spring |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| DST | Blues OD | Gain: 45 · Tone: 55 · Level: 65 |
| AMP | Dark Twin | Vol: 72 · Output: 62 · Bass: 55 · Middle: 50 · Treble: 52 · Bright: Off |
| NR | Gate 1 | Thr: 28 |
| CAB | DarkTW 2x12 | Level: 75 · High Cut: 50 |
| EQ | EQ 1 | Low: -1 · Mid: 2 · High: -1 · Level: 50 |
| RVB | Spring | Mix: 40 · Decay: 99 |

### Mapeamento rig real → GP-100

- Drive na frente do amp compensando o humbucker da gravação → `Blues OD`
- Fender® '65 Twin Reverb → `Dark Twin`
- Controle de hum (single coils + ganho) → `Gate 1`
- Falante JBL D120F do Twin → `DarkTW 2x12`
- Esculpir o som para fone/PC → `EQ 1`
- Mola do Twin/Fender → `Spring`

### Parâmetros módulo a módulo

### DST — Blues OD

| Parâmetro | Valor |
|---|---|
| Gain | 45 |
| Tone | 55 |
| Level | 65 |

### AMP — Dark Twin

| Parâmetro | Valor |
|---|---|
| Vol | 72 |
| Output | 62 |
| Bass | 55 |
| Middle | 50 |
| Treble | 52 |
| Bright | Off |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 28 |

### CAB — DarkTW 2x12

| Parâmetro | Valor |
|---|---|
| Level | 75 |
| High Cut | 50 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | -1 |
| Mid | 2 |
| High | -1 |
| Level | 50 |

### RVB — Spring

| Parâmetro | Valor |
|---|---|
| Mix | 40 |
| Decay | 99 |


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

**Nome no painel**: `PMH01BA` · **Slot sugerido**: **U23**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U23**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**DST** `Blues OD` (Gain 45 / Tone 55 / Level 65) → **AMP** `Dark Twin` (Vol 72 / Output 62 / Bass 55 / Middle 50 / Treble 52 / Bright Off) → **NR** `Gate 1` (Thr 28) → **CAB** `DarkTW 2x12` (Level 75 / High Cut 50) → **EQ** `EQ 1` (Low -1 / Mid 2 / High -1 / Level 50) → **RVB** `Spring` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `PMH01BA`.

---

## 🚫 9. Evite com este patch

- ⛔ DST Gain ≥ 60 — vira pedal audível
- ⛔ Bright ON
- ⛔ Reverb Mix > 30

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
