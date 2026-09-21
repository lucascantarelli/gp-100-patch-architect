# 📁 Banco local de IRs

Aqui vivem os **packs de Impulse Response** baixados — a camada que a política do projeto consulta **antes** de procurar na internet (política completa: fábrica no `.prst` → banco local → internet → fallback fábrica; ver seção 📡 3 de cada `patch.md`).

## 📥 Como acrescentar packs

```bash
# 1. Extraia o pack em uma subpasta com o nome do pack:
#    impulse_responses/<Nome do Pack>/<gabinetes>/<arquivos>.wav

# 2. Reindexe (valida cada WAV e regenera os catálogos):
python tools/ir_library.py
```

Os agentes consultam `tools/ir-library.json` e `reference/16-ir-library.md` — se a captura já existe aqui, **não pesquisam na internet**.

## ✅ Formato aceito pela GP-100

| Exigência | Valor |
|---|---|
| Canais | **Mono** (1 canal) |
| Profundidade | **24 bits** |
| Taxa | **44,1 kHz** (pastas 48/96 kHz de um mesmo pack são as mesmas capturas — use sempre a 44.1) |
| Tamanho | O editor aparar em **1024 samples** (~23 ms) ao carregar; a cauda longa ("room") é descartada — normal para cab IR |

## 📦 Conteúdo atual

- **Origin Effects — IR-Cab Library V3** (gratuita; cadastro no site) — 291 WAVs em 9 gabinetes, incluindo os alvos dos patches: `American Twin 2x12` (Twin/JBL), `British Straight 4x12` (Marshall), `Brown Deluxe 1x12` (AC30), `Tweed Combo 1x12` (Bassman).

**Quer mais?** Packs gratuitos recomendados por lacuna (metal, V30 mix-ready, baixo…): [`reference/17-free-ir-packs.md`](../reference/17-free-ir-packs.md).

## 🔌 Como carregar na pedaleira

1. Conecte a pedaleira e abra o **GP-100 Edits** → **IR Manager / User IR**.
2. Escolha o **slot (1–20)** e carregue o `.wav`.
3. No patch: bloco **CAB** → navegue até `User IR n` → ajuste **Low Cut / High Cut / Level** (sugestões na seção 📡 3 de cada `patch.md`).

---

[`📖 README do projeto`](../README.md) · [`📚 reference/16-ir-library.md`](../reference/16-ir-library.md) · [`🎸 patches/`](../patches/README.md)
