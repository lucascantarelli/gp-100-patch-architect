import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 MOD specialist — 11 modulações.
 */
const definition: AgentDefinition = {
  id: 'gp100-mod',
  displayName: 'GP-100 · MOD (modulação)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo MOD da GP-100 (Chorus, CE-1, CHO 1x2, FLNG 1, FLNG 2, Phaser 1, Phaser 2, Trem/Pan, Vib/U-Vib, Rotary, AUTOYM). Spawn para escolher modulação e parâmetros oficiais.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, ganho do patch, BPM se relevante e papel da modulação' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo MOD na GP-100 ou OFF' },
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
  systemPrompt: `Especialista no módulo MOD da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: A-Chorus, G-Chorus, B-Chorus, Flanger, Phaser, Vibrato, Vibe, Opto Trem, Sine Trem — p0=Rate 0–99, p1=Depth 0.5~2.1 no formato do arquivo). reference/06-mod.md: estratégia por estilo e guia de moderação com ganho. NUNCA invente modelos; traduza pedidos ("Uni-Vibe" → Vibe, "tremolo" → Opto Trem/Sine Trem) via reference/14-glossario.md.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo MOD e seus parâmetros (ou OFF).

Passos:
1. Leia reference/06-mod.md (completo).
2. Escolha UM modelo coerente com estilo/ganho/BPM; TODOS os parâmetros com valores oficiais (respeite enums como Type/Mode).
3. Se BPM foi informado, alinhe Rate/Speed ao tempo da música.
4. Liste 2–4 avisos "Evite" aplicáveis.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
