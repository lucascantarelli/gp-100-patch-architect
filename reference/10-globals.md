# GP-100 — Configurações Globais e Utilidades
> Páginas impressas 7–16 do manual. Configurações que afetam o som geral além dos módulos de efeito.

## Volume e saída

### MASTER VOLUME
- Knob físico no painel — controla o volume geral de saída da pedaleira (não é salvo por patch).
- Ao testar patches no projeto: fixe o MASTER VOLUME numa posição confortável (60–70%) e **não mude mais** — os volumes devem ser equilibrados dentro dos patches.

### OUTPUT (menu GLOBAL)
- Roteamento de saída: saída linha L/R, fone (PHONE), USB.
- **Modo de gravação USB** (para o projeto: saída conectada ao computador): o GP-100 vira interface de áudio 44,1 kHz / 16 ou 24 bits. No Windows, instalar o **driver ASIO** da Valeton para latência mínima.
- Cablagem do projeto: guitarra → INPUT; OUTPUT L/R → entrada de áudio do PC (ou USB direto); fones monitores na saída PHONE para avaliação.

## Pedal EXP (expressão)

- Integrado ao painel; também aceita pedal externo.
- Funções por patch (configuráveis): **Volume** (master do patch), **Wah** (controla V-Wah do PRE), ou parâmetro atribuído (ex.: Rate do MOD, Mix do DLY).
- **Calibração**: SYSTEM → Pedal Calib (calcular curso mínimo/máximo do pedal) — rode após atualização ou se o pedal "pula" valores.
- Dica do projeto: patches de lead podem mapear EXP = Volume para swells; patches funk psicodélico mapeiam EXP = Wah.

## Afinador

- Abrir: **segurar TAP**.
- Cromático; display mostra nota e desvio; **mudo automático** enquanto afinando.
- Referência A4 ajustável (padrão 440 Hz).
- Flat tunings: calibrar referência ou afinar de ouvido com o drum desligado.

## Drum Machine

- 100 padrões (Rock, Funk, Pop, Blues, World, Jazz, Metro) — lista completa em `13-preset-list.md`.
- Controles: padrão (No.), **tempo** (BPM, default 120 na maioria), **volume** do drum.
- Tap tempo: botão TAP define o BPM na hora.
- O drum **não é salvo no patch** — é utilidade de prática/estúdio.
- Para testar patches rítmicos (funk/metal): use o drum no BPM alvo e avalie a definição do riff.

## Looper (pré-efeitos)

- Gravação de até **90 segundos**.
- **Pré-efeitos**: o loop é gravado ANTES da cadeia — ao trocar de patch, o timbre do loop muda (perfeito para testar camadas: grave clean, toque com drive por cima).
- Controles: gravar/overdub/parar/play; apagar com segurar.
- Uso no projeto: gravar 4 compassos com o patch base e testar variações de timbre sobre o loop.

## Salvamento

- **SAVE** no painel → escolher slot **U01–U99** → renomear → confirmar.
- Salva: cadeia, modelo/parâmetros de cada módulo, Low/High Cut/Level do CAB, nome do patch.
- **Não salva**: MASTER VOLUME, drum, looper, calibração do EXP (são globais/temporários).

## Biblioteca de patches

- **99 slots de usuário (U01–U99)** + **99 de fábrica (F01–F99)**.
- Os de fábrica são organizados por estilo (lista completa em `13-preset-list.md`) — servem como ponto de partida, mas o projeto cria patches próprios nos slots U.
- Sugestão de organização dos slots U para o projeto: U01–U10 clean, U11–U30 blues/rock, U31–U50 hard/metal, U51–U70 experimental/ambient, U71–U90 estilo específico sob encomenda, U91–U99 utilidades.

## Firmware e editor

- Firmware atual: **V1.8** (atualizável via USB; o manual em PDF é da V1.8).
- **Editor PC/Mac (GP-100 Edits)**: edita todos os parâmetros via tela, gerencia presets e carrega **IRs de usuário** (arquivos .wav).
- No projeto, patches documentados em MD podem ser digitados no painel OU montados no editor — receita de digitação em cada `patch.md`.

## O que evitar (Evite)
- **MASTER VOLUME como compensação de patch**: se um patch está baixo, aumente o Level do EQ/Master do AMP dentro do patch — MASTER é global e afeta todos.
- **Drum alto durante teste de dinâmica**: o drum "encobre" a resposta do patch; teste também sem drum.
- **Salvar patch sem renomear**: você perde o histórico do projeto; sempre renomeie (ex.: "BL-ST-D01").
- **Trocar de patch com volume alto sem NR**: saltos de volume entre patches pegam de surpresa — equilibre por Level interno, não pelo MASTER.
- **Calibrar EXP com a guitarra plugada em volume alto**: falso sinal pode confundir a calibração; calibre com as cordas mudas.
