"""
add_momentos.py — Injeta os "momentos de atuação" (liga/desliga módulos) nos
patches de tools/patches-defs.json.

Um patch GP-100 não precisa nascer em cópia para cada momento da música: a
pedaleira liga/desliga qualquer módulo em tempo real (painel slot a slot ou
FS-A/FS-B no modo STOMP). Cada momento declara (nome, [(modulo, 'ON'|'OFF')],
quando, dica) e é validado contra o spec: só é injetado se o módulo existir
na cadeia e o estado pedido for o inverso do atual. Módulos OFF com modelo
escolhido viram "sobressalentes" documentados no patch.md.

Uso: python tools/add_momentos.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
DEFS_PATH = ROOT / 'tools' / 'patches-defs.json'

# (nome, [(modulo, 'ON'|'OFF')], quando, dica)
MOMENTOS = {
    # ---- Pulse: sobressalentes de eco (DLY Sweet OFF = eco do solo a um clique)
    'SOF01EC': [('Base seca (partes cantadas)', [('DLY', 'OFF')], 'Entre a intro e os solos, toque os acordes sem eco.', 'Religue o DLY para voltar ao som da intro.')],
    'SOF01BA': [('Solo (com eco)', [('DLY', 'ON')], 'Frases entre os acordes: ligue e você tem o eco do solo sem trocar de patch.', '')],
    'SOF01SO': [('Base seca', [('DLY', 'OFF')], 'Refrões/acordes — eco some, sobra o sustain do amp.', '')],
    'WDF01BA': [('Solo (com eco)', [('DLY', 'ON')], 'Ao chegar no solo, ligue o DLY: o eco do solo já está projetado.', '')],
    'WDF01SO': [('Ritmo seco', [('DLY', 'OFF')], 'Base do riff — acordes secos para marcar o groove.', '')],
    'LTF01BA': [('Solo espacial', [('DLY', 'ON')], 'O solo da música vive do eco — ligue o sobressalente.', '')],
    'LTF01SO': [('Base sem eco', [('DLY', 'OFF')], 'Acompanhamento limpo — o chorus segue, o eco sai.', '')],
    'KTB01BA': [('Solo (eco)', [('DLY', 'ON')], 'Solo principal com o eco na duração da nota.', '')],
    'KTB01SO': [('Refrão seco', [('DLY', 'OFF')], 'Acordes do refrão sem eco (o canto responde).', '')],
    'KTB01FZ': [('Verso sem fuzz', [('DST', 'OFF')], 'O Big Muff sai e sobra o crunch do Flagman — um patch para a música toda.', 'Religue o DST no solo.')],
    'CBK01AR': [('Ponte seca', [('DLY', 'OFF')], 'Seção pontual sem eco (a base dos arpejos volta com DLY ON).', '')],
    'SIA01FZ': [('Verso (crunch)', [('DST', 'OFF')], 'Versos de crunch do Flagman; DST ON = intro/solo de fuzz.', 'Este é o patch "música inteira" de Sorrow.')],
    'SIA01SO': [('Acordes (sem lead)', [('DLY', 'OFF')], 'Colchão do verso com o eco desligado.', '')],
    'ABIETWBA': [('Solo (eco)', [('DLY', 'ON')], 'Chegou o solo: ligue o DLY e o patch vira o solo do Muro.', '')],
    'ABIETWSO': [('Base seca', [('DLY', 'OFF')], 'Groove do riff sem eco (só o solo usa).', '')],
    'TM01BA': [('Solo (eco curto)', [('DLY', 'ON')], 'Para puxar frases do solo de Time na base, com o eco curto certo.', '')],
    'TM01SO': [('Verso seco', [('DLY', 'OFF')], 'Acompanhamento do verso sem eco.', '')],
    'MNY01BA': [('Solo (eco)', [('DLY', 'ON')], 'Solo do 7/4 com o eco do projeto.', '')],
    'MNY01SO': [('Groove seco', [('DLY', 'OFF')], 'Riff do 7/4 seco — definição total.', '')],
    'USAT01BA': [('Solo aéreo', [('DLY', 'ON')], 'Frases sobre a balada — o eco completa o vazio.', '')],
    'USAT01SO': [('Base (sem eco)', [('DLY', 'OFF')], 'Acompanhamento discretíssimo.', '')],
    'BRT01BA': [('Solo espacial', [('DLY', 'ON')], 'Sobressalente para frases entre os acordes.', '')],
    'BTK02BA': [('Solo (eco)', [('DLY', 'ON')], 'Frases sobre a reprise.', '')],
    'BD01BA': [('Solo (eco)', [('DLY', 'ON')], 'Frases entre os versos.', '')],
    # WYWH01IN: o seeder do Pulse já entrega DLY ON (o patch É intro/solo com eco),
    # então um momento [DLY ON] é sempre inválido — só o "Arpejo seco" vale.
    'WYWH01IN': [('Arpejo seco', [('DLY', 'OFF'), ('RVB', 'OFF')], 'Versão "na sua cara" do arpejo (gravação/técnica).', '')],
    'CNW01SO': [('Acordes do refrão', [('DLY', 'OFF')], 'Os acordes da música pedem seco; o eco é do solo.', '')],
    'CNW01S2': [('Acordes do refrão', [('DLY', 'OFF')], 'Mesma dica do 1º solo: refrão seco, solo com eco.', '')],
    'RLH01RI': [('Ensaio no tempo', [('DLY', 'OFF')], 'Ensaie o riff seco — o eco da parede esconde atrasos de timing. Ao vivo, religue.', '')],
    'RLH01SO': [('Ritmo (sem eco)', [('DLY', 'OFF')], 'Acordes do verso sem a parede de eco.', '')],
    'SFTM01AM': [('Textura crua', [('DLY', 'OFF'), ('RVB', 'OFF')], 'Swell puro, sem ambiência (para camadas na gravação).', '')],
    'ONR01AM': [('Textura crua', [('DLY', 'OFF')], 'Só o reverb ambiente — o delay industrial sai.', '')],
    # ---- Zappa
    'URM01SL': [('Solo seco de Zappa', [('RVB', 'OFF')], 'A produção de Zappa é seca até na base — para frases à frente do vocal, desligue o Plate.', '')],
    # ---- Nirvana (Wishkah): o stomp DST É a dinâmica quiet-loud
    'DRY01AR': [('Refrão punk', [('DST', 'ON')], 'Refrão: ligue o DST e a base vira parede de som.', 'Volte ao arpejo desligando no verso.'),
                ('Solo punk', [('MOD', 'OFF')], 'Para o solo central, desligue o chorus: som seco e presente.', '')],
    'DRY01RI': [('Verso limpo', [('DST', 'OFF'), ('MOD', 'ON')], 'O verso é arpejo limpo com chorus — o inverso exato deste patch.', 'É o patch DRY01AR em um stomp só.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente: um EQ realce para o solo, se tocar no mesmo patch.', '')],
    'ANE01AR': [('Refrão pesado', [('DST', 'ON')], 'A explosão do refrão é um stomp: DST ON = wall of sound.', 'Volte ao quiet-loud desligando.'),
                ('Solo livre', [('MOD', 'OFF'), ('DST', 'ON')], 'Solo de fechamento: chorus sai, distorção entra.', '')],
    'SLT01CL': [('Riff do século', [('DST', 'ON')], 'Pré-refrão chegou? DST ON = o riff F–Bb–Ab–Db no talo.', 'O verso volta com DST OFF.'),
                ('Solo gaguejado', [('EQ', 'ON')], 'Sobressalente: realce de médios para o solo cantado.', '')],
    'SLT01RI': [('Verso limpo', [('DST', 'OFF'), ('MOD', 'ON')], 'O verso é LIMPO com chorus — o erro clássico é tocar sujo.', 'Mesma ideia do SLT01CL em um stomp.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente para o solo gaguejado.', '')],
    'POL01CL': [('Refrão elétrico', [('DST', 'ON')], 'Refrão: a elétrica de 1989 explode — DST ON.', 'Verso volta em palm mute seco.'),
                ('Verso com mordida', [('EQ', 'ON')], 'Sobressalente: leve realce se o verso estiver tímido.', '')],
    'BRE01RI': [('Solo gritado', [('EQ', 'ON')], 'Sobressalente: realce para as frases do meio.', '')],
    'LIT01AR': [('Refrão "yeah yeah"', [('DST', 'ON')], 'Refrão: DST ON = acordes estourados.', 'Arpejo volta com DST OFF.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente para o solo curto.', '')],
    'LIT01RI': [('Verso pop', [('DST', 'OFF'), ('MOD', 'ON')], 'O verso é arpejo com chorus — este patch em um stomp.', 'É o LIT01AR sem trocar de patch.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente: realce de médios.', '')],
    'HSB01AR': [('Refrão pesado', [('DST', 'ON')], 'Refrão: DST ON = parede de DS-1.', 'O colchão do verso volta com DST OFF.'),
                ('Solo punk', [('MOD', 'OFF')], 'Solo do meio: chorus sai para o lead morder.', '')],
    'HSB01RI': [('Verso claro', [('DST', 'OFF'), ('MOD', 'ON')], 'O verso é colchão limpo com chorus — um stomp só.', 'É o HSB01AR sem trocar de patch.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente: realce para as frases do meio.', '')],
    'MIL01RI': [('Verso seco', [('DST', 'OFF')], 'Pausa seca do verso — DST OFF e o patch respira.', 'A parede volta com DST ON.'),
                ('Solo', [('EQ', 'ON')], 'Sobressalente: realce para o final.', '')],
    'SCE01RI': [('Solo denso', [('EQ', 'ON')], 'Sobressalente: realce para as frases sobre o loop.', '')],
    'BEE01RI': [('Solo dissonante', [('EQ', 'ON')], 'Sobressalente: realce para o solo tenso.', '')],
    'SLV01RI': [('Verso seco', [('DST', 'OFF')], '"Grandma take me home" em palm mute SECO — DST OFF.', 'Refrão volta com DST ON.'),
                ('Intro do coro', [('MOD', 'ON')], 'A intro é colchão com vibe (patch SLV01AR) — aqui é um stomp.', '')],
    'SLV01AR': [('Riff principal', [('DST', 'ON'), ('MOD', 'OFF')], 'Entrada do riff: chorus sai, distorção entra.', 'Volte à textura no verso seguinte.'),
                ('Verso sem vibe', [('MOD', 'OFF')], 'Verso "grandma" em palm mute, sem o colchão da vibe.', '')],
    'SPK01SO': [('Base punk', [('DST', 'OFF'), ('MOD', 'ON')], 'Para a base da jam, desligue o lead: chorus limpo.', 'Solo volta com DST ON.')],
    'NEG01RI': [('Solo com feedback', [('EQ', 'ON')], 'Sobressalente: realce para o grito de guitarra.', '')],
    'BLE01RI': [('Solo psicodélico', [('EQ', 'ON')], 'Solo final: realce de presença para os harmônicos sobre o fuzz.', '')],
    'TOU01RI': [('Meio-tempo', [('DST', 'OFF')], 'Se ensaiar mais devagar, DST OFF = crunch limpo.', 'Caos volta com DST ON.')],
}

data = json.loads(DEFS_PATH.read_text(encoding='utf-8'))
por_nome = {}
for s in data['songs']:
    for p in s['patches']:
        por_nome[p['nome']] = (s, p)

injetados, pulados = 0, []
for nome, momentos in MOMENTOS.items():
    if nome not in por_nome:
        pulados.append((nome, 'patch não encontrado'))
        continue
    _, p = por_nome[nome]
    mods = p['spec']['modules']
    validados = []
    for (display, alvos, quando, dica) in momentos:
        ok = []
        for (mnome, estado) in alvos:
            if mnome not in mods:
                pulados.append((nome, f'{mnome} não existe no spec'))
                continue
            atual_on = mods[mnome].get('on', False)
            quer_on = (estado == 'ON')
            if atual_on == quer_on:
                pulados.append((nome, f'{mnome} já está {"ON" if atual_on else "OFF"}'))
                continue
            ok.append([mnome, estado])
        if ok:
            validados.append({'nome': display, 'mods': ok, 'quando': quando, 'dica': dica})
    if validados:
        p['doc']['momentos'] = validados
        injetados += len(validados)

# ---- copia params do delay do patch-irmão de solo para bases com momento "liga o eco" ----
# O toggle DLY→ON deve soar EXATAMENTE como o solo: o módulo OFF herda name+params
# do patch SO da mesma música (estado OFF + params presentes = igual aos exports de fábrica).
copiados = 0
for s, p in por_nome.values():
    momentos = p['doc'].get('momentos', [])
    quer_dly = any(('DLY', 'ON') in [tuple(a) for a in mo['mods']] for mo in momentos)
    if not quer_dly:
        continue
    dly = p['spec']['modules'].get('DLY', {})
    if dly.get('on') or (dly.get('params') and len(dly['params'])):
        continue
    irmao = next((q for q in s['patches'] if q['nome'] != p['nome']
                  and q['spec']['modules'].get('DLY', {}).get('on')), None)
    if irmao:
        src = irmao['spec']['modules']['DLY']
        dly['name'], dly['params'] = src['name'], dict(src['params'])
        copiados += 1

DEFS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'OK: {injetados} momentos injetados, {copiados} delays de solo herdados por bases'
      + (f' | pulados: {pulados}' if pulados else ''))
