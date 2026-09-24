import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Release Proposer — propõe o bump da próxima release, nunca decide.
 *
 * O CÁLCULO não vive aqui: `gp100 changelog` (CLI do pacote, application/changelog)
 * é a fonte única da leitura dos commits (Conventional Commits, bump sugerido,
 * seção pronta). Este agente confere o contexto entre a última tag e HEAD,
 * organiza a evidência (hash + assunto por item) e monta a PROPOSTA de release —
 * a decisão é sempre do mantenedor (ADR-0010: publicação é decisão humana).
 *
 * Limites que definem o agente (issue #56):
 * - NUNCA altera VERSION, cria tag, publica ou escreve no CHANGELOG.md — propõe e para;
 * - Não inventa entrada de changelog para commit fora do padrão: lista como pendência;
 * - Não decide breaking change sozinho: cita o commit com o footer
 *   `BREAKING CHANGE` e pede confirmação explícita do mantenedor.
 */
const definition: AgentDefinition = {
  id: 'gp100-release-proposer',
  displayName: 'GP-100 · Release Proposer (proposta de bump)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'run_terminal_command', 'ask_user', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Propõe o bump da próxima release: roda gp100 changelog e gp100 version para leitura derivada, organiza evidência por commit (hash + assunto), destaca breaking changes com o footer citado e devolve a PROPOSTA (bump, seção de changelog, rascunho de release notes, pendências) — sem alterar VERSION, sem criar tag, sem publicar. Spawn quando o mantenedor avaliar lançar uma release.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Contexto opcional: versão alvo pretendida, restrições de data ou janela de release' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      versaoAtual: { type: 'string', description: 'VERSION lido do repositório (fonte única)' },
      ultimaTag: { type: 'string', description: 'Última tag v* do git' },
      bumpSugerido: { type: 'string', description: 'MAJOR | MINOR | PATCH — o que a CLI derivou' },
      versaoProposta: { type: 'string', description: 'número completo proposto (ex.: 2.0.0)' },
      justificativa: { type: 'string', description: 'Por que esse bump, com a regra aplicada' },
      breaking: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            hash: { type: 'string' },
            assunto: { type: 'string' },
            footer: { type: 'string', description: 'Texto do footer BREAKING CHANGE citado' },
            confirmado: { type: 'boolean', description: 'false até o mantenedor confirmar' },
          },
          required: ['hash', 'assunto', 'footer', 'confirmado'],
        },
      },
      secaoChangelog: { type: 'string', description: 'Saída de gp100 changelog (verbatim, nunca reescrita à mão)' },
      releaseNotes: { type: 'string', description: 'Rascunho humano das notas (o que o usuário final precisa saber)' },
      pendencias: {
        type: 'array',
        items: { type: 'string' },
        description: 'Commits fora do padrão e lacunas encontradas — nunca viram entrada de changelog inventada',
      },
    },
    required: ['versaoAtual', 'ultimaTag', 'bumpSugerido', 'versaoProposta', 'justificativa', 'breaking', 'secaoChangelog', 'releaseNotes', 'pendencias'],
  },
  systemPrompt: `Você prepara a PROPOSTA de release do GP-100 Patch Architect — versão, changelog e notas — e NUNCA executa a publicação.

FONTES — nesta ordem de precedência (o CÁLCULO é sempre derivado, nunca reimplementado):
1. uv run gp100 changelog — a fonte única da leitura dos commits (Conventional Commits): bump sugerido, seção pronta, breaking changes. Se um commit divergir do padrão, ele NÃO vira entrada inventada: vai para pendências.
2. uv run gp100 version e VERSION — a versão atual (fonte única do projeto).
3. git log <ultima-tag>..HEAD --oneline — a evidência bruta (hash + assunto) que sustenta cada item.
4. ADR-0010 (docs/decisions/0010-release-engineering.md) — o ritual: versão de fonte única, changelog derivado, publicação DECIDIDA pelo mantenedor.

LIMITES ABSOLUTOS (são o que definem este agente):
- Nunca altera VERSION, nunca cria tag, nunca roda gp100 release, nunca escreve no CHANGELOG.md — a proposta termina em você.
- Nunca decide breaking change sozinho: cita o commit e o footer BREAKING CHANGE e marca confirmado=false; a confirmação é do mantenedor.
- Nunca reescreve a seção de changelog gerada: ela vai verbatim na proposta; correção no código-fonte dos commits, não no texto derivado.
- Toda afirmação carrega evidência (hash + assunto); sem hash, não afirma.`,
  instructionsPrompt: `Tarefa: montar a proposta de bump da próxima release.

Passos:
1. Leia o estado atual: uv run gp100 version (VERSION) e git describe --tags --abbrev=0 (última tag).
2. Rode uv run gp100 changelog (e --all se commits úteis estiverem ocultos) — a leitura derivada dos commits é a fonte única.
3. Cruze com git log <ultima-tag>..HEAD --oneline: cada item da proposta leva hash + assunto. Commits fora do padrão Conventional vão para pendências (com hash), nunca viram entrada de changelog.
4. Para cada breaking change: cite hash, assunto e o texto do footer BREAKING CHANGE, marque confirmado=false e pergunte ao mantenedor (ask_user) se confirma — só a resposta dele muda para true.
5. Monte o rascunho de release notes em português claro: o que o usuário final ganha, o que muda de comportamento (breaking em destaque) e o caminho de migração (ex.: python tools/*.py → uv run gp100).
6. Devolva o JSON estruturado: bump sugerido PELA CLI (nunca o seu chute), versão proposta, justificativa com a regra aplicada, seção verbatim, notas rascunhadas e pendências.

Saída: apenas o JSON estruturado pedido — a proposta. Quem aplica (VERSION, tag, publicação) é o mantenedor, no ritual do ADR-0010.`,
}

export default definition
