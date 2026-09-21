import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Tone Mapper — recebe o dossiê do gp100-tone-research e traduz cada
 * equipamento real para os modelos REAIS da GP-100 (fw 2.0), com similaridade
 * e parâmetros sugeridos. Fecha a ponte referência → patch.
 */
const definition: AgentDefinition = {
  id: 'gp100-tone-mapper',
  displayName: 'GP-100 · Tone Mapper (referência → GP-100)',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Recebe o dossiê de equipamentos do gp100-tone-research e mapeia cada item para os modelos reais da GP-100 (fw 2.0) com justificativa de similaridade e parâmetros sugeridos. Spawn DEPOIS do gp100-tone-research, alimentando o gp100-patch-architect.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Dossiê do gp100-tone-research (JSON) + captador que o usuário usará + contexto (casa/fone/banda)' },
  },
  outputMode: 'structured_output',
  outputSchema: {
    type: 'object',
    properties: {
      alvo: { type: 'string' },
      mapeamentos: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            equipamentoReal: { type: 'string', description: 'Ex.: Marshall JCM800 + Greenbacks' },
            categoria: { type: 'string', description: 'AMP | DST | CAB | PRE | MOD | DLY | RVB | EQ | NR' },
            modeloGP100: { type: 'string', description: 'Nome EXATO do modelo no fw 2.0, ou NENHUM-EQUIVALENTE' },
            similaridade: { type: 'string', description: 'alta | media | baixa' },
            justificativa: { type: 'string', description: 'Por que este modelo se aproxima (topologia, caráter, "based on" do manual)' },
            parametros: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  nome: { type: 'string' },
                  valor: { type: 'string' },
                  motivo: { type: 'string' },
                },
                required: ['nome', 'valor', 'motivo'],
              },
              description: 'Parâmetros-chave para se aproximar do alvo (respeitando ranges do fw 2.0)',
            },
            adaptacao: { type: 'string', description: 'O que não dá para reproduzir e como compensar (ex.: single coil vs humbucker)' },
          },
          required: ['equipamentoReal', 'categoria', 'modeloGP100', 'similaridade', 'justificativa', 'parametros', 'adaptacao'],
        },
      },
      resumoCadeia: { type: 'string', description: 'Cadeia GP-100 resultante em 1 linha: PRE→DST→AMP→NR→CAB→EQ→MOD→DLY→RVB' },
      avisos: { type: 'array', items: { type: 'string' } },
    },
    required: ['alvo', 'mapeamentos', 'resumoCadeia', 'avisos'],
  },
  systemPrompt: `Tradutor de referências para a Valeton GP-100. FONTES OBRIGATÓRIAS: reference/15-firmware2-effects.md (catálogo REAL fw 2.0 — nomes EXATOS na saída), reference/03-amp.md e reference/02-dst.md (tabelas "Based on" e caráter de cada modelo), reference/14-glossario.md (tradução de nomes clássicos), reference/04-cab-ir.md (casamento amp×cab) e 05–09 para os demais módulos. Guitarra do usuário: Squier Strat SINGLE COILS — adapte: suba Gain ~+5 vs receitas para humbucker, Treble moderado, NR com ganho ≥ 55. Se um equipamento real não tem equivalente razoável, declare NENHUM-EQUIVALENTE e proponha a alternativa mais próxima com similaridade 'baixa' explicando o porquê — NUNCA invente modelos.`,
  instructionsPrompt: `Tarefa: mapear o dossiê de referência para modelos da GP-100.

Passos:
1. Leia reference/15-firmware2-effects.md e os arquivos das categorias presentes no dossiê (03, 02, 04, 06, 08, 09, 01, 05, 07 conforme o caso).
2. Para cada equipamento real relevante (amp, cab, drive, modulação, delay, reverb), escolha o modelo GP-100 mais próximo, com similaridade e justificativa técnica (use a coluna "Based on" do manual: ex. Marshall → UK 45/UK 50JP/UK 800; Fender Tweed → Tweedy; Tube Screamer → Green OD; RAT → La Charger).
3. Defina 3–6 parâmetros-chave por mapeamento, coerentes com captador single coil e o contexto informado.
4. Descreva adaptações honestas (o que a GP-100 não reproduz e como compensar com EQ/CAB/pedais).
5. Monte o resumo da cadeia final e os avisos (NR, volumes, espacial dominante).

Saída: apenas o JSON estruturado.`,
}

export default definition
