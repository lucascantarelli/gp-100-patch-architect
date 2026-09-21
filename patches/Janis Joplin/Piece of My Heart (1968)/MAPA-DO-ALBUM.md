# 🎸 Cheap Thrills — Piece of My Heart (1968) — Mapa de patches

### *Janis Joplin · 1 música(s) · 2 patches (1 conjunto exclusivo por música)*

![Patches](https://img.shields.io/badge/patches-2-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Nomes](https://img.shields.io/badge/nome-MÚSICA--CAMADA-6f42c1?style=flat-square)

> 💡 Cada música tem **seus próprios patches**, divididos nas camadas que ela contém (base, solo, riff, clean, arpejos…). Nomenclatura: `MÚSICA+versão` + `CAMADA` — ex.: `STH01BA` = Something 01, **BA**se · `URM01SL` = Uncle Remus 01, **SL**ide.

## 🗺️ Música → patches

| Música | Patches (camada) | Captador (Strat) | IR recomendada | Slots |
|---|---|---|---|---|
| **Piece of My Heart** | [`💔 PMH01BA`](./Piece%20of%20My%20Heart/PMH01BA/patch.md) (Base) · [`⚡ PMH01SO`](./Piece%20of%20My%20Heart/PMH01SO/patch.md) (Solo) | Base: posição 4 · Solo: bridge | 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` · 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` | U23, U24 |

> **📡 IR**: 📁 = o banco local (`impulse_responses/`) tem captura melhor do gabinete real — arquivo indicado na seção 3 do `patch.md`. ⚙️ = o CAB de fábrica já é o alvo correto. Em ambos os casos o `.prst` funciona imediatamente, sem carregar IR.

## 🎛️ Sequência de slots sugerida

| Slot | Patch | Uso | IR (se usar User IR) |
|---|---|---|---|
| U23 | `PMH01BA` | Piece of My Heart — Base | 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` |
| U24 | `PMH01SO` | Piece of My Heart — Solo | 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` |

## 🧬 Como as camadas foram decididas

Cada faixa foi analisada isoladamente: o que a guitarra faz em cada seção e se o timbre muda entre elas. Só há mais de um patch quando o **timbre muda de verdade** na gravação.

## 📚 Rig real do álbum (fontes)

- **John**: Casino (P90) — Come Together direto no canal da mesa; AC30 no crunch; Leslie nos lentos.
- **George**: Les Paul **Lucy**, Strat e Tele — Twin/Bassman/AC30; **Leslie 147RV** nos solos de Something/Because/Sun King.
- **Paul**: Casino no AC30 (Oh! Darling), baixo no resto; primeiro solo de The End.
- **Zero pedais** — todo ganho vem de amp estufado ou do canal da mesa.
- 📖 Fontes: Guitar World *"Abbey Road guitar gear: the complete guide"* (Geoff Emerick) · boostguitarpedals.co.uk.

## 📥 Importação

1. **GP-100 Edits** (≥ 1.2.0) conectado à pedaleira (firmware 2.1).
2. Importe cada `patches/<Banda>/Cheap Thrills — Piece of My Heart (1968)/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue os WAVs 📁 da tabela nos slots **User IR 1–4** (GP-100 Edits → IR Manager) e troque o CAB do patch para o User IR correspondente — passo a passo na seção **📡 3** de cada `patch.md`.

---

[`🎸 Biblioteca de patches`](../../README.md) · [`📖 README do projeto`](../../../README.md)
