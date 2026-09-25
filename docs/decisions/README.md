# Architecture Decision Records (ADRs)

Registro das decisões que **custam caro reverter**: formato, camadas, toolchain,
contratos com terceiros. Uma decisão que qualquer PR pode mudar sozinho não é
ADR — é convenção de código (nesse caso, `CONTRIBUTING.md` ou o próprio doc).

> **Por que existem**: o projeto já pagou por decisão não registrada. A cadeia de
> módulos viveu copiada em quatro arquivos até alguém notar (doc 21, achado M1);
> o pipeline documentado teve cinco passos enquanto o real tinha sete (doc 22).
> Nenhuma dessas divergências precisou de discussão — precisou de um lugar único
> onde a decisão estava escrita.

## Índice

| ADR | Decisão | Status |
|---|---|---|
| [0001](0001-pacote-python-com-uv.md) | Pacote Python em `src/`, ambiente e comandos com uv | aceito |
| [0002](0002-camadas-pragmaticas.md) | Camadas pragmáticas (domain/application/infrastructure/interfaces) | aceito |
| [0003](0003-cli-typer-rich.md) | CLI com Typer + Rich substituindo scripts soltos | aceito |
| [0004](0004-ui-via-api-na-2-1.md) | UI só na 2.1, sobre uma API — nunca sobre os módulos internos | aceito |
| [0005](0005-qualidade-ruff-mypy-pytest.md) | Qualidade: ruff + mypy --strict + pytest, cobertura com piso | aceito |
| [0006](0006-ci-cd-sem-escrita.md) | CI/CD: workflows separados, uv com lockfile, zero escrita no repositório | aceito |
| [0007](0007-documentacao-em-duas-camadas.md) | Documentação em duas camadas (`docs/` × `reference/`) | aceito |
| [0008](0008-agents-e-contrato.md) | `.agents/` é contrato com o Freebuff — não se move para `.ai/` | aceito |
| [0009](0009-governanca-open-source.md) | Governança: labels, milestones e templates com taxonomia única | aceito (itens 3 e a alternativa "issue-mãe" revogados por ADR-0012) |
| [0010](0010-release-engineering.md) | Release: `VERSION` como fonte única, changelog gerado, tag assinada | aceito |
| [0011](0011-gestao-de-project-com-pat.md) | Gestão de Project v2 com PAT em secret, e permissões verificadas pelo auditor | aceito |
| [0012](0012-epics-com-sub-issues.md) | Milestone é a release; a fase é um epic com sub-issues e `blocked by` nativo | aceito |
| [0013](0013-modelo-de-artefatos-em-escala.md) | Modelo de artefatos em escala: o defs é a única fonte versionada; derivados são construídos, não armazenados | aceito |
| [0014](0014-publicacao-derivada-pages-unificado.md) | Publicação 100% derivada: um deploy para todo o Pages, contagens sem edição manual | aceito |

## Auditoria 2026-09 (pós-2.0.0, issue #125)

Revisão completa dos ADRs 0001–0014 contra a realidade da `develop` — veredito
por ADR, com a marcação feita no `Status` de cada arquivo:

| ADR | Veredito | Observação |
|---|---|---|
| 0001 | ✅ vigente — transição concluída | as ⚠️ de convivência com `tools/` (shims, `param_names.py`) se resolveram: extinto na #33 |
| 0002 | ✅ vigente | contagens do contexto são da época (o linter não as cobra — EXCETO) |
| 0003 | ✅ vigente | |
| 0004 | ✅ vigente | UI/API continua futura (2.1); #90 fase 2 reavaliou o gatilho (doc 19 §7) |
| 0005 | ⚠️ **parcialmente revogado** | pytest adotado na 2.0 (issue #23) e o escopo `tools/` do gate extinto — ver Status do arquivo |
| 0006 | ✅ vigente — desenho futuro realizado | release/security/pages/project-automation rodando exatamente como desenhado |
| 0007 | ✅ vigente | |
| 0008 | ✅ vigente | |
| 0009 | ✅ vigente — parcialmente revogado desde o ADR-0012 | já marcado no Status |
| 0010 | ✅ vigente — nota de época | "hoje `1.0.0`" era o estado da decisão; 2.0.0 publicada pelo mesmo ritual |
| 0011 | ✅ vigente | |
| 0012 | ✅ vigente | |
| 0013 | ✅ vigente — implementado | schema v2 (#8), split, `.prst` fora do git no corte (#82); import "all" investigado na #83 (parte física pendente do mantenedor) |
| 0014 | ✅ vigente | já nasce com consumidores (linter regra 7; release-proposer) |

## Formato

Um ADR é curto e datado. Sem "contexto histórico detalhado", sem código
colado — o que não cabe aqui vira comentário no módulo ou doc em `reference/`.

```markdown
# ADR-XXXX — Título curto no imperativo

- **Status**: aceito | proposto | substituído por ADR-YYYY
- **Data**: AAAA-MM
- **Decisão relacionada**: issue #N, ADR-YYYY

## Contexto
O problema real, com o sintoma observado (não a teoria).

## Decisão
O que fica decidido, em uma frase direta.

## Consequências
- ✅ o que melhora
- ⚠️ o que piora ou passa a exigir disciplina

## Alternativas descartadas
- **X** — por que não (custo, risco ou desalinhamento com o resto)
```

## Regras

1. **Um ADR aceito não é reescrito.** Decisão revista vira ADR novo com status
   `substituído por`.
2. **ADR acompanha o PR que a implementa** — não existe decisão futura
   especulativa no índice.
3. **Toda issue de arquitetura referencia o ADR** que a fundamenta.
