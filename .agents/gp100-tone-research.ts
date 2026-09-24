import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Tone Research — pesquisa na internet os equipamentos usados pelo
 * artista/na música informada (guitarra, amps, pedals, estúdio) e devolve um
 * dossiê estruturado. NÃO interpreta para a GP-100 — isso é trabalho do tone-mapper.
 *
 * Issue #91: quando o alvo já tem patch na biblioteca, o ponto de partida é
 * `gp100 find <alvo> --json` (o que já existe, slots e camadas) — pesquisa na
 * internet só do que a biblioteca ainda não cobre.
 */
const definition: AgentDefinition = {
  id: 'gp100-tone-research',
  displayName: 'GP-100 · Tone Research (referências de artistas)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['web_search', 'read_files', 'run_terminal_command', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Pesquisa na internet os equipamentos e técnicas de um artista/música informada (guitarra, captadores, amps, cabines, pedals de efeito, estúdio/era/gravação). Spawn ANTES do gp100-tone-mapper. Retorna dossiê com fontes.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Artista, música/era/álbum específico (se houver), e o que o usuário quer extrair (riff, solo, timbre geral)' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      alvo: { type: 'string', description: 'Artista/música/era pesquisada e o alvo sonoro (riff/solo/timbre geral)' },
      guitarra: { type: 'array', items: { type: 'string' }, description: 'Guitarras/captadores usados, com confiabilidade' },
      amplificador: { type: 'array', items: { type: 'string' }, description: 'Amps e cabines, com contexto (estúdio/ao vivo/era)' },
      pedais: { type: 'array', items: { type: 'string' }, description: 'Pedais de efeito (overdrive, fuzz, delay, reverb, modulação), com confiabilidade' },
      tecnicas: { type: 'array', items: { type: 'string' }, description: 'Técnicas relevantes: afinação, captador usado na gravação, camadas, dinâmica' },
      contextoEstudio: { type: 'string', description: 'Como foi gravado (amp real no estúdio, DI, simulações, era/gravação)' },
      confianca: { type: 'string', description: 'alta | media | baixa — com justificativa (quantas fontes concordam)' },
      fontes: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            titulo: { type: 'string' },
            url: { type: 'string' },
            pontoChave: { type: 'string' },
          },
          required: ['titulo', 'url', 'pontoChave'],
        },
      },
      lacunas: { type: 'array', items: { type: 'string' }, description: 'O que não foi possível confirmar' },
    },
    required: ['alvo', 'guitarra', 'amplificador', 'pedais', 'tecnicas', 'contextoEstudio', 'confianca', 'fontes', 'lacunas'],
  },
  systemPrompt: `Pesquisador de timbres: descobre COM QUE EQUIPAMENTOS um artista/música foi gravado. Fontes em ordem de confiança: entrevistas do próprio artista e técnicos de gravação > revistas especializadas (Guitar World, Premier Guitar, Guitar.com) > rig databases (Equipboard etc.) > fóruns/Reddit > blogs. Sempre registrar URL e o ponto-chave de cada fonte. Cuidado com mitos repetidos: se fontes divergem, declare confiança 'media' ou 'baixa' e explique a divergência em lacunas. Pesquise em inglês (mais fontes) e em português se necessário. Use 2–4 web_search com queries específicas (ex.: "John Frusciante Under the Bridge amp recording", "David Gilmour Time solo gear rig delay", "<artista> <música> guitar tone breakdown").`,
  instructionsPrompt: `Tarefa: montar o dossiê de equipamentos/técnicas para o alvo informado.

Passos:
1. Extraia do prompt: artista, música/era/álbum (se especificado), e o que interessa (riff, solo, timbre geral).
2. ANCORAGEM LOCAL: rode uv run gp100 find <artista-ou-música> --json — se a biblioteca já tem patches do alvo, liste-os no dossiê (slots/camadas existentes) e foque a pesquisa no que falta (era diferente, camada específica).
3. Rode 2–4 web_search cobrindo: gear/rig do artista para aquela era, breakdown específico da música, se necessário captador/afinação usada.
3. Para CADA categoria do schema (guitarra, amplificador, pedais, técnicas), liste itens como "equipamento — contexto (confiança: alta/média/baixa)".
5. contextoEstudio: 1–3 frases sobre como o som foi realmente obtido (amp no estúdio? pedal direto? sobreposição de camadas?).
6. confianca geral + fontes (3–6, cada uma com o ponto-chave que sustenta a conclusão) + lacunas honestas.

Não interprete para a GP-100 — quem faz o mapeamento é o gp100-tone-mapper. Saída: apenas o JSON estruturado.`,
}

export default definition
