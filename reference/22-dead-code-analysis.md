# 22 · Análise de código obsoleto e morto (set/2026)

> **Pergunta de origem**: "temos arquivos obsoletos? dead code? depois dessas
> melhorias?" **Resposta curta**: o repositório está enxuto — nenhum arquivo
> obsoleto, nenhum script morto. O scan encontrou **4 itens de nível linha**
> (2 imports mortos, 1 constante morta, 1 validação declarada mas nunca
> conectada) e **3 documentações defasadas do pipeline canônico** — todos
> corrigidos no PR desta análise.

## 1 · Método (reproduzível)

1. **Inventário + referência cruzada**: cada arquivo de `tools/`,
   `.github/scripts/` e `setup_repo.sh` foi procurado (`grep -rln`) em
   README/CONTRIBUTING/knowledge/reference/workflows/testes — arquivo sem
   nenhuma citação seria candidato.
2. **Scanner AST de imports** (stdlib pura): todo `import` cujo nome não
   aparece como `Name`/uso no módulo.
3. **Scanner AST de símbolos**: toda função/constante de nível de módulo
   com **zero uso no próprio arquivo** (AST) **e zero referência externa**
   (`git grep -w` no repo inteiro) — os dois filtros juntos evitam os falsos
   positivos de helper-de-arquivo.
4. **Verificação de pipeline canônico**: os passos documentados nos READMEs e
   no doc 12 comparados com o `PIPELINE` do guarda de sincronia (`TestH`), que
   é a ordem autoritativa.

## 2 · Achados — todos corrigidos

| # | Achado | Onde | Correção |
|---|---|---|---|
| D1 | `import json` morto (sobrou da validação na porta, PR #21) | `gp100.py`, `build_release.py` | removido |
| D2 | `AMP_FLAG_CLEAN` — único membro não usado da família de presets do seeder | `add_pulse_defs.py:72` | removido |
| D3 | `CAMS` (catálogo de camadas) declarado como "documental" e **nunca conectado** | `defs_schema.py` | virou validação real do campo `sufixo` (os 15 sufixos usados passam; `VOX` mantido como allowance histórico, hoje sem uso) |
| D4 | Pipeline canônico nos docs com **5 passos**; o `PIPELINE` real tem **7** (faltavam os seeders Wishkah e Santana) | `README.md` (×2), `CONTRIBUTING.md`, doc 12 | docs espelhados no `TestH` |

## 3 · Verificados e vivos (não remover)

- **Seeders `add_*.py`** (os maiores arquivos do repo): são a *fonte executável*
  da história do defs — o guarda de sincronia (`TestH`) e o `PIPELINE` da CLI
  os rodam para reproduzir o `patches-defs.json` do zero. Removê-los quebraria
  a reprodutibilidade. **Decisão de arquitetura, não acidente**: quando o
  schema v2 (issue #8) dividir o defs por álbum, os seeders se aposentam com
  dignidade — é o plano, não dead code hoje.
- **`render_manual_page.py`**, **`analyze_prst.py`**, **`audit_workflows.py`**,
  **`setup_repo.sh`**: citados em docs/workflows com papel ativo.
- **`param_names.py`, `chain.py`**: fontes únicas recentes (PRs #18/#21).
- Nenhum `.pyc`/`__pycache__` rastreado pelo git.

## 4 · Anomalia fora desta análise

`tools/param_names.py` tem comentários removidos na working tree **que não
fazem parte desta análise nem dos PRs anteriores** (mudança de terceiro,
provavelmente outro agente/editor). Fica intocada — decidir manter ou
`git checkout -- tools/param_names.py`.

## 5 · Prevenção (barata)

- O scanner AST desta análise pode virar teste (`tests/test_dead_code.py`) —
  ~40 linhas, roda em <1 s, reprova PR que deixar import/símbolo morto.
- O schema v2 eliminaria por construção as duplicações restantes (B2/B4 do
  doc 21) e aposentaria os seeders.

---
[`📖 README do projeto`](../README.md) · [`📚 Reference`](README.md) · [`🔍 Doc 21`](21-code-review.md)
