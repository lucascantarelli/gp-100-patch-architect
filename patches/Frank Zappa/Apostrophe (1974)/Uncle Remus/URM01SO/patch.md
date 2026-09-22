# 🔪 URM01SO
### Uncle Remus — Solo
##### Frank Zappa · Apostrophe (') (1974)

![Genero](https://img.shields.io/badge/Genero-Rock-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Solo-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Solo do Zappa: cirúrgico, seco, médios à frente — Super OD + Marshall JTM45, zero reverb**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: Seletor 1 (bridge) · Volume 10 · Tone 8**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 1 — bridge (articulação para frases rápidas) |
| **Volume** | 10 |
| **Tone** | 8 |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Frases curtas e angulares com espaços — o solo do Zappa 'fala', não canta
2. Dobles de parada (staccato) com palheta firme; trémolo seco onde a frase exige
3. NADA de sustains longos: a assinatura é a precisão rítmica, deixe o silêncio trabalhar

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U22** (seção 8).
> 3. Toque *solo central da faixa (após o 2º refrão)* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| gordo demais | Super OD Drive -4 |
| sem mordida | EQ Mid +4 |
| com 'eco' | RVB OFF (a referência é seca) |

### Protocolo universal (vale para todos os patches)

- Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.
- Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.
- Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).
- Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.

---

## 📡 3. Impulse Response (CAB) — o gabinete do patch

**O que está no arquivo `.prst` agora**: CAB de fábrica **`UK-GN 2x12`** — o modelo GP-100 que reproduz o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.

> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).
>
> Uma IR boa **substitui** o CAB — não empilha com ele.

### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta

O banco local tem a captura **British Straight 4x12** — casamento direto com o gabinete real deste patch:

1. No **GP-100 Edits** → IR Manager, carregue no **User IR 4** o arquivo:
   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/British Straight 4x12/British Straight 4x12 Medium Mix.wav`
2. No patch: bloco CAB → troque `UK-GN 2x12` por **User IR 4**.
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

**Nota específica deste patch**: Recomendada: British Straight 4x12 Medium Mix (User IR 2) — o Marshall da era (Low Cut 5 · High Cut 8000 · Level 0).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | ⚪ OFF | `COMP` |
| DST | **🔴 ON** | `Super OD` |
| AMP | **🔴 ON** | `UK 45` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `UK-GN 2x12` |
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

**O que este patch é**: Solo do Zappa: cirúrgico, seco, médios à frente — Super OD + Marshall JTM45, zero reverb.

Sátira de Zappa/Duke sobre promessas vazias: base brilhante de slide de Tony Duran sobre piano de George Duke e os solos cirúrgicos e SECOS do próprio Zappa. Basic track nas sessões de 1972 (Paramount, LA), overdubs 73-74.

**Teste recomendado**: solo central da faixa (após o 2º refrão) · **Drum**: Rock 96 BPM

**Como saber que está certo**:

- ☑️ cada nota seca e definida
- ☑️ médios cortando a mix
- ☑️ reverb praticamente inexistente

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
| Tony Duran: slide/rhythm guitar (brilho agudo, ataque crocante) | alta | MusicBrainz — Apostrophe (') |
| Frank Zappa: solos cirúrgicos e secos, sem reverb | alta | Rock & Roll Globe — Apostrophe (') 50 anos (2024) |
| George Duke: piano/co-autoria preenchendo o meio | alta | Rock & Roll Globe + Wikipedia |
| Sessões: basic track 1972 (Paramount Studios, LA) + overdubs 73/74 | média | Frank Zappa Lyrics Book / análises de sessão |

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

| PRE | DST | AMP | NR | CAB | EQ | MOD | DLY | RVB |
|---|---|---|---|---|---|---|---|---|
| ~~⚪~~ PRE | **🔴** DST · Super OD | **🔴** AMP · UK 45 | **🔴** NR · Gate 1 | **🔴** CAB · UK-GN 2x12 | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Room |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| DST | Super OD | Drive: 62 · Tone: 58 · Level: 66 |
| AMP | UK 45 | Vol: 66 · PRSE: 60 · Output: 60 · Bass: 50 · Middle: 62 · Treble: 58 |
| NR | Gate 1 | Thr: 28 |
| CAB | UK-GN 2x12 | Level: 75 · High Cut: 55 |
| EQ | EQ 1 | Low: -1 · Mid: 3 · High: 0 · Level: 50 |
| RVB | Room | Mix: 20 · Pre Delay: 19 ms · Decay: 31 · Trail: Off |

### Mapeamento rig real → GP-100

- Overdrive de médio afiado (o solo "cirúrgico") → `Super OD`
- Marshall® JTM45 (backline da era de Zappa) → `UK 45`
- Controle de hum (single coils + ganho) → `Gate 1`
- Gabinete Marshall® com Greenbacks → `UK-GN 2x12`
- Esculpir o som para fone/PC → `EQ 1`
- Sala curta e seca (Abbey Road, groove de timba) → `Room`

### Parâmetros módulo a módulo

### DST — Super OD

| Parâmetro | Valor |
|---|---|
| Drive | 62 |
| Tone | 58 |
| Level | 66 |

### AMP — UK 45

| Parâmetro | Valor |
|---|---|
| Vol | 66 |
| PRSE | 60 |
| Output | 60 |
| Bass | 50 |
| Middle | 62 |
| Treble | 58 |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 28 |

### CAB — UK-GN 2x12

| Parâmetro | Valor |
|---|---|
| Level | 75 |
| High Cut | 55 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | -1 |
| Mid | 3 |
| High | 0 |
| Level | 50 |

### RVB — Room

| Parâmetro | Valor |
|---|---|
| Mix | 20 |
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

**Nome no painel**: `URM01SO` · **Slot sugerido**: **U22**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U22**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**DST** `Super OD` (Drive 62 / Tone 58 / Level 66) → **AMP** `UK 45` (Vol 66 / PRSE 60 / Output 60 / Bass 50 / Middle 62 / Treble 58) → **NR** `Gate 1` (Thr 28) → **CAB** `UK-GN 2x12` (Level 75 / High Cut 55) → **EQ** `EQ 1` (Low -1 / Mid 3 / High 0 / Level 50) → **RVB** `Room` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `URM01SO`.

---

## 🚫 9. Evite com este patch

- ⛔ Reverb/delay audíveis — Zappa mixava o solo SECO
- ⛔ Vibrato largo — a expressão dele vem do ritmo, não do bend

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
