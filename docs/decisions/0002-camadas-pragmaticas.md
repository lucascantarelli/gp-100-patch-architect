# ADR-0002 — Camadas pragmáticas, sem cerimônia de Clean Architecture

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #27; PKG-003

## Contexto

O domínio real do projeto é pequeno e bem definido: a cadeia fixa de nove
módulos, o catálogo de parâmetros por modelo, a validação do defs, o arquivo
`.prst` e a colagem de patches. O que faltava não era abstração — era **fronteira
entre regra e I/O**: `gp100.py`, `gen_indexes.py` e `build_release.py` liam o
JSON cru, então um defs inválido só explodia longe da causa.

## Decisão

Quatro camadas, com dependência em uma direção só (`interfaces →
application → domain`, `application/infrastructure → domain`):

| Camada | Contém | Regra dura |
|---|---|---|
| `domain/` | cadeia, catálogo de params, modelo, validação, exceções | puro: sem `pathlib` de I/O, sem `typer`, sem `rich`, sem tocar disco |
| `infrastructure/` | defs JSON, formato `.prst`, zip de release | pode importar `domain`; **nada importa de volta** |
| `application/` | casos de uso que orquestram os dois | recebe dados/caminhos, devolve objetos tipados, **nunca imprime** |
| `interfaces/cli/` | Typer + Rich | só traduz caso de uso em texto, cor e código de saída |

Sem classes de serviço, sem repositório genérico, sem DTO de camada para camada:
onde o dado é um `dict` do JSON (o `spec`/`doc` do patch), ele atravessa como
`dict` tipado — inventar uma conversão só para "parecer hexagonal" é custo sem
benefício.

## Consequências

- ✅ A regra que mais importa ("o defs é a fonte única e é validado na porta")
  fica imposta por **uma** função (`infrastructure.defs.carregar_e_validar`), não
  por disciplina de quem escreve script.
- ✅ Domínio testável sem disco: os 53 testes unitários rodam em milissegundos.
- ✅ A API/UI futura (ADR-0004) reusa `application/` inteira, sem herdar `print`
  ou código de saída do terminal.
- ⚠️ `application/` nasce quase vazia — é honesto: os casos de uso migram nos
  PRs PKG-004…006, não num único salto.
- ⚠️ Exige revisão para o domínio não virar depósito de conveniência: I/O que
  "só essa regra precisa" é I/O que pertence à infraestrutura.

## Alternativas descartadas

- **DDD completo (agregados, repositórios, eventos)** — o sistema não tem
  invariante transacional nem ciclo de vida de agregado; seria nomenclatura sem
  função.
- **Hexagonal com portas/adaptadores formais** — mesma avaliação: uma porta
  abstrata para ler um JSON que existe em um único caminho é indireção pura.
- **Monorepo com pacotes separados (`gp100-core`, `gp100-cli`)** — dois pacotes
  para ~300 linhas de núcleo quebrariam a migração incremental e a CLI ficaria
  sem consumidor publicado.
