import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 NR specialist — noise gate.
 */
const definition: AgentDefinition = {
  id: 'gp100-nr',
  displayName: 'GP-100 · NR (noise reduction)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo NR da GP-100 (Thr -80~0 dB, Rel 0~99). Spawn para calibrar o gate conforme ganho total do patch.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Ganho total (DST Gain + AMP Gain), uso de fuzz, contexto de gravação' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Sempre "NR"' },
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
  systemPrompt: `Especialista no módulo NR da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (modelos reais do firmware 2.0: Gate 1, Gate 2). reference/07-nr.md: estratégia de Threshold/Release por ganho. Regra central: NR é obrigatório com ganho total ≥ 55 (single coils são ruidosos), mas nunca engole caudas/sustain. Fuzz pede gate mais aberto. Guitarra: Squier Strat single coils ligada direto — hum/ruído presente.`,
  instructionsPrompt: `Tarefa: definir Thr e Rel do NR (ou OFF em patches ultra-limpos).

Passos:
1. Leia reference/07-nr.md (completo).
2. Calcule o ganho total aproximado do patch (informado no prompt: DST + AMP) e escolha Thr/Rel da tabela de startpoint, ajustando ao contexto (gravação em casa pede um pouco mais fechado).
3. Justifique e liste 2–3 avisos "Evite" (caudas engolidas, fuzz estrangulado).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
