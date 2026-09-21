import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 RVB specialist — 6 reverbs.
 */
const definition: AgentDefinition = {
  id: 'gp100-rvb',
  displayName: 'GP-100 · RVB (reverb)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo RVB da GP-100 (Room, Hall, Church, Plate, Spring, Air). Spawn para escolher reverb e parâmetros oficiais.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, papel do reverb (riff vs solo), o que o DLY está fazendo' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo RVB na GP-100 ou OFF' },
      on: { type: 'boolean' },
      parametros: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            nome: { type: 'string' },
            valor: { type: 'string' },
            range: { type: 'string' },
          },
          required: ['nome', 'valor', 'range'],
        },
      },
      porQue: { type: 'string' },
      evite: { type: 'array', items: { type: 'string' } },
    },
    required: ['modelo', 'on', 'parametros', 'porQue', 'evite'],
  },
  systemPrompt: `Especialista no módulo RVB da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: Room, Hall, Church, Plate, Spring, Clear Sky, N-Star, Deep Sea, Mod Verb — p0~p3 no formato do arquivo). reference/09-rvb.md: guia de escolha por estilo e regras de moderação (riff = Mix baixo; Damp 40–60 com hi-gain; um espacial dominante por patch). Guitarra: Squier Strat single coils. NUNCA invente modelos.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo RVB e seus parâmetros (ou OFF).

Passos:
1. Leia reference/09-rvb.md (completo).
2. Escolha UM modelo com a tabela de escolha/startpoint; TODOS os 4 parâmetros com valores oficiais e coerentes com ganho e com o DLY informado.
3. Justifique em 1 parágrafo.
4. Liste 2–4 avisos "Evite" aplicáveis.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
