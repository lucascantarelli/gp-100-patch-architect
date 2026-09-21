import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Globals specialist — master, EXP, tuner, looper, USB, save.
 */
const definition: AgentDefinition = {
  id: 'gp100-globals',
  displayName: 'GP-100 · Globais & Utilidades',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista em configurações globais da GP-100: MASTER VOLUME, saída/USB, pedal EXP (mapeamento/calibração), afinador, drum machine, looper e fluxo de salvamento. Spawn para orientar setup global e escolha de slot de usuário.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Contexto: gravação em PC, show, prática com drum; e o patch ao qual as globais se aplicam' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      masterVolume: { type: 'string', description: 'Orientação de MASTER VOLUME para a sessão' },
      saidaUSB: { type: 'string', description: 'Configuração de saída/USB recomendada (44,1 kHz, ASIO etc.)' },
      expMapeamento: { type: 'string', description: 'Função sugerida do pedal EXP para este patch (Volume/Wah/parâmetro) ou N/A' },
      slotUsuario: { type: 'string', description: 'Slot U01–U99 sugerido conforme mapa de organização' },
      nomePainel: { type: 'string', description: 'Nome curto para o painel (8–10 caracteres)' },
      drumParaTeste: { type: 'string', description: 'Drum pattern + BPM sugerido para testar o patch, ou N/A' },
      orientacoes: { type: 'array', items: { type: 'string' } },
    },
    required: ['masterVolume', 'saidaUSB', 'expMapeamento', 'slotUsuario', 'nomePainel', 'drumParaTeste', 'orientacoes'],
  },
  systemPrompt: `Especialista em configurações globais da Valeton GP-100. Fontes: reference/10-globals.md (master, EXP, tuner, looper, USB, save) e reference/13-preset-list.md (drum patterns + BPMs). Regra de ouro do projeto: MASTER VOLUME é fixo da sessão (60–70%) e NUNCA compensa patch; volumes se equilibram dentro do patch. Fluxo de áudio do projeto: guitarra → GP-100 → PC (USB ou L/R) + fones PHONE. Você também cobre os MODOS DOS FOOTSWITCHES (reference/00-signal-chain.md): modo PATCH (FS-A/B trocam preset) vs modo STOMP (FS-A/B ligam/desligam módulos ao vivo — SYSTEM → Mode → Stomp) — oriente o modo e a atribuição dos switches quando a documentação de um patch tiver momentos de toggle.`,
  instructionsPrompt: `Tarefa: definir o setup global e utilidades para o patch/sessão informado.

Passos:
1. Leia reference/10-globals.md e, se sugerir drum, reference/13-preset-list.md.
2. Preencha cada campo do JSON: master, saída/USB (inclua dica de ASIO no Windows se for gravação), EXP (só se fizer sentido: Volume p/ swells, Wah p/ V-Wah), slot de usuário conforme mapa (clean U01–U10, blues/rock U11–U30, hard/metal U31–U50, experimental U51–U70, sob encomenda U71–U90, utilidades U91–U99), nome curto de painel, drum+BPM para teste.
3. Liste 2–4 orientações práticas (ex.: segurar TAP para afinador, calibrar EXP).

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
