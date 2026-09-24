"""Renderização do `patch.md` — documentação prática-primeiro do patch (issue #30).

Migração de `tools/build_song_patches.py`: as funções de template saem do script
e viram biblioteca **pura** — recebem `spec`, `song`, `patch`, o índice de IRs e
os dados dos álbuns, e devolvem texto. Nenhuma lê disco, nenhuma imprime.

A separação existe para a UI futura: a mesma função que gera o Markdown do
repositório passa a poder gerar a página do site (#43) e a prévia da UI sem
herdar `print` nem caminho de arquivo.

Ordem fixa das seções (o prático ANTES do técnico): cabeçalho com badges →
🎸 1. Sua guitarra agora → 🔧 2. Ajustes finos → 📡 3. Impulse Response
(fábrica → banco local → internet → fallback) → 🔊 4. Modos de atuação →
🎯 5. Objetivo do som → 📚 6. Referência real → 🎛️ 7. Cadeia e parâmetros →
💾 8. Carregar na pedaleira → 🚫 9. Evite.

Markdown puro (sem HTML cru — o viewer do usuário não renderiza `<div>`/`<br>`).
"""

from __future__ import annotations

from typing import Any

from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.params import PARAM_NAMES
from gp100_architect.infrastructure.ir_catalog import melhor_mix

__all__ = ['BASE_MAP', 'CIRCLE', 'DOT', 'build_doc', 'ir_mixes']

DOT, CIRCLE = '**🔴**', '~~⚪~~'

# base real de cada modelo (mapeamento rig real → GP-100, exibido na doc)
BASE_MAP = {
    (
        'PRE',
        'Boost',
    ): 'Boost transparente na frente do amp (papel do "volume extra" do rig real) → `Boost`',
    ('PRE', 'AC Sim'): 'Violão real da gravação → `AC Sim` + CAB `D`',
    ('PRE', 'COMP4'): 'Compressor transparente nivelando a dinâmica do slide → `COMP4`',
    ('DST', 'Blues OD'): 'Drive na frente do amp compensando o humbucker da gravação → `Blues OD`',
    ('DST', 'Green OD'): 'Overdrive verde empurrando o amp (crunch do Casino) → `Green OD`',
    ('DST', 'La Charger'): 'Clipping áspero de mesa (RAT-style) → `La Charger`',
    ('DST', 'Red Haze'): 'Fuzz Big Muff "Civil War" do rig de 1994 → `Red Haze`',
    ('DST', 'Tube Clipper'): 'Tube Driver de baixo ganho (boost quente) → `Tube Clipper`',
    ('DST', 'Super OD'): 'Overdrive de médio afiado (o solo "cirúrgico") → `Super OD`',
    ('DST', 'Yellow OD'): 'Overdrive amarelo empurrando o amp (o corte do groove) → `Yellow OD`',
    ('AMP', 'L-Star CL'): 'Mesa/Boogie® Lone Star™ — o "gordo e liso" do Santana → `L-Star CL`',
    ('AMP', 'Solo100 LD'): 'Soldano® SLO-100 (lead denso e cantável) → `Solo100 LD`',
    ('CAB', 'L-Star 2x12'): 'Combo vintage 1x12 do Lone Star → `L-Star 2x12`',
    ('CAB', 'Mess-D 4x12'): 'Gabinete Mesa/Boogie® Rectifier 4x12 → `Mess-D 4x12`',
    ('AMP', 'Dark Twin'): "Fender® '65 Twin Reverb → `Dark Twin`",
    ('AMP', 'Foxy 30TB'): 'VOX® AC30 Top Boost → `Foxy 30TB`',
    ('AMP', 'Bellman 59N'): "Fender® '59 Bassman → `Bellman 59N`",
    ('AMP', 'UK 45'): 'Marshall® JTM45 (backline da era de Zappa) → `UK 45`',
    ('AMP', 'Flagman'): 'Hiwatt® DR103 da turnê de 1994 (clean potente com headroom) → `Flagman`',
    ('AMP', 'Knights CL'): 'Hiwatt® DR103 + Alembic F-2B (limpo, aberto, dinâmico) → `Knights CL`',
    ('AMP', 'UK 50JP'): 'Marshall® JMP50 (o 4x12 Marshall da pilha de 1994) → `UK 50JP`',
    ('CAB', 'DarkTW 2x12'): 'Falante JBL D120F do Twin → `DarkTW 2x12`',
    ('CAB', 'Foxy 1x12'): 'Gabinete do AC30 → `Foxy 1x12`',
    ('CAB', 'TWD 2x12'): 'Gabinete do Bassman → `TWD 2x12`',
    ('CAB', 'UK-GN 2x12'): 'Gabinete Marshall® com Greenbacks → `UK-GN 2x12`',
    (
        'CAB',
        'UK-LD 4x12',
    ): 'Pilha 4x12 Marshall da turnê (Greenbacks; papel do WEM/Fane) → `UK-LD 4x12`',
    (
        'CAB',
        'J-120 2x12',
    ): 'Cabine neutra de JBL (faz o papel da "mesa" da gravação) → `J-120 2x12`',
    ('CAB', 'D'): 'Corpo dreadnought → `D`',
    ('MOD', 'A-Chorus'): 'Leslie/rotary lento da gravação → `A-Chorus` (velocidade baixa)',
    ('MOD', 'Vibe'): 'Leslie 147RV da gravação → `Vibe` (velocidade baixa)',
    ('DLY', 'Slapbk'): 'Slapback curto de estúdio → `Slapbk`',
    ('DLY', 'Sweet'): 'Delay com 1 repetição na duração da nota (eco do solo) → `Sweet`',
    ('DLY', 'T-Echo'): 'O efeito Binson Echorec das jams espaciais → `T-Echo`',
    ('RVB', 'Spring'): 'Mola do Twin/Fender → `Spring`',
    ('RVB', 'Plate'): 'Plate de estúdio ("splash" da faixa) → `Plate`',
    ('RVB', 'Room'): 'Sala curta e seca — corpo curto que sustenta sem lambear → `Room`',
    ('RVB', 'Hall'): 'Hall etéreo das seções lentas → `Hall`',
    ('NR', 'Gate 1'): 'Controle de hum (single coils + ganho) → `Gate 1`',
    ('EQ', 'EQ 1'): 'Esculpir o som para fone/PC → `EQ 1`',
}

PROTOCOLO_UNIVERSAL = [
    'Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.',
    'Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.',
    'Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).',
    'Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.',
]


def ir_mixes(cab_lib: str, ir_index: dict[str, list[str]]) -> str | None:
    """Arquivo Mix recomendado da captura local (Medium > Bright > Dark > primeiro)."""
    return melhor_mix(ir_index.get(cab_lib, []))


def fmt_val(v: Any) -> str:
    """Converte o valor do spec em string para exibição/tabelas."""
    return str(v)


def disp(label: str, v: Any) -> str:
    """Exibição amigável de switches (Bright, Char, Mode, Sync) e unidades (Time)."""
    if label == 'Bright' and str(v) in ('0', '1'):
        return 'Off' if str(v) == '0' else 'On'
    if label == 'Char' and str(v) in ('0', '1'):
        return 'Cool' if str(v) == '0' else 'Hot'
    if label == 'Mode' and str(v) in ('0', '1', '2', '3'):
        return ('STD', 'Jumbo', 'ENH', 'Piezo')[int(str(v))]
    if label in ('Sync', 'Trail') and str(v) in ('0', '1'):
        return 'Off' if str(v) == '0' else 'On'
    if label in ('Time', 'Pre Delay'):  # faixas do manual: 20ms-4000ms / 0ms-100ms
        try:
            return f'{int(float(str(v)))} ms'
        except ValueError:
            return fmt_val(v)
    return fmt_val(v)


def build_ir_section(
    spec: dict[str, Any], ir_nota: str, *, ir_local: dict[str, Any], ir_index: dict[str, list[str]]
) -> str:
    """Seção exclusiva de IR da documentação (seção 3 do patch.md).

    Três degraus, na ordem da política: CAB de fábrica (o `.prst` já funciona)
    → banco local (`impulse_responses/`, arquivo exato + slot de User IR) →
    internet (catálogo curado) → fallback garantido.
    """
    cab = spec['modules'].get('CAB', {})
    cab_nome = cab.get('name') or '(sem CAB)'
    linhas = [
        '## 📡 3. Impulse Response (CAB) — o gabinete do patch',
        '',
        f'**O que está no arquivo `.prst` agora**: CAB de fábrica **`{cab_nome}`** — o modelo GP-100 que reproduz '
        'o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.',
        '',
        '> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).',
        '>',
        '> Uma IR boa **substitui** o CAB — não empilha com ele.',
        '',
    ]
    par: dict[str, Any] | None = ir_local.get(cab_nome)
    cab_lib = str(par['captura']) if par else ''
    slot = str(par['slot']) if par else ''
    tem_local = bool(cab_lib and ir_index.get(cab_lib))
    if tem_local:
        arquivo = ir_mixes(cab_lib, ir_index)
        linhas += [
            '### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta',
            '',
            f'O banco local tem a captura **{cab_lib}** — casamento direto com o gabinete real deste patch:',
            '',
            f'1. No **GP-100 Edits** → IR Manager, carregue no **{slot}** o arquivo:',
            f'   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/{cab_lib}/{arquivo}`',
            f'2. No patch: bloco CAB → troque `{cab_nome}` por **User IR {slot.split()[-1]}**.',
            '3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), **Level** comece em 0 e compare com o bypass.',
            '   Alternativas do mesmo gabinete no banco: '
            + ', '.join(f'`{f}`' for f in ir_index.get(cab_lib, []) if f != arquivo)
            + '.',
            '',
        ]
    else:
        linhas += [
            '### 🔍 Não há captura melhor no nosso banco para este alvo',
            '',
            f'O CAB de fábrica `{cab_nome}` **já é a representação correta** deste alvo — nenhum gabinete do banco '
            'casa melhor (o catálogo local é consultado em `reference/16-ir-library.md`).',
            '',
        ]
    linhas += [
        '### 🌍 Procurar na internet (só se quiser experimentar algo diferente)',
        '',
        'O agente **pesquisa IRs gratuitas automaticamente** quando o banco local não cobre o alvo — catálogo '
        'curado em `reference/17-free-ir-packs.md` (Origin Effects, OwnHammer free, Redwirez mixIR, Celestion Pulse '
        'free, ML Sound Lab, Bogren Digital, packs de baixo etc.). Ao baixar um pack novo:',
        '',
        '```',
        'impulse_responses/<Nome do Pack>/   ← extraia aqui',
        'python tools/ir_library.py          ← reindexa e valida os WAVs',
        '```',
        '',
        '**Formato obrigatório**: `.wav` **44,1 kHz · 24 bits · mono** · máx **1024 samples** (cabinet IR; '
        'não use room/reverb IR). Pack com pastas 48/96 kHz → use sempre a pasta **44.1 kHz**. '
        'Confira sempre a **licença** (todas do catálogo 17 permitem uso pessoal).',
        '',
        '### ✅ Fallback garantido',
        '',
        'Se nenhuma IR entregar o que você quer, **mantenha o CAB de fábrica** — este patch foi afinado com ele.',
        '',
    ]
    if ir_nota:
        linhas += [f'**Nota específica deste patch**: {ir_nota}', '']
    return '\n'.join(linhas)


def detail_tables(spec: dict[str, Any]) -> str:
    """Gera as tabelas "Parâmetro | Valor" por módulo ON (seções técnicas do patch.md).

    Usa PARAM_NAMES para rotular cada params_i; slots sem nome oficial viram
    `pN` e, se houver algum, a tabela ganha uma nota de rodapé dizendo isso —
    nunca um nome inventado. Switches (Bright/Char/Mode) saem por extenso via
    disp(). Módulos OFF ou ausentes são ignorados.
    """
    out = []
    tem_sem_nome = False
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or not m.get('on'):
            continue
        name = m['name']
        out.append(f'### {mod} — {name}\n')
        out.append('| Parâmetro | Valor |')
        out.append('|---|---|')
        names = PARAM_NAMES.get((mod, name), [])
        params = m.get('params', {})
        if not params:
            out.append('| (template de fábrica) | — |')
        else:
            for k in sorted(params, key=int):
                idx = int(k)
                label = names[idx] if idx < len(names) else f'p{idx}'
                if label.startswith('p') and label[1:].isdigit():
                    tem_sem_nome = True
                out.append(f'| {label} | {disp(label, params[k])} |')
        out.append('')
    if tem_sem_nome:
        out.append(
            '> ℹ️ **`pN`** = slot de parâmetro deste modelo **sem nome oficial documentado** '
            '(o manual V1.8 só cobre os modelos antigos) — ajuste por orelha, comparando '
            'com o bypass; os demais nomes seguem o manual da GP-100.'
        )
        out.append('')
    return '\n'.join(out)


def typing_recipe(spec: dict[str, Any], doc: dict[str, Any] | None = None) -> str:
    """Receita de digitação no painel: módulos ON na ordem da cadeia.

    Ao final, lista os SOBRESSALENTES (módulos OFF citados nos momentos da
    música) com seus parâmetros — assim quem ligar o módulo na hora sabe o
    que ajustar. Módulos OFF sem params usam o template de fábrica.
    """
    parts = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or not m.get('on'):
            continue
        names = PARAM_NAMES.get((mod, m['name']), [])
        params = m.get('params', {})
        if mod == 'RVB':
            # valores do .prst estão em escala interna; no painel, ajuste fino é por orelha
            parts.append(f'**{mod}** `{m["name"]}` (ajuste fino no painel — seção 3 📡)')
            continue
        kv = ' / '.join(
            f'{names[int(k)] if int(k) < len(names) else "p" + k} {disp(names[int(k)] if int(k) < len(names) else "", v)}'
            for k, v in sorted(params.items(), key=lambda x: int(x[0]))
        )
        parts.append(f'**{mod}** `{m["name"]}`' + (f' ({kv})' if kv else ''))
    momentos_mods = {m for mo in (doc or {}).get('momentos', []) for (m, _e) in mo['mods']}
    extras = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or m.get('on') or mod not in momentos_mods:
            continue
        names = PARAM_NAMES.get((mod, m['name']), [])
        params = m.get('params', {})
        if params:
            kv = ' / '.join(
                f'{names[int(k)] if int(k) < len(names) else "p" + k} {disp(names[int(k)] if int(k) < len(names) else "", v)}'
                for k, v in sorted(params.items(), key=lambda x: int(x[0]))
            )
            extras.append(f'SOBRESSALENTE **{mod}** `{m["name"]}` ({kv})')
        else:
            extras.append(
                f'SOBRESSALENTE **{mod}** `{m["name"]}` (template de fábrica — ajuste por orelha ao ligar)'
            )
    if extras:
        parts.append(' · '.join(extras))
    return ' → '.join(parts)


def ajustes_table(ajustes: list[str]) -> str:
    """Transforma as linhas "sintoma → ação" em tabela Markdown de ajustes finos."""
    rows = []
    for a in ajustes:
        if '→' in a:
            sintoma, acao = a.split('→', 1)
            rows.append(f'| {sintoma.strip()} | {acao.strip()} |')
        else:
            rows.append(f'| — | {a.strip()} |')
    return '\n'.join(rows)


def build_momentos_section(spec: dict[str, Any], doc: dict[str, Any]) -> str:
    """Seção "Modos de atuação": liga/desliga módulos em tempo real.

    Mostra o estado de fábrica dos 9 módulos do spec, os momentos definidos
    para a música (doc['momentos'], validados pelo add_momentos.py — só
    módulos presentes, só pedidos inversos ao estado atual) e as instruções
    de toggle ao vivo (painel slot a slot e modo STOMP com FS-A/B).
    """
    momentos = doc.get('momentos', [])
    linhas = [
        '## 🎛️ 4. Modos de atuação — ligue e desligue efeitos no momento',
        '',
        'A GP-100 liga/desliga **qualquer módulo em tempo real**: no **painel**, slot a slot (gire o Knob até o módulo → pressione para alternar **ON/OFF**), ou pelos **footswitches FS-A/FS-B no modo STOMP**. **Desligar um módulo não apaga seus parâmetros** — religou, o som do patch-base volta intacto.',
        '',
        '> 💡 Pense neste patch como uma **pedalboard de 9 espaços**: os módulos desligados são "pedais sobressalentes" prontos para entrarem na música.',
        '',
        '### Estado de fábrica do patch (o que já vem ligado)',
        '',
        '| Módulo | Estado no `.prst` | Modelo |',
        '|---|---|---|',
    ]
    for mod in CHAIN:
        m = spec['modules'].get(mod, {})
        estado = '**🔴 ON**' if m.get('on') else '⚪ OFF'
        nome = f'`{m["name"]}`' if m.get('name') else '—'
        linhas.append(f'| {mod} | {estado} | {nome} |')
    linhas.append('')
    if momentos:
        linhas += [
            '### 🎭 Momentos desta música (validados para este patch)',
            '',
            'Mude SÓ os módulos indicados — o resto permanece como na tabela acima:',
            '',
        ]
        for i, mo in enumerate(momentos, 1):
            mods_txt = ' + '.join(f'**{m} → {e}**' for m, e in mo['mods'])
            linhas.append(f'{i}. **{mo["nome"]}** — {mods_txt}')
            linhas.append(f'   *Quando*: {mo["quando"]}')
            if mo.get('dica'):
                linhas.append(f'   *Dica*: {mo["dica"]}')
            linhas.append('')
    else:
        linhas += [
            '### 🎭 Momentos desta música',
            '',
            'Este patch foi afinado para **um** papel — use os sobressalentes da tabela acima para variar na hora '
            '(ex.: desligar o DLY para uma seção seca). Momentos dedicados estão nos patches irmãos da mesma '
            'música (veja o mapa do álbum).',
            '',
        ]
    stomps = doc.get('stomps') or []
    if stomps:
        linhas += [
            '### 🦶 FS-A / FS-B deste patch (modo STOMP)',
            '',
            'Atribuição pronta dos footswitches — ligue **SYSTEM → Mode → Stomp** e o patch vira uma pedalboard:',
            '',
            '| FS | O que faz | Quando pisar |',
            '|---|---|---|',
        ]
        for st in stomps:
            fs = st.get('fs', '?')
            mods_txt = ' + '.join(f'**{m} → {e}**' for m, e in st.get('mods', []))
            linhas.append(f'| **FS-{fs}** | {mods_txt} | {st.get("quando", "—")} |')
            if st.get('dica'):
                linhas.append('| — | *Dica: ' + st['dica'] + '* | — |')
        linhas.append('')
    exp1 = spec.get('exp1')
    if isinstance(exp1, dict) and exp1.get('módulo'):
        mn, mx = exp1.get('min', 0), exp1.get('max', 99)
        linhas += [
            '### 🎚️ Pedal de expressão (EXP1)',
            '',
            f'O pedal de expressão **já vem amarrado no `.prst`** ao parâmetro **{exp1["param"]} '
            f'do {exp1["módulo"]}** (curso {mn}→{mx}, calcanhar→bico):',
            '',
            '| Controle | Valor |',
            '|---|---|',
            f'| Módulo controlado | **{exp1["módulo"]}** |',
            f'| Parâmetro | **{exp1["param"]}** |',
            f'| Curso | {mn} (calcanhar) → {mx} (bico) |',
            '',
            'Conecte um pedal de expressão na entrada **EXP1/CTRL** da GP-100 e mexa — sem atribuir nada no painel. ',
            'Para mudar a amarração, edite o spec no defs (`exp1`) e regenere.',
            '',
        ]
    linhas += [
        '### 🦶 Ligar/desligar ao vivo (modo STOMP)',
        '',
        '1. **SYSTEM → Mode → Stomp**: os footswitches A/B param de trocar de patch e passam a alternar módulos.',
        '2. Atribua cada footswitch ao módulo que você mais liga/desliga nesta música (ex.: FS-A = DLY, FS-B = DST).',
        '3. Para voltar a navegar entre patches, retorne **SYSTEM → Mode → Patch**.',
        '',
        '> ⚠️ **Cuidado**: os módulos **AMP e CAB** sustentam o volume e o corpo do patch — desligá-los muda tudo. '
        'Os momentos deste patch nunca mexem neles.',
        '',
    ]
    return '\n'.join(linhas)


def build_doc(
    song: dict[str, Any],
    patch: dict[str, Any],
    spec: dict[str, Any],
    slot: str,
    *,
    albums: dict[str, Any],
    ir_local: dict[str, Any],
    ir_index: dict[str, list[str]],
) -> str:
    """Renderiza o patch.md completo de um patch (documento prático-primeiro).

    Dados que antes vinham de globais do script (`ALBUMS`, `IR_LOCAL_POR_CAB`,
    `IR_LIB`) entram por parâmetro: a função é pura e testável sem disco.
    """
    alb = albums[song['idAlbum']]
    banda, album, ano = alb['banda'], alb['album'], alb['ano']
    g = patch['doc']['guitarra']
    doc = patch['doc']

    chain_row = '| ' + ' | '.join(CHAIN) + ' |'
    chain_sep = '|' + '---|' * len(CHAIN)
    cells = []
    for mod in CHAIN:
        m = spec['modules'].get(mod, {})
        cells.append(f'{DOT} {mod} · {m["name"]}' if m.get('on') else f'{CIRCLE} {mod}')
    chain_cells = '| ' + ' | '.join(cells) + ' |'

    compact = []
    for mod in CHAIN:
        m = spec['modules'].get(mod, {})
        if m.get('on'):
            names = PARAM_NAMES.get((mod, m['name']), [])
            params = m.get('params', {})
            vals = ' · '.join(
                f'{names[int(k)] if int(k) < len(names) else "p" + k}: {disp(names[int(k)] if int(k) < len(names) else "", v)}'
                for k, v in sorted(params.items(), key=lambda x: int(x[0]))
            )
            compact.append(f'| {mod} | {m["name"]} | {vals or "(template)"} |')

    refs = '\n'.join(f'| {r["role"]} | {r["conf"]} | {r["src"]} |' for r in song['referencias'])
    mapping = '\n'.join(
        f'- {BASE_MAP[(mod, spec["modules"][mod]["name"])]}'
        for mod in CHAIN
        if spec['modules'].get(mod, {}).get('on')
        and (mod, spec['modules'][mod]['name']) in BASE_MAP
    )
    tecnicas = '\n'.join(f'{i + 1}. {t}' for i, t in enumerate(g['tecnicas']))
    escutar = '\n'.join(f'- ☑️ {e}' for e in doc['teste']['escutar'])
    ajustes = ajustes_table(doc['ajustes'])
    protocolo = '\n'.join(f'- {p}' for p in PROTOCOLO_UNIVERSAL)
    evite = '\n'.join(f'- ⛔ {e}' for e in doc['evite'])
    ir_section = build_ir_section(spec, doc.get('irNota', ''), ir_local=ir_local, ir_index=ir_index)
    momentos_section = build_momentos_section(spec, doc)

    return f"""# {patch['emoji']} {patch['nome']}
### {song['song']} — {patch['camada']}
##### {banda} · {album} ({ano})

![Genero](https://img.shields.io/badge/Genero-{spec['type']}-e02d2d?style=flat-square) ![Camada](https://img.shields.io/badge/Camada-{patch['camada'].split()[0]}-f3a637?style=flat-square) ![Captador](https://img.shields.io/badge/Captador-{g['seletorCurto'].replace(' ', '%20')}-2ea44f?style=flat-square) ![Contexto](https://img.shields.io/badge/Contexto-fone%20%2B%20PC-6f42c1?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square)

> 💡 **{patch['timbre']}**

---

## 🎸 1. Sua guitarra agora — leia isto primeiro

> **⚡ Ajuste a Strat antes de tocar: {g['receita']}**

| Controle na guitarra | Ajuste |
|---|---|
| **Seletor de captadores** | {g['seletor']} |
| **Volume** | {g['volume']} |
| **Tone** | {g['tone']} |

**🎯 Técnica que completa o som** (a dinâmica da mão vale tanto quanto os parâmetros):

{tecnicas}

> 🚀 **Comece por aqui (3 passos)**:
> 1. Ajuste a guitarra conforme a tabela acima.
> 2. Carregue o patch no slot **{slot}** (seção 8).
> 3. Toque *{doc['teste']['riff']}* e confira o checklist da seção 5.

---

## 🔧 2. Ajustes finos

Só mexa na pedaleira **depois** de acertar a guitarra — ela resolve 80% do som.

### Este patch, especificamente

| Se você ouvir… | Faça isto |
|---|---|
{ajustes}

### Protocolo universal (vale para todos os patches)

{protocolo}

---

{ir_section}

---

{momentos_section}

---

## 🔊 5. Objetivo do som

**O que este patch é**: {patch['timbre']}.

{song['resumo']}

**Teste recomendado**: {doc['teste']['riff']} · **Drum**: {doc['teste']['drum']}

**Como saber que está certo**:

{escutar}

---

## 📚 6. Referência real (dossiê do rig original)

| Equipamento / prática real | Confiança | Fonte |
|---|---|---|
{refs}

*Fontes completas e contexto: ver dossiê do álbum no mapa. O mapeamento equipamento-real → modelo GP-100 está na seção 7.*

---

## 🎛️ 7. Cadeia e parâmetros (dados técnicos)

### Cadeia de sinal

{chain_row}
{chain_sep}
{chain_cells}

_Legenda: **🔴** ligado · ⚪ desligado — a ordem é o caminho do sinal._

### Resumo rápido

| Módulo | Modelo | Valores |
|---|---|---|
{chr(10).join(compact)}

### Mapeamento rig real → GP-100

{mapping}

### Parâmetros módulo a módulo

{detail_tables(spec)}

### Globais da sessão

| Item | Valor |
|---|---|
| MASTER VOLUME | 65% fixo — não compensar nível por aqui |
| Afinador | A ≈ 442 Hz (discos da época correm acima de A440) |
| USB/Saída | 44,1 kHz · driver ASIO no Windows |
| Fones | saída PHONE (monitores) |

> *RVB (*): valores na escala interna do firmware — o `.prst` carrega o template de fábrica; ajuste fino de reverb é feito no painel conforme o descrito na seção 3.*

---

## 💾 8. Carregar na pedaleira

**Nome no painel**: `{patch['nome']}` · **Slot sugerido**: **{slot}**

1. **GP-100 Edits (recomendado)**: conecte a GP-100 por USB → importe `<NOME>.prst` desta pasta → salve no slot **{slot}**.
2. **Digitar no painel** (receita na ordem dos menus):

```
{typing_recipe(spec, doc)}
```

3. **SAVE** no slot → renomeie para `{patch['nome']}`.

---

## 🚫 9. Evite com este patch

{evite}

---

| Data | Versão | Mudança | Motivo |
|---|---|---|---|
| 2026-09-19 | D3 | patch exclusivo da música (MUSICA-CAMADA) | reorganização da biblioteca |
| 2026-09-19 | D4 | doc reestruturada: guitarra e ajustes finos primeiro | feedback do usuário |
| 2026-09-20 | D5 | seção exclusiva de IR (fábrica → banco local → internet → fallback) | política de IR documentada |
| 2026-09-20 | D6 | seção "Modos de atuação" (ligar/desligar módulos; momentos por música; modo STOMP) | uso real do toggle da GP-100 |

---

[`🗺️ Mapa do álbum`](../MAPA-DO-ALBUM.md) · [`🎸 Biblioteca`](../../../README.md)
"""
