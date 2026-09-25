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
6. **Persistência**: acrescentar o patch ao fragmento do álbum (`data/defs/<CHAVE>.json`) e rodar o pipeline (`build_song_patches.py` → `gen_indexes.py`) e a suíte (guarda de determinismo). O `patch.md` e o `.prst` são **gerados** pelo pipeline, não escritos à mão.
7. **Entrega**: resumir o patch na conversa + apontar os arquivos gerados.

## Nomenclatura de patches (vigente)
- **Um patch por música**, em `patches/<Banda>/<Álbum>/<Música>/<NOME>/`.
- Nome no painel = MÚSICA(≤4 letras) + versão(2 dígitos) + CAMADA(2 letras), máx. **12 caracteres** — ex.: `STH01BA`, `CNW01S2`, `PMH01SO`.
- Camadas: BA=base · SO=solo · RI=riff · CL=clean · FL=fills · AR=arpejos · AC=acústico · VO=voz-líder.
- Slots de patch U01…Uxx são **calculados** pela ordem dos defs (não há mapa fixo) — ver `patches/README.md`. Não confundir com os slots de **User IR 1–20** da pedaleira (knowledge.md, regra 10).

## Estrutura de arquivo gerado por patch
```
patches/<Banda>/<Álbum>/<Música>/<NOME>/
├── patch.md              # documento completo — renderizado pelo build_doc()
└── <NOME>.prst           # single fw 2.1, CAB de fábrica
```
Nenhum desses é escrito à mão: o pipeline do pacote (`gp100 build`) os gera a partir de
`data/defs/` — o spec vai **in-memory** ao codec (ADR-0013: nenhum
intermediário em disco; o antigo `spec.json` foi eliminado). IRs de terceiros **não** entram na biblioteca — elas vivem em
`impulse_responses/<Pack>/`, fora do git (política em knowledge.md, regra 10).

```
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
- [ ] **Pipeline rodado**: `gp100 build` (e de novo após baixar pack de IR) — o guarda de determinismo da suíte reprova derivado divergente do que o defs produz (`patches/**` não é commitado).
- [ ] **Suíte verde**: `uv run pytest` — `TestB_FonteUnica_IR` reprova mapa e `patch.md` divergindo sobre IR; `TestG_Indices` reprova índice defasado; `TestH_DadosEmSincronia` é o guarda de determinismo (pipeline numa cópia × derivados).

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

## Pipeline de dados (é o que o guarda de determinismo da suíte roda)
Qualquer elemento novo (música, camada, patch, modelo de efeito, momento de toggle, pack de IR) exige rodar o pipeline, na ordem — `patches/**` é construído, não armazenado (ADR-0013):

```bash
uv run gp100 build    # 1–3. IRs → patches → índices (data/ir-library.json + reference/16)
uv run pytest         # 4. guarda de determinismo: pipeline numa cópia × derivados
```

**Isso é literalmente o que o `TestH_DadosEmSincronia` roda**, a cada `pytest` — local e no CI. **Nenhum job escreve no repositório**: se algum derivado estiver defasado, o teste reprova e imprime o comando exato de conserto, para o autor rodar e commitar.

O último passo é o que separa "rodei o pipeline" de "biblioteca coerente": sem ele, um PR pode mergear com artefato defasado. A fonte única é o defs (`data/defs/`, schema v2) — nenhum script mantém tabela própria de músicas, álbuns ou cabs, e **nada do que o pipeline produz é commitado**: em clone limpo o build recria tudo a partir do defs.

## Limites declarados do projeto
- A GP-100 não tem reorder de cadeia; não criar expectativa de "trocar ordem dos efeitos".
- Não há bloco de IR separado do CAB — IR substitui o CAB.
- O `.prst` **é gerado** (codec `infrastructure/prst`, formato single fw 2.1 validado no aparelho) e a entrega inclui `.prst` + `patch.md` + receita de digitação; IR de terceiros entra **documentada** (não embutida).
- Teste sonoro final é humano (músico + fones); o agente otimiza a probabilidade de acerto.
