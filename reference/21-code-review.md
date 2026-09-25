# 21 · Code review — código Python do projeto (set/2026)

> **Escopo**: os 16 módulos de `tools/`, os de `tests/` e os scripts de
> `.github/scripts/` — padrão do projeto (stdlib pura, Python 3.14 apenas).
> **Método**: leitura integral dos módulos núcleo (`build_song_patches`,
> `generate_prst`, `defs_schema`, `gp100`, `gp100_setlist`, `build_release`,
> `gen_changelog`, `gen_indexes`, `analyze_prst`) e dirigida dos auxiliares;
> cada achado tem arquivo/linha verificável. **Veredito geral: código sadio** —
> o projeto tem disciplina rara (fonte única de verdade, validação na porta,
> zero escrita nos testes); os achados abaixo são de consolidação, não de
> correção de bugs.

## 1 · Forças (o que manter)

| Prática | Onde | Por quê importa |
|---|---|---|
| Fonte única de verdade | `slot_map`, `PARAM_NAMES`, defs como fonte da biblioteca | índices, `.prst` e docs nunca divergem |
| Validação na porta | `defs_schema.carregar_e_validar()` no build | dado inválido morre cedo, com caminho JSON e correção |
| Timestamp determinístico | `generate_prst` (`GP100_BUILD_TIME`) | fim do churn de merge em 97+ arquivos |
| Guarda de sincronia | `TestH` (pipeline em cópia temp) | derivado defasado reprova com comando de conserto |
| Testes sem efeito colateral | tmpdirs + constantes de módulo | CI com `contents: read` é possível |
| Erros acionáveis | `defs_schema`, `gp100`, `gp100_setlist` | `SystemExit` sugere a correção, não só o erro |
| Trava de runtime | `defs_schema` + step 0/2 do CI | política 3.14 em código, não em prosa |
| `main(argv=None)` testável | `gp100`, `gp100_setlist` | testes chamam a função, não subprocess |

## 2 · Achados — severidade Média

**M1 · `CHAIN` definido em 4 módulos** — `build_song_patches.py:66`,
`defs_schema.py:38`, `generate_prst.py:61` e `gp100.py:40` declaram a mesma
lista `['PRE','DST','AMP','NR','CAB','EQ','MOD','DLY','RVB']`. Risco real: o
projeto já documenta que cópia inline vence a referência em silêncio (doc do
`patch-validator`). Se a cadeia do fw 2.2 mudar, são 4 lugares para errar.
**Correção**: mover para `param_names.py` (que já é o módulo "catálogo") ou um
novo `chain.py`; reexportar onde preciso. `EXPORT_ORDER`/`CHAIN_POS` ficam em
`generate_prst` (são particulares do formato `.prst`).

**M2 · Loaders que pulam a validação** — `gen_indexes.load_defs()`,
`gp100.carregar_defs()` e `build_release.collect_patches()` leem o defs com
`json.loads` cru. Hoje o defs está válido, mas a rede de proteção da #14 só
existe no `build_song_patches`: um defs quebrado gera índices errados na CLI
(e na cola de palco) **sem erro nenhum**. **Correção**: `carregar_e_validar()`
nas três portas (import de `defs_schema`; sem ciclo — `defs_schema` não importa
nenhum deles).

**M3 · RETIRADO durante a verificação** — a suspeita inicial (subprocess sem
eco em `_rodar` e `GP100_BUILD_TIME` não propagado em `gp100 build`) não se
sustenta no código real: `_rodar` imprime `$ python {passo}` antes de cada
passo, usa `subprocess.run` (não shell) e herda o ambiente — com
`GP100_BUILD_TIME` definido, ele chega ao gerador; sem, o default é o mesmo do
pipeline manual. Registrado na seção 4 como prática verificada.

## 3 · Achados — severidade Baixa

**B1 · Comentário defasado** — `analyze_prst.py:40` fala em "62 patches da
própria biblioteca"; a biblioteca tem 97. Comentário que erra número mina
confiança no resto do arquivo.

**B2 · `slotSugestao` à mão** — os `doc.slotSugestao` do defs (ex.: `U01+U02`)
são string escrita à mão, enquanto o slot verdadeiro vem do `slot_map`. Os
testes de índice pegam drift grosseiro, mas a fonte duplicada existe.
**Correção (2.0)**: gerar do `slot_map` no build (o mesmo caminho do schema v2).

**B3 · `gp100_setlist.Biblioteca.padrao`** — hardcoded `{'RI','RI1','BA','AM'}`;
se um álbum futuro usar sufixo diferente como "riff principal", o default erra
silenciosamente (cai no primeiro patch). Aceitável hoje; documentar no docstring
(pendente abaixo).

**B4 · Duplicação de helpers de mídia** — `song_pasta`/`song_display` existem
em `gen_indexes`, `gp100` e (variante) `build_release`. Mesma mecânica do M1,
menor porque raramente muda.

**B5 · `gp100_setlist.plano_json` tem campo `slot` morto** — `None` preenchido
depois num loop que não existe; ou remova o campo ou preencha no loop de
construção (o slot está disponível via `slot_map`).

## 4 · Boas práticas verificadas (sem ação)

- `encoding='utf-8'` explícito em toda leitura/escrita — porta Windows à prova
  de cp1252; `reconfigure` nos CLIs.
- Docstrings **explicam decisão**, não sintaxe (`slot_map`, `load_ir_library`,
  `collect_patches`).
- `re.search` com `re.escape` e fronteira (`assert_valid_prst`), ranges por
  rótulo no schema (Time em ms) — detalhes que evitam falsos positivos.
- `collections.defaultdict` bem usado; `dataclasses` onde caberia (`templates`
  continua dict, mas o acesso é centralizado).
- `_rodar`/`git()` capturam stderr e falham com mensagem, sem `check=True`
  nu; `_rodar` faz eco de cada passo antes de executar e herda o ambiente
  (`GP100_BUILD_TIME` propaga para o gerador).

## 5 · Proposta: agente `gp100-code-reviewer`

O mesmo padrão dos demais agentes se aplica a revisão de código — com uma
fronteira importante: **regra vivendo em arquivo, julgamento no agente**.

| Aspecto | Proposta |
|---|---|
| `id` | `gp100-code-reviewer` |
| Papel | Revisor cético de PRs: Python (tools/tests), YAML (.github/workflows), TS (.agents) e docs gerados |
| `toolNames` | `read_files`, `code_search`, `run_terminal_command`, `end_turn` (precisa rodar suíte/tsc para *provar*, não só ler) |
| Fontes (precedência) | 1. este doc (doc 21 — critérios e anti-padrões do projeto) · 2. `CONTRIBUTING.md` (fluxo e convenções) · 3. `knowledge.md` (regras de patch quando o PR tocar neles) |
| Saída | `structured_output` como o `patch-validator`: `aprovado`, `problemas[]` (severidade/arquivo/linha/correção), `checklist[]` |
| Gatilho | Spawneado no fim do fluxo de quem abre PR; opcionalmente um job de CI que roda o agente e comenta o PR (sem poder bloquear — sugestão, não portão) |
| Checklist mínimo | suíte passa localmente? derivados sincronizados (guarda)? nenhuma escrita em teste? fonte única respeitada (nada de CHAIN/loader duplicado)? encoding utf-8? erro acionável em falha nova? |
| Limite honesto | o agente NÃO substitui CI nem o review humano: ele padroniza a primeira passada e reprovando cedo o que hoje só aparece no CI |

Custo: 1 arquivo `.ts` (~80 linhas, modelo atual) + entrada no
`spawnableAgents`; nenhum novo serviço. Risco: falsos positivos de estilo —
mitigado mantendo o prompt curto e delegando critério ao doc 21, como o
`patch-validator` faz com o doc 12.

## 6 · Plano sugerido (ordem de custo/benefício)

1. **M1 + M2 + B1 + B5** (uma PR pequena): `chain.py` + `carregar_e_validar`
   nas 3 portas + comentário do `analyze_prst` + campo `slot` do JSON. Risco
   baixo, suíte verde — é o tipo de PR que o próprio projeto chama de
   "fundações". — **✅ executado neste mesmo PR**
2. **B3** documentar no docstring da `Biblioteca` na próxima passada pela CLI.
3. **B2/B4** entram naturalmente no schema v2 (issue #8) — não fazer antes.
4. **Agente `gp100-code-reviewer`** (seção 5) — pequeno, independente.

---
[`📖 README do projeto`](../README.md) · [`📚 Reference`](README.md) · [`🗺 Roadmap`](19-roadmap-v2.md)
