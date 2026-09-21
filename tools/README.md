# 🔧 Tools — scripts de geração e análise

Utilitários Python (sem dependências além da biblioteca padrão; Windows OK) que sustentam o [GP-100 Patch Architect](../README.md).

## 🎼 Ciclo de vida de um patch

```bash
# 1. Edite a fonte única (músicas, camadas, params, doc de guitarra, ajustes finos)
#    → patches-defs.json

# 2. (Se baixou pack novo de IR) indexe a biblioteca
python ir_library.py                        # tools/ir-library.json + reference/16-ir-library.md

# 3. Reinsira/atualize os álbuns seedados e os momentos de toggle
python add_pulse_defs.py                    # idempotente; já encadeia add_momentos.py

# 4. Construa specs + patch.md + .prst de TODOS os patches
python build_song_patches.py

# 5. Regenere mapas dos álbuns e o README da biblioteca
python gen_indexes.py

# 6. Valide tudo (mesma suíte que o CI roda) e confira que nada gerado ficou fora
python -m unittest discover -s tests -v
python check_data_freshness.py              # falha se um artefato estiver defasado vs HEAD
```

> **Essa é exatamente a sequência do job `dados` do CI** (`.github/workflows/ci.yml`): o pipeline roda inteiro e, se o resultado não for o que está commitado, o build reprova dizendo o que rodar. Quem acrescenta música, camada, patch, efeito, momento de toggle ou pack de IR precisa rodar isto e commitar os derivados.

**Criar um patch isolado:** escreva um `spec.json` (o formato completo está documentado no docstring de `generate_prst.py`) e chame `python generate_prst.py spec.json saida.prst`.

## 📜 Scripts

| Script | Comando | O que faz |
|---|---|---|
| `build_song_patches.py` | `python build_song_patches.py` | **Construtor principal.** Lê `patches-defs.json`, escreve `spec.json` + `patch.md` + `<NOME>.prst` de cada patch em `patches/<Banda>/<Álbum>/<Música>/<NOME>/` e valida o resultado (XML conforme, nome ≤ 12 caracteres). Slots U01…Uxx calculados pela ordem global dos defs. |
| `add_pulse_defs.py` | `python add_pulse_defs.py` | (Re)insere as 24 músicas / 38 patches do Pulse em `patches-defs.json`, na ordem do álbum — idempotente; já encadeia `add_momentos.py` no final. |
| `add_momentos.py` | `python add_momentos.py` | Injeta os momentos de toggle por patch (seção "Modos de atuação"): valida contra o spec (só estado inverso), herda o delay do patch-irmão de solo para as bases e registra os SOBRESSALENTES. |
| `generate_prst.py` | `python generate_prst.py <spec.json> <saída.prst>` | Gera **um** `.prst` no formato **single-patch, firmware 2.1** — réplica exata do export single que importou com sucesso no aparelho (sem `<ppIRInfo>`, com `<ppCtrl>`/`<ppEXP1>`, atributos na ordem exata, cadeia x=0–8). Valida nomes contra o catálogo fw 2.0. |
| `gen_indexes.py` | `python gen_indexes.py` | Regenera os `MAPA-DO-ALBUM.md` de cada álbum e o `patches/README.md` **a partir do defs** (`albums`, `ir_local`, `pasta`/`display`) — tabelas música→patches, captador, IR recomendada e sequência de slots. `build_all()` é pura (monta o texto sem escrever) e `main()` só grava: é isso que a suíte usa para detectar índice defasado. |
| `ir_library.py` | `python ir_library.py` | Indexa `impulse_responses/`: valida cada WAV (mono/24 bits/44.1 kHz) e gera `ir-library.json` (manifesto para os agentes) + `reference/16-ir-library.md`. **Rode sempre que baixar packs novos.** |
| `check_data_freshness.py` | `python check_data_freshness.py` | **Guarda do CI.** Compara os artefatos GERADOS no disco (`patches/**` `.prst`/`.md`/`.json`, `patches-defs.json`, `ir-library.json`, `reference/16`) com o HEAD, ignorando `preset_info/@time` (o único byte que muda a cada build). Reprova com o comando exato de conserto quando alguém acrescentou elemento sem rodar o pipeline. Rode antes de commitar. |
| `analyze_prst.py` | `python analyze_prst.py <arquivo.prst> [--json out.json]` | Disseca qualquer export da pedaleira: modelos por módulo com effectCode, estatísticas empíricas de `params_0..14` (min/max/distintos), catálogo completo com cadeias. **É dele que nasceu o catálogo fw 2.0** (`factory-catalog.json`). |
| `render_manual_page.py` | `python render_manual_page.py <impressa> [mais…] · --all` | Renderiza páginas do `manual.pdf` **sob demanda** (requer pymupdf): PNG alta + JPG leve em `manual_pages/` (efêmero). Página impressa NN = arquivo NN+2. |

## 🗃️ Arquivos de dados

| Arquivo | Papel |
|---|---|
| `patches-defs.json` | **Fonte única**: `meta`, `albums` (banda/ano/pasta/título/dossiê do rig), `ir_local` (captura recomendada por CAB) e `songs` (música, `pasta`/`display`, camadas, params, doc de guitarra, ajustes finos, momentos de toggle, notas de IR). Nenhum script guarda tabela própria de músicas/álbuns/cabs. |
| `factory-catalog.json` | Catálogo empírico do firmware 2.0/2.1 (extraído do export de fábrica via `analyze_prst.py`) — base dos templates de params |
| `ir-library.json` | Manifesto do banco local de IRs (gerado — não editar à mão) |
| `check_data_freshness.py` | Não gera nada: só compara disco × HEAD (o dado em si vive nos arquivos acima) |

## 🧪 Testes

```bash
python -m unittest discover -s tests -v      # 19 testes, stdlib pura (nada a instalar)
```

`tests/test_pipeline.py` valida as invariantes que já quebraram uma vez: defs (ids/nomes únicos, nome ≤ 12 chars), **coerência mapa × `patch.md` sobre IR** (a divergência dos 38 patches do Pulse), formato `.prst` single fw 2.1, as 9 seções obrigatórias + zero HTML cru + zero rótulo placeholder `(pN)`, momentos de toggle válidos (nunca AMP/CAB), cobertura de `PARAM_NAMES` (allowlist explícita para os modelos do fw 2.0 sem nome oficial), **drift dos índices** e a normalização do check de frescor (`TestH_DadosEmSincronia`: ignora o `time`, equipara CRLF/LF e não mascara mudança de parâmetro).

Rodam no CI a cada push (`.github/workflows/ci.yml`), que também roda o **pipeline de dados inteiro** e o `check_data_freshness.py` (job `dados`) e faz `tsc --noEmit` nos agentes.

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
