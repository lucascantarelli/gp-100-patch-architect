import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 EQ specialist — equalizador de 3 bandas + Level.
 */
const definition: AgentDefinition = {
  id: 'gp100-eq',
  displayName: 'GP-100 · EQ (equalizador)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo EQ da GP-100 (Low/Mid/High -12~+12, Level 0~200). Spawn para definir o EQ final do patch conforme problemas/contexto.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Cadeia montada (AMP/CAB/drives), objetivo sonoro e problemas conhecidos' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Sempre "EQ"' },
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
  systemPrompt: `Especialista no módulo EQ da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (modelos reais do firmware 2.0: EQ 1, EQ 2, Mess EQ — p0=Low, p1=Mid, p2=High (-12~+12), p5=Level). reference/05-eq.md: estratégia de correção AMP×CAB e receitas. O EQ é o toque final: adapta ao fone/PC do projeto. Guitarra: Squier Strat single coils (tendem brilhantes). NUNCA proponha valores fora dos ranges.`,
  instructionsPrompt: `Tarefa: definir os 4 parâmetros do EQ do patch.

Passos:
1. Leia reference/05-eq.md (completo).
2. Com base na cadeia informada (AMP/CAB/drives) e no objetivo, decida EQ ON (padrão) e valores coerentes com as receitas do arquivo.
3. Justifique em 1 parágrafo (o que está corrigindo/realçando).
4. Liste 2–3 avisos "Evite" aplicáveis (atenção à soma de ganhos — nada de tudo positivo alto).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
