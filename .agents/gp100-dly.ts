import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 DLY specialist — 6 delays.
 */
const definition: AgentDefinition = {
  id: 'gp100-dly',
  displayName: 'GP-100 · DLY (delay)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo DLY da GP-100 (Dly Mono, Dly Dual, Ping Pong, Analog, Tape, Beat). Spawn para escolher delay, tempo e parâmetros oficiais.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, BPM (se souber), papel do delay e o que o RVB está fazendo' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo DLY na GP-100 ou OFF' },
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
      tempoMsOuBeat: { type: 'string', description: 'Tempo em ms ou subdivisão Beat, com cálculo (45000/BPM etc.)' },
      porQue: { type: 'string' },
      evite: { type: 'array', items: { type: 'string' } },
    },
    required: ['modelo', 'on', 'parametros', 'tempoMsOuBeat', 'porQue', 'evite'],
  },
  systemPrompt: `Especialista no módulo DLY da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: Sweet, M-Echo, M-Echo2, P-Echo, Ping Pong, Slapbk, T-Echo, 999 Echo, Rev Echo, Vin-Rack — formato p0=Fdbk %, p1=Delay ms, p2=High Cut-like). reference/08-dly.md: estratégia por estilo e cálculo de tempos (dotted 1/8 = 45000/BPM; 1/4 = 60000/BPM; 1/8 = 30000/BPM). Regra: delay e reverb não disputam — um é o "grande" do patch. NUNCA invente modelos.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo DLY e seus parâmetros (ou OFF).

Passos:
1. Leia reference/08-dly.md (completo — tabela de tempos).
2. Com BPM informado, calcule o tempo exato; sem BPM, proponha valor e explique como ajustar com TAP.
3. TODOS os parâmetros com valores oficiais; High Cut musical (3000–8000 típico).
4. Coerência com o RVB informado (evite dois espaciais gigantes).
5. Liste 2–4 avisos "Evite" (feedback run-away, slapback infinito etc.).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
