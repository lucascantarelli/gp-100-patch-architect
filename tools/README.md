# 🔧 Tools — scripts de geração e análise

Utilitários Python (sem dependências além da biblioteca padrão; Windows OK) que sustentam o [GP-100 Patch Architect](../README.md).

## 🎼 Ciclo de vida de um patch

```bash
# 1. Edite a fonte única (músicas, camadas, params, doc de guitarra, ajustes finos)
#    → patches-defs.json

# 2. Construa specs + patch.md + .prst de TODOS os patches
python build_song_patches.py

# 3. Regenere mapas dos álbuns e o README da biblioteca
python gen_indexes.py
```

**Criar um patch isolado:** escreva um `spec.json` (o formato completo está documentado no docstring de `generate_prst.py`) e chame `python generate_prst.py spec.json saida.prst`.

## 📜 Scripts

| Script | Comando | O que faz |
|---|---|---|
| `build_song_patches.py` | `python build_song_patches.py` | **Construtor principal.** Lê `patches-defs.json`, escreve `spec.json` + `patch.md` + `<NOME>.prst` de cada patch em `patches/<Banda>/<Álbum>/<Música>/<NOME>/` e valida o resultado (XML conforme, nome ≤ 12 caracteres). Slots U01…Uxx calculados pela ordem global dos defs. |
| `add_pulse_defs.py` | `python add_pulse_defs.py` | (Re)insere as 24 músicas / 38 patches do Pulse em `patches-defs.json`, na ordem do álbum — idempotente; já encadeia `add_momentos.py` no final. |
| `add_momentos.py` | `python add_momentos.py` | Injeta os momentos de toggle por patch (seção "Modos de atuação"): valida contra o spec (só estado inverso), herda o delay do patch-irmão de solo para as bases e registra os SOBRESSALENTES. |
| `generate_prst.py` | `python generate_prst.py <spec.json> <saída.prst>` | Gera **um** `.prst` no formato **single-patch, firmware 2.1** — réplica exata do export single que importou com sucesso no aparelho (sem `<ppIRInfo>`, com `<ppCtrl>`/`<ppEXP1>`, atributos na ordem exata, cadeia x=0–8). Valida nomes contra o catálogo fw 2.0. |
| `gen_indexes.py` | `python gen_indexes.py` | Regenera os `MAPA-DO-ALBUM.md` de cada álbum e o `patches/README.md` a partir dos defs — tabelas música→patches, captador, IR recomendada e sequência de slots. |
| `ir_library.py` | `python ir_library.py` | Indexa `impulse_responses/`: valida cada WAV (mono/24 bits/44.1 kHz) e gera `ir-library.json` (manifesto para os agentes) + `reference/16-ir-library.md`. **Rode sempre que baixar packs novos.** |
| `analyze_prst.py` | `python analyze_prst.py <arquivo.prst> [--json out.json]` | Disseca qualquer export da pedaleira: modelos por módulo com effectCode, estatísticas empíricas de `params_0..14` (min/max/distintos), catálogo completo com cadeias. **É dele que nasceu o catálogo fw 2.0** (`factory-catalog.json`). |
| `render_manual_page.py` | `python render_manual_page.py <impressa> [mais…] · --all` | Renderiza páginas do `manual.pdf` **sob demanda** (requer pymupdf): PNG alta + JPG leve em `manual_pages/` (efêmero). Página impressa NN = arquivo NN+2. |

## 🗃️ Arquivos de dados

| Arquivo | Papel |
|---|---|
| `patches-defs.json` | **Fonte única** de todos os patches: música, camadas, params, doc de guitarra/ajustes finos, momentos de toggle, notas de IR |
| `factory-catalog.json` | Catálogo empírico do firmware 2.0/2.1 (extraído do export de fábrica via `analyze_prst.py`) — base dos templates de params |
| `ir-library.json` | Manifesto do banco local de IRs (gerado — não editar à mão) |

## ⚠️ Armadilhas conhecidas (já resolvidas nos scripts)

- **Formato single ≠ all** — importar `.prst` com `<ppIRInfo>` dá "Wrong patch file type (single/all)".
- `firmware="2.0"` no export antigo → o editor rejeita; o gerador emite **2.1**.
- Ordem dos atributos do `<Effect>` importa (`params_0` antes de `x/y`) — mantida idêntica ao exemplo funcional.
- Nomes no painel: **máx. 12 caracteres** (`ppName` truncado).
- Console Windows em cp1252: os scripts reconfiguram o stdout para UTF-8.
- **`preset_info/@time` muda a cada build** (epoch ms, imitando o export real do GP-100 Edits) — o `.prst` NÃO é byte-idêntico entre gerações; isso é intencional. Para diffar parâmetros, compare os `spec.json` (fonte determinística), não os `.prst`.
- Modelos reais do fw 2.0 ausentes no export de fábrica ficam em `EXTRA_TEMPLATES` no `generate_prst.py` (atualmente `PRE/Saturate` — o Tube Driver do Gilmour).

---

[`📖 README do projeto`](../README.md) · [`🎸 patches/`](../patches/README.md)
