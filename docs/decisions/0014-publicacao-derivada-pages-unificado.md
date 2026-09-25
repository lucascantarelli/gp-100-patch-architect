# ADR-0014 — Publicação 100% derivada: um deploy para todo o Pages, contagens sem edição manual

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: #11 (site da biblioteca), #60 (docs no Pages), #90 fase 1
  (catálogo JSON), #113/#115 (auditorias de contagens e workflows), #117 (badges
  derivados), #119 (`/stats/`); funda-se na [ADR-0013](0013-modelo-de-artefatos-em-escala.md)
  (derivados construídos, não armazenados) e na [ADR-0006](0006-ci-cd-sem-escrita.md)
  (nenhum workflow escreve no repositório)

## Contexto

A auditoria de workflows (#115) encontrou uma colisão estrutural que a decisão
registrada no encerramento da #60 ("a doc entra no mesmo Pages, em `/docs/`")
nunca conseguiu implementar: **`pages.yml` (biblioteca, #11) e `docs-pages.yml`
(docs, #60) deployavam cada um o site inteiro na mesma raiz**. O
`actions/deploy-pages@v4` não tem input de subcaminho — cada deploy substitui
o site completo. Last-writer-wins: o último deploy derrubava o site do outro
(o ar mostrava a biblioteca porque o `pages.yml` venceu a última corrida).

Na mesma semana, as auditorias de contagens (#113) e de badges manuais provaram
o segundo sintoma: contagem editada à mão apodrece de **três** formas —
envelhece ("release-1.0" com a 2.0.0 publicada), diverge entre docs ("321" vs
"384" testes) e **erra na hora de consertar** ("382" escrito à mão onde a suíte
real tinha 381 — e depois "393" onde a derivação mostrou 392).

## Decisão

> **Todo o GitHub Pages do projeto é UM artefato derivado, publicado por UM
> workflow; toda contagem pública é derivada de fonte única no momento do
> deploy. Nada publicado se edita à mão.**

1. **Pages unificado** — o `pages.yml` gera no deploy, a partir do checkout
   fresco: biblioteca na **raiz** (`gp100 site`), docs de engenharia em
   **`/docs/`** (`prep_docs` + `mkdocs build --strict`), badges em
   **`/badges/*.json`** (`gp100 badges`) e estatísticas em
   **`/stats/`** (`gp100 site --stats`). O `docs-pages.yml` foi removido.
2. **Fonte única em dados** — `badges.dados_derivados(defs)` produz as
   contagens (versão do `VERSION`, agentes/skills do `git ls-files`, patches
   do defs, políticas do pyproject, testes da coleção pytest); badges,
   `/stats/stats.json` e `/stats/index.html` são **renderizações** dessa
   mesma chamada — um não diverge do outro, por construção.
3. **README consome endpoints** — os badges de contagem são
   `img.shields.io/endpoint?url=…/badges/<nome>.json`; regenerados a cada push
   na `develop`, nunca editados. Fatos que não são contagens (firmware
   confirmado no device, licença) permanecem estáticos.

## Consequências

- ✅ **A colisão morre por construção**: um deploy só — biblioteca e docs nunca
  mais competem pela raiz.
- ✅ **Contagem não apodrece**: mudou o repo, muda o deploy — o badge de testes
  corrigiu sozinho de 381→387→392 sem ninguém editar nada.
- ✅ **Agentes e integrações consomem dados**: `/stats/stats.json` com shape
  estável (espírito do `/catalog/` da #90) e `/badges/*.json` em formato
  shields.io endpoint.
- ⚠️ **O deploy ficou mais pesado** (~40–60s): coleção pytest para contar
  testes + build do MkDocs além do `gp100 site`. Aceito: roda só no deploy.
- ⚠️ **Página nova = deploy novo**: não há preview por PR de site (Pages só
  publica a `develop`); validação local obrigatória antes do merge.
- ⚠️ **`stats.json` é contrato**: mudar chaves é breaking para agentes
  (mesma regra do `/catalog/`).

## Alternativas descartadas

- **`deploy-pages@v4` com input `path` (manter 2 workflows)** — o input não
  existe (verificado no action.yml oficial): `token`, `timeout`, `error_count`,
  `reporting_interval`, `artifact_name`, `preview`. Foi o motivo de a decisão
  da #60 nunca ter funcionado; não há como "consertar" os dois deploys.
- **Dois ambientes/Pages distintos** (biblioteca num `gh-pages`/repositório
  irmão, docs em outro) — resolve a colisão ao custo de **duas URLs** (quebra
  os links vivos do README, da #11 e da #60), dois badges de deploy, dois
  lugares para endurecer (o `audit_workflows.py` dobraria a tabela de tetos)
  e repositório extra para manter. Rejeitado: complexidade permanente para
  economizar um job.
- **Docs como submódulo/subpasta do site da biblioteca, gerados por HTML
  próprio** — reimplementar navegação, busca e `--strict` que o MkDocs já dá;
  duplica infraestrutura (o erro que a #33 extinguiu). Rejeitado.
- **`gp-pages` por branch (`actions-gh-pages`)** — exige workflow **com
  `contents: write`** (fere a ADR-0006 e a regra "nenhum job escreve no
  repositório", que é check obrigatório da branch protection) e publica uma
  branch como fonte do Pages (o caminho legado que o GitHub recomenda
  migrar para Actions). Rejeitado de frente.
- **Badges fixados por job de CI que commita o `badges.json`** — commit
  automático = `contents: write` no CI (mesma violação da ADR-0006) + churn de
  commits no histórico a cada push + race com o merge. Rejeitado; a resposta
  foi publicar os JSON **como derivado do deploy** (ADR-0013 aplicado ao site).
- **shield.io static badge com número manual** — era o estado anterior; apodrece
  das três formas documentadas acima. Rejeitado por definição deste ADR.
- **GitHub Pages "monorepo" com roteamento por Actions (symlink como diretório
  real)** — funciona, mas depende de tar com dereference (provado no
  `upload-pages-artifact`) + convenção frágil de mesclagem em `run:`; trocou
  um problema de infra por um script ad-hoc no deploy. Rejeitado em favor da
  mesclagem explícita em 3 linhas de `mkdir`/`cp` (o que é, na prática, o
  mesmo custo — mas legível e testável localmente).

## Evidências do primeiro uso

- Deploy unificado (run `36142689687` e seguintes): biblioteca na raiz, 59
  páginas em `/docs/`, 7 badges em `/badges/` — tudo num artefato só.
- `/stats/stats.json` ao vivo corrigiu **duas** contagens manuais da mesma
  semana (381→"382" e 392→"393"): a derivação venceu o humano.
