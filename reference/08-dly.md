# GP-100 — Módulo DLY (Delay)
> Página impressa 30 do manual. 6 modelos. Um patch usa **um** DLY por vez (ou DLY OFF). Nomes EXATOS.

## Modelos e parâmetros oficiais

### 1. Dly Mono
- Delay estéreo central (eco clássico).
- `Delay(0~1900)` ms — tempo do eco.
- `Fdbk(0~99)` — repetições (feedback).
- `High Cut(1000~20000)` Hz — escurece as repetições (analog feel).
- `Mix(0~99)` — mistura do eco com o som seco.

### 2. Dly Dual
- Delay estéreo (dois ecos independentes L/R com tempos próprios).
- `Delay(0~1900)` ms — tempo do primeiro eco.
- `Delay L(0~1900)` ms — tempo do segundo eco (esquerdo).
- `Fdbk(0~99)`
- `High Cut(1000~20000)` Hz
- `Mix(0~99)`

### 3. Ping Pong
- Delay ping-pong (ecos alternando L/R).
- `Delay(0~1900)` ms
- `Fdbk(0~99)`
- `High Cut(1000~20000)` Hz
- `Mix(0~99)`

### 4. Analog
- Delay analógico (BB preamp estilo BBD, eco que degrada e escurece).
- `Delay(0~1000)` ms
- `Fdbk(0~99)`
- `High Cut(500~10000)` Hz — degradação do eco (o charme analógico).
- `Mix(0~99)`

### 5. Tape
- Delay tape (máquina de fita, eco wobble/warm).
- `Delay(0~1000)` ms
- `Fdbk(0~99)`
- `High Cut(1000~20000)` Hz
- `Mix(0~99)`

### 6. Beat
- Delay com subdivisões rítmicas sincronizadas ao BPM.
- `Beat(1/4, 1/8, dotted 1/8, 1/16...)` — subdivisão rítmica do delay.
- `Fdbk(0~99)`
- `High Cut(1000~20000)` Hz
- `Mix(0~99)`

## Tabela de tempos úteis (BPM → ms de colcheia pontuada)
| BPM | dotted 1/8 | 1/4 |
|---|---|---|
| 80 | 562 | 750 |
| 90 | 500 | 667 |
| 100 | 450 | 600 |
| 110 | 409 | 545 |
| 120 | 375 | 500 |
| 140 | 321 | 429 |
| 160 | 281 | 375 |

Fórmula: dotted 1/8 = 45000 ÷ BPM · 1/4 = 60000 ÷ BPM · 1/8 = 30000 ÷ BPM.

## Guia de estilo (Strat)

| Estilo | Modelo | Startpoint |
|---|---|---|
| Rockabilly/slapback | `Analog` | Delay 90 ms, Fdbk 15, High Cut 3500, Mix 25 |
| Blues espaçoso | `Dly Mono` | Delay 420 ms, Fdbk 25, High Cut 4000, Mix 30 |
| U2/ambient rítmico | `Beat` | Beat dotted 1/8, Fdbk 45, High Cut 6000, Mix 45 |
| Country chickee (duplo) | `Dly Dual` | Delay 120 / Delay L 240, Fdbk 25, Mix 30 |
| Post-rock/expansivo | `Ping Pong` | Delay 550 ms, Fdbk 55, High Cut 8000, Mix 45 |
| Solo épico | `Dly Mono` | Delay 480 ms, Fdbk 35, High Cut 5000, Mix 35 |
| Dub/psicodélico | `Tape` | Delay 350 ms, Fdbk 60, High Cut 3000, Mix 45 |
| Industrial/ético | `Dly Mono` | Delay 1900 ms, Fdbk 70, Mix 40 (self-osc controlado) |

## O que evitar (Evite)
- **Fdbk ≥ 60 em Mono/Dual**: run-away de eco (auto-oscilação); a menos que o objetivo seja o caos musical.
- **Delay ≥ 1500 ms + RVB junto**: charco sonoro; em ambient, escolha UM dominante.
- **Mix ≥ 60**: o eco fica mais alto que o seco — a menos que seja efeito principal (shoegaze), mantenha 25–45.
- **High Cut no máximo (20000)**: eco digital duro/brilhante; em geral 3000–8000 soa musical.
- **Analog com High Cut ≥ 6000**: perde o propósito (analógico escuro); use 1500–3500.
- **Beat sem definir o BPM do patch**: o delay fica dessincronizado com o drum machine — defina o tempo no patch antes.
- **Slapback (80–120 ms) com Fdbk ≥ 30**: vira "slap infinito"; use Fdbk ≤ 20.
