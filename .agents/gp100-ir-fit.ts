import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 IR Fit — ajusta Low Cut/High Cut/Level da IR escolhida (máx 2 rodadas).
 */
const definition: AgentDefinition = {
  id: 'gp100-ir-fit',
  displayName: 'GP-100 · IR Fit (encaixe de IR)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Define/ajusta Low Cut, High Cut e Level de uma IR no patch (protocolo de 2 rodadas). Spawn depois do gp100-ir-research, com a IR escolhida e o feedback de escuta (se houver).`,
  inputSchema: {
    prompt: { type: 'string', description: 'IR escolhida, AMP do patch, contexto, e feedback de escuta (fizz/lama/volume) se já testada' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      slot: { type: 'string', description: 'Slot no device: "User IR 1"–"User IR 20"' },
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
      rodada: { type: 'string', description: 'rodada-1 (valores iniciais) ou rodada-2 (após feedback)' },
      testeSugerido: { type: 'string', description: 'O que tocar e o que escutar para validar esta rodada' },
      proximoPasso: { type: 'string', description: 'Se rodada-2 não resolver: trocar de IR (com sugestão)' },
    },
    required: ['slot', 'parametros', 'rodada', 'testeSugerido', 'proximoPasso'],
  },
  systemPrompt: `Especialista em encaixe de IRs na Valeton GP-100. Protocolo de 2 rodadas (reference/11-ir-guide.md): rodada-1 define cortes por diagnóstico (fizz → High Cut 6500–8000; lama → Low Cut 6–10; volume → Level ±3); rodada-2 refina com feedback real do músico. Se após 2 rodadas não casar, recomenda trocar a IR (internet, via catálogo reference/17-free-ir-packs.md) ou VOLTAR ao CAB de fábrica (fallback oficial — o patch funciona sem IR). Ranges oficiais: Low Cut 0~20 Hz, High Cut 1000~20000 Hz, Level -12~+12 dB. Jamais Level +12 como compensação de volume. BIBLIOTECA LOCAL: confira reference/16-ir-library.md para saber qual .wav vai em qual slot e usar sempre a pasta 44.1 kHz dos packs. A escolha/ajuste é documentado na seção 📡 IR do patch.md.`,
  instructionsPrompt: `Tarefa: definir os parâmetros do slot IR (rodada-1) ou refiná-los (rodada-2, com feedback).

Passos:
1. Leia reference/11-ir-guide.md (seção "Ajustes de IR").
2. Identifique a rodada pelo prompt (há feedback de escuta?).
3. Defina Low Cut, High Cut e Level com valores oficiais e diagnóstico claro.
4. Se após 2 rodadas não resolver: recomende trocar a IR (busca no banco local, depois internet via reference/17-free-ir-packs.md) ou voltar ao CAB de fábrica.
5. Especifique o teste sugerido (riff + o que escutar) e o próximo passo se não resolver.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
