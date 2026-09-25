# GP-100 — Módulo DST (Overdrive / Distorção / Fuzz)
> Página 21 do manual. Um patch usa **um** modelo DST por vez (ou DST OFF). Baseado em pedais clássicos — use os nomes EXATOS da coluna FX Title.
> **Fonte dos nomes**: onde o catálogo empírico do fw 2.0 (`15-firmware2-effects.md`, extraído do export de fábrica) divergir destes nomes do manual V1.8, o catálogo **vence** — ex.: o fw 2.0 não tem `RIP`/`Fat Fuzz`/`D-Zero`/`Metal`; os equivalentes reais são `La Charger`/`Red Haze`/`SM Dist`/`Darktale`. Detalhes em `14-glossario.md` e #139.

## Modelos e parâmetros oficiais

### 1. T-S OD
- **Base**: Tube Screamer®.
- `Gain(0~99)` — saturação.
- `Tone(0~99)` — brilho.
- `Level(0~99)` — volume de saída.

### 2. BLUES
- **Base**: Blues Driver (BD-2).
- `Gain(0~99)`
- `Tone(0~99)`
- `Level(0~99)`

### 3. OD-1
- **Base**: clássico overdrive amarelo (OD-1).
- `Gain(0~99)` — 0~49: timbre cru; 50~99: mais ganho com T-S clipping.
- `Tone(0~99)`
- `Level(0~99)`

### 4. LO OD
- **Base**: Lovepedal® Eternity.
- `Gain(0~99)`
- `Treble(0~99)`
- `Bass(0~99)`
- `Level(0~99)`

### 5. MX Dist
- **Base**: MXR® Distortion+.
- `Gain(0~99)`
- `Color(0~99)` — freq. central da resposta em freq. do EQ.
- `Level(0~99)`

### 6. Dist+
- **Base**: DIST+ (estilo distorção suave).
- `Gain(0~99)`
- `Tone(0~99)`
- `Level(0~99)`

### 7. RIP
- **Base**: ProCo RAT.
- `Gain(0~99)`
- `Color(0~99)` — frequência central da resposta em freq. do EQ.
- `Level(0~99)`

### 8. D-Zero
- **Base**: Distorção Zero (DS-1).
- `Gain(0~99)`
- `Tone(0~99)` — "controla o tom".
- `Level(0~99)`

### 9. Metal
- **Base**: Metal Zone (MT-2).
- `Gain(0~99)`
- `Color(0~99)` — frequência central da resposta em freq. do EQ.
- `Level(0~99)`

### 10. Fat Fuzz
- **Base**: Fuzz clássico.
- `Gain(0~99)`
- `Tone(0~99)`
- `Level(0~99)`

### 11. TRI Fuzz
- **Base**: Fuzz Triangle (Big Muff π versão triangle).
- `Sust.(0~99)` — sustain.
- `Tone(0~99)`
- `Vol(0~99)`

### 12. BIG Fuzz
- **Base**: Fuzz (Big Muff π versão ram's head).
- `Sust.(0~99)`
- `Tone(0~99)`
- `Vol(0~99)`

### 13. OCT Fuzz
- **Base**: Octavia.
- `Tone(0~99)`
- `Dist.(0~99)` — distorção.
- `Level(0~99)`

### 14. Clari OD
- **Base**: Timmy.
- `Bass(0~99)` — controla o nível de graves.
- `Treble(0~99)` — controla o nível de agudos.
- `Gain(0~99)`
- `Level(0~99)`

### 15. PRINC OD
- **Base**: Prince of Tone.
- `High(0~99)` — "ajusta o brilho".
- `Vol(0~99)` — volume de saída.
- `Dist.(0~99)` — distorção.

## Sugestões de uso por estilo (guitarra Strat single coil)

| Estilo | Modelo | Valores iniciais |
|---|---|---|
| Blues quebrado | `BLUES` | Gain 45, Tone 55, Level 65 |
| Blues rock (solo) | `T-S OD` | Gain 35, Tone 60, Level 70 (empurrando o AMP) |
| Rock clássico | `OD-1` | Gain 45–55, Tone 50, Level 65 |
| Indie/alternativo | `LO OD` | Gain 50, Treble 60, Bass 45, Level 65 |
| Rock 70s/garagem | `RIP` | Gain 55, Color 45, Level 60 |
| Punk | `D-Zero` | Gain 70, Tone 55, Level 65 |
| Grunge | `RIP` ou `BIG Fuzz` | Gain 65 / Sust. 60, Tone 45, Vol 60 |
| Metal moderno | `Metal` | Gain 75, Color 50, Level 60 (com AMP high gain) |
| Doom/Stoner | `BIG Fuzz` ou `OCT Fuzz` | Sust. 70/Tone 40/Vol 60 ou Dist. 60 |
| Psychedelic solo | `OCT Fuzz` | Tone 50, Dist. 55, Level 60 |
| Boost de solo | `Clari OD` | Gain 25, Treble 60, Bass 50, Level 75 |
| Country chicken pickin' | `PRINC OD` | High 60, Vol 65, Dist. 25 |

## O que evitar (Evite)
- **T-S OD com Gain ≥ 65**: perde o caráter "mid-hump" e vira distorção genérica — o Tube Screamer brilha entre 25 e 50.
- **Metal com Gain 99**: embola e vira ruído; além de 80 oAttack definido; 60–75 já é agressivo o bastante.
- **Fuzz (TRI/BIG/OCT) antes de compressor**: o ataque compactado mata a textura do fuzz.
- **Fuzz + wah no PRE em cadeia longa**: impedância briga — se ficar estranho, teste wah depois (nesta cadeia fixa, prefira V-Wah e teste ordem efeito a efeito).
- **Level do DST ≥ 80 com AMP já saturado**: clipagem digital na entrada do AMP modelado; mantenha Level 55–70 e compense no Output do AMP.
- **Dist+ e MX Dist juntos com NR muito fechado**: a cauda da distorção é cortada bruscamente — abra o Threshold do NR.
- **Dois drives "empilhados"**: nesta GP-100 só há 1 slot DST; o "empilhamento" deve ser DST + ganho do AMP (ex.: BLUES + UK 800).
