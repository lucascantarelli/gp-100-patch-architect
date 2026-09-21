import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 PRE specialist — pré-efeitos (COMP, COMP4, Boost, AC Sim, wahs, OCTA).
 */
const definition: AgentDefinition = {
  id: 'gp100-pre',
  displayName: 'GP-100 · PRE (pré-efeitos)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo PRE da GP-100 (COMP, COMP4, Boost, AC Sim, T-WAH, A-WAH, V-Wah, C-Wah, OCTA). Spawn para escolher modelo PRE e parâmetros dentro dos ranges oficiais.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, contexto, captador e papel do PRE no patch' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo PRE na GP-100 ou OFF' },
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
      porQue: { type: 'string', description: '1 parágrafo justificando em PT-BR' },
      evite: { type: 'array', items: { type: 'string' }, description: 'Avisos do que evitar neste contexto' },
    },
    required: ['modelo', 'on', 'parametros', 'porQue', 'evite'],
  },
  systemPrompt: `Especialista no módulo PRE da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: COMP, COMP4, Boost, AC Sim, T-Wah, V-Wah, C-Wah, OCTA, Pitch, Saturate, Step Filter). reference/01-pre.md: estratégia, receitas por estilo e avisos. Guitarra-alvo: Squier Strat single coils. NUNCA invente modelos; se o pedido citar algo inexistente, ofereça o mais próximo pelo nome real do firmware e explique a adaptação.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo PRE e seus parâmetros para o pedido recebido.

Passos:
1. Leia reference/01-pre.md (completo) e reference/00-signal-chain.md (seção cadeia).
2. Decida se PRE fica ON ou OFF (às vezes OFF é a melhor resposta — diga por quê).
3. Escolha UM modelo e defina TODOS os parâmetros dele com valores dentro do range oficial, coerentes com: estilo, captador (posição na Strat), módulos vizinhos informados.
4. Justifique em 1 parágrafo e liste 2–4 avisos "Evite" aplicáveis.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
