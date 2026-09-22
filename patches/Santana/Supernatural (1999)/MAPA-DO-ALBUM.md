# 🎸 Supernatural (1999) — Mapa de patches

### *Santana · 1 música(s) · 4 patches (1 conjunto exclusivo por música)*

![Patches](https://img.shields.io/badge/patches-4-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Nomes](https://img.shields.io/badge/nome-MÚSICA--CAMADA-6f42c1?style=flat-square)

> 💡 Cada música tem **seus próprios patches**, divididos nas camadas que ela contém (base, solo, riff, clean, arpejos…). Nomenclatura: `MÚSICA+versão` + `CAMADA` — ex.: `STH01BA` = Something 01, **BA**se · `URM01SL` = Uncle Remus 01, **SL**ide.

## 🗺️ Música → patches

| Música | Patches (camada) | Captador (Strat) | IR recomendada | Slots |
|---|---|---|---|---|
| **Smooth** | [`🔥 SMOO1RI`](./Smooth/SMOO1RI/patch.md) (Riff) · [`✨ SMOO1CL`](./Smooth/SMOO1CL/patch.md) (Base) · [`🎺 SMOO1SO`](./Smooth/SMOO1SO/patch.md) (Solo) · [`🪘 SMOO1FL`](./Smooth/SMOO1FL/patch.md) (Camada) | Riff: middle · Base: middle+neck · Solo: bridge · Camada: middle+bridge | ⚙️ fábrica `L-Star 2x12` · ⚙️ fábrica `L-Star 2x12` · ⚙️ fábrica `Mess-D 4x12` · ⚙️ fábrica `L-Star 2x12` | U63, U64, U65, U66 |

> **📡 IR**: 📁 = o banco local (`impulse_responses/`) tem captura melhor do gabinete real — arquivo indicado na seção 3 do `patch.md`. ⚙️ = o CAB de fábrica já é o alvo correto. Em ambos os casos o `.prst` funciona imediatamente, sem carregar IR.

## 🎛️ Sequência de slots sugerida

| Slot | Patch | Uso | IR (se usar User IR) |
|---|---|---|---|
| U63 | `SMOO1RI` | Smooth — Riff | ⚙️ fábrica `L-Star 2x12` |
| U64 | `SMOO1CL` | Smooth — Base limpa | ⚙️ fábrica `L-Star 2x12` |
| U65 | `SMOO1SO` | Smooth — Solo | ⚙️ fábrica `Mess-D 4x12` |
| U66 | `SMOO1FL` | Smooth — Camada | ⚙️ fábrica `L-Star 2x12` |

## 🧬 Como as camadas foram decididas

Cada faixa foi analisada isoladamente: o que a guitarra faz em cada seção e se o timbre muda entre elas. Só há mais de um patch quando o **timbre muda de verdade** na gravação.

## 📚 Rig real (fontes)

- **Carlos Santana**: PRS Santana signature (humbuckers gordos, sustain longo) direto na **Mesa/Boogie** — o Mark I é o clássico dele desde Woodstock; em estúdio o tom do *Smooth* é o 'gordo e liso' de Mesa com gain moderado.
- **Groove**: riff festonado em Am–D sobre percussão afro (timba/conga); o baixo dokiisha dobra o riff — por isso a base do patch acompanha, não disputa.
- **Solo**: pentatônica menor de Am com frases longas e vibrato largo — sustain de amp + sustain do dedo, sem pedal de distorção extra.
- 📖 Fontes: guitarchalk.com ('Amp Settings for "Smooth"' — PRS Santana + Mesa) · tonesmatch.com (Smooth riff tone) · Supernatural (1999), Arista · Wikipedia.

## 📥 Importação

1. **GP-100 Edits** (≥ 1.2.0) conectado à pedaleira (firmware 2.1).
2. Importe cada `patches/Santana/Supernatural (1999)/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue os WAVs 📁 da tabela nos slots **User IR 1–4** (GP-100 Edits → IR Manager) e troque o CAB do patch para o User IR correspondente — passo a passo na seção **📡 3** de cada `patch.md`.

---

[`🎸 Biblioteca de patches`](../../README.md) · [`📖 README do projeto`](../../../README.md)
