# ADR-0008 — `.agents/` é contrato com o Freebuff: não se move para `.ai/`

- **Status**: aceito
- **Data**: 2026-09
- **Decisão relacionada**: issues #25, #33

## Contexto

O repositório tem 19 agentes `.ts` tipados, 11 skills versionadas e 4 prompts
canônicos. A reorganização típica de projeto open source pediria uma pasta
neutra (`.ai/`) com `agents/`, `skills/`, `rules/`, `prompts/` — o que soa
organizado, mas **quebra o carregamento**: o Freebuff lê `.agents/` por
convenção, e `.agents/skills/<nome>/SKILL.md` é o formato do padrão Agent Skills.
Mover a pasta não é refatoração de arquivo: é desligar as skills.

## Decisão

1. **`.agents/` permanece na raiz**, com a estrutura que a ferramenta carrega:
   agentes `.ts` na raiz, `skills/<nome>/SKILL.md`, `types/`, `README.md`.
2. **Skills de terceiros não são reformatadas nem "melhoradas"**: entram
   versionadas como recebidas (o `ruff format` nem as enxerga, justamente porque
   o formato 0.14+ reescreve blocos Python dentro do Markdown).
3. **Precedência documentada** (doc 23): regras do projeto (`knowledge.md`,
   `reference/`) > skills do GP-100 > skills genéricas > skills globais da máquina.
   Skill genérica que conflita com a convenção do projeto **perde** — o caso
   concreto é a skill de testes `pytest`-cêntrica, que venceu apenas porque a 2.0
   adotou pytest (ADR-0005).
4. **Skill nova segue o padrão das existentes**: frontmatter acionável ("use
   quando…"), fonte única citada por caminho (nunca regra copiada) e rodapé de
   precedência.

## Consequências

- ✅ As skills continuam carregando automaticamente, inclusive fora do projeto.
- ✅ Os agentes passam a ter onde consultar arquitetura: `docs/decisions/` e
  `ARCHITECTURE.md` são fontes que uma skill pode citar.
- ⚠️ A organização "neutra" (`.ai/`) fica proibida por contrato — quem propuser
  precisa primeiro ter a ferramenta suportando o caminho novo.
- ⚠️ Versionar skill de terceiro cria a obrigação de manter a origem: mudanças
  locais (tradução, ajuste) devem ser registradas no doc 23.

## Alternativas descartadas

- **`.ai/` como pasta neutra com symlink para `.agents/`** — symlink não
  sobrevive ao checkout no Windows, e o repositório é usado nele.
- **Só documentar prompts e apagar as skills** — perde o gatilho automático que é
  o motivo de existirem.
- **Mover agentes para o pacote Python** — confunde ferramenta de IA com código
  de produto; `.ts` não é distribuível via `pyproject`.
