# 🎸 Cheap Thrills — Piece of My Heart (1968) — Mapa de patches

### *Janis Joplin (Big Brother & The Holding Company) · 1 música(s) · 2 patches (1 conjunto exclusivo por música)*

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

- **Duas guitarras, dois papéis**: **James Gurley** (o pai da guitarra psicodélica de San Francisco — cerca de 60% dos leads) e **Sam Andrew** (formação clássica, rítmica cravada por trás dele).
- **Guitarra**: **Gibson SG** nos dois — o instrumento padrão da cena de 67–68, citado nominalmente com Gurley e Andrew; Gurley chegou ao SG depois de perder a Les Paul Junior modificada (com o fuzz embutido dentro da guitarra).
- **AMP**: **Fender Twin Reverb** — o amp do álbum para as duas guitarras. O sujo de Sam vem do próprio Twin estourado, não de pedal.
- **Efeitos**: **Maestro FZ-1 (Fuzz Tone)** no Gurley (solos de Summertime e I Need a Man to Love) · **Fender Dimension IV Sound Expander** (eco a óleo — a textura psicodélica dessas duas faixas). Em **Piece of My Heart NÃO há fuzz**: Gurley faz a parte limpa e Sam a parte suja, provavelmente só um Twin estourado.
- **Gravação**: seis meses entre estúdios de Nova York e Los Angeles, base ao vivo e muitas sobreposições; **Ball and Chain** é a única faixa totalmente ao vivo (Winterland — Gurley na Telecaster e Sam na Jazzmaster); disco **#1 por seis semanas**.
- Sem pitch fixo no ensaio: a afinação solta e o vibrato/bend são a assinatura do álbum — não tente imitar com chorus.
- 📖 Fontes: Guitar Player / Jas Obrecht (entrevista de 1978 com Sam Andrew e James Gurley, arquivo FoundSF) · Vintage Guitar, Pop 'N Hiss: Quicksilver Messenger Service (jun/2025 — SG de Gurley e Andrew) · The Gear Page, Big Brother… Fuzz Pedal? (2022, análise com fotos de estúdio) · Equipboard (band page).

## 📥 Importação

1. **GP-100 Edits** (≥ 1.2.0) conectado à pedaleira (firmware 2.1).
2. Importe cada `patches/Janis Joplin/Piece of My Heart (1968)/<Música>/<NOME>/<NOME>.prst` no slot da tabela acima.
3. Sem PC: receita de digitação na seção 8 de cada `patch.md` (sobressalentes incluídos).
4. **Opcional (som de referência)**: carregue os WAVs 📁 da tabela nos slots **User IR 1–4** (GP-100 Edits → IR Manager) e troque o CAB do patch para o User IR correspondente — passo a passo na seção **📡 3** de cada `patch.md`.

---

[`🎸 Biblioteca de patches`](../../README.md) · [`📖 README do projeto`](../../../README.md)
