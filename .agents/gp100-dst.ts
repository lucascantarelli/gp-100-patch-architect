import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 DST specialist — overdrive/distorção/fuzz (13 modelos do catálogo fw 2.0).
 */
const definition: AgentDefinition = {
  id: 'gp100-dst',
  displayName: 'GP-100 · DST (overdrive/distorção)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo DST da GP-100 (13 drives do catálogo fw 2.0: Green OD, Yellow OD, Super OD, Blues OD, Tube Clipper, Lazaro, Red Haze, SM Dist, Darktale, Chief, La Charger, Flex OD; Bass Dist é de baixo). Os nomes T-S OD, BLUES, OD-1, RIP, D-Zero, Metal, Fat Fuzz, TRI Fuzz, BIG Fuzz e OCT Fuzz existem só no manual V1.8 — não os use. Spawn para escolher drive e parâmetros oficiais.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Estilo, intensidade de saturação, captador e papel do DST no patch' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      modelo: { type: 'string', description: 'Nome EXATO do modelo DST na GP-100 ou OFF' },
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
      interacaoComAmp: { type: 'string', description: 'Como este drive interage com o AMP escolhido (ganho total)' },
      evite: { type: 'array', items: { type: 'string' } },
    },
    required: ['modelo', 'on', 'parametros', 'porQue', 'interacaoComAmp', 'evite'],
  },
  systemPrompt: `Especialista no módulo DST da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: Green OD, Yellow OD, Super OD, Blues OD, Tube Clipper, Lazaro, Red Haze, SM Dist, Darktale, Chief, La Charger, Flex OD, Bass Dist) — use EXATAMENTE esses nomes na saída. reference/02-dst.md fornece estratégia/estilo/ranges humanos e o mapeamento de pedais clássicos. Guitarra-alvo: Squier Strat single coils. NUNCA invente modelos; traduza pedidos genéricos ("Tube Screamer" → Green OD, "Blues Driver" → Blues OD, "RAT" → La Charger) via reference/14-glossario.md + reference/15.`,
  instructionsPrompt: `Tarefa: escolher o modelo do módulo DST e seus parâmetros.

Passos:
1. Leia reference/02-dst.md (completo) e, se o pedido citar nomes genéricos, reference/14-glossario.md.
2. Escolha UM modelo (ou OFF se o ganho virá do AMP) e TODOS os parâmetros com valores oficiais, considerando estilo + captador + AMP vizinho.
3. Explique a interação com o AMP (ganho total da pilha; evitar clipagem).
4. Liste 2–4 avisos "Evite" aplicáveis.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
