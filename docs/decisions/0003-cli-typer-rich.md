# ADR-0003 — CLI oficial com Typer + Rich

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issue #27; PKG-004

## Contexto

Hoje a "CLI" é `tools/gp100.py` + cinco scripts irmãos: cada um faz o seu
`argparse` (ou lê `sys.argv` na mão), tem o seu formato de saída e o seu próprio
código de retorno. Não existe `--help` coerente, `--version` nem completion. A
automation do próprio repositório (release, índices) chama scripts por caminho e
depende de texto impresso — contrato implícito, fácil de quebrar sem perceber.

## Decisão

A interface de linha de comando passa a ser **um** app Typer (`gp100`), com
**Rich** para a saída humana, distribuído como console script:

```
gp100 validate        valida o defs (hoje)
gp100 setlist ...     cola de palco                (PKG-006)
gp100 find/show/diff  consulta da biblioteca       (PKG-005)
gp100 build/verify    pipeline e guarda de frescor (PKG-004)
gp100 release ...     empacotamento e changelog    (PKG-007)
```

Contrato do adaptador (não negociável, é o que torna a CLI testável):

1. **Nenhuma regra na CLI** — ela monta caminho, chama o caso de uso e traduz o
   resultado (texto, cor, exit code). A API da 2.1 expõe o mesmo comportamento.
2. **Códigos de saída estáveis**: `0` sucesso, `1` entrada inválida, `2` erro de
   uso (emitido pelo Typer). Script de automação depende disso.
3. **`--version` é `is_eager`**: responde antes de qualquer trabalho e sem tocar
   o defs.

## Consequências

- ✅ `gp100 --help` vira a documentação viva da ferramenta, e o completion
  (`gp100 --install-completion`) elimina a memorização de caminhos.
- ✅ Testável como contrato com `typer.testing.CliRunner` (já é: 6 testes cobrem
  `--version`, `validate` e os códigos de saída).
- ✅ Mensagens acionáveis ganham cor e estrutura sem `print` espalhado.
- ⚠️ **Duas dependências de runtime** (typer → click/shellingham, rich) — fim da
  stdlib pura *na CLI*. Decisão consciente: o núcleo de dados (defs, `.prst`)
  continua sem dependência nenhuma, e é ele que roda no pipeline.
- ⚠️ Os scripts legados continuam existindo até PKG-008; a saída em texto deles
  é o que o TestH compara, então a migração é **uma família de comandos por PR**.

## Alternativas descartadas

- **`argparse` puro (stdlib)** — manteria zero dependências, mas exige escrever à
  mão help, subcomandos, validação de tipos, completion e formatação; já sabemos
  onde isso termina (seis parsers divergentes).
- **Click direto** — é a base do Typer; escrever decorators manuais e converter
  tipos à mão é trabalho que o Typer faz por anotação, sem ganho em troca.
- **Textual (TUI)** — resolveria a UI de terminal, não a interface de automação;
  a hipótese de TUI entra só se a 2.1 mostrar uso real (ver ADR-0004).
