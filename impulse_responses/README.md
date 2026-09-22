# 📁 Banco local de IRs

Aqui vivem os **packs de Impulse Response** baixados — a camada que a política do projeto consulta **antes** de procurar na internet (política completa: fábrica no `.prst` → banco local → internet → fallback fábrica; ver seção 📡 3 de cada `patch.md`).

## ⚠️ Este banco NÃO é versionado — leia antes de dar `git add`

Os `.wav` daqui são **ignorados pelo git** (`.gitignore` → `impulse_responses/*`). Só este README entra no repositório. O motivo é licença, não tamanho: a IR-Cab Library V3 é **gratuita com cadastro** no site da Origin Effects, mas a licença dela não concede redistribuição — e um repositório público que versiona os WAVs é redistribuição.

O que **é** versionado, e é insumo da documentação:

| Arquivo | Papel |
|---|---|
| `tools/ir-library.json` | Manifesto estruturado que os agentes e os geradores consultam |
| `reference/16-ir-library.md` | Catálogo legível, gerado a partir do manifesto |

Esses dois são a **última indexação conhecida**: `build_song_patches.py` os usa para citar o arquivo exato na seção 📡 de cada `patch.md`, e `gen_indexes.py` para marcar 📁 no mapa do álbum. É por isso que o banco sair do git **não** torna `tools/ir_library.py` dispensável — ao contrário, é ele que mantém as 62 docs corretas.

**Consequências práticas de clonar o repositório sem o banco:**

- `python tools/ir_library.py` **avisa e sai com 0**, sem zerar os catálogos commitados. O CI fica verde em um clone limpo.
- Os patches continuam documentando a captura recomendada, com o caminho exato do arquivo — você só precisa baixar o pack e extrair em `impulse_responses/` para usá-la.
- O `.prst` nunca depende disso: ele sai com **CAB de fábrica** e funciona ao importar.

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

## 📦 Conteúdo da última indexação conhecida

- **Origin Effects — IR-Cab Library V3** (gratuita; cadastro no site) — 291 WAVs em 9 gabinetes, incluindo os alvos dos patches: `American Twin 2x12` (Twin/JBL), `British Straight 4x12` (Marshall), `Brown Deluxe 1x12` (AC30), `Tweed Combo 1x12` (Bassman).
- **25 Analog Cab IRs** — 25 WAVs.

> 🛡️ **Guarda contra encolhimento do catálogo.** Se você rodar o pipeline com o banco incompleto, o catálogo perderia packs que a documentação dos patches cita — e nem a suíte nem o `check_data_freshness.py` reclamariam, porque o `patch.md` e o mapa do álbum cairiam para "fábrica" **juntos**. Por isso `ir_library.py` reprova a rodada nesse caso:
>
> ```text
> ❌ Esta rodada ENCOLHERIA o catálogo commitado de IRs:
>    - pack ausente nesta rodada: Origin Effects - IR-Cab Library V3 (291 WAVs)
>    Nada foi escrito. Se a remoção do pack é intencional, repita com --force.
> ```
>
> Remover um pack de propósito é legítimo — só não pode ser acidente: `python tools/ir_library.py --force`.

**Quer mais?** Packs gratuitos recomendados por lacuna (metal, V30 mix-ready, baixo…): [`reference/17-free-ir-packs.md`](../reference/17-free-ir-packs.md).

## 🔌 Como carregar na pedaleira

1. Conecte a pedaleira e abra o **GP-100 Edits** → **IR Manager / User IR**.
2. Escolha o **slot (1–20)** e carregue o `.wav`.
3. No patch: bloco **CAB** → navegue até `User IR n` → ajuste **Low Cut / High Cut / Level** (sugestões na seção 📡 3 de cada `patch.md`).

---

[`📖 README do projeto`](../README.md) · [`📚 reference/16-ir-library.md`](../reference/16-ir-library.md) · [`🎸 patches/`](../patches/README.md)
