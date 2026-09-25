# ADR-0010 — Release: `VERSION` como fonte única, changelog gerado, tag assinada

- **Status**: aceito — **ritual provado em produção** (auditoria #125): a
  2.0.0 foi publicada por este fluxo (tag anotada, 8 assets, notas de migração
  geradas); o "hoje `1.0.0`" do contexto é o estado da época da decisão.
- **Data**: 2026-09
- **Decisão relacionada**: issues #27, #32; `reference/18-project-management.md`

## Contexto

Existem `VERSION` (hoje `1.0.0`), `CHANGELOG.md` gerado por
`tools/gen_changelog.py`, `tools/build_release.py` (ZIPs + notas) e
`release.yml`. O que não existe é **fonte única**: a versãoaparece escrita à mão na documentação, no `pyproject.toml` (novo, dinâmico)e na documentação; e o changelog depende de o autor lembrar do formato.

## Decisão

1. **`VERSION` é a única fonte da versão.** O `pyproject.toml` a lê
   dinamicamente; o changelog e o empacotamento a leem do arquivo — ninguém mais
   escreve número de versão à mão.
2. **SemVer com regra escrita**: Conventional Commits determinam o bump
   (`fix:` → patch, `feat:` → minor, `!`/`BREAKING CHANGE:` → major). O bump é
   **calculado**, não escolhido.
3. **Release é um ritual com portões**: suíte verde → build regenerado e
   idempotente (TestH) → changelog gerado → `VERSION` atualizado → commit de
   release → tag → PR `develop → main` → artefatos anexados.
4. **Publicação é decisão humana.** Nenhum agente altera versão, cria tag ou
   publica sozinho: o agente de versionamento (se criado, ver F5) **propõe** o
   bump e o changelog; o mantenedor aprova.
5. **Nada de release "de passagem"**: a release consolida milestones fechados. A
   dívida atual (`main` em 1.0.0 com v1.1.0 e v1.2.0 entregues) é justamente o
   que essa regra existe para impedir.

## Consequências

- ✅ Um só lugar para mudar a versão, e ele é verificável em teste
  (`gp100 --version` = `VERSION` = metadado do pacote).
- ✅ Changelog deixa de depender de disciplina: a entrada é derivada dos commits.
- ✅ O mesmo ritual pode ser executado por um agente, com revisão humana no
  ponto de publicação.
- ⚠️ Exige commit em formato Conventional — já é a convenção, agora com
  consequência automática (bump).
- ⚠️ Enquanto o pacote não for publicado, "release" significa: tag + GitHub
  Release + artefatos ZIP. Empacotar para PyPI é decisão futura.

## Alternativas descartadas

- **Release Please / semantic-release** — automatizam bump por PR próprio, mas
  exigem escrita no repositório por bot (conflita com ADR-0006) e trazem um
  fluxo de PR que o projeto não usa.
- **Commitizen / towncrier** — resolvem metade (commit/record de mudança) e
  somam dependência; o `gen_changelog.py` já faz o necessário e é testado.
- **Versão escrita à mão no `pyproject.toml`** — cria a segunda fonte que este
  ADR elimina.
