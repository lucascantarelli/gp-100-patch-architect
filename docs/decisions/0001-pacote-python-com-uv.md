# ADR-0001 — Pacote Python em `src/`, ambiente e comandos com uv

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #26; PKG-001/PKG-002

## Contexto

O projeto tinha 17 scripts em `tools/`, ~6.300 linhas de Python, **nenhum
`pyproject.toml`** — nada era instalável, importável como pacote ou verificável
por ferramenta alguma. O sintoma prático aparecia em três lugares:

1. **Onboarding**: um contribuidor não tinha sequer um comando para rodar a
   suíte; cada script precisava ser invocado por caminho (`python tools/x.py`) e
   só funcionava com `tools/` no `sys.path`.
2. **Import cruzado frágil**: `build_song_patches` fazia `from param_names import
   PARAM_NAMES` — import que só resolve se o diretório estiver na busca, e que
   colide com qualquer coisa de mesmo nome.
3. **Qualidade inexistente**: sem pacote, não havia como rodar lint, type check
   ou medir cobertura com escopo definido.

## Decisão

O código passa a ser um **pacote Python com layout `src/`**, ambiente e execução
gerenciados por **uv**, com **lockfile versionado**. O import name é
`gp100_architect` e o console script é `gp100`.

```
pyproject.toml      metadados, deps, entry point e config das ferramentas
uv.lock             resolução travada (o CI roda `uv sync --frozen`)
src/gp100_architect/...
VERSION             fonte única da versão (lida dinamicamente pelo pyproject)
```

Onboarding alvo:

```bash
git clone <repo> && cd gp-100-patch-architect
uv sync                       # cria .venv e instala tudo do lockfile
uv run pytest -q              # suíte completa
uv run gp100 validate         # CLI oficial
```

**Por que `gp100_architect` e não `gp100`**: o script legado `tools/gp100.py`
(ainda documentado e usado até PKG-008) **sombreia** o pacote — testes dele e
qualquer `sys.path` com `tools/` importam o arquivo, não o pacote. O nome de
import evita a colisão sem tocar no legado; o nome que o usuário digita (o
comando) continua `gp100`. Quando o legado sair, o import name pode ser revisto
sem impacto em quem consome a CLI.

## Consequências

- ✅ `git clone && uv sync && uv run pytest` funciona em qualquer máquina, com a
  mesma resolução de dependências.
- ✅ uv passa a ser a única ferramenta de ambiente (sem `venv`+`pip` paralelo,
  sem `requirements.txt`), e o lockfile transforma "verde ontem" em "verde sob
  as mesmas versões".
- ✅ `py.typed` + `mypy --strict` viram possíveis — o pacote é verificável.
- ⚠️ **Primeira dependência real do projeto**: uv passa a ser exigido para
  desenvolver (o runtime dos scripts legados continua stdlib pura).
- ⚠️ A convivência pacote × legado é temporária e explícita: shims em `tools/`
  reexportam o pacote durante a migração (PKG-003…008).
- ⚠️ Duas verdades enquanto `tools/param_names.py` existir (conteúdo idêntico ao
  do domínio): a remoção é o último passo da migração, não antes.

## Alternativas descartadas

- **Continuar com scripts soltos** — nenhuma ferramenta de qualidade dá escopo
  confiável sem pacote; o custo já estava pago em retrabalho manual.
- **Nome de import `gp100`** — colide com `tools/gp100.py` sempre que `tools/`
  entra no `sys.path`; renomear o legado agora reescreveria documentação
  histórica (`reference/19`, `21`, `22`) e falsificaria registro.
- **`requirements.txt` + `venv`** — sem resolução travada nem resolução de
  dependências de desenvolvimento; `uv` já estava instalado no ambiente do
  mantenedor.
- **Poetry/PDM/Hatch** — resolvem o mesmo problema com mais configuração e sem
  o ganho de velocidade do uv; nenhum é usado hoje no repositório.
