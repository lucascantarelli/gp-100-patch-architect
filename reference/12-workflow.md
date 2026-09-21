# GP-100 — Metodologia do Projeto (Workflow do Agente)

## Missão
Criar patches para a **Valeton GP-100** sob demanda: o usuário pede um estilo/música/objetivo, o agente entrega um patch completo (documentado em MD) pronto para digitar na pedaleira ou montar no editor, otimizado para **Squier Stratocaster com single coils** ligada direto na pedaleira.

## Instrumento fixo do projeto
- **Squier Stratocaster**, 3 single coils (neck/middle/bridge), potes 250k.
- Perfil: brilhante, dinâmica forte, menos output que humbuckers, ruído 60 Hz audível com ganho alto.
- Implicações: drives precisam de Level/Middle generosos; hi-gain pede NR; Treble do AMP moderado (55–65); Bridge = mais agressivo (baixe Gain ~5 pontos); Neck = mais escuro/gordo (suba Treble ~5, baixe Bass ~5).

## Fluxo de criação (o orquestrador executa esta sequência)

1. **Entrevista** (se o pedido for vago): estilo/música, limpar vs sujo, contexto (banda, casa, fone), referências de timbre.
2. **Decisão de cadeia**: escolher módulos ON/OFF e modelos dentro das skills de efeito (usar `spawn_agents` para consultar 2–4 skills em paralelo quando o pedido for complexo).
3. **Encaixe**: montar a cadeia final PRE→DST→AMP→NR→CAB→EQ→MOD→DLY→RVB com valores; respeitar regras de ouro (00-signal-chain).
4. **IR** (se aplicável): acionar `gp100-ir-research` para achar IR gratuita + `gp100-ir-fit` para cortes/Level.
5. **Validação**: passar o patch inteiro pelo `gp100-patch-validator` (nomes, ranges, coerência).
6. **Documentação**: gerar `patches/<ID>/patch.md` (template) + receita de digitação.
7. **Entrega**: resumir o patch na conversa + apontar os arquivos gerados.

## Nomenclatura de patches
- ID do projeto: `<ESTILO>-<CARACT>-<Nº>` ex.: `BL-CLN-D01` (blues clean dev 01), `MT-HG-D02`.
- Nome no painel (máx. 8–10 caracteres): versão curta ex.: `BL-CLN-1`.
- Slot de usuário sugerido: ver mapa em `10-globals.md`.

## Estrutura de arquivo gerado por patch
```
patches/<ID>/
├── patch.md              # documento completo (template em /templates)
└── (ir/                  # IRs usadas, se houver — .wav + créditos/licença)
```

## Checklist de qualidade (antes de entregar)
- [ ] Todos os nomes de efeito/parâmetro conferem com `reference/` (nada inventado).
- [ ] Todos os valores dentro dos ranges oficiais.
- [ ] Máx. 9 módulos; cadeia na ordem fixa correta.
- [ ] NR ligado em qualquer patch com Gain ≥ 55.
- [ ] Volumes equilibrados (nenhum módulo Level < 40 ou > 130 sem justificativa).
- [ ] Uma "camada espacial" dominante (DLY ou RVB), nunca dois gigantes.
- [ ] Patches de riff e de solo separados (ou EXP mapeada) quando pedirem "um patch só para show".
- [ ] **Momentos de toggle documentados** (seção "Modos de atuação", após a IR): estado dos 9 módulos + transições por música (só módulos no estado INVERSO; nunca AMP/CAB) + modo STOMP — a GP-100 liga/desliga módulos em tempo real sem perder parâmetros.
- [ ] Instruções de digitação na ordem real dos menus da pedaleira (incluindo os SOBRESSALENTES citados nos momentos).
- [ ] Sugestão de captador (posição na Strat) para o timbre.
- [ ] Teste sugerido (riff + o que escutar).

## Fluxo de ajuste (iteração com o músico)
1. Músico testa e volta com descrição ("muito agudo", "cauda engolida", "riff some na banda").
2. Agente mapeia a reclamação para o módulo certo (tabela de troubleshooting abaixo).
3. Aplica mudanças mínimas (1–2 parâmetros) e atualiza o `patch.md` (seção Changelog).

## Tabela de troubleshooting → módulo
| Reclamação | Módulo/parâmetro típico |
|---|---|
| "Muito agudo/piante" | EQ High -, AMP Treble -, CAB High Cut ↓, IR High Cut |
| "Sem corpo/fino" | EQ Low +, AMP Bass +, DST Bass/Color |
| "Embolado/lama" | EQ Low -, CAB Low Cut ↑, AMP Bass -, RVB Mix ↓ |
| "Cauda engolida" | NR Thr ↑ (menos agressivo), Rel ↑ |
| "Chiado/hum audível" | NR Thr mais fechado, checar cabos |
| "Fzz digital" | CAB/IR High Cut 6500–8000 |
| "Eco mais alto que o seco" | DLY Mix ↓ |
| "Riff some na banda" | EQ Mid +, DST Level +, reverbs ↓ |
| "Volume salta ao ligar efeito" | Level do efeito ≈ bypass (igualar) |
| "Solo não corta" | EQ Mid +3 / Level +15, patch de solo separado |

## Limites declarados do projeto
- A GP-100 não tem reorder de cadeia; não criar expectativa de "trocar ordem dos efeitos".
- Não há bloco de IR separado do CAB — IR substitui o CAB.
- `.prst` (arquivo do editor) não é gerado binariamente pelo agente nesta fase; entrega é via receita de digitação + montagem no editor.
- Teste sonoro final é humano (músico + fones); o agente otimiza a probabilidade de acerto.
