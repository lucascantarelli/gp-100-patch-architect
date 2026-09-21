# GP-100 — Cadeia de Sinal, Módulos e Fluxo de Edição
> Fonte: `manual.pdf` (GP-100 Online Manual EN, Firmware V1.8). **Para NOMES de modelos, prevalece o catálogo do firmware 2.0/2.1** (`reference/15-firmware2-effects.md`) — nunca invente nomes fora destas tabelas.

## A cadeia (9 módulos simultâneos, máximo)

```
GUITAR IN → [PRE] → [DST] → [AMP] → [NR] → [CAB] → [EQ] → [MOD] → [DLY] → [RVB] → OUT
```

- **PRE** = bloco de pré-efeitos (Compressor, Boost, AC Sim, Wah, Octaver).
- **NR** = Noise Reduction (fica entre AMP e CAB na cadeia real).
- A ordem dos módulos é **fixa** — a GP-100 **não** permite reordenar blocos (só ligar/desligar e escolher modelos dentro de cada bloco).
- Máximo de **9 efeitos simultâneos** (especificação oficial: "Maximum Simultaneous Effects: 9").
- O **looper é pré-efeitos**: ao trocar de patch, o loop gravado muda de timbre também ("pre-effects looper").

## Módulos e seus modelos (resumo navegável)

| Módulo | O que faz | Modelos (contagem) | Referência |
|---|---|---|---|
| PRE | dinâmica, boost, sim acústico, wah, oitava | 9 | `01-pre.md` |
| DST | overdrive / distorção / fuzz | 15 | `02-dst.md` |
| AMP | simulação de amplificador (guitarra, baixo, acústico) | 40 | `03-amp.md` |
| NR | noise gate/reduction | 1 | `07-nr.md` |
| CAB | gabinete + IR (40 de fábrica + 20 slots de usuário) | 39 + D | `04-cab-ir.md` |
| EQ | equalizador paramétrico de 3 bandas | 1 | `05-eq.md` |
| MOD | chorus/flanger/phaser/tremolo/vibrato/rotary | 11 | `06-mod.md` |
| DLY | delays (digital, analógico, tape, beat, Hold) | 6 | `08-dly.md` |
| RVB | reverbs (Room, Hall, Church, Plate, Spring, Air) | 6 | `09-rvb.md` |

## O painel (controles físicos)

| Elemento | Função |
|---|---|
| DISPLAY | exibe nome/parâmetro do patch |
| Knob | ajusta valor do parâmetro em edição |
| ▲ / ▼ (PAGE) | navegação de páginas |
| ► / ◄ | navegação de parâmetros |
| SAVE | abre o fluxo de salvamento (escolha de slot U01–U99) |
| TAP | tempo do delay/drum; segurar abre afinador |
| EXIT | volta um nível de menu |
| FS-A / FS-B | troca de patch (modo PATCH) ou liga/desliga módulos (modo STOMP) |
| EXP pedal | expressão (volume/wah/controle de parâmetro); calibrável |

## Fluxo de edição (menu a menu)

1. **HOME** — nome do patch; girar o Knob troca de patch.
2. Pressione o Knob (ou PAGE) para entrar no patch → **página de cadeia** com 9 slots.
3. Slot a slot: ligar/desligar (ON/OFF), selecionar **modelo** (girando o Knob), entrar em **Edit** para parâmetros.
4. Parâmetros: ► / ◄ selecionam, Knob ajusta valor.
5. **SAVE** → escolher slot de usuário U01–U99 → confirmar (Salva tudo: cadeia, parâmetros, IRs, nome).
6. Renomear o patch durante o fluxo de salvamento.

## Ajustes globais (afetam todos os patches)

- **MASTER VOLUME**: nível geral de saída (físico no painel).
- **MASTER EQ** (página GLOBAL do menu): low/mid/high global — comece em 0/0/0.
- **OUTPUT / USB**: roteamento de saída; modo de gravação USB; o GP-100 funciona como interface de áudio (44.1 kHz, 16/24 bits, driver ASIO no Windows).
- **TUNER**: segurar TAP; referência padrão A4 = 440 Hz (ajustável ±); mudo automático ao afinar.
- **EXP pedal calibração**: SYSTEM → Pedal Calib.
- **DRUM**: 100 padrões (lista em `13-preset-list.md`); volume ajustável; não grava no patch.
- **LOOP**: gravação de 90 s, pré-efeitos.

## Modos dos footswitches

- **PATCH mode**: FS-A = patch anterior, FS-B = próximo patch.
- **STOMP mode**: FS-A e FS-B ligam/desligam módulos individuais (ideal para tocar ao vivo com um patch só).

## Página do EXP (expression pedal)

Funções típicas: Volume (volume geral do patch), Wah (controla os módulos V-Wah/A-Wah), ou parâmetro atribuído (ex.: Depth do delay). Configurada por patch.

## Regras de ouro para montagem de patch (resumo rápido)

1. Sempre: defina **AMP primeiro**, depois **CAB/IR**, depois DST, depois tempo/espacialização (DLY→RVB).
2. Sempre ligue o **NR** em patches com ganho alto.
3. Volume de saída final do patch = AMP Output/Master × EQ Level × MOD Level × DLY Mix × RVB Mix — mantenha a soma visível equilibrada; use MASTER VOLUME para o ajuste final global.
4. Um único grande "espacial" por patch (DLY **ou** RVB dominante) — os dois juntos só em ambientes/ambient.
5. Single coils (a Strat do projeto) são brilhantes e ruidosas com ganho alto: NR mais presente, Treble do AMP moderado.
