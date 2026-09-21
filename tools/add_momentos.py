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
    'WYWH01IN': [('Solo (com eco)', [('DLY', 'ON')], 'O sobressalente dá o eco do solo de abertura.', ''),
                 ('Arpejo seco', [('DLY', 'OFF'), ('RVB', 'OFF')], 'Versão "na sua cara" do arpejo (gravação/técnica).', '')],
    'CNW01SO': [('Acordes do refrão', [('DLY', 'OFF')], 'Os acordes da música pedem seco; o eco é do solo.', '')],
    'CNW01S2': [('Acordes do refrão', [('DLY', 'OFF')], 'Mesma dica do 1º solo: refrão seco, solo com eco.', '')],
    'RLH01RI': [('Ensaio no tempo', [('DLY', 'OFF')], 'Ensaie o riff seco — o eco da parede esconde atrasos de timing. Ao vivo, religue.', '')],
    'RLH01SO': [('Ritmo (sem eco)', [('DLY', 'OFF')], 'Acordes do verso sem a parede de eco.', '')],
    'SFTM01AM': [('Textura crua', [('DLY', 'OFF'), ('RVB', 'OFF')], 'Swell puro, sem ambiência (para camadas na gravação).', '')],
    'ONR01AM': [('Textura crua', [('DLY', 'OFF')], 'Só o reverb ambiente — o delay industrial sai.', '')],
    # ---- Zappa
    'URM01SL': [('Solo seco de Zappa', [('RVB', 'OFF')], 'A produção de Zappa é seca até na base — para frases à frente do vocal, desligue o Plate.', '')],
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
