# 🎸 Apostrophe (’) (1974) — Mapa de patches

### *Frank Zappa · 1 música(s) · 2 patches (1 conjunto exclusivo por música)*

![Patches](https://img.shields.io/badge/patches-2-e02d2d?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Nomes](https://img.shields.io/badge/nome-MÚSICA--CAMADA-6f42c1?style=flat-square)

> 💡 Cada música tem **seus próprios patches**, divididos nas camadas que ela contém (base, solo, riff, clean, arpejos…). Nomenclatura: `MÚSICA+versão` + `CAMADA` — ex.: `STH01BA` = Something 01, **BA**se · `URM01SL` = Uncle Remus 01, **SL**ide.

## 🗺️ Música → patches

| Música | Patches (camada) | Captador (Strat) | IR recomendada | Slots |
|---|---|---|---|---|
| **Uncle Remus** | [`🛞 URM01SL`](./Uncle%20Remus/URM01SL/patch.md) (Slide) · [`🔪 URM01SO`](./Uncle%20Remus/URM01SO/patch.md) (Solo) | Slide: bridge · Solo: bridge | 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` · 📁 `British Straight 4x12 — British Straight 4x12 Medium Mix.wav` | U21, U22 |

> **📡 IR**: 📁 = o banco local (`impulse_responses/`) tem captura melhor do gabinete real — arquivo indicado na seção 3 do `patch.md`. ⚙️ = o CAB de fábrica já é o alvo correto. Em ambos os casos o `.prst` funciona imediatamente, sem carregar IR.

## 🎛️ Sequência de slots sugerida

| Slot | Patch | Uso | IR (se usar User IR) |
|---|---|---|---|
| U21 | `URM01SL` | Uncle Remus — Slide (base) | 📁 `American Twin 2x12 — American Twin 2x12 Medium Mix.wav` |
| U22 | `URM01SO` | Uncle Remus — Solo | 📁 `British Straight 4x12 — British Straight 4x12 Medium Mix.wav` |

## 🧬 Como as camadas foram decididas

Cada faixa foi analisada isoladamente: o que a guitarra faz em cada seção e se o timbre muda entre elas. Só há mais de um patch quando o **timbre muda de verdade** na gravação.

## 📚 Rig real (fontes)

- **Tony Duran**: slide/rhythm guitar (créditos de Apostrophe ('); MusicBrainz) — brilho agudo com ataque crocante.
- **Frank Zappa**: solos cirúrgicos e secos (Rock & Roll Globe: "scalpel-sharp guitar solos") — sem reverb, médios à frente.
- **George Duke**: piano elétrico e clavinet preenchendo o meio (co-autor da faixa).
- Sessões: basic track 1972 (Paramount Studios, LA) + overdubs 1973–74.
- 📖 Fontes: Rock & Roll Globe ("How Frank Zappa Embraced the Mainstream with Apostrophe (')", 2024) · MusicBrainz (créditos) · Wikipedia (Apostrophe (')).

## 📥 Importação

1. **GP-100 Edits** (≥ 1.2.0) conectado à pedaleira (firmware 2.1).
2. Importe cada `patches/Frank Zappa/Apostrophe (1974)/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue os WAVs 📁 da tabela nos slots **User IR 1–4** (GP-100 Edits → IR Manager) e troque o CAB do patch para o User IR correspondente — passo a passo na seção **📡 3** de cada `patch.md`.

---

[`🎸 Biblioteca de patches`](../../README.md) · [`📖 README do projeto`](../../../README.md)
