# ADR-0007 — Documentação em duas camadas: `docs/` para engenharia, `reference/` para o domínio

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issue #31

## Contexto

O projeto tem 24 documentos em `reference/` (00…23) que são o ativo mais
valioso do repositório: catálogo de parâmetros, workflow de ajuste, dossiês de
álbum, decisões de IR, roadmap. Eles servem a **dois públicos distintos**:

- o **músico/agente** que precisa do domínio (o que é "lamacento", qual slot usar,
  qual modelo do firmware V2.0) — e que já consulta `reference/`;
- o **contribuidor de software** que precisa de arquitetura, setup, fluxo de
  release e padrão de commit — que hoje não tem onde ler.

Misturar os dois numa pasta só produz o pior dos dois mundos: quem chega para
programar cai num catálogo de amplificador, e quem quer ajustar timbre tropeça em
`mypy`.

## Decisão

Documentação em **duas camadas, com dono explícito**:

| Onde | Público | Conteúdo | Natureza |
|---|---|---|---|
| `docs/` | contribuidor / mantenedor | arquitetura, ADRs, desenvolvimento, release, guias de contribuição | **normativa**: descreve o que existe e o que é exigido |
| `reference/` | usuário, músico e agentes | domínio GP-100, dossiês, workflow de timbre, histórico de decisão musical | **de domínio**: descreve o equipamento e as escolhas musicais |

Complementos de raiz, exigidos pelo ecossistema open source: `README.md`
(porta de entrada), `CONTRIBUTING.md` (como contribuir), `SECURITY.md`,
`CHANGELOG.md`, `ARCHITECTURE.md` (visão curta que aponta para `docs/decisions/`).

Regras:

1. `ARCHITECTURE.md` é **resumo** e aponta para o ADR; não duplica decisão.
2. `reference/` não descreve arquitetura de software e `docs/` não descreve
   timbre — a fronteira é o que impede as duas de divergirem.
3. Documento de site (`docs/`, publicado com MkDocs Material) é gerado do
   Markdown versionado: nenhuma cópia manual.

## Consequências

- ✅ Cada público acha o que precisa no primeiro clique, e o README aponta para os
  dois.
- ✅ `reference/` permanece como registro histórico (docs 19–23 documentam
  decisões e auditorias já feitas) — não é reescrito para "parecer atual".
- ⚠️ Custa disciplina de fronteira: dúvida nova precisa ser classificada em
  `docs/` ou `reference/` na hora de escrever, não depois.
- ⚠️ Link entre camadas é permitido em uma direção (docs → reference para
  contexto de domínio), nunca o contrário.

## Alternativas descartadas

- **Tudo em `docs/`** — moveria 24 documentos que já têm referência histórica em
  issues, PRs e agentes; quebraria todos os links existentes em troca de nada.
- **Tudo em `reference/` somado de `ARCHITECTURE.md`** — mantém o contribuidor
  perdido no meio do domínio e não cria lugar para ADR.
- **Wiki do GitHub** — sai do versionamento junto com o código: um PR não pode
  alterar arquitetura e a sua descrição no mesmo commit.
