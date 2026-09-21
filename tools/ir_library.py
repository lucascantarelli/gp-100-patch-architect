"""
ir_library.py — Indexa a biblioteca local de IRs (impulse_responses/) para a GP-100.

Uso:  python tools/ir_library.py            # regenera tools/ir-library.json + reference/16-ir-library.md

Compatibilidade GP-100 (por WAV):
  - mono, 24 bits, 44.1 kHz  → OK direto
  - qualquer desvio          → CONVERTER (o editor pode aceitar, mas converta p/ segurança)
Limites do device: IR de até 1024 samples (~23 ms @ 44.1 kHz) — arquivos mais longos
são aparados pelo editor (a cauda longa = "room" do IR é descartada; normal p/ cab IR).

Saídas:
  - tools/ir-library.json   (manifesto estruturado p/ os agentes)
  - reference/16-ir-library.md (catálogo legível; atualizado a cada rodada)
"""
import json
import sys
import wave
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
IR_DIR = ROOT / 'impulse_responses'
OUT_JSON = ROOT / 'tools' / 'ir-library.json'
OUT_MD = ROOT / 'reference' / '16-ir-library.md'

KNOWN_PACKS = {
    'Origin Effects - IR-Cab Library V3': {
        'source': 'https://origineffects.com/product/ir-cab-library/',
        'license': 'Gratuita (cadastro manual no site da Origin Effects)',
        'notes': 'Capturas profissionais dos cabines reais; mixes Bright/Medium/Dark + mics individuais (87=U87 FET, 160=RCA 160 ribbon, 421=SM421, 57=SM57).',
    },
}


def wav_info(path: Path):
    """Inspeciona um WAV e devolve taxa/canais/bits/duração + flags de compatibilidade.

    compatible: mono (1 canal), 24 bits e 44.1 kHz — o formato aceito direto
    pela GP-100. over_1024: mais de 1024 samples (o editor aparar a cauda ao
    carregar). Em caso de erro de leitura, devolve {'error': ..., 'compatible': False}.
    """
    try:
        w = wave.open(str(path))
        n, fr, ch, sw = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
        w.close()
        return {
            'rate': fr, 'channels': ch, 'bits': sw * 8,
            'duration_ms': round(n / fr * 1000),
            'compatible': ch == 1 and sw * 8 == 24 and fr == 44100,
            'over_1024': n > 1024,
        }
    except Exception as e:
        return {'error': str(e), 'compatible': False}


def cab_of(rel_posix: str) -> str:
    """Nome do gabinete: pasta do arquivo; se a pasta for '... Mics', sobe um nível."""
    parts = rel_posix.split('/')[:-1]
    if parts and parts[-1].endswith('Mics'):
        parts = parts[:-1]
    return parts[-1] if parts else '(raiz)'


def main():
    """Varre impulse_responses/, indexa os packs e regenera as duas saídas.

    Saídas: tools/ir-library.json (manifesto completo para os agentes) e
    reference/16-ir-library.md (catálogo legível: packs, gabinetes, mixes
    recomendados e compatibilidade). Imprime o resumo no console.
    """
    if not IR_DIR.exists():
        raise SystemExit(f'Pasta {IR_DIR} não existe.')
    packs = {}
    for wav in sorted(IR_DIR.rglob('*.wav')):
        rel = wav.relative_to(IR_DIR)
        pack = rel.parts[0] if len(rel.parts) > 1 else '(raiz)'
        info = wav_info(wav)
        entry = {
            'file': rel.as_posix(),
            'size_kb': round(wav.stat().st_size / 1024),
            **info,
        }
        packs.setdefault(pack, []).append(entry)

    manifest = {'packs': {}, 'generated_by': 'tools/ir_library.py'}
    for pack, files in packs.items():
        wavs = [f for f in files if 'error' not in f]
        cabs = sorted({cab_of(f['file']) for f in wavs})
        manifest['packs'][pack] = {
            'wavs': len(wavs), 'cabs': cabs,
            'all_compatible': all(f['compatible'] for f in wavs),
            'meta': KNOWN_PACKS.get(pack, {}),
            'files': files,
        }

    OUT_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')

    # ---- referência MD ----
    lines = [
        '# 📚 Biblioteca local de IRs — catálogo', '',
        '> **Gerado por** `tools/ir_library.py` — rode de novo após baixar packs novos.',
        '> Os agentes (gp100-cab-ir, gp100-ir-fit, gp100-ir-research) consultam **este arquivo**',
        '> e `tools/ir-library.json` antes de sugerir IR de terceiros: se já existe na biblioteca,',
        '> **não pesquise na internet — use a local**.', '',
    ]
    for pack, mp in manifest['packs'].items():
        ok = '✅' if mp['all_compatible'] else '⚠️ (parte precisa conversão)'
        meta = mp['meta']
        lines.append(f'## 📦 {pack} {ok}')
        if meta:
            lines.append(f"- Fonte: {meta['source']}")
            lines.append(f"- Licença: {meta['license']}")
            if meta.get('notes'):
                lines.append(f"- Notas: {meta['notes']}")
        lines.append(f"- WAVs: {mp['wavs']} · Gabinetes: {', '.join(mp['cabs'])}")
        lines.append('')
        # tabela: só os Mix (recomendados p/ começar); mics individuais ficam no JSON
        shown = [f for f in mp['files'] if 'error' not in f and f['file'].endswith('Mix.wav')]
        n_mics = mp['wavs'] - len(shown)
        lines.append('| Mix recomendado | Taxa | Bits | Dur. | Compatível GP-100 |')
        lines.append('|---|---|---|---|---|')
        for f in shown:
            comp = '✅ direto' if f['compatible'] else '⚠️ converter'
            tail = ' · aparar >1024 samp.' if f.get('over_1024') else ''
            lines.append(
                f"| `{f['file'].split('/', 1)[1]}` | {f['rate']} | {f['bits']} | "
                f"{f['duration_ms']} ms | {comp}{tail} |")
        lines.append(f"")
        lines.append(f"> Variações de microfone individuais: {n_mics} arquivos (ver `tools/ir-library.json`).")
        lines.append('')
        lines.append('> 💡 Packs com pastas 44.1/48/96 kHz: **use sempre a pasta 44.1 kHz** — as outras')
        lines.append('> são as mesmas capturas em outra taxa (a GP-100 exige 44.1 kHz).')
        lines.append('')

    lines += [
        '## 🔌 Como carregar uma IR local na GP-100', '',
        '1. Conecte a pedaleira e abra o **GP-100 Edits**.',
        '2. Menu **IR Manager / User IR**: escolha o **slot (1–20)** e carregue o `.wav`.',
        '3. O slot passa a existir como cabine **“User IR n”** dentro do bloco CAB.',
        '4. No patch: bloco CAB → navegue até `User IR n` → ajuste **Low Cut / High Cut / Level**.',
        '5. Exporte/importe patches normalmente — o `.prst` fica associado ao slot.',
        '',
        '> ⚠️ Regra dos agentes: `.prst` gerado por `tools/generate_prst.py` usa CAB de fábrica',
        '> (formato single validado). Para patch com User IR, documente o swap manual ou use o',
        '> arquivo experimental gerado com `ir_cab_user_slot` — teste na pedaleira antes de adotar.',
        '',
        '## 🌍 Packs gratuitos para ampliar a biblioteca',
        '',
        'Ver seção ao final deste catálogo em cada rodada — mantida pelo agente `gp100-ir-research`.',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')

    total = sum(m['wavs'] for m in manifest['packs'].values())
    print(f'✅ {total} WAVs em {len(packs)} pack(s) indexados.')
    for pack, mp in manifest['packs'].items():
        print(f"  - {pack}: {mp['wavs']} WAVs · cabs: {', '.join(mp['cabs'])} · compatível: {mp['all_compatible']}")


if __name__ == '__main__':
    main()
