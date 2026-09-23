# ADR-0004 — UI na 2.1, sobre uma API — nunca sobre os módulos internos

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #30

## Contexto

A UI é o próximo grande passo depois da 2.0, e a pergunta que decide toda a
arquitetura é: **o que a UI importa?** Se ela importar `build_song_patches` e
`gen_indexes` (como faria um app que "chama os scripts"), a 2.0 vira refém do
legado: cada mudança de formato de arquivo quebra a tela, e o núcleo precisa
carregar estado de apresentação.

Somam-se dois fatos do projeto: o produto gera **arquivos** (97 `.prst` + doc) e
a operação real acontece em máquina local (não há servidor, usuário nem dado
central).

## Decisão

1. **A UI não entra na 2.0.** A 2.0 entrega o núcleo profissional e a CLI.
2. A UI da 2.1 consome uma **API FastAPI** local, e a API consome os mesmos
   **casos de uso** que a CLI — mesmo código, duas portas.
3. O caminho é sempre `UI → API → application → domain`. Nenhuma tela importa
   `infrastructure` diretamente.
4. A API expõe contrato versionado (`/v1/...`), OpenAPI gerado do código e
   health/readiness — porque a partir daí existe um processo de longa duração.

```
CLI (2.0)  ─┐
            ├─→ application/ ─→ domain/ ─→ infrastructure/ (defs, .prst, zip)
API (2.1)  ─┘
UI (2.1)  → API
```

## Consequências

- ✅ O núcleo não aprende nada sobre apresentação: a 2.0 fica estável enquanto a
  UI é construída.
- ✅ Ganho imediato mesmo sem UI: os casos de uso testados uma vez servem CLI e
  API (sem duplicar regra, que é a falha que o doc 21 já flagrou uma vez).
- ✅ Abre a porta para automação externa (integração, script de terceiro) sem
  exigir a instalação do pacote.
- ⚠️ FastAPI + uvicorn entram como dependências **da 2.1**, num grupo separado
  (`[project.optional-dependencies] api`) — quem só usa a CLI não instala.
- ⚠️ Custa uma camada de serialização (DTOs) que a CLI não precisa; o preço é
  pago na 2.1, não agora.
- ⚠️ Autenticação fica explicitamente **fora**: a API nasce local (loopback) e
  só ganha auth quando/se houver implantação compartilhada.

## Alternativas descartadas

- **UI desktop empacotada (Electron/Tauri) sobre os scripts** — acopla a tela ao
  formato de arquivo e não cria contrato reutilizável; cada mudança de pipeline
  vira mudança de UI.
- **Streamlit/Gradio direto sobre o domínio** — rápido para protótipo, mas o
  protótipo vira a arquitetura: sem contrato estável, sem versionamento da API,
  sem teste de contrato.
- **TUI (Textual) como "UI" da 2.0** — resolve o terminal, não a experiência
  visual; a hipótese continua viva, mas depende de uso real que só a 2.1 mostra.
