# Patch GP-100 — {NOME DO PATCH}

| | |
|---|---|
| **ID do projeto** | {XX-YYY-Dnn} |
| **Slot de usuário sugerido** | {Uxx} |
| **Nome no painel** | {NOMECURTO} |
| **Data de criação** | {AAAA-MM-DD} |
| **Firmware alvo** | V1.8 |
| **Instrumento** | Squier Stratocaster (single coils) |
| **Autor** | GP-100 Patch Architect |

## 1. Intenção sonora
{2–4 frases: estilo, referências, o que o músico deve sentir ao tocar.}

## 2. Setup do instrumento
- **Captador recomendado**: {posição (bridge/middle/neck) + por quê}
- **Volume/tom da guitarra**: {ex.: Volume 10, Tone 8}
- **Cabo/cadeia física**: guitarra → GP-100 INPUT → OUTPUT L/R → PC (gravação) · PHONE → fones monitores

## 3. Cadeia de módulos
```
PRE({modelo}) → DST({modelo}) → AMP({modelo}) → NR(ON) → CAB({modelo}) → EQ(ON) → MOD({modelo}) → DLY({modelo}) → RVB({modelo})
```
| Módulo | Estado | Modelo |
|---|---|---|
| PRE | {ON/OFF} | {…} |
| DST | {ON/OFF} | {…} |
| AMP | {ON/OFF} | {…} |
| NR | {ON/OFF} | — |
| CAB | {ON/OFF} | {… ou USER IR} |
| EQ | {ON/OFF} | — |
| MOD | {ON/OFF} | {…} |
| DLY | {ON/OFF} | {…} |
| RVB | {ON/OFF} | {…} |

## 4. Parâmetros módulo a módulo

### PRE
| Parâmetro | Valor | Range oficial | Por quê |
|---|---|---|---|
| | | | |

_(repita por módulo; para enums como Mode/Type/Char use os valores exatos)_

### CAB / IR {se USER IR}
- **Arquivo**: {nome.wav} · **Fonte**: {URL} · **Licença**: {…}
- **Slot**: {U40–U59}
- Low Cut {v} Hz · High Cut {v} Hz · Level {v} dB

## {N} Impulse Response (CAB) — seção EXCLUSIVA obrigatória (logo após os ajustes finos)
Política de 4 passos (nunca omitir, mesmo quando a resposta é "fábrica já é o alvo"):
1. **No `.prst` agora**: {CAB de fábrica do patch} — funciona imediatamente, sem carregar IR.
2. **Banco local** (`impulse_responses/`): {se houver captura do gabinete real — arquivo exato + slot User IR 1–20 + Low/High Cut/Level; se não houver, declarar que a fábrica é o alvo}.
3. **Internet**: {se nem fábrica nem banco cobrem — link de download gratuito de reference/17-free-ir-packs.md; formato 44,1 kHz/24 bits/mono/máx 1024 samples}.
4. **Fallback**: mantenha o CAB de fábrica (o patch foi afinado com ele).
> A IR substitui o CAB (não empilha). Máx. 1 IR por patch. Pacote com pastas 48/96 kHz → usar sempre a 44.1 kHz.

## {N} Modos de atuação (toggle) — seção EXCLUSIVA obrigatória (logo após a IR)

A GP-100 liga/desliga qualquer módulo em tempo real: no painel (slot a slot, ON/OFF) ou pelos footswitches FS-A/FS-B no modo STOMP. Desligar não apaga parâmetros — religar restaura o som do patch-base.

1. **Estado de fábrica**: tabela dos 9 módulos com ON/OFF e modelo (o que o `.prst` carrega).
2. **Momentos da música**: para cada momento — nome, módulos a alternar (SÓ os indicados), quando usar e dica. Módulos OFF com modelo escolhido são "sobressalentes"; cada momento deve inverter o estado atual (nunca "ligar o que já está ligado").
3. **Modo STOMP**: como atribuir FS-A/FS-B aos módulos-chave do patch (ex.: FS-A = DLY, FS-B = DST) e voltar ao modo Patch.
> Nunca sugerir toggle de AMP/CAB (sustentam volume e corpo do patch).

## 5. Globais
- **MASTER VOLUME**: {posição fixa da sessão, ex.: 65%} (não muda por patch)
- **EXP pedal**: {função mapeada ou N/A}
- **Saída/USB**: {44,1 kHz · ASIO no Windows}

## 6. Como carregar na pedaleira
**Opção A — digitar no painel** (receita completa):
1. {Gire o Knob até um slot U livre → pressione para editar}
2. {Slot a slot: ligue módulos, escolha modelos, ajuste parâmetros com ► ◄ + Knob}
3. {SAVE → escolha {Uxx} → renomeie para {NOMECURTO} → confirme}

**Opção B — editor GP-100 Edits**: {montar na tela seguindo as tabelas acima; salvar no slot; se IR, carregar o .wav no slot U4x antes}.

## 7. Teste de som sugerido
- **Riff/referência**: {o que tocar — ex.: riff de 12 compassos em A com swing}
- **Drum para acompanhar**: {pattern + BPM}
- **O que escutar**: {ataque, sustain, ruído, definição, equilíbrio}
- **2 ajustes finos rápidos**: {ex.: "se agudo demais → EQ High -1"; "se cauda engolida → NR Thr -45"}

## 8. Evite com este patch
- {avisos específicos do contexto}

## 9. Changelog
| Data | Versão | Mudança | Motivo (feedback do músico) |
|---|---|---|---|
| {data} | D1 | criação | — |
