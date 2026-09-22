# NOTICE — escopo da licença e conteúdo de terceiros

O [`LICENSE`](LICENSE) deste repositório é **MIT**, e vale para **o código e a
documentação originais do projeto**: os scripts em `tools/`, os testes em
`tests/`, os agentes em `.agents/`, os templates, e os textos em `reference/`,
`prompts/` e `knowledge.md`.

Este arquivo existe separado de propósito: o `LICENSE` precisa conter apenas o
texto canônico do MIT para que o GitHub (e ferramentas de compliance) o
identifiquem automaticamente como `MIT`. Qualquer texto adicional no mesmo
arquivo rebaixa a detecção para `NOASSERTION` — foi o que aconteceu quando o
escopo abaixo estava lá dentro.

## O que NÃO é coberto pelo MIT

Continua pertencendo aos respectivos titulares:

| Item | Situação |
|---|---|
| **Marcas, modelos e nomes de equipamento** — Valeton, GP-100, Fender, Marshall, Vox, Celestion, Origin Effects, e amplificadores/pedais citados | Uso **nominativo e descritivo**, para identificar o equipamento que cada patch reproduz. Nada neste repositório é afiliado, patrocinado ou endossado pelos fabricantes. Ver [`reference/14-glossario.md`](reference/14-glossario.md) |
| **Títulos de músicas, nomes de artistas e de álbuns** | Usados como referência para identificar o timbre documentado. Não há transcrição de letra, partitura nem áudio de obra alguma |
| **Packs de Impulse Response de terceiros** | **Não versionados aqui** justamente por isso. A IR-Cab Library V3 é gratuita com cadastro no site da Origin Effects, mas a licença não concede redistribuição. Ver [`impulse_responses/README.md`](impulse_responses/README.md) |
| **Manual oficial da Valeton** (`manual.pdf`) | Obra de terceiro. Não versionado — obtenha no site do fabricante. `tools/render_manual_page.py` o lê localmente, se você o tiver |
| **`.prst` da biblioteca `patches/`** | Estes **são** do projeto: gerados por `tools/build_song_patches.py` e cobertos pelo MIT |

## Precisa corrigir uma atribuição?

Abra uma issue ou um PR. Correções de atribuição e de crédito são bem-vindas e
costumam ser rápidas — ver [`CONTRIBUTING.md`](CONTRIBUTING.md).
