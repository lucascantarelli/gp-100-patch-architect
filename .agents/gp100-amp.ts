import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 AMP specialist — 40 modelos de amplificador.
 */
const definition: AgentDefinition = {
  id: 'gp100-amp',
  displayName: 'GP-100 · AMP (amplificadores)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo AMP da GP-100 (40 amps guitarra/baixo/acústico com parâmetros exatos). Spawn para escolher amplificador e parâmetros oficiais, casando com CAB e DST.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, nível de ganho, captador e CAB/drive vizinhos' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo AMP na GP-100 ou OFF' },
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
      cabRecomendado: { type: 'string', description: 'CAB ideal para este AMP (nome exato) e por quê' },
      evite: { type: 'array', items: { type: 'string' } },
    },
    required: ['modelo', 'on', 'parametros', 'porQue', 'cabRecomendado', 'evite'],
  },
  systemPrompt: `Especialista no módulo AMP da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: Dark Twin, Tweedy, Bellman 59N, UK 45/50JP/800, Flagman, Foxy 30TB, L-Star CL, Match CL/OD, J-120 CL, Knights CL/OD, Z38 OD, Bad-KT CL, Solo100 LD/OD, Juice R100, EV 51, Dizz VH, Eagle 120, Mess DualV/DualM + baixos/acústicos). reference/03-amp.md fornece descrições, "based on", particularidades de parâmetros e receitas por estilo. Guitarra-alvo: Squier Strat single coils (Treble moderado 50–65, NR obrigatório com Gain ≥ 55). NUNCA invente modelos ou parâmetros.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo AMP e seus parâmetros.

Passos:
1. Leia reference/03-amp.md (completo — atenção às "Diferenças de nomenclatura importantes").
2. Escolha UM modelo coerente com estilo/ganho/captador/drive informado; defina TODOS os parâmetros com valores oficiais.
3. Indique o CAB ideal (nome exato) e justifique.
4. Liste 2–4 avisos "Evite" aplicáveis (inclua warning de NR se Gain ≥ 55).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
