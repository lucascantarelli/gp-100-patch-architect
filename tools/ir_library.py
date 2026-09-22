"""
ir_library.py — Indexa a biblioteca local de IRs (impulse_responses/) para a GP-100.

Uso:  python tools/ir_library.py            # regenera tools/ir-library.json + reference/16-ir-library.md
      python tools/ir_library.py --force    # aceita encolher o catálogo (pack removido de propósito)

O banco em si (`impulse_responses/**`) NÃO é versionado — as licenças dos packs
são de terceiros. Só o `impulse_responses/README.md` e os dois catálogos gerados
entram no git. Sem o banco este script avisa e sai com 0, sem zerar os catálogos.

Por que este script existe mesmo com o banco fora do git: o catálogo que ele gera
é INSUMO da documentação — `build_song_patches.py` cita o arquivo exato do banco
na seção 📡 de cada `patch.md` e `gen_indexes.py` marca 📁 no mapa do álbum.
Versionar o banco é problema de licença; gerar o catálogo é o que mantém as 62
docs corretas. Deletar este script apagaria essa recomendação de todos os patches.

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
        'license': 'Gratuita (cadastro manual no site da Origin Effects) — redistribuição não concedida',
        'notes': 'Capturas profissionais dos cabines reais; mixes Bright/Medium/Dark + mics individuais (87=U87 FET, 160=RCA 160 ribbon, 421=SM421, 57=SM57).',
    },
}

# O banco de IRs NÃO é versionado (licença de terceiros: baixe no site do
# fabricante). Só este README e os catálogos gerados vivem no git — por isso o
# índice precisa degradar em silêncio quando a pasta está ausente/vazia.


def wav_order(path: Path) -> str:
    """Chave de ordenação estável entre sistemas operacionais.

    `Path` compara com `normcase`, que **minúsculas no Windows** e é identidade no
    Linux — usar Path como chave faz o manifesto sair em ordem diferente no CI
    (ex.: `4x12 MFB` × `4x12 Metal American`). Comparar o caminho POSIX como
    `str` (ordem de code point) dá exatamente o mesmo resultado em qualquer OS.
    """
    return path.relative_to(IR_DIR).as_posix()


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


def encolhimento_do_catalogo(manifest):
    """Problemas se esta rodada fosse ENCOLHER o catálogo já commitado.

    Por que este guarda existe: o catálogo de IRs é insumo da documentação de 62
    patches. Se um pack conhecido desaparece da rodada, `build_song_patches.py`
    para de emitir a seção "📁 Melhor opção no nosso banco" e `gen_indexes.py`
    passa a marcar ⚙️ (fábrica) no mapa do álbum — **os dois juntos**, então
    `TestB_FonteUnica_IR` aprova e o `check_data_freshness.py` também. Ou seja:
    quem roda o pipeline com o banco incompleto apagaria a recomendação de IR dos
    patches sem nenhum sinal. Como o banco não é versionado, isso passou a ser um
    acidente fácil — aqui ele vira erro explícito.

    Devolve [] quando está tudo bem, ou a lista de regressões encontradas.
    """
    if not OUT_JSON.exists():
        return []
    try:
        antigo = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    except Exception:
        return []                      # catálogo ilegível: não bloqueia a rodada
    problemas = []
    for nome, mp in antigo.get('packs', {}).items():
        novo = manifest['packs'].get(nome)
        if novo is None:
            problemas.append(f"pack ausente nesta rodada: {nome} ({mp.get('wavs', 0)} WAVs)")
        elif novo['wavs'] < mp.get('wavs', 0):
            problemas.append(
                f"pack reduzido: {nome} ({mp.get('wavs', 0)} → {novo['wavs']} WAVs)")
    return problemas


def main():
    """Varre impulse_responses/, indexa os packs e regenera as duas saídas.

    Saídas: tools/ir-library.json (manifesto completo para os agentes) e
    reference/16-ir-library.md (catálogo legível: packs, gabinetes, mixes
    recomendados e compatibilidade). Imprime o resumo no console.

    Banco ausente ou vazio (o caso do CI: só `impulse_responses/README.md` é
    versionado) → **não** sobrescreve os catálogos commitados com um manifesto
    vazio, apenas avisa e sai com 0. É o que mantém o job de dados verde em um
    clone limpo, sem transformar "não baixei o pack" em build vermelho.

    Banco incompleto → reprova, a menos que venha `--force`. Ver
    `encolhimento_do_catalogo`.
    """
    wavs = sorted(IR_DIR.rglob('*.wav'), key=wav_order) if IR_DIR.exists() else []
    if not wavs:
        print('ℹ️  Banco local de IRs ausente ou vazio — nada a indexar.')
        print('   Os catálogos commitados (tools/ir-library.json e')
        print('   reference/16-ir-library.md) ficam como estão, com a última')
        print('   indexação conhecida — os agentes continuam consultando-os.')
        print('   Para indexar: baixe o pack e extraia em impulse_responses/<Nome do Pack>/.')
        return 0
    packs = {}
    for wav in wavs:
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

    problemas = encolhimento_do_catalogo(manifest)
    if problemas and '--force' not in sys.argv:
        print('❌ Esta rodada ENCOLHERIA o catálogo commitado de IRs:', file=sys.stderr)
        for p in problemas:
            print(f'   - {p}', file=sys.stderr)
        print('\n   Efeito: os patches perderiam a recomendação do banco local — a seção 📡',
              file=sys.stderr)
        print('   de cada patch.md e o marcador 📁 do mapa do álbum voltariam para o CAB',
              file=sys.stderr)
        print('   de fábrica. A suíte NÃO reprova isso (os dois caem juntos).', file=sys.stderr)
        print('   Nada foi escrito. Se a remoção do pack é intencional, repita com --force.',
              file=sys.stderr)
        return 1

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
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
