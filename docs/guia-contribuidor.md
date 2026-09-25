# Guia do contribuidor — do clone ao PR aceito

**Leia isto se** você vai **mexer no código ou no defs**: regenerar a
biblioteca, adicionar patch/álbum, trocar o pipeline. A definição de "PR
aceitável" e o caminho de validação de um patch novo estão aqui — sem ler os
13 ADRs (só os que cada seção citar).

## 1 · Setup em máquina limpa (o contrato de onboarding)

```bash
git clone https://github.com/lucascantarelli/gp-100-patch-architect.git
cd gp-100-patch-architect
uv sync
uv run pre-commit install
uv run pytest -q
```

Verde = ambiente pronto. Essa sequência **é testada pela auditoria do DoD**
(`docs/audit-dod-2.0.md`, achado A1): nenhum teste lê derivado do disco.

## 2 · O que é um PR aceitável

A barreira é a **mesma do CI** — se passa local, passa lá:

- **Suíte verde**: `uv run pytest` (pirâmide unit → contract → integration → e2e)
- **Gates**: `uv run ruff check . && uv run ruff format --check . && uv run mypy`
- **Agentes**: `npx -y -p typescript@5.9.2 tsc --noEmit -p tsconfig.json`
  (se mexer em `.agents/`)
- **Docs consistentes**: o linter (#58) reprova issue citada inexistente,
  caminho que nunca existiu, link quebrado, milestone fantasma — rode
  `uv run python .github/scripts/audit_docs.py` antes do push
- **Guardian** cobra labels (`type:`, `size:`, `scope:`), assignee, milestone
  e issue vinculada no corpo (`Closes #N` — a keyword fecha a issue no merge)

Processo completo (branch, fluxo da develop, review): doc 18
([reference/18](../reference/18-project-management.md)).

## 3 · Como um patch novo é validado

O fluxo do defs → pedaleira tem **cada etapa cobrada por uma máquina**:

1. **Dossiê do rig com fontes** — o `album.rig` e as `referencias` da música
   citam fonte por afirmação (o validador cobra campos)
2. **Schema v2 do defs** — `uv run gp100 validate` reprova: modelo inexistente
   no catálogo de fábrica, parâmetro fora do nome oficial (`PARAM_NAMES`),
   slot de IR incompatível, stomp que não faz nada, momento invertendo o que
   já está ON
3. **Pipeline** — `uv run gp100 build --quiet` gera `.prst` + `patch.md` +
   índices; **erro vira mensagem acionável, nunca traceback**
4. **Guarda de sincronia (TestH)** — o e2e regenera tudo em sandbox e compara
   **byte a byte**: esqueceu de rodar o build, o CI pega
5. **Import real** — a prova final é no aparelho; o formato single fw 2.1 é
   verificado por teste de contrato byte a byte (doc 15)

## 4 · Onde mexer em quê

| Quero… | Arquivo |
|---|---|
| Novo patch/álbum | `data/defs/<ÁLBUM>.json` (schema v2) |
| Regra de validação | `src/gp100_architect/domain/validation.py` |
| Geração do `.prst` | `src/gp100_architect/infrastructure/prst/codec.py` |
| Geração do `patch.md` | `src/gp100_architect/application/rendering/patch_md.py` |
| Novo comando da CLI | `src/gp100_architect/interfaces/cli/main.py` |
| Novo agente | `.agents/*.ts` (contrato no doc 23, guarda no CI) |

---

**Próximo passo**: pegue uma issue com label `status: ready-for-pr` do
[milestone](https://github.com/lucascantarelli/gp-100-patch-architect/milestones),
abra a branch `feat/<número>-<slug>` e suba o PR. Para **gerir release e
board**, vá para o [guia do mantenedor](guia-mantenedor.md).
