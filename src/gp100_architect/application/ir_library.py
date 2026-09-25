"""Indexação da biblioteca local de IRs — manifesto e catálogo (issue #30).

Migração de `tools/ir_library.py`: as regras puras vêm para a camada de
aplicação (ordenar arquivos de forma estável entre sistemas, nomear o gabinete,
montar o manifesto, renderizar o catálogo legível, detectar encolhimento) e a
varredura/escrita fica com a CLI + `infrastructure.wav`/`escrita`.

Por que a indexação existe mesmo com o banco fora do git: o catálogo gerado é
INSUMO da documentação — `build_song_patches` cita o arquivo exato do banco na
seção 📡 de cada `patch.md` e `gen_indexes` marca 📁 no mapa do álbum.
Versionar o banco é problema de licença; gerar o catálogo é o que mantém as
docs corretas.

Camada: application (devolve texto/estruturas; quem lê WAV é infrastructure).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = [
    'CONHECIDOS',
    'GERADO_POR',
    'PROBLEMAS_DE_FORMATO',
    'cab_of',
    'catalogo_md',
    'encolhimento',
    'montar_manifesto',
    'wav_order',
]

GERADO_POR = 'gp100 build (ir_library)'

# Packs com procedência e licença conhecidas — o resto do manifesto registra o
# que foi lido, mas sem fonte citável (o agente de IR reporta a ausência).
CONHECIDOS: dict[str, dict[str, str]] = {
    'Origin Effects - IR-Cab Library V3': {
        'source': 'https://origineffects.com/product/ir-cab-library/',
        'license': 'Gratuita (cadastro manual no site da Origin Effects) — redistribuição não concedida',
        'notes': 'Capturas profissionais dos cabines reais; mixes Bright/Medium/Dark + mics individuais (87=U87 FET, 160=RCA 160 ribbon, 421=SM421, 57=SM57).',
    },
}

PROBLEMAS_DE_FORMATO = (
    '   Efeito: os patches perderiam a recomendação do banco local — a seção 📡\n'
    '   de cada patch.md e o marcador 📁 do mapa do álbum voltariam para o CAB\n'
    '   de fábrica. A suíte NÃO reprova isso (os dois caem juntos).\n'
    '   Nada foi escrito. Se a remoção do pack é intencional, repita com --force.'
)


def wav_order(path: Path, ir_dir: Path) -> str:
    """Chave de ordenação estável entre sistemas operacionais.

    `Path` compara com `normcase`, que **minúsculas no Windows** e é identidade
    no Linux — usar Path como chave faz o manifesto sair em ordem diferente no
    CI (ex.: `4x12 MFB` × `4x12 Metal American`). Comparar o caminho POSIX como
    `str` (ordem de code point) dá exatamente o mesmo resultado em qualquer OS.
    """
    return path.relative_to(ir_dir).as_posix()


def cab_of(rel_posix: str) -> str:
    """Nome do gabinete: pasta do arquivo; se a pasta for '... Mics', sobe um nível."""
    partes = rel_posix.split('/')[:-1]
    if partes and partes[-1].endswith('Mics'):
        partes = partes[:-1]
    return partes[-1] if partes else '(raiz)'


def montar_manifesto(registros: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrupa os registros lidos do disco no manifesto por pack.

    Cada registro é `{'file': <posix relativo>, 'size_kb': N, **infos do WAV}`
    (montado pela CLI com `infrastructure.wav.inspecionar`). Arquivos com
    `error` entram no pack mas não contam como WAV nem como gabinete — o
    catálogo registra a falha em vez de escondê-la.
    """
    packs: dict[str, list[dict[str, Any]]] = {}
    for entrada in registros:
        pack = entrada['file'].split('/')[0] if '/' in entrada['file'] else '(raiz)'
        packs.setdefault(pack, []).append(entrada)

    manifesto: dict[str, Any] = {'packs': {}, 'generated_by': GERADO_POR}
    for pack, arquivos in packs.items():
        validos = [f for f in arquivos if 'error' not in f]
        manifesto['packs'][pack] = {
            'wavs': len(validos),
            'cabs': sorted({cab_of(f['file']) for f in validos}),
            'all_compatible': all(f['compatible'] for f in validos),
            'meta': CONHECIDOS.get(pack, {}),
            'files': arquivos,
        }
    return manifesto


def encolhimento(antigo: dict[str, Any], novo: dict[str, Any]) -> list[str]:
    """Problemas se esta rodada fosse ENCOLHER o catálogo já commitado.

    Por que este guarda existe: o catálogo de IRs é insumo da documentação dos
    patches. Se um pack conhecido desaparece da rodada, `build_song_patches`
    para de emitir a seção "📁 Melhor opção no nosso banco" e `gen_indexes`
    passa a marcar ⚙️ (fábrica) no mapa do álbum — **os dois juntos**, então o
    guarda de sincronia também aprova. Como o banco não é versionado, isso
    passou a ser um acidente fácil; aqui ele vira erro explícito.

    Devolve [] quando está tudo bem, ou a lista de regressões encontradas.
    """
    problemas: list[str] = []
    for nome, mp in (antigo.get('packs') or {}).items():
        pack_novo = (novo.get('packs') or {}).get(nome)
        if pack_novo is None:
            problemas.append(f'pack ausente nesta rodada: {nome} ({mp.get("wavs", 0)} WAVs)')
        elif pack_novo['wavs'] < mp.get('wavs', 0):
            problemas.append(
                f'pack reduzido: {nome} ({mp.get("wavs", 0)} → {pack_novo["wavs"]} WAVs)'
            )
    return problemas


def catalogo_md(manifesto: dict[str, Any]) -> str:
    """Renderiza o `reference/16-ir-library.md` (catálogo legível dos packs)."""
    linhas = [
        '# 📚 Biblioteca local de IRs — catálogo',
        '',
        '> **Gerado por** `gp100 build` — rode de novo após baixar packs novos.',
        '> Os agentes (gp100-cab-ir, gp100-ir-fit, gp100-ir-research) consultam **este arquivo**',
        '> e `data/ir-library.json` antes de sugerir IR de terceiros: se já existe na biblioteca,',
        '> **não pesquise na internet — use a local**.',
        '',
    ]
    for pack, mp in manifesto['packs'].items():
        ok = '✅' if mp['all_compatible'] else '⚠️ (parte precisa conversão)'
        meta = mp['meta']
        linhas.append(f'## 📦 {pack} {ok}')
        if meta:
            linhas.append(f'- Fonte: {meta["source"]}')
            linhas.append(f'- Licença: {meta["license"]}')
            if meta.get('notes'):
                linhas.append(f'- Notas: {meta["notes"]}')
        linhas.append(f'- WAVs: {mp["wavs"]} · Gabinetes: {", ".join(mp["cabs"])}')
        linhas.append('')
        # tabela: só os Mix (recomendados p/ começar); mics individuais ficam no JSON
        mostrados = [f for f in mp['files'] if 'error' not in f and f['file'].endswith('Mix.wav')]
        n_mics = mp['wavs'] - len(mostrados)
        linhas.append('| Mix recomendado | Taxa | Bits | Dur. | Compatível GP-100 |')
        linhas.append('|---|---|---|---|---|')
        for f in mostrados:
            comp = '✅ direto' if f['compatible'] else '⚠️ converter'
            cauda = ' · aparar >1024 samp.' if f.get('over_1024') else ''
            linhas.append(
                f'| `{f["file"].split("/", 1)[1]}` | {f["rate"]} | {f["bits"]} | '
                f'{f["duration_ms"]} ms | {comp}{cauda} |'
            )
        linhas.append('')
        linhas.append(
            f'> Variações de microfone individuais: {n_mics} arquivos (ver `data/ir-library.json`).'
        )
        linhas.append('')
        linhas.append(
            '> 💡 Packs com pastas 44.1/48/96 kHz: **use sempre a pasta 44.1 kHz** — as outras'
        )
        linhas.append('> são as mesmas capturas em outra taxa (a GP-100 exige 44.1 kHz).')
        linhas.append('')

    linhas += [
        '## 🔌 Como carregar uma IR local na GP-100',
        '',
        '1. Conecte a pedaleira e abra o **GP-100 Edits**.',
        '2. Menu **IR Manager / User IR**: escolha o **slot (1–20)** e carregue o `.wav`.',
        '3. O slot passa a existir como cabine **“User IR n”** dentro do bloco CAB.',
        '4. No patch: bloco CAB → navegue até `User IR n` → ajuste **Low Cut / High Cut / Level**.',
        '5. Exporte/importe patches normalmente — o `.prst` fica associado ao slot.',
        '',
        '> ⚠️ Regra dos agentes: `.prst` gerado pelo codec do pacote usa CAB de fábrica',
        '> (formato single validado). Para patch com User IR, use a variante experimental',
        '> `<NOME>-USERIR.prst` gerada com `build_song_patches.py --with-user-ir` — a captura',
        '> e o slot vêm do `ir_local` do defs (issue #10). Teste na pedaleira antes de adotar.',
        '',
        '## 🌍 Packs gratuitos para ampliar a biblioteca',
        '',
        'Ver seção ao final deste catálogo em cada rodada — mantida pelo agente `gp100-ir-research`.',
    ]
    return '\n'.join(linhas)
