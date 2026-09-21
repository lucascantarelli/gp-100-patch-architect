# 🛞 URM01SL
### Uncle Remus — Slide (base)
##### Frank Zappa · Apostrophe (') (1974)

![Genero](https://img.shields.io/badge/Genero-Blues-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-Slide-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-bridge-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **Slide de Duran: brilho agudo crocante com sustain de vidro — Twin estufado + comprimido**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: SLIDE na 4ª/5ª corda · Seletor 1 (bridge) · Volume 9 · Tone 8–9**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | Posição 1 — bridge (brilho para o slide cortar) |
| **Volume** | 9 |
| **Tone** | 8–9 (aberto) |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

1. Slide de tubo/porcelana na 4ª–5ª corda, paralelo ao traste, pressão leve
2. Vibrato de SLIDE (empurre o tubo atrás da nota, não com os dedos) — é o 'choro' da base
3. Sincronize com a mão direita: as notas de slide devem nascer LIMPAS, o crocante vem do amp

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **U21** (seção 8).
> 3. Toque *base + respostas de slide entre as frases do vocal* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
| estridente | CAB High Cut 60 ou Tone da guitarra -1 |
| slide sem sustain | COMP4 p0 +5 |
| crocante demais | DST p0 -3 |

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

**Nota específica deste patch**: Recomendada: American Twin 2x12 Medium Mix (User IR 1) — é o Twin real da sessão (Low Cut 5 · High Cut 9000 · Level 0).


---

## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento

A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.

> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.

### Estado de fábrica do patch (o que já vem ligado)

| Módulo | Estado no `.prst` | Modelo |
|---|---|---|
| PRE | **🔴 ON** | `COMP4` |
| DST | **🔴 ON** | `Blues OD` |
| AMP | **🔴 ON** | `Dark Twin` |
| NR | **🔴 ON** | `Gate 1` |
| CAB | **🔴 ON** | `DarkTW 2x12` |
| EQ | **🔴 ON** | `EQ 1` |
| MOD | ⚪ OFF | `A-Chorus` |
| DLY | ⚪ OFF | `Sweet` |
| RVB | **🔴 ON** | `Plate` |

### 🎭 Momentos desta música (validados para este patch)

Mude SÓ os módulos indicados — o resto permanece como na tabela acima:

1. **Solo seco de Zappa** — **RVB → OFF**
   *Quando*: A produção de Zappa é seca até na base — para frases à frente do vocal, desligue o Plate.

### 🦶 Ligar/desligar ao vivo (modo STOMP)

1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.
2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).
3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.

> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. Os momentos deste patch nunca mexem neles.


---

## 🔊 5. Objetivo do som

**O que este patch é**: Slide de Duran: brilho agudo crocante com sustain de vidro — Twin estufado + comprimido.

Sátira de Zappa/Duke sobre promessas vazias: base brilhante de slide de Tony Duran sobre piano de George Duke e os solos cirúrgicos e SECOS do próprio Zappa. Basic track nas sessões de 1972 (Paramount, LA), overdubs 73-74.

**Teste recomendado**: base + respostas de slide entre as frases do vocal · **Drum**: Soul/Funk 96 BPM

**Como saber que está certo**:

- ☑️ brilho crocante sem estridência
- ☑️ sustain de vidro nas notas longas
- ☑️ nada de lama no conjunto

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
| **🔴** PRE · COMP4 | **🔴** DST · Blues OD | **🔴** AMP · Dark Twin | **🔴** NR · Gate 1 | **🔴** CAB · DarkTW 2x12 | **🔴** EQ · EQ 1 | ~~⚪~~ MOD | ~~⚪~~ DLY | **🔴** RVB · Plate |

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
| PRE | COMP4 | Thresh: 40 · Attack: 55 · Tone: 60 · Level: 62 |
| DST | Blues OD | Gain: 40 · Tone: 70 · Level: 62 |
| AMP | Dark Twin | Vol: 64 · Output: 60 · Bass: 48 · Middle: 55 · Treble: 62 · Bright: Off |
| NR | Gate 1 | Thr: 26 |
| CAB | DarkTW 2x12 | Level: 75 · High Cut: 55 |
| EQ | EQ 1 | Low: 0 · Mid: 2 · High: 1 · Level: 50 |
| RVB | Plate | Decay*: 30 · Pre-D*: 40 · Damp*: 50 · Mix*: 1 |

### Mapeamento rig real → GP-100

- Compressor transparente nivelando a dinâmica do slide → `COMP4`
- Drive na frente do amp compensando o humbucker da gravação → `Blues OD`
- Fender® '65 Twin Reverb → `Dark Twin`
- Controle de hum (single coils + ganho) → `Gate 1`
- Falante JBL D120F do Twin → `DarkTW 2x12`
- Esculpir o som para fone/PC → `EQ 1`
- Plate de estúdio ("splash" da faixa) → `Plate`

### Parâmetros módulo a módulo

### PRE — COMP4

| Parâmetro | Valor |
|---|---|
| Thresh | 40 |
| Attack | 55 |
| Tone | 60 |
| Level | 62 |

### DST — Blues OD

| Parâmetro | Valor |
|---|---|
| Gain | 40 |
| Tone | 70 |
| Level | 62 |

### AMP — Dark Twin

| Parâmetro | Valor |
|---|---|
| Vol | 64 |
| Output | 60 |
| Bass | 48 |
| Middle | 55 |
| Treble | 62 |
| Bright | Off |

### NR — Gate 1

| Parâmetro | Valor |
|---|---|
| Thr | 26 |

### CAB — DarkTW 2x12

| Parâmetro | Valor |
|---|---|
| Level | 75 |
| High Cut | 55 |

### EQ — EQ 1

| Parâmetro | Valor |
|---|---|
| Low | 0 |
| Mid | 2 |
| High | 1 |
| Level | 50 |

### RVB — Plate

| Parâmetro | Valor |
|---|---|
| Decay* | 30 |
| Pre-D* | 40 |
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

**Nome no painel**: `URM01SL` · **Slot sugerido**: **U21**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **U21**.
2. **Digitar no painel** (receita na ordem dos menus):

```
**PRE** `COMP4` (Thresh 40 / Attack 55 / Tone 60 / Level 62) → **DST** `Blues OD` (Gain 40 / Tone 70 / Level 62) → **AMP** `Dark Twin` (Vol 64 / Output 60 / Bass 48 / Middle 55 / Treble 62 / Bright Off) → **NR** `Gate 1` (Thr 26) → **CAB** `DarkTW 2x12` (Level 75 / High Cut 55) → **EQ** `EQ 1` (Low 0 / Mid 2 / High 1 / Level 50) → **RVB** `Plate` (ajuste fino no painel — seção 3 📡)
```

3. **SAVE** no slot → renomeie para `URM01SL`.

---

## 🚫 9. Evite com este patch

- ⛔ Reverb longo — a produção de Zappa é seca até na base
- ⛔ Slide com Tone fechado — mata o efeito 'vidro'

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
