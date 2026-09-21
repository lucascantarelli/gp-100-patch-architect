# GP-100 — Módulo PRE (pré-efeitos)
> Páginas 17–20 do manual. O PRE é o primeiro bloco da cadeia. Um patch usa **um** modelo PRE por vez.

## Modelos e parâmetros oficiais

### 1. COMP
- **Base**: Ross® Compressor.
- **Parâmetros**:
  - `Sens(0~99)` — sensibilidade: quanto mais alto, mais sinal aciona a compressão.
  - `Attack(0~99)` — tempo de ataque da compressão (0 = mais rápido/agressivo).
  - `Sustain(0~99)` — quantidade de sustain adicionado.
  - `Level(0~99)` — volume de saída do compressor.

### 2. COMP4
- **Base**: Keeley® C4 Compressor.
- **Parâmetros**:
  - `Sens(0~99)`
  - `Level(0~99)`
  - `Attack(0~99)`
  - `Tone(0~99)` — brilho aplicado ao sinal comprimido.

### 3. Boost
- **Base**: pedal EP Booster®.
- **Parâmetros**:
  - `Gain(0~99)` — quantidade de ganho.
  - `Boost(0~99)` — volume do boost.
  - `EQ(0~99)` — ajuste de equalização do boost.

### 4. AC Sim
- **Base**: simulação de violão/acústico.
- **Parâmetros**:
  - `Body(0~99)` — corpo do acústico.
  - `Top(0~99)` — brilho.
  - `Vol(0~99)` — volume.
  - `Mode(STD/Jumbo/ENH/Piezo)` — tipo de corpo acústico simulado.

### 5. T-WAH
- **Base**: auto-wah sensível ao toque (Touch Wah).
- **Parâmetros**:
  - `Sens(0~99)`
  - `Freq(0~99)` — frequência central do wah.
  - `Q(0~99)` — ressonância/abertura do filtro.
  - `Mode(Down/Up)` — direção da varredura do filtro.

### 6. A-WAH
- **Base**: auto-wah rítmico.
- **Parâmetros**:
  - `Sync(0~99)` — sincronização com o BPM do patch.
  - `Speed(0~99)` — velocidade da varredura.
  - `Q(0~99)` — ressonância do filtro.

### 7. V-Wah
- **Base**: wah de voz (vox-style), controlável pelo pedal EXP.
- **Parâmetros**:
  - `Range(0~99)` — amplitude da varredura.
  - `Q(0~99)` — ressonância.
  - `Vol(0~99)` — volume de saída.

### 8. C-Wah
- **Base**: wah por envelope do sinal.
- **Parâmetros**:
  - `Range(0~99)`
  - `Q(0~99)`
  - `Vol(0~99)`

### 9. OCTA
- **Base**: octaver polifônico.
- **Parâmetros**:
  - `Oct1(-12~0)` — oitava abaixo (sub-oitava).
  - `Oct2(-24~-12)` — duas oitavas abaixo.
  - `Direct(0~99)` — nível do sinal direto (sem oitavas).

## Sugestões de uso por estilo
- **Pop/Funk/Soul (Strat)**: `COMP` Sens 55–70, Attack 30–50, Sustain 40–60, Level 65 — attack "padrão Nashville". Alternativa moderna: `COMP4` para compressão mais limpa com Tone 50–60.
- **Blues clean**: `COMP` leve (Sens 35–45, Sustain 30) para sustain sem tirar dinâmica; ou nenhum PRE e deixar o AMP trabalhar.
- **Solo/levante**: `Boost` (Gain 30, Boost 45) na frente de AMP crunch para empurrar o canal.
- **Violaão/aproximação acústica**: `AC Sim` com Body 55, Top 65, Mode STD (Jumbo para mais corpo; ENH para dedilhado; Piezo para timbre mais "captador embutido").
- **Funk clássico**: `T-WAH` Sens 60, Freq 55, Q 50, Mode Up.
- **Funk/PSYCH agressivo**: `A-WAH` Speed 60, Q 55, Sync conforme BPM.
- **Expressivo (solos tipo Hendrix/Clapton)**: `V-Wah` controlado pelo pedal EXP (Range 60, Q 55).
- **Doom/Stoner/Sludge**: `OCTA` Oct1 -12, Direct 60 para engrossar riffs.

## O que evitar (Evite)
- **COMP com Sustain ≥ 75 + AMP alto ganho**: bombeamento ("pumping") e ruído amplificado — em single coils isso expõe chiado do braço da guitarra.
- **COMP antes de DST com Sens muito alta**: o compressor "achata" o sinal e a distorção fica sem dinâmica (som de "zumbido").
- **T-WAH/A-WAH com Q no máximo (99)**: apito/ressonância desagradável; fique abaixo de 70.
- **Boost com Gain ≥ 70**: deixa de ser boost vira quase um drive sujo — para limpeza use Gain ≤ 40.
- **OCTA com Direct ≤ 30**: o som original desaparece e sobra só o sub — use Direct ≥ 50.
- **AC Sim antes de distorção forte**: soa artificial; AC Sim foi feito para CAB neutro e MOD leve.
- **Esquecer Level do COMP mais alto que o bypass**: efeito "volume mágico" ao ligar/desligar; iguale o volume (Level 60–70).
