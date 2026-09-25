# GP-100 — Glossário e Tradução de Nomes

## Regra nº 1
**Nunca use nomes genéricos ou de outros equipamentos na resposta final.** O usuário vê nomes como `T-S OD`, `UK 800`, `Foxy 30TB` na tela da pedaleira. Traduções deste glossário existem apenas para interpretar o pedido do usuário; a saída SEMPRE usa os nomes oficiais da GP-100.

## Mapeamento "nome comum" → nome oficial GP-100

### Pré-efeitos (PRE)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| compressor / Ross compressor | `COMP` |
| Keeley compressor / comp 4 botões | `COMP4` |
| boost / EP booster / clean boost | `Boost` |
| simulador de violão / acoustic | `AC Sim` |
| touch wah / auto wah por ataque | `T-WAH` |
| auto wah rítmico | `A-WAH` |
| vox wah / wah de pedal | `V-Wah` |
| envelope wah | `C-Wah` |
| octaver / octávio | `OCTA` |

### Distorção (DST)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| Tube Screamer / TS9 / TS808 | `T-S OD` |
| Blues Driver / BD-2 | `BLUES` |
| OD-1 / overdrive amarelo | `OD-1` |
| Eternity / Lovepedal | `LO OD` |
| MXR Distortion+ | `MX Dist` |
| Dist+ / distorção suave | `Dist+` |
| RAT / ProCo | `La Charger` |
| DS-1 / distorção clássica | `SM Dist` |
| Metal Zone / MT-2 | `Darktale` |
| Fuzz Face / fuzz clássico | `Red Haze` |
| Big Muff triangle | `TRI Fuzz` |
| Big Muff ram's head | `BIG Fuzz` |
| Octavia | `OCT Fuzz` |
| Timmy | `Clari OD` |
| Prince of Tone | `PRINC OD` |

> **Fonte dos nomes (DST)**: o catálogo empírico do fw 2.0 (`15-firmware2-effects.md`, extraído do export de fábrica — `data/factory-catalog.json`) é a fonte primária e **vence o manual V1.8** onde divergem. Nomes como `RIP`, `Fat Fuzz`, `D-Zero` e `Metal` existem no manual impresso, mas **não existem no firmware 2.0** (sem `effectCode` — não graváveis em `.prst`); a tabela usa os equivalentes reais do catálogo. Reconciliação completa do legado V1.8 nesta página: #139.

### Amplificadores (AMP)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| Twin Reverb / Fender clean | `Dark Twin` |
| Lone Star clean | `L-Star CL` |
| AC30 normal | `Foxy 30N` |
| AC30 top boost | `Foxy 30TB` |
| Shiva limpo | `BogSV CL` |
| Shiva drive | `BogSV OD` |
| Jazz Chorus / JC-120 | `J-120 CL` |
| Matchless limpo | `Match CL` |
| Matchless sujo | `Match OD` |
| Pendragon limpo | `Knights CL` |
| Pendragon drive | `Knights OD` |
| Maz 38 limpo | `Z38 CL` |
| Maz 38 sujo | `Z38 OD` |
| Hot Cat limpo | `Bad-KT CL` |
| JTM45 / plexi suave | `UK 45` |
| JMP50 / plexi | `UK 50JP` |
| JCM800 | `UK 800` |
| Brown Eye | `Flagman` (BE) / `Flagman+` (canal +) |
| Bassman | `Bellman 59B` |
| Supro / 1624T | `SUPDual OD` |
| Mark II C+ | `Mess2C + 1` / `Mess2C + 2` |
| Mark IV lead | `Mess4 LD` |
| Dual Rectifier vintage | `Mess DualV` |
| Dual Rectifier modern | `Mess DualM` |
| VH4 / Diezel | `Dizz VH` |
| Savage 120 / ENGL | `Eagle 120` |
| 5150 / Peavey | `EV 51` |
| SLO100 / Soldano | `Solo100 LD` |
| Powerball II | `Power LD` |
| Rockerverb / Orange | `Juice R100` |
| Ecstasy blue vintage | `Bog BlueV` |
| Ecstasy blue modern | `Bog RedM` |
| Ampeg B-15 | `B-Mani` |
| SVT | `SVT 40` |
| SVT-VR | `B-MAN500` |
| BassBase 600 | `H-K B15` |
| DI de baixo | `B-DI` |
| fretless | `B-ND` |
| SWR SM-400 | `SWR SM` |
| amp violão 15W | `A-15` |
| amp violão 60W | `A-60` |
| amp violão c/ chorus | `A-CH` |

### Gabinetes (CAB)
Ver tabela completa em `04-cab-ir.md`. Regra: nomes curtos (`1x12 63`, `4x12 GB`, `D`) — nunca dizer "gabinete Marshall Greenback" no patch; dizer `4x12 GB`.

### Modulação (MOD)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| chorus simples | `Chorus` |
| CE-1 / chorus vintage | `CE-1` |
| chorus 2 vozes | `CHO 1x2` |
| flanger jet | `FLNG 1` |
| flanger suave | `FLNG 2` |
| phaser 4 estágios | `Phaser 1` |
| Small Stone / phaser hollow | `Phaser 2` |
| tremolo / panner | `Trem/Pan` |
| vibrato / Uni-Vibe | `Vib/U-Vib` |
| Leslie / rotary | `Rotary` |
| volume swell automático | `AUTOYM` |

### Delay (DLY)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| delay digital / eco | `Dly Mono` |
| delay dual / 2 tempos | `Dly Dual` |
| ping pong | `Ping Pong` |
| delay analógico / DM-2 | `Analog` |
| delay de fita / tape echo | `Tape` |
| delay sincronizado | `Beat` |

### Reverb (RVB)
| O usuário pede | Nome oficial GP-100 |
|---|---|
| sala / ambiente pequeno | `Room` |
| salão / concert | `Hall` |
| igreja / catedral | `Church` |
| placa / estúdio | `Plate` |
| mola / surf | `Spring` |
| ar / brilho | `Air` |

## Parâmetros com nomes não óbvios
| Nome na GP-100 | Significado |
|---|---|
| `PRSE` | Presence (presença/agudos do estágio final) |
| `Thr` | Threshold (do noise gate) |
| `Rel` | Release (do noise gate) |
| `Fdbk` | Feedback (repetições do delay; ressonância do flanger/phaser) |
| `Pre-D` | Pre-delay (do reverb) |
| `Damp` | Damping (absorção de agudos do reverb) |
| `Mix` | Mistura dry/wet |
| `Sust.` | Sustain (fuzz Big Muff) |
| `Char` | Character (ganho do Foxy 30TB: Cool/Hot) |
| `Cut` | Tone Cut (VOX/Dr.Z: **invertido** — alto = escuro) |
| `Bright` | Switch de brilho extra |
| `Sync` | Sincronização com BPM |
| `Doppler` | Intensidade do efeito giratório (Rotary) |
| `Crossov` | Crossover (Rotary) |
| `Direct` | Sinal direto sem efeito (OCTA) |
| `Beat` | Subdivisão rítmica (delay Beat) |

## Nomenclatura de slots
- Presets: **F01–F99** (fábrica), **U01–U99** (usuário).
- IRs de usuário: slots **U40–U59** (20 slots) dentro do bloco CAB.
- IDs de patch do projeto: `XX-YYY-Dnn` (ver `12-workflow.md`).
