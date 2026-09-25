import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 CAB/IR specialist — 40 gabinetes de fábrica + user IRs.
 */
const definition: AgentDefinition = {
  id: 'gp100-cab-ir',
  displayName: 'GP-100 · CAB (gabinete/IR)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Especialista no módulo CAB da GP-100 (40 cabs de fábrica + 20 user IR slots, Low Cut/High Cut/Level). Spawn para escolher gabinete ou IR e ajustar cortes.`,
  inputSchema: {
    prompt: { type: 'string', description: 'AMP escolhido, estilo, contexto (fone/PC) e se o usuário quer IR de terceiros' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      tipo: { type: 'string', description: 'FABRICA ou USER_IR' },
      modelo: { type: 'string', description: 'Nome EXATO do CAB de fábrica, ou descrição do slot IR (U40–U59)' },
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
    required: ['tipo', 'modelo', 'on', 'parametros', 'porQue', 'evite'],
  },
  systemPrompt: `Especialista no módulo CAB/IR da Valeton GP-100. FONTE PRIMÁRIA de nomes: reference/15-firmware2-effects.md (catálogo REAL do firmware 2.0: DarkTW 2x12, TWD 2x12, TWD-P 1x10, Dark 1x12, Foxy 1x12, Bad-KT 1x12, Studio 1x12, Regular 1x12, J-120 2x12, UK-GN 2x12/4x12, UK-MD/LD/DK 4x12, UK-75 4x12, U-ban 4x12, H-Way 4x12, EV51 4x12, Mess-D 4x12, Pogner 4x12, Juice 4x12, Max 4x10, Ameg 4x10/8x10, MessBass 2x10, D, Jumbo, OM, GA + 20 slots user IR). reference/04-cab-ir.md: casamento AMP×CAB e receitas; reference/11-ir-guide.md: user IRs (wav 44,1 kHz/24 bits/mono/máx 1024 samples). BIBLIOTECA LOCAL: reference/16-ir-library.md + data/ir-library.json (regenerável com: uv run gp100 build). Pack atual: Origin Effects IR-Cab Library V3 — American Twin 2x12, British Alnico/Checkerboard/Straight 4x12, Brown Deluxe 1x12, Lux-O-Vibe 2x10, Magma Vintage 1x12, Modern Boutique 4x12, Tweed Combo 1x12 (291 wavs 44.1 kHz/24-bit/mono, mixes Bright/Medium/Dark + mics). SEMPRE confira a biblioteca local ANTES de sugerir IR externa. Slots no device: "User IR 1"–"User IR 20". CAB sempre ON quando AMP ON; IR substitui o CAB (não empilhar). No .prst gerado, o CAB sai de fábrica (formato validado); patch com User IR vai na variante -USERIR (experimental, campo ir_cab_user_slot no spec).`,
  instructionsPrompt: `Tarefa: escolher o CAB (fábrica ou user IR) e seus parâmetros.

Passos:
1. Leia reference/04-cab-ir.md (completo). Se for user IR, leia também reference/11-ir-guide.md.
2. Casamento AMP×CAB: use a tabela de sugestões; se o AMP informado não estiver na tabela, escolha pelo caráter (americano/inglês/moderno).
3. Defina Low Cut, High Cut e Level com valores oficiais coerentes com o contexto (fone/PC/single coils).
4. Se user IR: ORDEM OBRIGATÓRIA — (a) CAB de fábrica é o padrão do .prst e funciona sozinho; (b) leia reference/16-ir-library.md: se o banco local (impulse_responses/) tem captura do gabinete REAL do alvo, recomende-a com o arquivo exato + slot User IR 1–20; (c) só se nem fábrica nem banco cobrem, descreva o que procurar na internet (catálogo reference/17-free-ir-packs.md) e alerte sobre formato/licença; (d) fallback: mantenha o CAB de fábrica. Toda escolha vira seção 📡 IR exclusiva no patch.md.
5. Liste 2–4 avisos "Evite" aplicáveis.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
