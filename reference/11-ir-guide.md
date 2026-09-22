# GP-100 — Guia de User IRs (Impulse Responses)
> Base: página impressa 26 do manual (CAB/IR) + prática da comunidade Valeton. A GP-100 tem **20 slots de IR de usuário** que aparecem no bloco CAB junto com os 40 gabinetes de fábrica.

## O que é uma IR
Uma **Impulse Response** é a "impressão digital" sonora de um gabinete + microfone (ou de uma sala, ou de um amp capturado). Ao tocar sua guitarra, o sinal é **convoluído** com a IR — o resultado é como se você estivesse ligado àquele gabinete naquela posição de mic.

## Especificações aceitas pela GP-100
- Formato: **.wav**
- Taxa: **44,1 kHz**
- Profundidade: **24 bits** (16 bits pode funcionar, mas 24 é o padrão)
- Canais: **mono** (estéreo precisa ser mesclado antes)
- Comprimento: **até 1024 samples** (~23 ms) — IRs de sala/acústica (500 ms+) não servem; só **cabinet IRs**.
- Carga: via **editor GP-100 Edits** (PC/Mac) conectado por USB; slots nomeáveis.

## Estratégia de pesquisa de IRs gratuitas (skill gp100-ir-research)

Sites confiáveis com IRs **gratuitas** (uso livre em patches):
- **OwnHammer** — pacotes de amostra gratuitos (impulse responses de cabs clássicos).
- **3 Sigma Audio** — free IRs mensais.
- **Redwirez** — mixIR free (Marshall 1960A com vários mics).
- **Celestion Pulse** — IRs oficiais de falantes (algumas gratuitas).
- **_freestompboxes/foros de comunidade_ — packs "IR pack for Valeton" feitos por usuários GP-100/GP-200.
- **GitHub / archives "open IR"** — coleções livres (ex.: "OpenIR", "SinnVanell IRs").

Critérios de escolha (a skill avalia):
1. **Casamento com o AMP**: IR de V30 para Mesa/ENGL; Greenback para Marshall; alnico para VOX; Jensen/C12N para Fender.
2. **Mic**: SM57 (ataque) × MD421 (corpo) × Ribbon R121 (suavidade) — para fone/strat single coil, comece por 57 + V30.
3. **Comprimento**: 200–1024 samples (a GP-100 trunca acima de 1024).
4. **Licença**: permitir uso pessoal; evitar IRs "ripped" de outras pedaleiras.

## Ajustes de IR dentro do patch (skill gp100-ir-fit)
Cada slot IR tem: **Low Cut (0~20) Hz**, **High Cut (1000~20000) Hz**, **Level (-12~+12) dB**.

Receita de encaixe:
1. Carregar IR → tocar → avaliar: "fizz" (agudo agulha)? "fart/lama" (grave estufado)? baixo volume?
2. **Fizz** → High Cut 6500–8000.
3. **Lama** → Low Cut 6–10.
4. **Volume** → Level ±3 (evitar +12; reequilibrar no EQ do patch).
5. **Duas rodadas no máximo**: 1ª ajusta cortes; 2ª ajusta Level/brilho fino. Se após 2 rodadas não casa, troque a IR.

## Onde as IRs moram
- Packs baixados ficam em `impulse_responses/<Pack>/` — **fora do git** (licença de terceiro) e
  **nunca** dentro de `patches/`, que é saída de script. Depois de baixar: `python tools/ir_library.py`.
- Não renomeie os arquivos do pack: o índice é gerado a partir do que existe na pasta e o
  `patch.md` recomenda o arquivo pelo caminho real.
- O que se anota é na seção 📡 da doc (campo `doc` do defs): o **slot de User IR (1–20)**, os cortes
  de Low/High Cut e o Level aplicados. O `.prst` sai sempre com CAB de fábrica.

## O que evitar (Evite)
- **IR de sala/reverb (longa)**: a GP-100 só comporta 1024 samples; salas não carregam direito (truncada = som de "clic").
- **IR estéreo**: mesclar para mono antes de carregar.
- **Stack de IR + CAB de fábrica**: use **ou** o CAB de fábrica **ou** o user IR — não empilhe (não há 2 blocos CAB).
- **IR de "amp capturado" (NAM/Kemper)** com AMP ON: duplique a saturação (capture já tem o amp). Se usar captura, coloque-a no lugar do **AMP+CAB**: DST OFF, usar IR no CAB com AMP neutro/limpo ou AMP OFF conforme manual — testar sempre.
- **Level +12 na IR para "volumizar"**: distorce o conversor; ajuste volume no EQ/AMP.
- **Confiar só no nome do arquivo**: IRs renomeadas enganam; ouça antes de registrar no projeto.
- **IR de 16 bits renomeada para .wav 24**: checar formato real no editor antes de carregar (carregamento falha silenciosamente às vezes).
