"""
build_song_patches.py — Constrói todos os patches por MÚSICA a partir de tools/patches-defs.json.

Para cada patch:
  1. escreve <pasta da música>/<NOME>/spec.json
  2. escreve <...>/patch.md  (documentação prática-primeiro, Markdown puro)
  3. gera <...>/<NOME>.prst  via tools/generate_prst.py (formato single fw 2.1)
  4. valida o XML resultante

Estrutura da doc (o prático vem ANTES do técnico):
  1. Sua guitarra agora   — seletor/volume/tone + técnica (o usuário toca certo já no 1º minuto)
  2. Ajustes finos        — tabela sintoma → ajuste + protocolo universal
  3. Impulse Response     — SEÇÃO EXCLUSIVA: fábrica → biblioteca local → internet → fallback fábrica
  4. Objetivo do som      — o que ouvir + teste
  5. Referência real      — dossiê com fontes
  6. Cadeia e parâmetros  — dados técnicos completos
  7. Carregar na pedaleira
  8. Evite

Uso: python tools/build_song_patches.py
"""
import copy
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS = json.loads((ROOT / 'tools' / 'patches-defs.json').read_text(encoding='utf-8'))

# ---- FONTE ÚNICA: tudo abaixo é DERIVADO de tools/patches-defs.json --------
# (antes estas tabelas eram literais aqui E em gen_indexes.py e divergiram —
#  o mapa do álbum passou a recomendar "fábrica" onde o patch.md mandava
#  carregar uma IR do banco local. Não reintroduza literais de música/álbum.)
ALBUMS = DEFS['albums']                                                  # {'AR': {banda, album, ano, display, pasta, rig}}
ALBUM_DIR = {k: ROOT / 'patches' / v['pasta'] for k, v in ALBUMS.items()}
SONG_FOLDER = {s['id']: s.get('pasta') or s['song'] for s in DEFS['songs']}
# captura local recomendada por CAB de fábrica: {'CAB': (captura, 'User IR n')}
IR_LOCAL_POR_CAB = {cab: (v['captura'], v['slot']) for cab, v in DEFS['ir_local'].items()}

# Nome OFICIAL de cada params_i, por (módulo, modelo).
# Só entram nomes com origem citável: reference/03-amp.md (Flagman, Knights CL),
# convenção do módulo (todo CAB = Level/High Cut; ver os 6 CABs da tabela) e
# reference/01..09 (manual V1.8). Slot sem nome oficial fica de fora da lista e
# a doc o imprime como `pN` + nota de rodapé (nunca um nome inventado).
PARAM_NAMES = {
    ('PRE', 'COMP'): ['Sens', 'Attack', 'Sustain', 'Level'],
    ('PRE', 'COMP4'): ['Thresh', 'Attack', 'Tone', 'Level'],
    ('PRE', 'Boost'): ['Ganho', 'Boost'],
    ('PRE', 'AC Sim'): ['Body', 'Top', 'Vol', 'Mode'],
    ('DST', 'Blues OD'): ['Gain', 'Tone', 'Level'],
    ('DST', 'Green OD'): ['Gain', 'Tone', 'Level'],
    ('DST', 'La Charger'): ['Gain', 'Tone', 'Volume'],
    ('DST', 'Super OD'): ['Drive', 'Tone', 'Level'],
    ('AMP', 'Dark Twin'): ['Vol', 'Output', 'Bass', 'Middle', 'Treble', 'Bright'],
    ('AMP', 'Foxy 30TB'): ['Vol', 'Cut', 'Master', 'Bass', 'Treble', 'Char'],
    ('AMP', 'Flagman'): ['Gain', 'PRSE', 'Master', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'Knights CL'): ['Gain', 'Vol', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'Bellman 59N'): ['Vol', 'PRSE', 'Output', 'Bass', 'Middle', 'Treble'],
    ('AMP', 'UK 45'): ['Vol', 'PRSE', 'Output', 'Bass', 'Middle', 'Treble'],
    ('NR', 'Gate 1'): ['Thr'],
    ('NR', 'Gate 2'): ['Thr', 'Release'],
    ('CAB', 'DarkTW 2x12'): ['Level', 'High Cut'],
    ('CAB', 'Foxy 1x12'): ['Level', 'High Cut'],
    ('CAB', 'TWD 2x12'): ['Level', 'High Cut'],
    ('CAB', 'J-120 2x12'): ['Level', 'High Cut'],
    ('CAB', 'UK-GN 2x12'): ['Level', 'High Cut'],
    ('CAB', 'UK-LD 4x12'): ['Level', 'High Cut'],
    ('CAB', 'D'): ['Level', 'High Cut'],
    ('EQ', 'EQ 1'): ['Low', 'Mid', 'High', 'Mid Freq', 'Presença', 'Level'],
    ('MOD', 'A-Chorus'): ['Rate', 'Depth', 'Mix', 'Level'],
    ('MOD', 'Vibe'): ['Intensidade', 'Velocidade', 'p2', 'Mix'],
    ('DLY', 'Sweet'): ['Fdbk', 'Delay ms', 'High Cut'],
    ('DLY', 'Slapbk'): ['Fdbk', 'Delay ms', 'High Cut'],
    ('RVB', 'Spring'): ['Decay*', 'Pre-D*', 'Damp*', 'Mix*'],
    ('RVB', 'Room'): ['Decay*', 'Pre-D*', 'Damp*', 'Mix*'],
    ('RVB', 'Plate'): ['Decay*', 'Pre-D*', 'Damp*', 'Mix*'],
    ('RVB', 'Hall'): ['Decay*', 'Pre-D*', 'Damp*', 'Mix*'],
}
CHAIN = ['PRE', 'DST', 'AMP', 'NR', 'CAB', 'EQ', 'MOD', 'DLY', 'RVB']
DOT, CIRCLE = '**🔴**', '~~⚪~~'

# base real de cada modelo (mapeamento rig real → GP-100, exibido na doc)
BASE_MAP = {
    ('PRE', 'Boost'): 'Boost transparente na frente do amp (papel do "volume extra" do rig real) → `Boost`',
    ('PRE', 'AC Sim'): 'Violão real da gravação → `AC Sim` + CAB `D`',
    ('PRE', 'COMP4'): 'Compressor transparente nivelando a dinâmica do slide → `COMP4`',
    ('DST', 'Blues OD'): 'Drive na frente do amp compensando o humbucker da gravação → `Blues OD`',
    ('DST', 'Green OD'): 'Overdrive verde empurrando o amp (crunch do Casino) → `Green OD`',
    ('DST', 'La Charger'): 'Clipping áspero de mesa (RAT-style) → `La Charger`',
    ('DST', 'Red Haze'): 'Fuzz Big Muff "Civil War" do rig de 1994 → `Red Haze`',
    ('DST', 'Tube Clipper'): 'Tube Driver de baixo ganho (boost quente) → `Tube Clipper`',
    ('DST', 'Super OD'): 'Overdrive de médio afiado (o solo "cirúrgico") → `Super OD`',
    ('AMP', 'Dark Twin'): 'Fender® \'65 Twin Reverb → `Dark Twin`',
    ('AMP', 'Foxy 30TB'): 'VOX® AC30 Top Boost → `Foxy 30TB`',
    ('AMP', 'Bellman 59N'): 'Fender® \'59 Bassman → `Bellman 59N`',
    ('AMP', 'UK 45'): 'Marshall® JTM45 (backline da era de Zappa) → `UK 45`',
    ('AMP', 'Flagman'): 'Hiwatt® DR103 da turnê de 1994 (clean potente com headroom) → `Flagman`',
    ('AMP', 'Knights CL'): 'Hiwatt® DR103 + Alembic F-2B (limpo, aberto, dinâmico) → `Knights CL`',
    ('AMP', 'UK 50JP'): 'Marshall® JMP50 (o 4x12 Marshall da pilha de 1994) → `UK 50JP`',
    ('CAB', 'DarkTW 2x12'): 'Falante JBL D120F do Twin → `DarkTW 2x12`',
    ('CAB', 'Foxy 1x12'): 'Gabinete do AC30 → `Foxy 1x12`',
    ('CAB', 'TWD 2x12'): 'Gabinete do Bassman → `TWD 2x12`',
    ('CAB', 'UK-GN 2x12'): 'Gabinete Marshall® com Greenbacks → `UK-GN 2x12`',
    ('CAB', 'UK-LD 4x12'): 'Pilha 4x12 Marshall da turnê (Greenbacks; papel do WEM/Fane) → `UK-LD 4x12`',
    ('CAB', 'J-120 2x12'): 'Cabine neutra de JBL (faz o papel da "mesa" da gravação) → `J-120 2x12`',
    ('CAB', 'D'): 'Corpo dreadnought → `D`',
    ('MOD', 'A-Chorus'): 'Leslie/rotary lento da gravação → `A-Chorus` (velocidade baixa)',
    ('MOD', 'Vibe'): 'Leslie 147RV da gravação → `Vibe` (velocidade baixa)',
    ('DLY', 'Slapbk'): 'Slapback curto de estúdio → `Slapbk`',
    ('DLY', 'Sweet'): 'Delay com 1 repetição na duração da nota (assinatura do solo de Gilmour) → `Sweet`',
    ('DLY', 'T-Echo'): 'O efeito Binson Echorec das jams espaciais → `T-Echo`',
    ('RVB', 'Spring'): 'Mola do Twin/Fender → `Spring`',
    ('RVB', 'Plate'): 'Plate de estúdio ("splash" da faixa) → `Plate`',
    ('RVB', 'Room'): 'Sala curta da Abbey Road → `Room`',
    ('RVB', 'Hall'): 'Hall etéreo das seções lentas → `Hall`',
    ('NR', 'Gate 1'): 'Controle de hum (single coils + ganho) → `Gate 1`',
    ('EQ', 'EQ 1'): 'Esculpir o som para fone/PC → `EQ 1`',
}

# ---------------------------------------------------------------- IR --------
# Política de IR (mesma regra dos agentes .agents/gp100-*):
#   1. FÁBRICA  — o .prst já sai com o CAB de fábrica (formato single validado);
#                  é o som garantido, funciona sem carregar nada.
#   2. BANCO LOCAL — se impulse_responses/ tem captura do gabinete real do rig,
#                  a doc indica o arquivo exato e o slot User IR.
#   3. INTERNET — se nem a fábrica nem o banco cobrem, o agente pesquisa em
#                  reference/17-free-ir-packs.md e indica o download.
#   4. FALLBACK — se nada acima entregar, mantém o CAB de fábrica.

def ir_catalog():
    """Índice (cabs -> [arquivos 44.1kHz compatíveis]) da biblioteca local de IRs.

    Se o manifesto não puder ser lido, AVISA no stderr e devolve {}: sem esse
    aviso, a seção 📡 de todos os patches passaria a dizer "não há captura
    melhor no banco" — foi assim que o mapa e o patch.md divergiram no passado.
    """
    try:
        data = json.loads((ROOT / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
    except Exception as exc:
        print(f"AVISO: não li tools/ir-library.json ({exc}).\n"
              "       A seção 📡 dos patches vai indicar só o CAB de fábrica.\n"
              "       Rode: python tools/ir_library.py", file=sys.stderr)
        return {}
    idx = {}
    for pack in data.get('packs', {}).values():
        for f in pack.get('files', []):
            if f.get('compatible'):
                cab = Path(f['file']).parts[-2].replace(' Mics', '')
                idx.setdefault(cab, []).append(Path(f['file']).parts[-1])
    return idx

IR_LIB = ir_catalog()


def ir_mixes(cab_lib):
    """Escolhe o arquivo Mix recomendado da captura local (Medium > Bright > Dark > primeiro)."""
    for pref in ('Medium Mix', 'Bright Mix', 'Dark Mix'):
        for f in IR_LIB.get(cab_lib, []):
            if pref in f:
                return f
    return IR_LIB.get(cab_lib, [None])[0]


def build_ir_section(spec, ir_nota):
    """Seção exclusiva de IR da documentação (seção 3 do patch.md)."""
    cab = spec['modules'].get('CAB', {})
    cab_nome = cab.get('name') or '(sem CAB)'
    linhas = [
        '## 📡 3. Impulse Response (CAB) — o gabinete do patch',
        '',
        f"**O que está no arquivo `.prst` agora**: CAB de fábrica **`{cab_nome}`** — o modelo GP-100 que reproduz "
        "o gabinete do rig real. Este patch **funciona imediatamente**, sem carregar IR alguma; continue para a seção 5 se preferir.",
        '',
        '> A GP-100 aceita **1 IR de usuário por patch** (slots User IR 1–20, wav 44,1 kHz/24 bits/mono, aparar acima de 1024 samples).',
        '>',
        '> Uma IR boa **substitui** o CAB — não empilha com ele.',
        '',
    ]
    par = IR_LOCAL_POR_CAB.get(cab_nome)
    tem_local = bool(par and IR_LIB.get(par[0]))
    if tem_local:
        cab_lib, slot = par
        arquivo = ir_mixes(cab_lib)
        linhas += [
            '### 📁 Melhor opção no nosso banco (`impulse_responses/`) — use esta',
            '',
            f"O banco local tem a captura **{cab_lib}** — casamento direto com o gabinete real deste patch:",
            '',
            f"1. No **GP-100 Edits** → IR Manager, carregue no **{slot}** o arquivo:",
            f'   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects IR Cab Library/{cab_lib}/{arquivo}`',
            f"2. No patch: bloco CAB → troque `{cab_nome}` por **User IR {slot.split()[-1]}**.",
            '3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), **Level** comece em 0 e compare com o bypass.',
            f"   Alternativas do mesmo gabinete no banco: " + ', '.join(f'`{f}`' for f in IR_LIB.get(cab_lib, []) if f != arquivo) + '.',
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


PROTOCOLO_UNIVERSAL = [
    'Patch inteiro alto/baixo demais → ajuste o **Output do AMP** (±3) — nunca o MASTER VOLUME.',
    'Muito agudo no fone → **CAB High Cut +5**. Muito escuro → High Cut −5.',
    'Ruído entre as notas → **NR Thr +2** (sobe até engolir o hum sem cortar a cauda).',
    'Efeito "sumindo" ao desligar → o Level do módulo desviou do bypass; iguale ao som com o módulo OFF.',
]


def fmt_val(v):
    """Converte o valor do spec em string para exibição/tabelas."""
    return str(v)


def disp(label, v):
    """Exibição amigável de switches (Bright, Char, Mode)."""
    if label == 'Bright' and str(v) in ('0', '1'):
        return 'Off' if str(v) == '0' else 'On'
    if label == 'Char' and str(v) in ('0', '1'):
        return 'Cool' if str(v) == '0' else 'Hot'
    if label == 'Mode' and str(v) in ('0', '1', '2', '3'):
        return ('STD', 'Jumbo', 'ENH', 'Piezo')[int(str(v))]
    return fmt_val(v)


def detail_tables(spec):
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
        out.append(f"### {mod} — {name}\n")
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
        out.append('> ℹ️ **`pN`** = slot de parâmetro deste modelo **sem nome oficial documentado** '
                   '(o manual V1.8 só cobre os modelos antigos) — ajuste por orelha, comparando '
                   'com o bypass; os demais nomes seguem o manual da GP-100.')
        out.append('')
    return '\n'.join(out)


def typing_recipe(spec, doc=None):
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
            parts.append(f"**{mod}** `{m['name']}` (ajuste fino no painel — seção 3 📡)")
            continue
        kv = ' / '.join(
            f"{names[int(k)] if int(k) < len(names) else 'p' + k} {disp(names[int(k)] if int(k) < len(names) else '', v)}"
            for k, v in sorted(params.items(), key=lambda x: int(x[0])))
        parts.append(f"**{mod}** `{m['name']}`" + (f" ({kv})" if kv else ''))
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
                f"{names[int(k)] if int(k) < len(names) else 'p' + k} {disp(names[int(k)] if int(k) < len(names) else '', v)}"
                for k, v in sorted(params.items(), key=lambda x: int(x[0])))
            extras.append(f"SOBRESSALENTE **{mod}** `{m['name']}` ({kv})")
        else:
            extras.append(f"SOBRESSALENTE **{mod}** `{m['name']}` (template de fábrica — ajuste por orelha ao ligar)")
    if extras:
        parts.append(' · '.join(extras))
    return ' → '.join(parts)


def ajustes_table(ajustes):
    """Transforma as linhas "sintoma → ação" em tabela Markdown de ajustes finos."""
    rows = []
    for a in ajustes:
        if '→' in a:
            sintoma, acao = a.split('→', 1)
            rows.append(f"| {sintoma.strip()} | {acao.strip()} |")
        else:
            rows.append(f"| — | {a.strip()} |")
    return '\n'.join(rows)


def build_momentos_section(spec, doc):
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
        nome = f"`{m['name']}`" if m.get('name') else '—'
        linhas.append(f'| {mod} | {estado} | {nome} |')
    linhas.append('')
    if momentos:
        linhas += ['### 🎭 Momentos desta música (validados para este patch)', '',
                   'Mude SÓ os módulos indicados — o resto permanece como na tabela acima:', '']
        for i, mo in enumerate(momentos, 1):
            mods_txt = ' + '.join(f'**{m} → {e}**' for m, e in mo['mods'])
            linhas.append(f'{i}. **{mo["nome"]}** — {mods_txt}')
            linhas.append(f'   *Quando*: {mo["quando"]}')
            if mo.get('dica'):
                linhas.append(f'   *Dica*: {mo["dica"]}')
            linhas.append('')
    else:
        linhas += ['### 🎭 Momentos desta música', '',
                   'Este patch foi afinado para **um** papel — use os sobressalentes da tabela acima para variar na hora '
                   '(ex.: desligar o DLY para uma seção seca). Momentos dedicados estão nos patches irmãos da mesma '
                   'música (veja o mapa do álbum).', '']
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


def build_doc(song, patch, spec, slot):
    """Renderiza o patch.md completo de um patch (documento prático-primeiro).

    Ordem fixa: cabeçalho com badges → 🎸 1. Sua guitarra agora (seletor,
    volume, tone, técnica) → 🔧 2. Ajustes finos → 📡 3. Impulse Response
    (fábrica → banco local → internet → fallback) → 🔊 4. Objetivo do som →
    📚 5. Referência real (dossiê com fontes) → 🎛️ 6. Parâmetros → 🚫 evite
    → 💾 receita de digitação + slot. Markdown puro (sem HTML cru — o viewer
    do usuário não renderiza <div>/<br>).
    """
    alb = ALBUMS[song['idAlbum']]
    banda, album, ano = alb['banda'], alb['album'], alb['ano']
    g = patch['doc']['guitarra']
    doc = patch['doc']

    chain_row = '| ' + ' | '.join(CHAIN) + ' |'
    chain_sep = '|' + '---|' * len(CHAIN)
    cells = []
    for mod in CHAIN:
        m = spec['modules'].get(mod, {})
        cells.append(f"{DOT} {mod} · {m['name']}" if m.get('on') else f"{CIRCLE} {mod}")
    chain_cells = '| ' + ' | '.join(cells) + ' |'

    compact = []
    for mod in CHAIN:
        m = spec['modules'].get(mod, {})
        if m.get('on'):
            names = PARAM_NAMES.get((mod, m['name']), [])
            params = m.get('params', {})
            vals = ' · '.join(
                f"{names[int(k)] if int(k) < len(names) else 'p' + k}: {disp(names[int(k)] if int(k) < len(names) else '', v)}"
                for k, v in sorted(params.items(), key=lambda x: int(x[0])))
            compact.append(f"| {mod} | {m['name']} | {vals or '(template)'} |")

    refs = '\n'.join(f"| {r['role']} | {r['conf']} | {r['src']} |" for r in song['referencias'])
    mapping = '\n'.join(
        f"- {BASE_MAP[(mod, spec['modules'][mod]['name'])]}"
        for mod in CHAIN
        if spec['modules'].get(mod, {}).get('on') and (mod, spec['modules'][mod]['name']) in BASE_MAP)
    tecnicas = '\n'.join(f"{i+1}. {t}" for i, t in enumerate(g['tecnicas']))
    escutar = '\n'.join(f"- ☑️ {e}" for e in doc['teste']['escutar'])
    ajustes = ajustes_table(doc['ajustes'])
    protocolo = '\n'.join(f'- {p}' for p in PROTOCOLO_UNIVERSAL)
    evite = '\n'.join(f'- ⛔ {e}' for e in doc['evite'])
    ir_section = build_ir_section(spec, doc.get('irNota', ''))
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


def main():
    """Ponto de entrada: regenera TODOS os patches definidos em patches-defs.json.

    Para cada patch: escreve spec.json (com author/notes derivados da música),
    patch.md (build_doc) e <NOME>.prst (delegando ao generate_prst.py), depois
    valida o XML resultante (nome ≤ 12 chars e igual ao definido). Os slots
    U01…Uxx são calculados pela ordem global dos defs (AR → ZP → PMH) — a
    numeração nunca fica defasada quando um álbum novo entra.
    """
    made = []
    # slots calculados pela ordem global dos defs (AR → ZP → PMH) — nunca defasados
    slot_map, n = {}, 0
    for song in DEFS['songs']:
        for patch in song['patches']:
            n += 1
            slot_map[patch['nome']] = f"U{n:02d}"
    for song in DEFS['songs']:
        album_root = ALBUM_DIR[song['idAlbum']]
        for patch in song['patches']:
            spec = copy.deepcopy(patch['spec'])
            slot = slot_map[patch['nome']]
            spec['author'] = 'GP-100 Patch Architect'
            spec['notes'] = f"{song['song']} ({ALBUMS[song['idAlbum']]['album']}) - {patch['camada']}"
            folder = album_root / SONG_FOLDER[song['id']] / patch['nome']
            folder.mkdir(parents=True, exist_ok=True)

            spec_path = folder / 'spec.json'
            spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

            (folder / 'patch.md').write_text(build_doc(song, patch, spec, slot), encoding='utf-8', newline='\r\n')

            prst = folder / f"{patch['nome']}.prst"
            r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'generate_prst.py'),
                                str(spec_path), str(prst)], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"FALHA {patch['nome']}: {r.stdout}{r.stderr}")
                sys.exit(1)
            root = ET.parse(prst).getroot()
            p = root.find('presets')
            assert p.get('ppName') == patch['nome'], f"nome no painel diverge: {p.get('ppName')}"
            assert len(p.get('ppName')) <= 12, f"nome > 12 chars: {patch['nome']}"
            made.append(f"{song['song']:45s} → {patch['nome']:9s} ({patch['camada']})")

    print(f"✅ {len(made)} patches gerados e validados:\n")
    for m in made:
        print('  ' + m)


if __name__ == '__main__':
    main()
