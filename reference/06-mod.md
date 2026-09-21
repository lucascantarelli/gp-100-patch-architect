# GP-100 — Módulo MOD (modulação)
> Páginas impressas 28–29 do manual. 11 modelos. Um patch usa **um** MOD por vez (ou MOD OFF). Nomes EXATOS.

## Modelos e parâmetros oficiais

### 1. Chorus
- Base: boss chorus clássico (CE-2).
- `Depth(0~99)` — profundidade do efeito.
- `Rate(0~99)` — velocidade.
- `Mix(0~99)` — mistura do sinal com efeito (0 = 100% dry).

### 2. CE-1
- Base: Boss CE-1 (chorus ensemble vintage, com preamp).
- `Mode(Vibrato/Chorus)` — Vibrato = só sinal modulado; Chorus = dry + modulado.
- `Intensity(0~99)`
- `Level(0~99)`

### 3. CHO 1x2
- Base: Johnson 2-voice chorus.
- `Depth(0~99)`
- `Rate(0~99)`
- `Mix(0~99)`
- `Q(0~99)` — largura/definição do segundo delay interno.

### 4. FLNG 1
- Base: Johnson flanger (estilo MXR/ADA).
- `Depth(0~99)`
- `Rate(0~99)`
- `Fdbk(0~99)` — feedback (quanto maior, mais metálico/jet).
- `Manual(0~99)` — atraso mínimo (desloca o "cor" do jet).
- `Mix(0~99)`

### 5. FLNG 2
- Base: Johnson flanger variante (post-mix, mais suave).
- `Depth(0~99)`
- `Rate(0~99)`
- `Fdbk(0~99)`
- `Manual(0~99)`
- `Mix(0~99)`

### 6. Phaser 1
- Base: Johnson phaser (estilo MXR Phase 100).
- `Speed(0~99)`
- `Range(0~99)` — largura da varredura de fase.
- `Fdbk(0~99)` — coloração/ressonância.
- `Level(0~99)`

### 7. Phaser 2
- Base: Johnson phaser variante (estilo Small Stone, mais "hollow").
- `Speed(0~99)`
- `Range(0~99)`
- `Fdbk(0~99)`
- `Level(0~99)`

### 8. Trem/Pan
- Base: Johnson tremolo/panner.
- `Type(Tremolo/Panning)` — Tremolo = volume oscila nos dois canais; Panning = alterna L/R.
- `Speed(0~99)`
- `Depth(0~99)`

### 9. Vib/U-Vib
- Base: Johnson vibrato / Uni-Vibe.
- `Type(Vibrato/Chorus)` — Vibrato = afinação oscila; Chorus = efeito "giratório" do Uni-Vibe.
- `Speed(0~99)`
- `Depth(0~99)`

### 10. Rotary
- Base: Johnson rotary speaker (Leslie).
- `Speed(Slow/Fast)` — alterna velocidade do rotor.
- `Doppler(0~99)` — intensidade do efeito doppler/desvio.
- `Depth(0~99)`
- `Crossov(0~99)` — crossover dividindo rotor grave/agudo.

### 11. AUTOYM
- Base: auto volume swells ( envelope automático).
- `Speed(0~99)` — velocidade do swell.
- `Depth(0~99)` — profundidade do corte/retorno de volume.

## Guia de estilo (Strat single coil)

| Estilo | Modelo | Startpoint |
|---|---|---|
| Clean pop/indie | `Chorus` | Depth 40, Rate 30, Mix 45 |
| Chorus anos 80 (The Police, The Cure) | `CE-1` | Mode Chorus, Intensity 55, Level 60 |
| Chorus "grande" (2 vozes) | `CHO 1x2` | Depth 50, Rate 25, Mix 50, Q 40 |
| Grunge/alternativo (AIW) | `FLNG 1` | Depth 55, Rate 20, Fdbk 55, Manual 45, Mix 50 |
| Jet agressivo (Van Halen) | `FLNG 2` | Depth 60, Rate 30, Fdbk 65, Manual 50, Mix 55 |
| Funk/psych 60s | `Phaser 1` | Speed 35, Range 55, Fdbk 40, Level 60 |
| Uni-Vibe (Hendrix, Robin Trower) | `Vib/U-Vib` | Type Chorus, Speed 30, Depth 60 |
| Country/rockabilly | `Trem/Pan` | Type Tremolo, Speed 40, Depth 45 |
| Ambiente/cinema | `Rotary` | Speed Slow, Doppler 55, Depth 55, Crossov 50 |
| Ambient/EDM swells | `AUTOYM` | Speed 45, Depth 65 |

## O que evitar (Evite)
- **Mix/Depth ≥ 75 com distorção**: a modulação vira "lavagem" e o riff perde definição; em hi-gain use Depth 25–40, Mix 30–40.
- **Rate/Speed ≥ 70** em chorus/phaser: efeito de helicóptero; reservado para efeitos pontuais.
- **Fdbk ≥ 70 no flanger**: auto-oscilação que não para; fique ≤ 65 exceto efeito proposital.
- **CE-1 em Mode Vibrato com Level alto**: salto de volume; iguale o Level ao bypass (60±5).
- **Trem/Pan Type Panning no fone**: o som "pula" de um ouvido pro outro e enjoa; para fone use Tremolo.
- **Rotary com Doppler ≥ 80 + reverb**: voa; é ambient extremo, não timbre de banda.
- **MOD antes de pensar no ritmo**: Speed/Rate devem casar com o BPM (ex.: Rate 30 ≈ 8th notes lentas em 120 BPM).
