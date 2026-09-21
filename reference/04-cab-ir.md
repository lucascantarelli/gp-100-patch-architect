# GP-100 — Módulo CAB (Gabinetes e IRs)
> Página impressa 26 do manual. Um patch usa **um** CAB por vez (ou CAB OFF — necessário só se você usar captura de amp via IR no próprio slot). 40 gabinetes de fábrica + 20 slots de IR do usuário.

## Como funciona
- O bloco CAB aplica a **Impulse Response** (resposta do gabinete + microfone) ao sinal vindo do AMP.
- **40 CABs de fábrica** já vêm carregados (CAB 1–39 + "D").
- **20 slots de usuário (USER IR)**: o usuário carrega arquivos `.wav` de terceiros (24 bits, 44,1 kHz, mono) via software editor — a GP-100 aceita IRs de até **1024 samples**.
- Cada slot (fábrica ou usuário) tem parâmetros **Low Cut (0~20) Hz**, **High Cut (1000~20000) Hz** e **Level (-12~+12) dB**.

## Lista oficial de gabinetes de fábrica

| # | Nome | Base |
|---|---|---|
| 1 | 1x12 63 | '63 Cab (Fender) |
| 2 | 1x12 65 | '65 Cab (Fender) |
| 3 | 2x12 65 | '65 Cab (Fender) |
| 4 | 1x12 JC | JC-120 Cab |
| 5 | 4x10 BS | Bassman 4x10 Cab |
| 6 | 2x12 VOX | AC30 Top Boost Cab |
| 7 | 4x12 68 | '68 Cab (Marshall) |
| 8 | 4x12 M70 | Marshall® Basketweave (1960) |
| 9 | 4x12 ST | Slant 1960A (Marshall) |
| 10 | 4x12 GB | Greenback (Marshall) |
| 11 | 4x12 MIX | Greenback + Vintage 30 Mix |
| 12 | 4x12 MR | Mesa Recto 4x12 |
| 13 | 4x12 TR | Mesa Traditional Recto |
| 14 | 2x12 MC | Matchless Chieftain Cab |
| 15 | 2x12 BD | Bogner 2x12 |
| 16 | 2x12 EN | Engl 2x12 |
| 17 | 4x12 EN | Engl 4x12 |
| 18 | 4x12 DV | Diezel 4x12 |
| 19 | 4x12 PC | Peavey 5150 Cab |
| 20 | 2x12 DR | Dr. Z 2x12 |
| 21 | 1x12 HD | 1x12 Hot |
| 22 | 1x12 ML | Matchless 1x12 |
| 23 | 1x12 VG | Vintage 1x12 |
| 24 | 2x12 TO | Tone King 2x12 |
| 25 | 1x12 SU | Supro 1x12 |
| 26 | 2x12 DE | Delux Reverb Cab |
| 27 | 2x12 SO | Soldano 2x12 |
| 28 | 4x12 SO | Soldano 4x12 |
| 29 | 4x12 OR | Orange 4x12 |
| 30 | 4x12 SL | Slant 6V 4x12 |
| 31 | 2x12 JA | Jazz 2x12 |
| 32 | 4x10 BS | Bassman 4x10 Cab |
| 33 | 8x10 AM | Ampeg 8x10 |
| 34 | 4x10 SW | SWR 4x10 |
| 35 | 1x15 AC | Acoustic 1x15 |
| 36 | 2x8 AC | Acoustic 2x8 |
| 37 | 2x12 A2 | Acoustic 2x12 |
| 38 | 4x10 AC | Acoustic 4x10 |
| 39 | 8x2 AC | Acoustic 8x2 |
| D | D | Dreadnought (violão dreadnought) |

## Parâmetros de qualquer CAB
- `Low Cut(0~20)` Hz — corta graves (controle de lama e "fart").
- `High Cut(1000~20000)` Hz — corta agudos (suaviza "fizz" digital).
- `Level(-12~+12)` dB — volume do CAB.

## Sugestões de uso (casamento AMP × CAB)
| AMP sugerido | CAB ideal | Por quê |
|---|---|---|
| Dark Twin / Bellman 59B | `1x12 65` ou `4x10 BS` | americanos brilhantes: gabinete Fender arredonda |
| J-120 CL | `1x12 JC` | casamento natural do Jazz Chorus |
| Foxy 30N / 30TB | `2x12 VOX` | alnico blues, top mais "squeaky" |
| UK 45 / UK 50JP / UK 800 | `4x12 68`, `4x12 ST`, `4x12 GB` | britânico: Greenback/75² |
| Flagman / Flagman+ | `4x12 MIX` | boutique: Greenback + V30 |
| Mess DualV / Mess DualM / Mess4 LD | `4x12 MR`, `4x12 TR` | Mesa precisa de V30 |
| EV 51 / Power LD | `4x12 PC`, `4x12 EN` | hi-gain moderno |
| Dizz VH | `4x12 DV` | Diezel |
| Eagle 120 | `4x12 EN` | ENGL |
| Juice R100 | `4x12 OR` | Orange |
| Solo100 LD | `4x12 SO` ou `4x12 MIX` | Soldano |
| Match CL/OD | `2x12 MC` | Matchless |
| BogSV/Bog BlueV/Bog RedM | `2x12 BD` | Bogner |
| Z38 CL/OD | `2x12 DR` ou `2x12 TO` | Dr.Z / boutique americano |
| SUPDual OD | `1x12 SU` | Supro |
| B-Mani / SVT 40 / B-MAN500 | `8x10 AM` | baixo clássico |
| H-K B15 / SWR SM | `4x10 SW` | baixo moderno |
| B-DI / B-ND | `4x10 BS` (baixo) | DI com corpo |
| AC Sim / A-15 / A-60 / A-CH | `D` (Dreadnought) | violão |

## Ajuste fino comum (receitas)
- **Fizz digital em hi-gain**: High Cut 6000–8000 Hz.
- **Lama em Drop tuning**: Low Cut 8–12 Hz (corta o sub que não se ouve mas "suj a").
- **CAB muito mais baixo que o resto**: Level +2 a +4 dB.
- **CAB "na cara" (estúdio)**: Low Cut 4–6, High Cut 12000, Level 0.

## User IR (slots 40–59)
- Carregue via software editor (arquivo .wav 44,1 kHz / 24 bits / mono).
- Slots nomeáveis; mesmos parâmetros Low Cut / High Cut / Level.
- Ideal para: capturas de amp (NAM/Kemper-style), cabs raras, mix de 2 cabs (somado no arquivo).
- **Consulte `gp100-ir-research`** para buscar IRs gratuitas na internet.

## O que evitar (Evite)
- **CAB OFF com AMP ON** no ouvido/fone: o som fica "dentado" e áspero (o amp simula só o head). CAB OFF só faz sentido ao usar IR de terceiros carregada em outro bloco — e na GP-100 não há esse bloco extra, então **mantenha sempre o CAB ON**.
- **Low Cut ≥ 15 Hz em guitarra padrão**: tira o corpo do som; use 4–10 Hz.
- **High Cut < 4000 Hz**: som abafado de rádio velho (a menos que seja o objetivo, ex.: lo-fi).
- **Level do CAB ≥ +6 dB**: desequilibra o patch e clipe o master — prefira compensar no Output/Master do AMP.
- **Escolher CAB 8x10 AM para guitarra**: é gabinete de baixo; engolirá os médios da guitarra.
- **User IR com Level +12 "para valer"**: IRs caseiras variam muito de ganho; comece em 0 dB e ajuste por orelha.
