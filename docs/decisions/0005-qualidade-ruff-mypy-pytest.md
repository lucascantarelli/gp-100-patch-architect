# ADR-0005 — Qualidade: ruff + mypy --strict + pytest, com piso de cobertura

- **Status**: aceito — **parcialmente revogado na 2.0** (auditoria #125): a
  migração planejada para o pytest foi CONCLUÍDA (issue #23; decisão registrada
  no doc 23 §3) e o escopo do gate citado abaixo mudou — `tools/` foi extinto
  na #33. O que permanece: ruff + mypy --strict + pytest com piso de cobertura.
  O resto desta página é o registro da decisão na época ("103 testes,
  unittest").
- **Data**: 2026-09
- **Decisão relacionada**: issues #26, #29, #23

## Contexto

A suíte existente é boa (103 testes, unittest, stdlib pura) e roda em CI — mas
**não havia lint, formatação nem type check de Python**. O resultado aparece em
dois achados de auditoria: imports mortos que sobreviveram a uma refatoração
(doc 22, D1) e um catálogo de camadas declarado e nunca conectado (D3). Nenhum
dos dois era bug de raciocínio: era ausência de verificação automática.

## Decisão

1. **ruff** para lint **e** formatação — um binário, uma config (`pyproject`).
2. **mypy `strict`** com escopo no pacote (`src/gp100_architect`); o legado entra
   módulo a módulo, junto com a migração.
3. **pytest** como runner oficial (decisão do mantenedor para a 2.0), com
   marcadores `unit/integration/contract/e2e` definindo a pirâmide.
4. **Cobertura com piso em 90%**, medida só no pacote — não no legado.
5. **pre-commit** local com os mesmos gates rápidos + higiene de arquivo.
6. **Escopo honesto do gate**: `tools/`, `.github/scripts/` e a suíte histórica
   ficam fora das listas de lint/formatação enquanto a migração não os traz.
   Cada arquivo sai da lista no PR que o migra — não existe "lintamos tudo
   depois".

## Consequências

- ✅ Um comando local reproduz o que o CI reprova: `ruff check`/`ruff format
  --check`/`mypy`/`pytest` — sem "funciona na minha máquina".
- ✅ `mypy --strict` no domínio já pegou, na primeira execução, três pontos reais
  de tipo (`object` tratado como `dict`, rótulo opcional em `join`).
- ✅ Cobertura medida onde importa (o núcleo): 91% hoje, piso 90 — regressão
  reprova, refatoração não trava.
- ⚠️ **pytest é a primeira dependência de desenvolvimento** e a sua adoção
  completa exige migrar 103 testes de `unittest` (issue #23): a convivência é
  suportada pelo pytest, então a migração é incremental e sem apagão.
- ⚠️ Duas listas de exclusão para manter (ruff e pre-commit) até o fim da
  migração; ficam comentadas com o mesmo critério de saída.
- ⚠️ `ruff format` reescreve blocos Python dentro de Markdown: as skills de
  terceiros em `.agents/skills/` **não** entram no gate (conteúdo externo).

## Alternativas descartadas

- **black + isort + flake8** — três ferramentas e três configs para o que o ruff
  faz com uma; o projeto não tem histórico que justifique mantê-las.
- **pyright** — excelente, mas exigiria Node no job de qualidade de Python; o
  `tsc` já roda em job próprio para os agentes.
- **Cobertura global (incluindo legado)** — puniria código em migração e
  esconderia o número que interessa (o núcleo).
- **`fail_under` alto no primeiro dia (95%)** — travaria refatoração legítima; o
  piso sobe quando o pacote estiver completo (PKG-009).
