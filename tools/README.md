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

# 6. Valide tudo (mesma suíte que o CI roda) — ela inclui o guarda de sincronia
python -m unittest discover -s tests -v
```

> **Essa é exatamente a sequência do guarda de sincronia da suíte** (`TestH_DadosEmSincronia`): o teste roda o pipeline inteiro numa cópia temporária do repositório e, se o resultado não for o que está commitado, reprova dizendo o que rodar. Quem acrescenta música, camada, patch, efeito, momento de toggle ou pack de IR precisa rodar isto e commitar os derivados. A suíte roda em push e em PR, e nos dois casos a correção é do autor: **nenhum job escreve no repositório**.

**Criar um patch isolado:** escreva um `spec.json` (o formato completo está documentado no docstring de `generate_prst.py`) e chame `python generate_prst.py spec.json saida.prst`.

## 📜 Scripts

| Script | Comando | O que faz |
|---|---|---|
| `build_song_patches.py` | `python build_song_patches.py` | **Construtor principal.** Lê `patches-defs.json`, escreve `patch.md` + `<NOME>.prst` (e o `spec.json` intermediário, não versionado) de cada patch em `patches/<Banda>/<Álbum>/<Música>/<NOME>/` e valida o resultado (XML conforme, nome ≤ 12 caracteres). Slots U01…Uxx calculados pela ordem global dos defs. |
| `add_pulse_defs.py` | `python add_pulse_defs.py` | (Re)insere as 24 músicas / 38 patches do Pulse em `patches-defs.json`, na ordem do álbum — idempotente; já encadeia `add_momentos.py` no final. |
| `add_momentos.py` | `python add_momentos.py` | Injeta os momentos de toggle por patch (seção "Modos de atuação"): valida contra o spec (só estado inverso), herda o delay do patch-irmão de solo para as bases e registra os SOBRESSALENTES. |
| `generate_prst.py` | `python generate_prst.py <spec.json> <saída.prst>` | Gera **um** `.prst` no formato **single-patch, firmware 2.1** — réplica exata do export single que importou com sucesso no aparelho (sem `<ppIRInfo>`, com `<ppCtrl>`/`<ppEXP1>`, atributos na ordem exata, cadeia x=0–8). Valida nomes contra o catálogo fw 2.0. |
| `gen_indexes.py` | `python gen_indexes.py` | Regenera os `MAPA-DO-ALBUM.md` de cada álbum e o `patches/README.md` **a partir do defs** (`albums`, `ir_local`, `pasta`/`display`) — tabelas música→patches, captador, IR recomendada e sequência de slots. `build_all()` é pura (monta o texto sem escrever) e `main()` só grava: é isso que a suíte usa para detectar índice defasado. |
| `ir_library.py` | `python ir_library.py` | Indexa `impulse_responses/`: valida cada WAV (mono/24 bits/44.1 kHz) e gera `ir-library.json` (manifesto para os agentes) + `reference/16-ir-library.md`. **Rode sempre que baixar packs novos.** |
| `analyze_prst.py` | `python analyze_prst.py <arquivo.prst> [--json out.json]` | Disseca qualquer export da pedaleira: modelos por módulo com effectCode, estatísticas empíricas de `params_0..14` (min/max/distintos), catálogo completo com cadeias. **É dele que nasceu o catálogo fw 2.0** (`factory-catalog.json`). |
| `render_manual_page.py` | `python render_manual_page.py <impressa> [mais…] · --all` | Renderiza páginas do `manual.pdf` **sob demanda** (requer pymupdf): PNG alta + JPG leve em `manual_pages/` (efêmero). Página impressa NN = arquivo NN+2. |

## 🗃️ Arquivos de dados

| Arquivo | Papel |
|---|---|
| `patches-defs.json` | **Fonte única**: `meta`, `albums` (banda/ano/pasta/título/dossiê do rig), `ir_local` (captura recomendada por CAB) e `songs` (música, `pasta`/`display`, camadas, params, doc de guitarra, ajustes finos, momentos de toggle, notas de IR). Nenhum script guarda tabela própria de músicas/álbuns/cabs. |
| `factory-catalog.json` | Catálogo empírico do firmware 2.0/2.1 (extraído do export de fábrica via `analyze_prst.py`) — base dos templates de params |
| `ir-library.json` | Manifesto do banco local de IRs (gerado — não editar à mão) |

## 🧪 Testes

```bash
python -m unittest discover -s tests -v      # 31 testes, stdlib pura (nada a instalar)
```

`tests/test_pipeline.py` valida as invariantes que já quebraram uma vez: defs (ids/nomes únicos, nome ≤ 12 chars), **coerência mapa × `patch.md` sobre IR** (a divergência dos 38 patches do Pulse), formato `.prst` single fw 2.1, as 9 seções obrigatórias + zero HTML cru + **zero rótulo placeholder** (`(pN)` e `pN` solto — todo slot setado tem nome oficial, ver `reference/15`), momentos de toggle válidos (nunca AMP/CAB), cobertura de `PARAM_NAMES` (allowlist hoje **vazia** — modelo novo sem nome de parâmetro reprova), **drift dos índices** e o **guarda de sincronia** (`TestH_DadosEmSincronia`: o pipeline roda numa cópia temporária do repositório e tem de reproduzir o commitado; ignora o `time`, equipara CRLF/LF e não mascara mudança de parâmetro).

Rodam no CI a cada push (`.github/workflows/ci.yml` — dois jobs em paralelo + portão `ci-gate`): a suíte (que inclui o **guarda de sincronia**) e o `tsc --noEmit` nos agentes (job `typecheck`). **Nenhum job escreve no repositório** — quando o guarda reprova por dado defasado, ele pede que o autor rode o pipeline e commite os derivados.

## ⚠️ Armadilhas conhecidas (já resolvidas nos scripts)

- **Formato single ≠ all** — importar `.prst` com `<ppIRInfo>` dá "Wrong patch file type (single/all)".
- `firmware="2.0"` no export antigo → o editor rejeita; o gerador emite **2.1**.
- Ordem dos atributos do `<Effect>` importa (`params_0` antes de `x/y`) — mantida idêntica ao exemplo funcional.
- Nomes no painel: **máx. 12 caracteres** (`ppName` truncado).
- Console Windows em cp1252: os scripts reconfiguram o stdout para UTF-8.
- **`preset_info/@time` muda a cada build** (epoch ms, imitando o export real do GP-100 Edits) — o `.prst` NÃO é byte-idêntico entre gerações; isso é intencional. Para diffar parâmetros, compare os `spec.json` (fonte determinística), não os `.prst`.
- Modelos reais do fw 2.0 ausentes no export de fábrica ficam em `EXTRA_TEMPLATES` no `generate_prst.py` (atualmente `PRE/Saturate` — o Tube Driver do Gilmour).
- **`sorted()` sobre `Path` é dependente do SO** — `Path` compara com `normcase`, que **minúsculas no Windows** e é identidade no Linux. Foi assim que o `ir-library.json` saiu com `4x12 Metal American` antes de `4x12 MFB` aqui e o inverso no CI (mesmo gerador, resultado diferente). Ao ordenar caminhos, use chave de **string** (`p.relative_to(...).as_posix()`), nunca o `Path` direto — há teste travando isso (`TestI_OrdemEstavel`).

---

[`📖 README do projeto`](../README.md) · [`🎸 patches/`](../patches/README.md)
