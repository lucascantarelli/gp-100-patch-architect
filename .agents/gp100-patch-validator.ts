import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Patch Validator — checklist final antes de entregar.
 */
const definition: AgentDefinition = {
  id: 'gp100-patch-validator',
  displayName: 'GP-100 · Patch Validator',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
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
  systemPrompt: `Validador de patches da Valeton GP-100. Você é cético: confira item a item contra reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0 — prevalece sobre tudo), reference/00-signal-chain.md, reference/12-workflow.md (checklist) e o arquivo da categoria de cada módulo. Nomes de modelo devem existir EXATAMENTE no catálogo do firmware 2.0; valores dentro dos ranges; cadeia PRE→DST→AMP→NR→CAB→EQ→MOD→DLY→RVB; máx 9 módulos; NR ON com ganho ≥ 55; Level de efeitos ≈ bypass; um espacial dominante; sem dupla IR/CAB empilhados; seção de IR presente (política de 4 passos) e seção de TOGGLE/Modos de atuação presente com momentos que alternam módulos no estado INVERSO ao atual — nunca toggle de AMP/CAB; captador e teste presentes se for documentação final.`,
  instructionsPrompt: `Tarefa: validar o patch recebido.

Passos:
1. Leia reference/12-workflow.md (checklist de qualidade) e reference/00-signal-chain.md.
2. Para cada módulo do patch, leia o arquivo da categoria em reference/ e confira: nome do modelo existe? todos os parâmetros pertencem ao modelo? valores nos ranges? coerência entre módulos (ganho total, espacial, volumes)?
3. Para cada falha: severidade (bloqueante/aviso), descrição e correção concreta.
4. aprovado = zero bloqueantes. Monte o checklist item a item.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
