# ADR-0006 — CI/CD: workflows separados, uv com lockfile, zero escrita no repositório

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #28, #32

## Contexto

O CI atual é bom no que faz (job de testes + `tsc`, portão de veredito único,
`permissions: contents: read`), mas nasceu em torno de stdlib pura: sem
instalação, sem lint, sem tipos, sem cobertura. E o desenho futuro (release,
segurança, dependências) não cabe em um arquivo só sem virar um pipeline longo
onde ninguém sabe qual etapa falhou.

## Decisão

1. **Um workflow por responsabilidade**, todos com portão de veredito quando
   fizer sentido: `ci.yml` (testes + qualidade + agentes), `security.yml`
   (CodeQL, dependency review, auditoria de workflows), `release.yml`
   (publicação), `project-automation.yml` (board). A Fase F3 (#32) extrai
   `quality.yml`/`docs.yml` quando o volume justificar — **não antes**.
2. **uv + lockfile no CI**: `uv sync --frozen`; o CI nunca resolve versão nova.
3. **Zero escrita no repositório** (mantido): com `contents: read`, a proteção do
   `main` não precisa de exceção para o app `github-actions` — e essa exceção
   valeria para *todo* workflow do repositório, que é exatamente o custo que se
   quer evitar.
4. **Trava de runtime 3.14** continua sendo o primeiro passo que executa Python.
5. **Cada job com `timeout-minutes`** e actions de primeira parte no major que já
   declara `using: node24` — regras verificadas pelo auditor
   `.github/scripts/audit_workflows.py` (roda no próprio CI).

## Consequências

- ✅ Falha tem endereço: job e etapa, não um log de 400 linhas.
- ✅ Cache de uv por lockfile deixa o job de testes no mesmo patamar de tempo do
  anterior, já com dependências instaladas.
- ✅ O auditor de workflows garante que runner flutuante, gatilho perigoso
  (`pull_request_target`/`workflow_run`) e interpolação de contexto não confiável
  em `run:` não entrem por descuido.
- ⚠️ Duplicação controlada de setup entre jobs (checkout + python + uv). O ganho
  é paralelismo e diagnóstico claro; se o custo crescer, a saída é composite
  action local, não fundir tudo num job.
- ⚠️ Sem escrita no repositório, **nada de auto-commit de artefato gerado**: a
  garantia é o guarda de frescor (TestH) reprovar e imprimir o comando de
  conserto. É a mesma decisão já tomada no doc 19 e ela se mantém.

## Alternativas descartadas

- **Um `ci.yml` monolítico com tudo** — o pipeline vira fila sequencial (lint
  esperando teste) e o veredito perde granularidade.
- **Jobs de matrix de SO** — os artefatos já são verificados byte a byte e a
  ordem estável entre sistemas é testada em um runner; rodar macOS/Windows
  multiplicaria minutos sem cobrir risco novo.
- **Auto-commit de artefatos** — exige escrita no `main`, quebra a proteção sem
  exceção e já foi descartado antes (doc 19): dois mecanismos para a mesma
  garantia, um deles sem CI.
- **Publicar no PyPI a cada tag** — a 2.0 ainda é uma biblioteca de conteúdo
  local; publicação é decisão de release, não de CI (ver ADR-0010).
