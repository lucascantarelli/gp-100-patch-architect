"""check_data_freshness.py — os artefatos GERADOS no disco batem com o commitado?

Metade deste repositório é **saída de script**: `patches/**` (`.prst`, `patch.md`,
`spec.json`, `MAPA-DO-ALBUM.md`), `tools/patches-defs.json` (escrito pelos
seeders), `tools/ir-library.json` e `reference/16-ir-library.md`. Quem acrescenta
música, camada, patch, modelo de efeito, momento de toggle ou pack de IR precisa
rodar o pipeline — este verificador transforma "esqueci de rodar" em falha de
build, com o comando exato de conserto.

O CI roda na ordem: **pipeline primeiro, este check depois**. Logo ele compara
"o que o pipeline produz agora" com "o que está commitado no branch testado":

    python tools/check_data_freshness.py    # 0 = sincronizado · 1 = defasado

Normalização: o `.prst` carrega `preset_info/@time` (epoch ms) que muda a cada
build **de propósito** — imita o export real do GP-100 Edits. É o único atributo
ignorado na comparação: todo o resto é byte-estável (medido em 215 arquivos,
0 drift com o pipeline rodado duas vezes). Fim de linha também é normalizado
(CRLF aqui, LF se outro checkout normalizar).
"""
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent

# ---- o que o pipeline escreve -------------------------------------------------
# patches/: só as extensões geradas (as pastas de IR ficam fora de patches/).
ARTIFACT_SUFFIXES = {'.prst', '.md', '.json'}
ARTIFACT_DIR = 'patches'
ARTIFACT_FILES = (
    'tools/patches-defs.json',     # reescrito pelos seeders (add_*_defs.py)
    'tools/ir-library.json',       # ir_library.py
    'reference/16-ir-library.md',  # ir_library.py
)

# Comandos na ordem real do pipeline (a mesma que o CI executa).
PIPELINE = (
    'python tools/ir_library.py',        # indexa impulse_responses/ (se baixou pack)
    'python tools/add_pulse_defs.py',    # seeders de álbum (já encadeia add_momentos)
    'python tools/add_momentos.py',      # momentos de toggle por patch
    'python tools/build_song_patches.py',  # spec.json + patch.md + .prst
    'python tools/gen_indexes.py',       # MAPA-DO-ALBUM.md + patches/README.md
)

_TIME_RE = re.compile(r'time="\d+"')


def normalize(text):
    """Texto comparável: ignora `preset_info/@time` e normaliza fim de linha."""
    return _TIME_RE.sub('time="T"', text.replace('\r\n', '\n'))


def is_artifact(rel_posix):
    """O caminho é saída do pipeline? (filtra a listagem do HEAD)."""
    if rel_posix in ARTIFACT_FILES:
        return True
    return rel_posix.startswith(f'{ARTIFACT_DIR}/') and Path(rel_posix).suffix in ARTIFACT_SUFFIXES


def on_disk():
    """Artefatos presentes no working tree, como caminhos POSIX relativos."""
    found = {p.relative_to(ROOT).as_posix()
             for p in (ROOT / ARTIFACT_DIR).rglob('*')
             if p.is_file() and p.suffix in ARTIFACT_SUFFIXES}
    found |= {f for f in ARTIFACT_FILES if (ROOT / f).is_file()}
    return found


def in_head():
    """Artefatos versionados no HEAD (nada de índice/staging: HEAD é a verdade)."""
    r = subprocess.run(['git', 'ls-tree', '-r', '-z', '--name-only', 'HEAD'],
                       cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError('git ls-tree falhou — HEAD existe? (repositório sem commit?)')
    tracked = r.stdout.decode('utf-8', 'surrogateescape').split('\0')
    return {t for t in tracked if t and is_artifact(t)}


def blobs_at_head(paths):
    """Conteúdo de vários arquivos no HEAD numa única chamada ao git.

    Devolve {caminho: texto} (caminhos ausentes no HEAD ficam de fora).
    Usa `git cat-file --batch` (um processo só, ~200 arquivos): spawning
    `git show` por arquivo custava ~16 s no Windows.
    """
    if not paths:
        return {}
    entrada = ''.join(f'HEAD:{p}\n' for p in paths).encode('utf-8', 'surrogateescape')
    r = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT, input=entrada,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode('utf-8', 'replace').strip())
    saida, pos, lidos = r.stdout, 0, {}
    for rel in paths:
        fim = saida.index(b'\n', pos)
        cabecalho = saida[pos:fim].decode('utf-8', 'replace')
        pos = fim + 1
        if cabecalho.endswith('missing'):
            continue                       # não existe no HEAD (arquivo novo)
        tamanho = int(cabecalho.rsplit(' ', 1)[1])
        lidos[rel] = saida[pos:pos + tamanho].decode('utf-8', 'replace')
        pos += tamanho + 1                 # +1 = LF que o cat-file anexa
    return lidos


def first_diff(old, new):
    """Descrição curta da primeira linha divergente (para o relatório)."""
    oa, nb = normalize(old).splitlines(), normalize(new).splitlines()
    for i, (a, b) in enumerate(zip(oa, nb), start=1):
        if a != b:
            return f'linha {i}: -{a.strip()[:70]} · +{b.strip()[:70]}'
    return f'{abs(len(oa) - len(nb))} linha(s) a mais/menos'


def main():
    """Compara disco × HEAD e imprime o relatório; exit 1 se houver defasagem."""
    try:
        disco, head = on_disk(), in_head()
    except RuntimeError as exc:
        print(f'⚠️  não consegui ler o HEAD: {exc}', file=sys.stderr)
        return 2
    if not head:
        print('⚠️  nenhum artefato gerado no HEAD — commit inicial?')
        return 2

    commitados = blobs_at_head([r for r in sorted(disco & head)])
    problemas = []
    for rel in sorted(disco | head):
        if rel not in head:
            problemas.append(('novo', rel, 'existe no disco, mas não está commitado'))
            continue
        if rel not in disco:
            problemas.append(('removido', rel, 'está no HEAD, mas não existe no disco'))
            continue
        atual = (ROOT / rel).read_text(encoding='utf-8', errors='replace')
        commitado = commitados.get(rel, '')
        if normalize(atual) != normalize(commitado):
            problemas.append(('diferente', rel, first_diff(commitado, atual)))

    if not problemas:
        print(f'✅ dados em sincronia: {len(head)} artefatos gerados == HEAD '
              f'(ignorando preset_info/@time)')
        return 0

    print(f'❌ {len(problemas)} artefato(s) gerado(s) defasado(s) em relação ao HEAD:\n')
    for tipo, rel, nota in problemas[:20]:
        print(f'  [{tipo:9s}] {rel}\n              {nota}')
    if len(problemas) > 20:
        print(f'  … e {len(problemas) - 20} outro(s)')
    print('\nRode o pipeline inteiro e commite o resultado:\n')
    for cmd in PIPELINE:
        print(f'    {cmd}')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
