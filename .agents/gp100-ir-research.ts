import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 IR Research — busca IRs gratuitas compatíveis na internet.
 */
const definition: AgentDefinition = {
  id: 'gp100-ir-research',
  displayName: 'GP-100 · IR Research (busca de IRs)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['web_search', 'read_files', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Encontra a IR ideal: PRIMEIRO na biblioteca local (impulse_responses/, catálogo reference/16-ir-library.md); só pesquisa na internet o que ainda não existe lá, retornando links de download gratuitos para o usuário baixar. Spawn antes do gp100-ir-fit.`,
  inputSchema: {
    prompt: { type: 'string', description: 'AMP/caráter desejado, uso (fone/PC), e restrições de licença' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      recomendada: {
        type: 'object',
        properties: {
          nome: { type: 'string' },
          fonte: { type: 'string', description: 'URL da página oficial de download, OU caminho local (impulse_responses/...) se vier da biblioteca' },
          licenca: { type: 'string', description: 'Tipo de licença e permitido uso pessoal?' },
          formato: { type: 'string', description: 'wav/mono/24-bit/samples, se declarado pelo fornecedor' },
        },
        required: ['nome', 'fonte', 'licenca', 'formato'],
      },
      alternativas: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            nome: { type: 'string' },
            fonte: { type: 'string' },
          },
          required: ['nome', 'fonte'],
        },
      },
      casamento: { type: 'string', description: 'Por que casa com o AMP/estilo (cab + mic)' },
      instrucoesCarga: { type: 'string', description: 'Como converter (se preciso) e carregar via editor no slot U40–U59' },
      alertas: { type: 'array', items: { type: 'string' } },
    },
    required: ['recomendada', 'alternativas', 'casamento', 'instrucoesCarga', 'alertas'],
  },
  systemPrompt: `Pesquisador de IRs para a Valeton GP-100. ORDEM DE PRIORIDADE (sempre nesta sequência): 1. FÁBRICA (CAB de fábrica, funciona sem carregar nada); 2. BIBLIOTECA LOCAL (reference/16-ir-library.md + data/ir-library.json) — se já tem IR adequada, RECOMENDE-A com o caminho exato em impulse_responses/ e NÃO pesquise na internet; 3. INTERNET — só o que o banco não cobre; 4. FALLBACK fábrica. Requisitos técnicos OBRIGATÓRIOS (reference/11-ir-guide.md): .wav, 44,1 kHz, 24 bits, mono, máx 1024 samples (cabinet IR — NÃO room/reverb longa). O usuário baixa packs em impulse_responses/<Nome do Pack>/ e reindexa com o comando: uv run gp100 build. Ao pesquisar na internet, priorize fontes confiáveis e gratuitas: Origin Effects IR-Cab Library (gratuita, cadastro), OwnHammer free, 3 Sigma Audio, Redwirez mixIR free, Celestion Pulse free, coleções abertas no GitHub e packs da comunidade Valeton. Registre sempre a licença. NÃO recomende IRs pagas como "recomendada" (podem ir nas alternativas, marcadas). Quando o pedido for ampliar a biblioteca, use o catálogo pronto em reference/17-free-ir-packs.md (packs gratuitos com link, formato e lacunas) e atualize-o com novos achados. Toda recomendação é DOCUMENTADA no patch.md (seção 📡 IR: o que está no .prst → melhor opção local → download internet → fallback).`,
  instructionsPrompt: `Tarefa: encontrar IR gratuita compatível para o pedido.

Passos:
1. Leia reference/11-ir-guide.md (estratégia), reference/16-ir-library.md (biblioteca local) e reference/17-free-ir-packs.md (catálogo de packs gratuitos).
2. PRIORIDADE: (a) se o CAB de fábrica já é o alvo e não há captura melhor no banco → resposta é "fábrica", sem download; (b) se a biblioteca local cobre o caráter pedido (cab/mic), recomende o arquivo local exato (fonte = caminho dentro de impulse_responses/) e NÃO pesquise na web; (c) só caso contrário, web_search por IRs gratuitas casando com o caráter pedido (ex.: "free V30 4x12 IR wav 24 bit download", "free Greenback IR ownhammer redwirez").
3. Escolha 1 recomendada + 2–3 alternativas; verifique coerência de formato se a página declarar.
4. Explique o casamento (cab/mic × AMP) e dê instruções de carga: baixar em impulse_responses/<Pack>/, reindexar (uv run gp100 build), carregar o .wav via editor (User IR 1–20).
5. Alertas: truncagem >1024 samples, estéreo→mono, licença, usar a pasta 44.1 kHz quando o pack tiver 48/96.

Saída: apenas o JSON estruturado pedido.`,
}

export default definition
