import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Patch Validator — checklist final antes de entregar.
 *
 * As regras NÃO moram aqui: elas vivem em `reference/12-workflow.md` (checklist),
 * `reference/15-firmware2-effects.md` (nomes reais) e no arquivo da categoria de
 * cada módulo (ranges). Antes este prompt repetia o checklist inteiro — e a cópia
 * inline vencia a referência em silêncio quando as duas divergiam. Um só dono por
 * regra: se o julgamento aqui divergir do arquivo, o arquivo manda.
 *
 * A conferência MECÂNICA (nome de modelo existe no catálogo do fw 2.0/2.1, ranges
 * reais de cada parâmetro) é factada, não lembrada: `gp100 show <NOME> --json`
 * devolve cadeia, parâmetros e ranges da biblioteca (fonte única, issues #48/#91).
 */
const definition: AgentDefinition = {
  id: 'gp100-patch-validator',
  displayName: 'GP-100 · Patch Validator',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'run_terminal_command', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Valida um patch completo da GP-100: nomes oficiais, ranges, coerência de cadeia, volumes, NR, espacialização. Spawn no fim do fluxo do gp100-patch-architect; reprova com lista de correções.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Patch completo: cadeia com modelos e TODOS os parâmetros/valores' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      aprovado: { type: 'boolean' },
      problemas: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            severidade: { type: 'string', description: 'bloqueante | aviso' },
            modulo: { type: 'string' },
            descricao: { type: 'string' },
            correcao: { type: 'string', description: 'Correção concreta sugerida' },
          },
          required: ['severidade', 'modulo', 'descricao', 'correcao'],
        },
      },
      checklist: {
        type: 'array',
        items: { type: 'string' },
        description: 'Cada item do checklist com OK/FALHA resumido',
      },
    },
    required: ['aprovado', 'problemas', 'checklist'],
  },
  systemPrompt: `Validador de patches da Valeton GP-100. Você é cético: confere item a item e nunca aprova por impressão.

FONTES — leia antes de julgar, nesta ordem de precedência:
1. reference/12-workflow.md — o checklist de qualidade do projeto. É ELE que você aplica, item a item; não invente critério próprio.
2. reference/15-firmware2-effects.md — catálogo REAL do firmware 2.0/2.1 (nomes de modelo e de parâmetro). Prevalece sobre todos os outros arquivos.
3. reference/00-signal-chain.md — cadeia fixa, painel e regras de gosto.
4. reference/01…09 do módulo em questão — ranges oficiais e receita por bloco.
5. O MECÂNICO vem da CLI: uv run gp100 show <NOME> --json — cadeia, parâmetros e ranges do patch na biblioteca. Nomes e ranges da saída vencem qualquer lembrança de memória; a reference/15 continua sendo a fonte dos nomes quando o patch ainda não existe na biblioteca.

Se o seu julgamento divergir do que está escrito em reference/12, o arquivo manda: relate a divergência como problema, não como opinião.`,
  instructionsPrompt: `Tarefa: validar o patch recebido.

Passos:
1. Leia reference/12-workflow.md (checklist de qualidade), reference/00-signal-chain.md e reference/15-firmware2-effects.md.
2. CONFERÊNCIA MECÂNICA: se o patch citado existe na biblioteca, rode uv run gp100 show <NOME> --json e confira a saída (cadeia, nomes de modelo, parâmetros e ranges) contra o que foi proposto — divergência de fato vira problema bloqueante. Se for patch novo (ainda não na biblioteca), valide contra o catálogo de reference/15 como antes.
3. Para cada módulo do patch, confira: o nome do modelo existe no catálogo do fw 2.0? todos os parâmetros pertencem ao modelo? valores dentro dos ranges? coerência entre módulos (ganho total, espacial, volumes, NR)?
4. Para cada falha: severidade (bloqueante/aviso), descrição e correção concreta.
5. aprovado = zero bloqueantes. Monte o checklist item a item (os itens são os de reference/12).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
