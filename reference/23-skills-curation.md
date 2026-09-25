# 23 · Curadoria de skills (set/2026)

> **Estado atual**: as skills vivem **versionadas no repositório**, em
> `.agents/skills/` (formato Agent Skills: pasta + `SKILL.md` com frontmatter
> `name`/`description`). O Freebuff as carrega junto com os 20 agentes de
> `.agents/*.ts`. O diretório global `~/.agents/skills/` mantém apenas as
> skills genéricas para uso fora do projeto — **sem divergência**: as skills
> do GP-100 existem só aqui.
>
> **Guarda de integridade (issue #63)**: `.github/scripts/audit_agents.py` roda
> no CI (job de agentes, junto do `tsc`) e reprova: caminho citado por agente
> inexistente no repositório, contrato ADR-0008 incompleto, skill sem
> frontmatter ou fora da curadoria deste doc. Skill sem consumidor explícito
> é **aviso**, não reprova — curadoria é decisão humana.

## 1 · Skills versionadas no projeto (11)

### Do GP-100 (4) — fonte canônica do repositório

| Skill | Origem | Papel |
|---|---|---|
| `gp100-criar-patch` | `prompts/criar-patch.md` | Fluxo de criação (entrevista → architect → pipeline) |
| `gp100-por-referencia` | `prompts/pesquisar-referencia.md` | research → mapper → architect (com golden set como régua) |
| `gp100-ajustar-patch` | `prompts/ajustar-patch.md` | A/B pós-teste (tabela do doc 12, mudanças mínimas) |
| `gp100-sugerir-timbres` | `prompts/sugerir-timbres.md` | Exploração antes de fechar patch |

> Os `prompts/*.md` continuam no repo como a **fonte canônica dos fluxos**
> (citados no README e no knowledge.md); as skills são a forma executável —
> qualquer divergência, os prompts e o doc 12 vencem.

### Genéricas (7) — curadoria aprovada

| Skill | Veredito | Papel neste projeto |
|---|---|---|
| `finishing-a-development-branch` | ✅ mantida | Formaliza o ritual de PR já praticado (suíte → PR → CI → merge → issue) |
| `writing-plans` | ✅ mantida | Planos de implementação — próximo uso: schema v2 (issue #8) |
| `brainstorming` | ✅ mantida | Design antes de implementar (v2.0: site, novos álbuns) |
| `github-actions-docs` | ✅ mantida | CI/release.yml/trava 3.14, ancorada em docs oficiais |
| `python-testing-patterns` | ✅ mantida e **promovida a convenção da 2.0** | A release 2.0 adota **pytest** (issue #23); até a 1.x a suíte segue unittest (stdlib pura) |
| `documentation-writer` | ✅ mantida | Diátaxis como régua para `reference/` |
| `frontend-design` | ✅ mantida | Dormente até o pilar do site (v2.0) |
| `python-performance-optimization` | ❌ **removida** (das globais; nunca entrou no repo) | Sem encaixe: suíte roda em ~1 min; profiling stdlib cobre se um dia precisar |

## 2 · Política de precedência

1. **`knowledge.md` e `reference/` do projeto** — vencem qualquer skill.
2. **Skills do projeto** (`.agents/skills/gp100-*`) — fluxos oficiais.
3. **Skills genéricas versionadas** (`.agents/skills/*`) — processo geral;
   quando conflitarem com a convenção vigente, a convenção vence (ex.:
   pytest-centric vs stdlib pura até a 1.x — ver issue #23).
4. **Globais** (`~/.agents/skills/`) — só o que não está no repo; manter em
   sincronia manual e registrar aqui qualquer mudança.

## 3 · A decisão pytest (registrada)

O mantenedor decidiu (set/2026): **a release 2.0 adota pytest**. Consequências:

- `python-testing-patterns` deixa de "conflitar com a convenção" e passa a ser
  a convenção-alvo da 2.0.
- O pytest será a **primeira dependência real** do projeto — a política
  "stdlib pura" vale até a 1.x; migração rastreada na **issue #23**
  (milestone v2.0.0) e no Pilar F do doc 19.

## 4 · Como adicionar/atualizar skills (para o futuro)

1. **Skill do GP-100**: a fonte canônica nasce no repo (`prompts/` ou doc de
   reference) → criar `.agents/skills/<nome>/SKILL.md` com frontmatter
   `name` + `description` acionável ("Use quando…") e o corpo do fluxo →
   rodapé de precedência apontando a fonte → commitar (é versionada).
2. **Skill genérica**: instalar no repo direto (curadoria aqui, tabela acima);
   só espelhar para `~/.agents/skills/` se o uso for fora do projeto.
3. Qualquer mudança de inventário passa por este doc — e o guarda
   `audit_agents.py` reprova skill no disco sem registro aqui (e registrada
   sem existir no disco).

---
[`📖 README do projeto`](../README.md) · [`📚 Reference`](README.md) · [`🤖 Agentes`](../.agents/README.md)
