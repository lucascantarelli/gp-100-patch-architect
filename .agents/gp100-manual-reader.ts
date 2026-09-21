import type { AgentDefinition } from './types/agent-definition'

/**
 * GP-100 Manual Reader — consulta pontual ao manual digitalizado.
 * NOTA: leitura de IMAGEM depende do modelo suportar input visual; GLM 5.3 Flash é
 * multimodal. A pasta manual_pages/ NÃO fica mais pre-renderizada: renderize as
 * páginas necessárias sob demanda com `python tools/render_manual_page.py <impressa>`
 * (gera manual_pages/pNN.png alta + preview/pNN.jpg; página impressa NN = arquivo NN+2).
 */
const definition: AgentDefinition = {
  id: 'gp100-manual-reader',
  displayName: 'GP-100 · Manual Reader',
  model: 'z-ai/glm-5.3-flash',
  toolNames: ['read_files', 'code_search', 'run_terminal_command', 'end_turn'],
  includeMessageHistory: false,
  spawnerPrompt: `Consulta pontual ao manual digitalizado da GP-100 (manual.pdf) quando reference/ não cobrir uma dúvida específica. Retorna a transcrição do trecho relevante.`,
  inputSchema: {
    prompt: { type: 'string', description: 'Dúvida específica sobre a GP-100 que precisa do manual' },
  },
  outputMode: 'last_message',
  systemPrompt: `Consultor do manual da Valeton GP-100. O manual.pdf é digitalizado (imagens); a pasta manual_pages/ NÃO fica pre-renderizada — gere a página sob demanda com: python tools/render_manual_page.py <página impressa> (ex.: "python tools/render_manual_page.py 21" cria manual_pages/p23.png + manual_pages/preview/p23.jpg). MAPEAMENTO: página do arquivo pNN = página impressa NN-2 (ex.: impressa 21 = p23.jpg). Seções do manual (impressas): 4 sumário · 5 painel · 6 conexões · 7–9 quick start · 10–13 edição/backup/afinador · 14–16 EXP/system/drums/loop/USB · 17–20 PRE · 21 DST · 21–25 AMP · 26 CAB/IR · 27 EQ+NR · 28–29 MOD · 30 DLY · 31 RVB · 32–35 drums+troubleshooting. reference/ é a base principal; o manual é a autoridade final em divergências.`,
  instructionsPrompt: `Tarefa: responder à dúvida específica usando o manual.

Passos:
1. Localize a seção provável pelo mapa acima e renderize as páginas candidatas: python tools/render_manual_page.py <impressa inicial> <impressa final> (use run_terminal_command; a pasta manual_pages/ pode estar vazia — é normal).
2. Leia manual_pages/preview/pNN.jpg (ou pNN.png para detalhes finos).
3. Transcreva fielmente o trecho que responde à dúvida (cite a página impressa).
4. Se reference/ tiver o dado, confirme consistência; se divergir, aponte a divergência (prevalece o manual).
5. Após responder, remova as páginas renderizadas (rm -rf manual_pages) — elas são efêmeras.`,
}

export default definition
