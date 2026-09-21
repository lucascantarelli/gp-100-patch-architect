#!/usr/bin/env python3
"""
render_manual_page.py — Renderiza páginas do manual.pdf sob demanda.

O manual.pdf é digitalizado (imagens): a leitura pelo agente usa as páginas
renderizadas em manual_pages/. Após a limpeza do projeto, a pasta não fica
mais pre-renderizada (34 MB de PNG/JPG); as páginas são geradas aqui só
quando uma dúvida pontual precisar da imagem original.

Uso:
    python tools/render_manual_page.py 23              # página IMPRESSA 23 (+2 do PDF)
    python tools/render_manual_page.py 23 24 25        # várias páginas impressas
    python tools/render_manual_page.py --all           # re-renderiza o manual inteiro

Saídas por página (o arquivo usa a numeração do PDF):
    manual_pages/pNN.png          — alta resolução (zoom 2.0), leitura pelo agente
    manual_pages/preview/pNN.jpg  — versão leve (~900 px) para consulta rápida

MAPEAMENTO: página impressa NN = página do PDF NN+2 (p23.jpg = impressa 21).
Dependência: pymupdf (`python -m pip install --user pymupdf`).
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 → UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import pymupdf
except ImportError:  # nome antigo da mesma biblioteca
    import fitz as pymupdf

ROOT = Path(__file__).parent.parent
PDF = ROOT / 'manual.pdf'
OUT = ROOT / 'manual_pages'
PREVIEW = OUT / 'preview'

ZOOM_ALTA = 2.0        # PNG para leitura detalhada
PREVIEW_LARGURA = 900  # JPG de consulta rápida


def render(page_num: int) -> tuple[Path, Path]:
    """Renderiza a página page_num (1-based do PDF) em PNG alta + JPG leve.

    Devolve os caminhos (png, jpg) gerados.
    """
    doc = pymupdf.open(PDF)
    if not 1 <= page_num <= doc.page_count:
        raise SystemExit(f'Página {page_num} fora do intervalo (1..{doc.page_count}).')
    page = doc[page_num - 1]
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_ALTA, ZOOM_ALTA))
    png = OUT / f'p{page_num:02d}.png'
    pix.save(png)

    escala = PREVIEW_LARGURA / pix.width
    prev = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_ALTA * escala, ZOOM_ALTA * escala))
    jpg = PREVIEW / f'p{page_num:02d}.jpg'
    prev.save(jpg)
    doc.close()
    return png, jpg


def main():
    """Converte páginas impressas (argv) em páginas do PDF (+2) e renderiza.

    Com --all, re-renderiza o manual inteiro (comportamento da época em que
    a pasta manual_pages/ ficava pre-renderizada no repositório).
    """
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not args:
        print(__doc__)
        sys.exit(1)

    doc = pymupdf.open(PDF)
    total = doc.page_count
    doc.close()

    if '--all' in sys.argv:
        nums = range(1, total + 1)
    else:
        nums = [int(a) + 2 for a in args]  # impressa → página do PDF

    for n in nums:
        png, jpg = render(n)
        print(f'✅ PDF p{n:02d} → {png.relative_to(ROOT)} + {jpg.relative_to(ROOT)}')

    if '--all' not in sys.argv:
        impressas = ', '.join(f'{int(a)}' for a in args)
        print(f'\n💡 Página impressa = arquivo p(NN+2). Renderizadas: {impressas}.')


if __name__ == '__main__':
    main()
