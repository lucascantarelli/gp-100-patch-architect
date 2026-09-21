# GP-100 — Módulo RVB (Reverb)
> Página impressa 31 do manual. 6 modelos. Um patch usa **um** RVB por vez (ou RVB OFF). Nomes EXATOS.

## Modelos e parâmetros oficiais

### 1. Room
- Reverb de sala pequena (ambiente de quarto/estúdio).
- `Decay(0~10)` — tamanho/tempo de cauda.
- `Pre-D(0~100)` ms — pre-delay.
- `Damp(0~99)` — absorção (quanto maior, mais abafado).
- `Mix(0~99)`

### 2. Hall
- Reverb de salão/concert hall.
- `Decay(0~10)` · `Pre-D(0~100)` ms · `Damp(0~99)` · `Mix(0~99)`

### 3. Church
- Reverb de igreja (cauda longa).
- `Decay(0~10)` · `Pre-D(0~100)` ms · `Damp(0~99)` · `Mix(0~99)`

### 4. Plate
- Reverb plate (placa metálica clássica de estúdio).
- `Decay(0~10)` · `Pre-D(0~100)` ms · `Damp(0~99)` · `Mix(0~99)`

### 5. Spring
- Reverb de mola (amp vintage, surf).
- `Decay(0~10)` · `Pre-D(0~100)` ms · `Damp(0~99)` · `Mix(0~99)`

### 6. Air
- Reverb "ar" (corta-frequency + curto; adiciona brilho/ambiente).
- `Decay(0~10)` · `Pre-D(0~100)` ms · `Damp(0~99)` · `Mix(0~99)`

## Guia de escolha

| Modelo | Quando usar |
|---|---|
| `Room` | timbre "seco de estúdio", riff precisa de definição; base de quase todo patch de banda |
| `Hall` | solos, baladas, pop; espaço grande sem exagero |
| `Church` | ambient/post-rock/cinema; arpeggios |
| `Plate` | vocal-like em solo, snare-like no ataque; clássico de estúdio para lead |
| `Spring` | surf, rockabilly, blues americano; combina com Twin |
| `Air` | "levantar" o som em mix abafada; complemento discreto (Mix 10–20) |

## Startpoint por estilo (Strat)

| Estilo | Modelo | Startpoint |
|---|---|---|
| Blues clássico | `Spring` | Decay 4, Pre-D 10, Damp 40, Mix 25 |
| Surf | `Spring` | Decay 6, Pre-D 0, Damp 25, Mix 40 |
| Pop/rock clean | `Room` | Decay 3, Pre-D 20, Damp 45, Mix 25 |
| Solo de balada | `Hall` | Decay 6, Pre-D 40, Damp 35, Mix 35 |
| Solo épico | `Plate` | Decay 5, Pre-D 30, Damp 30, Mix 35 |
| Ambient/post-rock | `Church` | Decay 9, Pre-D 60, Damp 30, Mix 45 |
| Metal (riff) | `Room` | Decay 2, Pre-D 10, Damp 50, Mix 15 |
| Metal (solo) | `Plate` | Decay 4, Pre-D 30, Damp 35, Mix 30 |
| Country clean | `Room` | Decay 3, Pre-D 15, Damp 40, Mix 20 |

## O que evitar (Evite)
- **Mix ≥ 45 em riff**: o riff se dissolve na cauda e a banda some — riff pede Mix 15–25.
- **Decay ≥ 8 com distorção**: lama; reverb longo em sinal saturado gera "wash" que embola tudo.
- **Damp ≤ 20 com hi-gain**: chiado e fizz amplificados na cauda; hi-gain pede Damp 40–60.
- **Spring com Decay ≥ 7**: deixa de ser surf e vira "banheiro com molas"; mantenha 3–6.
- **Pre-D > 80 em tocar rápido**: desconexão entre nota e espaço (estilo ambiental proposital, senão evite).
- **Church + Delay longo juntos**: o patch vira um efeito só — para ambient, tudo bem; para banda, não.
- **Esquecer o reverb no solo de um patch de riff**: mantenha DOIS patches (riff e solo) em vez de um reverb gigante que serve mal aos dois.
