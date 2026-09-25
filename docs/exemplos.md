# Exemplos de ponta a ponta — o fluxo comentado

**Leia isto se** você quer ver o fluxo **acontecendo** antes de ler regra. São
quatro trajetos reais do repositório, cada um com os comandos que o executam
e o arquivo que os prova. Todos os comandos são copiáveis (e o linter da #58
confere que existem).

## 1 · Do defs ao patch na pedaleira (`gp100 build`)

```
data/defs/SN.json  ──▶  gp100 build  ──▶  patches/Santana/…/SMOO1CL.prst + patch.md
     (fonte única)         (3 passos)         (derivados byte a byte reprodutíveis)
```

```bash
uv run gp100 build --quiet        # regenera TUDO do defs (idempotente)
uv run gp100 verify               # frescor: derivado = defs?
```

- **A máquina cobra**: o e2e do TestH regenera em sandbox e compara byte a
  byte — editou o defs e esqueceu o build? CI vermelho.
- **Prova viva**: `SMOO1CL.prst` (Smooth — slot U95) importa no aparelho.

## 2 · Consultar um patch como o agente lê (`gp100 show --json`)

```bash
uv run gp100 show FOXY01BA --json
```

Saída com spec completo, cadeia, parâmetros com **nome oficial** e contexto
(slot, música, álbum) — o **mesmo dossiê** que o site e o `/catalog/`
derivam. Contrato da #91: agentes não parseiam Markdown.

## 3 · Cola de palco — a setlist ótima (`gp100 setlist`)

```bash
uv run gp100 setlist Smooth Money
```

Ordena as músicas **minimizando trocas de módulos entre patches** (o que você
desliga no modo STOMP entre uma e outra) e imprime o roteiro de palco.

## 4 · Docs consistentes por máquina (`audit_docs.py`)

```bash
uv run python .github/scripts/audit_docs.py
```

Varre os 79 `.md`: issue citada existe e está no estado dito, caminho
resolvendo (presente, índice ou histórico), link relativo, milestone real,
comando válido. É o gate da #58 — a classe de erro "doc divergindo" morre aqui.

---

**Próximo passo**: monte o seu — escolha uma música no
[site](https://lucascantarelli.github.io/gp-100-patch-architect/), leia o
`patch.md` dela e toque. Para o fluxo completo de contribuição,
[guia do contribuidor](guia-contribuidor.md).
