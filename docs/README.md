# Documentação de engenharia

Esta pasta é a camada **normativa** da documentação: descreve o que existe, o que
é exigido e por quê. O domínio do equipamento (catálogo de timbres, IRs,
dossiês de álbum, workflow de criação de patch) vive em
[`reference/`](../reference/README.md) — a divisão é decisão registrada no
[ADR-0007](decisions/0007-documentacao-em-duas-camadas.md).

| Documento | Para quem | O que responde |
|---|---|---|
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | todos | como o sistema está organizado (1 página) |
| [`../DEVELOPMENT.md`](../DEVELOPMENT.md) | contribuidor | como rodar, testar e onde mexer |
| [`audit-2.0.md`](audit-2.0.md) | mantenedor | estado atual, achados por severidade, riscos, plano de migração |
| [`audit-dod-2.0.md`](audit-dod-2.0.md) | mantenedor | auditoria do DoD da 2.0 (#64): métrica a métrica com evidência e o que falta de verdade |
| [`roadmap-2.0.md`](roadmap-2.0.md) | mantenedor | fases, dependências e Definition of Done da 2.0 |
| [`decisions/`](decisions/README.md) | todos | as 14 decisões de arquitetura (ADRs) e o formato de ADR novo |
| [`guia-usuario.md`](guia-usuario.md) · [`faq.md`](faq.md) · [`exemplos.md`](exemplos.md) | usuário final | como usar a biblioteca e a CLI, dúvidas comuns e exemplos completos |
| [`guia-contribuidor.md`](guia-contribuidor.md) · [`guia-mantenedor.md`](guia-mantenedor.md) | contribuidor / mantenedor | fluxo de PR, gates locais, rotina de release e governança |

## Estrutura prevista

As pastas abaixo nascem na fase F4 (issue #31), quando houver conteúdo para
elas — pasta vazia com README de intenção é ruído:

```
docs/
├── decisions/     ADRs                             (existe)
├── architecture/  diagramas e visões por módulo     (F4)
├── development/   setup, testes, release            (F4 — DEVELOPMENT.md é o começo)
├── guides/        passo a passo por tarefa          (F4)
├── reference/     CLI e API geradas                 (F4 / 2.1)
├── contributing/  onboarding e revisão              (F4)
└── operations/    release, segurança, diagnóstico   (F4)
```

## Regras

1. **Nada aqui pode descrever algo que não existe.** Documento de fase futura
   diz explicitamente que é plano — e plano vive no roadmap, não num guia.
2. **Comando documentado é comando executado**: todo exemplo é copiável e roda
   como está.
3. **A decisão vive no ADR; o resumo aponta para ela** — não existe segunda
   fonte para o mesmo conteúdo.
4. **`reference/` não recebe conteúdo de engenharia**, e `docs/` não recebe
   conteúdo de timbre.
