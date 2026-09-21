# GP-100 — Catálogo REAL do Firmware 2.0/2.1
> **FONTE PRIMÁRIA**: catálogo empírico extraído do **export de fábrica** (biblioteca completa do aparelho, software editor 1.2.0, firmware 2.0) via `tools/analyze_prst.py` — dump completo em **`tools/factory-catalog.json`** (99 presets · 891 effects · 117 modelos). O export original foi removido do repositório na limpeza; para regenerar, exporte a biblioteca no GP-100 Edits e rode `python tools/analyze_prst.py <arquivo>.prst --json tools/factory-catalog.json`.
> O arquivo .prst é **XML** — os nomes abaixo são os que APARECEM no aparelho/editor do usuário. Onde divergirem do manual V1.8 impresso, **estes nomes vencem**.
> `code` = effectCode (usado na geração de .prst). `x` = posição na cadeia (fw 2.0 permite reordenar via editor; posições observadas: PRE 0–1, DST 1, AMP 2–3, CAB 4, EQ 2–7, MOD 6–7, DLY 5–7, RVB 8, NR variável).

## Mapeamento de gênero do patch (ppType)
`0`=Metal · `1`=World · `2`=Indie · `3`=Country · `4`=Rock · `5`=Funk · `6`=Pop · `7`=Blues · `8`=Jazz · `9`=Bass · `10`=Acoustic

## PRE (11 modelos reais)
| Nome real | Manual V1.8 | code | params_0..2 típicos (fábrica) |
|---|---|---|---|
| `COMP` | COMP (Ross) | 0 | Sens/Attack/Level — ex.: 25/40/50 (37 usos) |
| `COMP4` | COMP4 (Keeley C4) | 1 | 59/55/66/36… (4 params) |
| `Boost` | Boost (EP) | 26 | p0=ganho 10–50, p1=1 |
| `AC Sim` | AC Sim | 16777217 | p0–p3 (ex.: 45/68/99/0) |
| `T-Wah` | T-WAH | 16777231 | 75/75/79/99 |
| `V-Wah` | V-Wah | 83886081 | 0/80/75 |
| `C-Wah` | C-Wah | 83886088 | 50/50/50/49 |
| `OCTA` | OCTA | 16777249 | 8/30/50/50/40 |
| `Pitch` | — (novo no fw 2.0) | 16777251 | p1=semitons (-12), ex.: 23.2471/-12/3/99/26 |
| `Saturate` | — (novo) | 16777267 | 50/99/70/30/50/50/1 |
| `Step Filter` | — (novo) | 16777241 | 3/10/36/52/4/1/1 |

## DST (13 modelos reais)
| Nome real | Estilo equivalente (não oficial) | code | params fábrica (p0…) |
|---|---|---|---|
| `Green OD` | overdrive verde clássico (TS-style) — o mais usado (51x) | 50331648 | 0/50/50 |
| `Yellow OD` | overdrive amarelo clássico | 50331650 | 30/83/50/50/50 |
| `Super OD` | super overdrive | 50331654 | 0/55/60/0/49 |
| `Blues OD` | blues driver | 50331657 | 72/92/73/0/50 |
| `Tube Clipper` | clipper transparente | 50331659 | 80/65/50/50 |
| `Lazaro` | overdrive boutique | 50331682 | 25/0/65 |
| `Red Haze` | fuzz/haze vermelho | 50331684 | 50/50/49 |
| `SM Dist` | distorção SM clássica | 50331690 | 30/50/60/50/50 |
| `Darktale` | distorção moderna escura | 50331691 | 71/50/73 |
| `Chief` | overdrive boutique transparente | 50331693 | 20/50/50/50/50 |
| `La Charger` | distorção de rádio-fuzz (RAT-style) | 50331696 | 10/64/60 |
| `Flex OD` | overdrive flexível | 50331711 | 30/50/50/0/50 |
| `Bass Dist` | distorção de baixo | 50331712 | 0/39/50/50/50/1 |

## AMP (29 modelos reais; x=2, baixos x=2–3)
Nomes de amp IGUAIS ao manual V1.8 (Dark Twin, UK 45, UK 50JP, UK 800, Flagman, Bellman 59N, Foxy 30TB, L-Star CL, Match CL/OD, J-120 CL, Knights CL/OD, Z38 OD, Bad-KT CL, BogSV ausente no export, Dizz VH, Eagle 120, EV 51, Solo100 LD/OD, Mess DualV/DualM, Juice R100) + variantes de baixo/acústico:
| Nome real | code | observação |
|---|---|---|
| `Tweedy` | 117440513 | tweed americano (novo nome; ~Bassman/Deluxe) |
| `Bellman 59N` | 117440515 | manual V1.8: "Bellman 59B" |
| `Dark Twin` | 117440516 | |
| `J-120 CL` | 117440532 | |
| `Match CL` | 117440533 | |
| `L-Star CL` | 117440537 | |
| `Knights CL` | 117440543 | |
| `Bad-KT CL` | 117440546 | |
| `Foxy 30TB` | 117440551 | |
| `UK 45` | 117440554 | |
| `UK 50JP` | 117440559 | |
| `UK 800` | 117440565 | |
| `Match OD` | 117440584 | |
| `Z38 OD` | 117440585 | |
| `Solo100 OD` | 117440583 | |
| `Flagman` | 117440576 | |
| `Juice R100` | 117440595 | |
| `EV 51` | 117440602 | |
| `Solo100 LD` | 117440601 | |
| `Dizz VH` | 117440613 | |
| `Mess DualV` | 117440616 | |
| `Mess DualM` | 117440617 | |
| `Eagle 120` | 117440607 | |
| `Knights OD` | 117440636 | |
| `Classic Bass` | 117440627 | baixo |
| `Foxy Bass` | 117440629 | baixo |
| `Bass Pre` | 134217846 | preamp de baixo |
| `Mini Bass` | 134217845 | baixo |
| `AC Pre` | 134217850 | preamp acústico |

## NR (2 modelos)
| Nome | code | params |
|---|---|---|
| `Gate 1` | 27 | p0=threshold (30 típico) |
| `Gate 2` | 29 | p0=30, p1=20, p2=50 |

## CAB (31 nomes reais + user IR)
| Nome real | provável base | code |
|---|---|---|
| `TWD-P 1x10` | tweed 1x10 | 167772162 |
| `Dark 1x12` | dark 1x12 | 167772164 |
| `DarkTW 2x12` | Twin 2x12 | 167772178 |
| `Foxy 1x12` | AC30 1x12 | 167772168 |
| `Bad-KT 1x12` | Hot Cat 1x12 | 167772167 |
| `Studio 1x12` | estúdio | 167772172 |
| `Regular 1x12` | regular | 167772173 |
| `J-120 2x12` | JC-120 | 167772177 |
| `UK-GN 2x12` | Greenback 2x12 | 167772179 |
| `2Rick 2x12` | 2x12 Rickenbacker-ish | 167772188 |
| `TWD 2x12` | tweed 2x12 | 167772187 |
| `L-Star 2x12` | Lone Star | 167772185 |
| `UK-GN 4x12` | Greenback 4x12 | 167772194 |
| `UK-MD 4x12` | Modern 4x12 | 167772193 |
| `UK-LD 4x12` | Lead 4x12 | 167772191 |
| `UK-75 4x12` | 75W 4x12 | 167772208 |
| `UK-DK 4x12` | 4x12 escuro | 167772203 |
| `U-ban 4x12` | Uber-tight 4x12 | 167772204 |
| `H-Way 4x12` | Highway 4x12 | 167772202 |
| `EV51 4x12` | 5150 4x12 | 167772192 |
| `Mess-D 4x12` | Mesa Recto | 167772196 |
| `Pogner 4x12` | Bogner 4x12 | 167772199 |
| `Juice 4x12` | Orange 4x12 | 167772201 |
| `Max 4x10` | baixo 4x10 | 167772217 |
| `Ameg 4x10` | Ampeg 4x10 | 167772216 |
| `Ameg 8x10` | Ampeg 8x10 | 167772219 |
| `MessBass 2x10` | baixo Mesa 2x10 | 167772213 |
| `D` | Dreadnought (violão) | 167772220 |
| `Jumbo` | violão jumbo | 167772223 |
| `OM` | violão OM | 167772222 |
| `GA` | violão Grand Auditorium | 167772225 |

CAB params: p0=Level (0–99), p1=High Cut-ish (50–99 observados), demais slots de dados internos — **usar template do modelo de fábrica e alterar só p0/p1 quando necessário**.

## EQ (3 modelos)
| Nome | code | params |
|---|---|---|
| `EQ 1` | 16777269 | p0=Low, p1=Mid, p2=High (-12~+12), p3/p4/Q, p5=Level 50 |
| `EQ 2` | 16777274 | idem |
| `Mess EQ` | 16777276 | EQ estilo Mesa (p3/p4=15) |

## MOD (9 modelos reais)
| Nome real | manual V1.8 | code | params (p0=Rate, p1=Depth 0.5~2.1, p2/p3…) |
|---|---|---|---|
| `A-Chorus` | Chorus/CE-1 | 67108864 | 30/0.5/50 (58 usos — o mais comum) |
| `G-Chorus` | CHO 1x2 | 67108865 | 50/0.5/50 |
| `B-Chorus` | — | 67108872 | 59/0.7/50 |
| `Flanger` | FLNG | 67108881 | 60/0.9/79/11 |
| `Phaser` | Phaser 1/2 | 67108889 | 0.5/0/50/50 |
| `Vibrato` | Vib/U-Vib | 67108885 | 89/2.1 |
| `Vibe` | Uni-Vibe | 67108895 | 49/0.5/0/50 |
| `Opto Trem` | Trem/Pan | 67108897 | 65/1.9 |
| `Sine Trem` | — | 67108902 | 87/0.5/59 |

## DLY (10 modelos reais)
| Nome real | manual V1.8 | code | params (p0=Fdbk %, p1=Delay ms, p2=High Cut…) |
|---|---|---|---|
| `Sweet` | Dly Mono | 184549389 | 25/400/20 (56 usos — padrão) |
| `M-Echo` | Analog | 184549378 | 13/258/26 |
| `M-Echo2` | Dly Dual | 184549388 | 15/659/25/49 |
| `P-Echo` | Ping Pong (mono?) | 184549376 | 18/500/15 |
| `Ping Pong` | Ping Pong | 184549380 | 25/25/4/1 |
| `Slapbk` | — (slapback dedicado) | 184549381 | 11/160/20 |
| `T-Echo` | Tape | 184549387 | 15/415/15 |
| `999 Echo` | — | 184549394 | 65/550/50 |
| `Rev Echo` | — (reverso) | 184549395 | 20/35/500 |
| `Vin-Rack` | — (vinyl rack, tempos múltiplos) | 184549396 | 15/15/500/50/30 |

## RVB (9 modelos reais)
| Nome real | manual V1.8 | code | params (p0=Decay?, p1, p2, p3=?) |
|---|---|---|---|
| `Room` | Room | 201326592 | 20/19/31/0 |
| `Hall` | Hall | 201326593 | 50/50/50/1 (39 usos) |
| `Church` | Church | 201326594 | 25/57/50/0 |
| `Plate` | Plate | 201326595 | 30/40/50/1 (19 usos) |
| `Spring` | Spring | 201326596 | 40/99/50/0 |
| `Clear Sky` | Air | 201326597 | 39/87/0/0 |
| `N-Star` | — | 201326598 | 30/80/0/0 |
| `Deep Sea` | — | 201326599 | 31/49/0/0 |
| `Mod Verb` | — (modulado) | 201326600 | 30/50/85/0 |

## Estrutura do .prst (para geração)
```xml
<GP-100>
  <preset_info software="1.2.0" firmware="2.0" product="GP-100" count="N" platform="WINDOWS" time="..."/>
  <ppIRInfo> (20 entradas ppIRInfo0..19; ppIRNum = 168820736+i, ppIRCRC obrigatório)
  <presets ppBank="0" ppName="..." ppVolume="50" ppID="0" ppBPM="120" ppIRNum="27" ppType="4" ppAuthor="" ppNotes="" ppTypeName="Rock">
    <Effect effectModuleName="PRE" effectName="COMP" effectState="1" effectCode="0" params_0="25" x="0" y="0" params_1=... />
    ... 9 blocos Effect (PRE DST AMP NR CAB EQ MOD DLY RVB), todos presentes
  </presets>
</GP-100>
```
- `ppVolume` 0–99 · `ppBPM` · `ppType`/`ppTypeName` do mapa de gênero · `ppIRNum` = 168820736+slot (0–19) OU um número de IR de fábrica (ex.: 27) · `effectState` "1"=ON "0"=OFF · `x` = posição na cadeia 0–8 · CRLF line endings.
- **Importante**: ppIRCRC dos slots de IR deve ser copiado do export de fábrica (o editor recalcula ao carregar IRs novas).

## Regra de precedência
1. **Export de fábrica** (drenado em `tools/factory-catalog.json` + este documento) — nomes/codes/estrutura
2. `manual.pdf` V1.8 — descrições e "based on"
3. `reference/01–09` — estratégia, ranges humanos e receitas (ajustar nomes para os reais conforme esta tabela)
