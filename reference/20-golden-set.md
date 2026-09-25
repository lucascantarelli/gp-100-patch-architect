# 20 · Golden set — avaliação dos agentes de pesquisa



> **O que é**: o recorte canônico da biblioteca (uma seleção de músicas por

> álbum) com a **cadeia esperada** (a que o pipeline produziu e a suíte

> valida). Serve para medir a *qualidade* dos agentes `gp100-tone-research` e

> `gp100-tone-mapper` — hoje os testes cobrem o pipeline de dados, não o

> julgamento musical dos agentes.

>

> **Fonte**: a região entre as marcas `gerado:inicio`/`gerado:fim` é

> **derivada** pelo `gp100 build` (passo `golden_set`): as cadeias vêm do

> `spec.modules` do defs e a **seleção** (quais músicas formam a régua) do

> dado versionado `data/golden-set.json`. Notação: `BLOCO:Modelo+` (ligado)

> e `BLOCO:Modelo-` (presente, desligado) — a ordem é sempre PRE→DST→AMP→

> NR→CAB→EQ→MOD→DLY→RVB. A prosa deste doc (regras, placar, fontes) é

> editorial e não é tocada pelo build.



## Como usar



1. **Cegue o avaliado**: dê ao `gp100-tone-research` → `gp100-tone-mapper`

   apenas o nome da música/artista (não o patch existente).

2. **Compare** a cadeia mapeada com a esperada abaixo, bloco a bloco.

3. **Pontue** (o que define o "timbre" pesa mais):



   | Bloco | Peso | Por quê |

   |---|---|---|

   | AMP | ×2 | a alma do timbre |

   | DST, CAB | ×1 | caráter de drive e caixa |

   | PRE, MOD, DLY, RVB, NR, EQ | ×0,5 | acabamento |



   **Casamento do modelo** (quanto do peso o bloco ganha): modelo exato =

   100% · família com o mesmo "Based on" no catálogo (UK 45↔UK 50JP,

   Foxy 30TB↔Foxy 30N, Flagman↔Flagman+, DarkTW 2x12↔Dark 1x12…) = 60% ·

   mesma classe de caráter (overdrive/distorção/fuzz; clean-americano,

   rock-britânico, caixa-americana…) = 30% · **estado do bloco errado

   (ligado/desligado) = 0**, qualquer que seja o modelo.



   **Aprovação**: ≥ 70% dos pontos ponderados, com AMP correto — below that,

   investigue o research (fontes erradas?) antes do mapper (mapeamento errado?).

4. **Registre** o placar na issue/PR da avaliação — o golden set não é teste

   automático: é régua de regressão *musical* para mudanças nos prompts.



## O recorte · 7 álbuns representados



<!-- gerado:inicio (gp100 build — não editar; fonte: data/golden-set.json + data/defs) -->

> 23 músicas · 50 patches · 7 álbum(ns) — derivado do defs pelo `gp100 build`.

### The Beatles — Abbey Road (1969)

| Patch | Cadeia esperada |
|---|---|
| `CT01RIF` | PRE:COMP- DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `CT01VOX` | PRE:Boost+ DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `STH01BA` | PRE:COMP- DST:Blues OD- AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `STH01SO` | PRE:COMP- DST:Green OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Sweet- RVB:Hall+ |
| `OHB01BA` | PRE:COMP- DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+ |
| `OHB01SO` | PRE:Boost+ DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+ |

### Frank Zappa — Apostrophe (’) (1974)

| Patch | Cadeia esperada |
|---|---|
| `URM01SL` | PRE:COMP4+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Plate+ |
| `URM01SO` | PRE:COMP- DST:Super OD+ AMP:UK 45+ NR:Gate 1+ CAB:UK-GN 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |

### Janis Joplin (Big Brother & The Holding Company) — Cheap Thrills — Piece of My Heart (1968)

| Patch | Cadeia esperada |
|---|---|
| `PMH01BA` | PRE:COMP- DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Spring+ |
| `PMH01SO` | PRE:Boost+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe- DLY:Sweet- RVB:Spring+ |

### Pink Floyd — Pulse (1995)

| Patch | Cadeia esperada |
|---|---|
| `SOF01EC` | PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `SOF01BA` | PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Hall+ |
| `SOF01SO` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `TM01BA` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+ |
| `TM01SO` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `MNY01BA` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet- RVB:Plate+ |
| `MNY01SO` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `WYWH01IN` | PRE:Boost- DST:Blues OD- AMP:Knights CL+ NR:Gate 1- CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+ |
| `CNW01SO` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `CNW01S2` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |
| `RLH01RI` | PRE:Boost- DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Plate+ |
| `RLH01SO` | PRE:Saturate+ DST:Blues OD- AMP:Flagman+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Hall+ |

### Nirvana — Muddy Banks (1996)

| Patch | Cadeia esperada |
|---|---|
| `WIS01AM` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `SCH01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `SCH01SO` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `DRY01AR` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+ |
| `DRY01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `DRY01SO` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `ANE01AR` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+ |
| `ANE01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `ANE01SO` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `SLT01CL` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+ |
| `SLT01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `SLT01SO` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `LIT01AR` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+ |
| `LIT01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `LIT01SO` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `HSB01AR` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Slapbk- RVB:Room+ |
| `HSB01RI` | PRE:Boost- DST:La Charger+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |
| `POL01CL` | PRE:Boost- DST:La Charger- AMP:Dark Twin+ NR:Gate 1- CAB:DarkTW 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Slapbk- RVB:Room+ |

### Santana — Supernatural (1999)

| Patch | Cadeia esperada |
|---|---|
| `SMOO1RI` | PRE:COMP+ DST:Yellow OD+ AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `SMOO1CL` | PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1- MOD:A-Chorus+ DLY:Sweet+ RVB:Room+ |
| `SMOO1SO` | PRE:COMP+ DST:Yellow OD+ AMP:Solo100 LD+ NR:Gate 1+ CAB:Mess-D 4x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet+ RVB:Plate+ |
| `SMOO1FL` | PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+ |

### The Jimi Hendrix Experience — Are You Experienced — Jimi Hendrix (1967)

| Patch | Cadeia esperada |
|---|---|
| `FOXY01BA` | PRE:Boost+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate+ |
| `FOXY01SO` | PRE:Boost+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate+ |
| `PURP01BA` | PRE:COMP- DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:M-Echo- RVB:Plate- |
| `PURP01SO` | PRE:Saturate+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:M-Echo- RVB:Plate- |
| `WIND01BA` | PRE:COMP+ DST:Red Haze- AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe+ DLY:M-Echo- RVB:Spring+ |
| `WIND01SO` | PRE:COMP+ DST:Red Haze+ AMP:UK 45+ NR:Gate 1+ CAB:UK-LD 4x12+ EQ:EQ 1+ MOD:Vibe- DLY:T-Echo+ RVB:Spring+ |

<!-- gerado:fim -->

## Cobertura intencional do set



- **Escolas inteiras**: Beatles (groove/vox), Floyd (espaço/ambiência), Nirvana

  (punk limpo↔pesado na mesma cadeia), Santana (latin blues), Janis (blues

  rock), Zappa (híbrido experimental), Hendrix (fuzz psicodélico + octávio).

- **Dilemas clássicos de mapeamento**: Twin limpo × Crunch (STH01), mesmo amp

  com drive diferente (DRY01 AR/RI), chorus ligado só no limpo (SLT01CL),

  seções que só trocam estado de bloco (CT01 RI/VOX).

- **Armadilhas**: `POL01CL` é o único clean com MOD **desligado**; `SOF01EC`

  desliga NR (ambiente de estúdio); `URM01SL` usa COMP4 (não COMP);

  `PURP01BA` deixa o RVB **desligado** (a secura do disco); `WIND01SO`

  troca M-Echo por **T-Echo** (tape, não digital); `Red Haze` é o fuzz

  específico do Hendrix no catálogo fw 2.0 — não confundir com fuzz genérico.



> Manutenção: a região entre as marcas é regenerada pelo `gp100 build`

> (passo `golden_set`) e o **guarda de sincronia vigia este doc** — mudou o

> defs ou a seleção (`data/golden-set.json`), o build regenera; editou a

> região à mão, o teste reprova. Para mudar a régua (quais músicas entram),

> edite `data/golden-set.json` e rode o build. O linter de docs (#58, regra 7)

> cruza contagens literais com a derivação do ADR-0014 (`/stats/`, badges) —

> aqui elas são do recorte, não da biblioteca.



## Placar · rodada 2026-09 (baseline)



> **Método (honestidade antes de glória)**: sem credencial de spawn no

> ambiente de avaliação, os dossiês do `gp100-tone-research` foram

> **protocolados** com o procedimento oficial do agente (2–4 buscas por

> âncora: rig da era, breakdown da música; fontes registradas abaixo) e o

> `gp100-tone-mapper` **simulado** bloco a bloco a partir do dossiê, usando

> só as fontes obrigatórias do agente (doc 15, "Based on" dos docs 02/03,

> doc 14, doc 04) e as regras de adaptação do sistema (Squier single coils).

> É **baseline de método e régua**, não avaliação end-to-end do modelo

> `z-ai/glm-5.3-flash` — a rodada real de spawn segue quando houver

> credencial (ver "Próxima rodada"). O cálculo é mecanizado: cadeias como

> dados + regras de casamento em script (`scripts/placar-golden-set.py`),

> zero aritmética manual — o mesmo princípio da derivação do ADR-0014.



**Regras aplicadas**: exato 100% · família 60% · classe 30% · estado

errado = 0; pesos AMP ×2 · DST/CAB ×1 · resto ×0,5; aprovação = ≥70% e AMP

exato/família.



**Global: 313,8/350 = 89,7% · 48/50 patches aprovados.**



| Bloco | Placar | % | Agente dominante |

|---|---|---|---|

| AMP | 99,2/100 | **99,2%** | mapper |

| EQ | 24,5/25 | 98,0% | mapper |

| CAB | 48,0/50 | 96,0% | mapper |

| RVB | 24,0/25 | 96,0% | research+mapper |

| NR | 23,5/25 | 94,0% | mapper |

| DLY | 21,0/25 | 84,0% | research+mapper |

| PRE | 19,0/25 | 76,0% | mapper |

| MOD | 18,5/25 | 74,0% | mapper |

| DST | 36,1/50 | **72,2%** | mapper |



| Escola | Placar | % | Aprovados |

|---|---|---|---|

| Santana | 28,0/28 | 100,0% | 4/4 |

| Nirvana | 119,0/126 | 94,4% | 18/18 |

| Hendrix | 37,5/42 | 89,3% | 6/6 |

| Floyd | 72,5/84 | 86,3% | 12/12 |

| Janis | 12,0/14 | 85,7% | 2/2 |

| Zappa | 11,8/14 | 84,3% | 1/2 |

| Beatles | 33,0/42 | 78,6% | 5/6 |



**Leitura por agente** (o que cada um teria que melhorar):



- `gp100-tone-mapper` (AMP 99% mas **DST 72% e MOD 74%**): os erros

  concentram-se onde o catálogo é ambíguo — `La Charger` (doc 14 manda

  `RIP` para RAT; o próprio prompt do agente manda `La Charger`, que o

  catálogo fw 2.0 descreve como RAT-style) e fuzz clássico (`Fat Fuzz` do

  doc 14 × `Red Haze` "based on Fuzz Face" do doc 15). Conflito de fonte

  documentado — resolver no doc 14 (glossário) é alavanca direta de placar.

  `M-Echo` × `Slapbk` no espaço de Hendrix: o tape echo real (Binson/EP-3

  da era) pede `T-Echo`/`M-Echo`, mas a cultura "slapback curto" empurra

  para `Slapbk` — calibrar no doc 08 (DLY).

- `gp100-tone-research` (PRE 76% e estados): não distingue compressor de

  boost nos timbres de estúdio dos anos 60/70 (Twins pré-drive = COMP no

  defs) e leva o Small Clone do Cobain para camadas onde o defs o mantém

  desligado. Ambos são melhoráveis com instrução, não com pesquisa: é o

  tipo de erro que o doc de dossiê deve antecipar ("amp de estúdio limpo →

  considerar COMP em vez de Boost").

- Ambos (DLY 84%): slapback como padrão americano vs `Sweet` como padrão

  da biblioteca — a convenção de defaults do pipeline (doc 08) deveria

  estar no systemPrompt do mapper.



**Fontes do research** (por âncora): Abbey Road — Recording The Beatles

(Kehew & Ryan, via tdpri: Fender Twins nos cortes de 1969) × reputação Vox

AC30/EF86 (boostguitarpedals, equipboard) → confiança média, exatamente o

caso que o agente deve marcar como divergente. Apostrophe — Equipboard/

GuitarPlayer (Pignose modificado + Marshall JMP; SG Baby Snakes). Cheap

Thrills — entrevista Sam Andrew & James Gurley 1978 (FoundSF: "Fenders,

Twin Reverbs a lot") + Gear Page (SG + Maestro FZ-1 no solo de

Combination of the Two). DSOTM — gilmourish (settings por faixa),

guitar.com, faderandknob (Big Muff Pi → Hiwatt DR103, Binson Echorec).

Muddy Banks — livenirvana.com/equipment (rig ao vivo: Twin/Mesa + power

amp Crown/Crest), equipboard (DS-1, Small Clone, RAT). Supernatural —

ToneStakr/boogieforum/ultimatesantana (PRS + Mesa Mark IV, Dumble como

overdrive moderno; Soldano citado no timbre de lead). AYE — o dossiê do

próprio defs (Guitar World 2017, Equipboard, Roger Mayer: JTM45 combo,

Fuzz Face, Octavia, Strat invertida).



**Próxima rodada**: repetir com spawn real (Freebuff com credencial),

mantendo o cegamento e o scorer — o delta simulado × real mede o efeito

modelo; e resolver os conflitos doc 14 × prompt do mapper (`RAT`, fuzz)

antes, para o placar medir o agente e não a contradição das fontes.



---

