# 20 · Golden set — avaliação dos agentes de pesquisa

> **O que é**: 20 músicas canônicas da biblioteca com a **cadeia esperada** (a
> que o pipeline produziu e a suíte valida). Serve para medir a *qualidade* dos
> agentes `gp100-tone-research` e `gp100-tone-mapper` — hoje os testes cobrem o
> pipeline de dados, não o julgamento musical dos agentes.
>
> **Fonte única**: as cadeias vêm de `tools/patches-defs.json` (campo
> `spec.modules`, estado `on`). Se o defs mudar, regenere a tabela — este doc
> é derivado, como o `patch.md` e o `.prst`. Notação: `BLOCO:Modelo+` (ligado)
> e `BLOCO:Modelo-` (presente, desligado) — a ordem é sempre PRE→DST→AMP→NR→
> CAB→EQ→MOD→DLY→RVB.

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

   **Aprovação**: ≥ 70% dos pontos ponderados, com AMP correto — below that,
   investigue o research (fontes erradas?) antes do mapper (mapeamento errado?).
4. **Registre** o placar na issue/PR da avaliação — o golden set não é teste
   automático: é régua de regressão *musical* para mudanças nos prompts.

## As 20 músicas · 43 patches

### The Beatles — Abbey Road (1969)

| Patch | Cadeia esperada |
|---|---|
| `CT01RIF` | PRE:COMP- DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `CT01VOX` | PRE:Boost+ DST:La Charger+ AMP:Dark Twin- NR:Gate 1+ CAB:J-120 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `STH01BA` | PRE:COMP- DST:Blues OD- AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |
| `STH01SO` | PRE:COMP- DST:Green OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe+ DLY:Sweet- RVB:Hall+ |
| `OHB01BA` | PRE:COMP- DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+ |
| `OHB01SO` | PRE:Boost+ DST:Green OD+ AMP:Foxy 30TB+ NR:Gate 1+ CAB:Foxy 1x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Slapbk+ RVB:Room+ |

### Frank Zappa — One Size Fits All (1975)

| Patch | Cadeia esperada |
|---|---|
| `URM01SL` | PRE:COMP4+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Plate+ |
| `URM01SO` | PRE:COMP- DST:Super OD+ AMP:UK 45+ NR:Gate 1+ CAB:UK-GN 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Room+ |

### Janis Joplin — Pearl (1971)

| Patch | Cadeia esperada |
|---|---|
| `PMH01BA` | PRE:COMP- DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet- RVB:Spring+ |
| `PMH01SO` | PRE:Boost+ DST:Blues OD+ AMP:Dark Twin+ NR:Gate 1+ CAB:DarkTW 2x12+ EQ:EQ 1+ MOD:Vibe- DLY:Sweet- RVB:Spring+ |

### Pink Floyd — The Dark Side of the Moon (1973) e arredores

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

### Nirvana — From the Muddy Banks of the Wishkah (1996)

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
| `SMOO1CL` | PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1+ MOD:A-Chorus+ DLY:Sweet+ RVB:Room+ |
| `SMOO1SO` | PRE:COMP+ DST:Yellow OD+ AMP:Solo100 LD+ NR:Gate 1+ CAB:Mess-D 4x12+ EQ:EQ 1+ MOD:A-Chorus- DLY:Sweet+ RVB:Plate+ |
| `SMOO1FL` | PRE:COMP+ DST:Blues OD- AMP:L-Star CL+ NR:Gate 1+ CAB:L-Star 2x12+ EQ:EQ 1- MOD:A-Chorus- DLY:Sweet+ RVB:Room+ |

## Cobertura intencional do set

- **Escolas inteiras**: Beatles (groove/vox), Floyd (espaço/ambiência), Nirvana
  (punk limpo↔pesado na mesma cadeia), Santana (latin blues), Janis (blues
  rock), Zappa (híbrido experimental).
- **Dilemas clássicos de mapeamento**: Twin limpo × Crunch (STH01), mesmo amp
  com drive diferente (DRY01 AR/RI), chorus ligado só no limpo (SLT01CL),
  seções que só trocam estado de bloco (CT01 RI/VOX).
- **Armadilhas**: `POL01CL` é o único clean com MOD **desligado**; `SOF01EC`
  desliga NR (ambiente de estúdio); `URM01SL` usa COMP4 (não COMP).

> Manutenção: regenere as tabelas a partir do defs quando um patch mudar —
> a suíte não cobre este doc (é régua de avaliação, não artefato do pipeline).

---

[`📖 README do projeto`](../README.md) · [`📚 Reference`](README.md) · [`🤖 Agentes`](../.agents/README.md)
