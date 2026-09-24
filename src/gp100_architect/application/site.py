"""Site estático da biblioteca — mesma fonte do defs, sem backend (issue #11).

Pilar C do roadmap v2 (`reference/19-roadmap-v2.md` §5): página por álbum e por
patch (cadeia, parâmetros com nome oficial, ajustes, momentos/stomps, seção 📡)
e busca client-side por música/artista/álbum/captador sobre um índice JSON
**minúsculo** — os nomes, não o conteúdo. Sem dependência: HTML e JS nascem de
templates de string aqui e o índice carrega via `fetch` num `<script>` inline.

Fonte de dado: **só o defs** (`carregar_e_validar`) + `slots` — exatamente o
que `indices.build_all` e `consulta.dossie` consomem. O site é derivado como o
`patch.md` e o índice: quem edita a biblioteca edita o defs e roda
`gp100 build` (+ `gp100 site`, se for publicar).

Contrato da camada: devolve `{caminho_relativo: conteúdo_em_memória}` e nunca
escreve no disco — quem grava é o comando da CLI via `infrastructure.escrita`
(e o teste roda a geração inteira sem tmpdir).

O Pilar C previa um `tools/gen_site.py` autônomo; a migração da #33 extinguiu
os scripts e o gerador nasce já no pacote, como caso de uso da aplicação.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from html import escape
from pathlib import Path
from typing import Any

from gp100_architect.application.biblioteca import slots
from gp100_architect.application.consulta import rotulo_param
from gp100_architect.application.nomes import album_pasta, song_display
from gp100_architect.domain.chain import CHAIN

__all__ = ['gerar_site']

BASE_URL_PADRAO = '/gp-100-patch-architect/'


def _url_patch(nome: str) -> str:
    """Caminho relativo da página do patch (nome é seguro: ≤ 12 chars, [A-Z0-9])."""
    return f'patch/{nome}.html'


def _url_album(chave: str) -> str:
    return f'album/{chave}.html'


def _titulo_album(album: dict[str, Any]) -> str:
    """Título de exibição do álbum (`display`, com fallbacks derivados)."""
    return str(album.get('display') or f'{album["album"]} ({album.get("ano", "")})')


def _titulo_song(song: dict[str, Any]) -> str:
    """Título de exibição da música (mesma regra das tabelas do mapa)."""
    return song_display(song)


def _tabela_parametros(spec: dict[str, Any]) -> str:
    """Tabela de parâmetros dos módulos ligados, com nome oficial (nunca `pN`)."""
    linhas: list[str] = []
    for mod in CHAIN:
        m = spec['modules'].get(mod)
        if not m or not m.get('on') or not m.get('params'):
            continue
        pares = '<br>'.join(
            f'<code>{escape(rotulo_param(mod, m["name"], int(k)))}</code> = {escape(str(v))}'
            for k, v in sorted(m['params'].items(), key=lambda i: int(i[0]))
        )
        estado = '' if m.get('on') else ' (off)'
        linhas.append(
            f'<tr><th>{escape(mod)}{estado}</th><td>{escape(str(m["name"]))}</td>'
            f'<td>{pares}</td></tr>'
        )
    if not linhas:
        return '<p class="vazio">Sem parâmetros setados.</p>'
    return (
        '<table><thead><tr><th>Módulo</th><th>Modelo</th><th>Parâmetros</th></tr>'
        '</thead><tbody>' + ''.join(linhas) + '</tbody></table>'
    )


def _lista(titulos: tuple[str, ...], itens: list[Any], fmt: Callable[[Any], str]) -> str:
    """Seção opcional: some quando não há itens (páginas enxutas)."""
    if not itens:
        return ''
    corpo = ''.join(f'<li>{escape(str(fmt(item)))}</li>' for item in itens)
    return f'<h2>{titulos[0]}</h2><ul>{corpo}</ul>'


def _momentos(momentos: list[dict[str, Any]]) -> str:
    if not momentos:
        return ''
    linhas = ''.join(
        f'<tr><td>{escape(str(m.get("nome", "")))}</td>'
        f'<td>{escape(str(m.get("modulo", "")))}</td>'
        f'<td>{escape(str(m.get("para", m.get("estado", ""))))}</td></tr>'
        for m in momentos
    )
    return (
        '<h2>Momentos (toggle ao vivo)</h2><table><thead><tr><th>Nome</th>'
        '<th>Módulo</th><th>Para</th></tr></thead><tbody>' + linhas + '</tbody></table>'
    )


def _stomps(stomps: list[dict[str, Any]]) -> str:
    if not stomps:
        return ''
    linhas = ''.join(
        f'<tr><td>{escape(str(s.get("nome", "")))}</td>'
        f'<td>{escape(str(s.get("liga", "")))}</td>'
        f'<td>{escape(str(s.get("desliga", "")))}</td></tr>'
        for s in stomps
    )
    return (
        '<h2>Stomps (modo STOMP)</h2><table><thead><tr><th>Nome</th>'
        '<th>Liga</th><th>Desliga</th></tr></thead><tbody>' + linhas + '</tbody></table>'
    )


def _pagina(titulo: str, corpo: str, voltas: list[tuple[str, str]]) -> str:
    """Página inteira — o CSS é o mesmo para todas (uma cópia, no index)."""
    nav = ' · '.join(f'<a href="{escape(href)}">{escape(rotulo)}</a>' for rotulo, href in voltas)
    return (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{escape(titulo)} — GP-100 Patch Architect</title>\n'
        '<link rel="stylesheet" href="../style.css">\n'
        '</head><body>\n'
        f'<nav>{nav}</nav>\n<main>\n{corpo}\n</main>\n'
        '<footer>gerado por <code>gp100 site</code> — fonte única: data/defs/'
        ' (não edite à mão)</footer>\n</body></html>\n'
    )


def _css() -> str:
    return (
        ':root{color-scheme:light dark}'
        'body{font-family:system-ui,sans-serif;margin:0 auto;max-width:56rem;'
        'padding:0 1rem;line-height:1.5}'
        'nav{padding:.75rem 0;border-bottom:1px solid #8884}'
        'footer{margin:2rem 0 1rem;border-top:1px solid #8884;padding-top:.5rem;'
        'font-size:.85rem;opacity:.75}'
        'table{border-collapse:collapse;width:100%;margin:.5rem 0}'
        'th,td{border:1px solid #8884;padding:.35rem .6rem;text-align:left;'
        'vertical-align:top}'
        'code{font-family:ui-monospace,monospace;font-size:.95em}'
        '.vazio{opacity:.7}'
        '.busca{display:flex;gap:.5rem;margin:1rem 0}'
        '.busca input{flex:1;padding:.5rem .75rem;font-size:1rem}'
        'ul.resultados li{padding:.15rem 0}'
        '.slot{font-family:ui-monospace,monospace;white-space:nowrap}'
    )


def _indice_busca(defs: dict[str, Any]) -> str:
    """O índice minúsculo: só nomes que a busca filtra, nunca o conteúdo."""
    mapa = slots(defs)
    itens: list[dict[str, str]] = []
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]
        for patch in song['patches']:
            itens.append(
                {
                    'slot': mapa[patch['nome']],
                    'nome': patch['nome'],
                    'musica': _titulo_song(song),
                    'album': _titulo_album(album),
                    'banda': album['banda'],
                    'camada': patch.get('camada', ''),
                    'captador': (patch.get('doc', {}).get('guitarra', {}) or {}).get(
                        'seletorCurto', ''
                    ),
                }
            )
    return json.dumps(itens, ensure_ascii=False, separators=(',', ':'))


def _script_busca() -> str:
    """Busca client-side: filtra o índice no navegador, sem dependência."""
    return (
        'fetch("busca.json")'
        '.then(r=>r.json()).then(itens=>{'
        'const inp=document.querySelector("#q"),ul=document.querySelector("#r");'
        'const norm=s=>s.toLowerCase();'
        'function render(){'
        'const q=norm(inp.value.trim());'
        'if(!q){ul.innerHTML="";return}'
        'const partes=q.split(/\\s+/).filter(Boolean);'
        'const hits=itens.filter(i=>{'
        'const alvo=norm([i.nome,i.musica,i.album,i.banda,i.camada,i.captador,i.slot].join(" "));'
        'return partes.every(p=>alvo.includes(p))});'
        'ul.innerHTML=hits.slice(0,50).map(i=>'
        '`<li><span class="slot">${i.slot}</span> '
        '<a href="patch/${i.nome}.html">${i.nome}</a> — ${i.musica} '
        '<em>(${i.banda}, ${i.album})</em></li>`).join("");'
        'if(hits.length>50)ul.innerHTML+=`<li>… e mais ${hits.length-50}</li>`}'
        'inp.addEventListener("input",render)})'
    )


def _pagina_index(
    albums: list[tuple[str, dict[str, Any], int, int]],
) -> str:
    """Página raiz: busca + catálogo de álbuns."""
    linhas = ''.join(
        f'<tr><td><a href="{_url_album(chave)}">{_titulo_album(album)}</a></td>'
        f'<td>{escape(album["banda"])}</td><td>{ano}</td><td>{total}</td></tr>'
        for chave, album, ano, total in albums
    )
    corpo = (
        '<h1>Biblioteca de patches — GP-100</h1>'
        '<div class="busca"><input id="q" type="search" '
        'placeholder="Busca por música, artista, álbum, captador ou nome '
        '(ex.: smooth, strat, neck)…" '
        'autocomplete="off" autofocus></div><ul class="resultados" id="r"></ul>'
        '<h2>Álbuns</h2><table><thead><tr><th>Álbum</th><th>Banda</th><th>Ano</th>'
        '<th>Patches</th></tr></thead><tbody>' + linhas + '</tbody></table>'
        '<script>' + _script_busca() + '</script>'
    )
    return _pagina('Biblioteca', corpo, [('Início', 'index.html')])


def _pagina_album(
    chave: str,
    album: dict[str, Any],
    musicas: list[tuple[dict[str, Any], list[tuple[str, str, str]]]],
) -> str:
    """Página do álbum: as músicas e os patches de cada uma."""
    titulo = _titulo_album(album)
    secoes: list[str] = []
    for song, patches in musicas:
        itens = ''.join(
            f'<li><span class="slot">{escape(slot)}</span> '
            f'<a href="{_url_patch(nome)}">{escape(nome)}</a> — {escape(camada)}</li>'
            for slot, nome, camada in patches
        )
        secoes.append(f'<h3>{escape(_titulo_song(song))}</h3><ul>{itens}</ul>')
    corpo = (
        f'<h1>{escape(titulo)}</h1>'
        f'<p>{escape(album["banda"])} · {album.get("ano", "")}</p>' + ''.join(secoes)
    )
    return _pagina(
        titulo,
        corpo,
        [('Início', '../index.html'), (album_pasta(album), '../index.html')],
    )


def _pagina_patch(dados: dict[str, Any]) -> str:
    """Página do patch: o dossiê inteiro, na ordem do patch.md."""
    p = dados
    secoes = [
        f'<h1><span class="slot">{escape(p["slot"])}</span> {escape(p["nome"])}</h1>',
        f'<p><strong>{escape(p["musica"])}</strong> — {escape(p["banda"])} ({p["ano"]}) · '
        f'camada: {escape(p["camada"] or "—")} · captador: {escape(p["captador"] or "—")}</p>',
        f'<h2>Cadeia</h2><p><code>{escape(p["cadeia"])}</code></p>',
        '<h2>Parâmetros</h2>' + _tabela_parametros(p['spec']),
        _lista(('Receita (guitarra)',), [p['receita']] if p['receita'] else [], str),
        _momentos(p['momentos']),
        _stomps(p['stomps']),
        _lista(('Ajustes finos',), p['ajustes'], str),
        f'<h2>📡 IR</h2><p>{escape(p["ir"] or "CAB de fábrica já é o alvo.")}</p>',
        (
            f'<h2>EXP1</h2><p><code>{escape(json.dumps(p["exp1"], ensure_ascii=False))}</code></p>'
            if p.get('exp1')
            else ''
        ),
        (f'<p class="vazio">Fontes na biblioteca: <code>{escape(p["arquivo"])}</code></p>'),
    ]
    return _pagina(
        f'{p["nome"]} — {p["musica"]}',
        ''.join(secoes),
        [('Início', '../index.html'), (p['album'], f'../{_url_album(p["chaveAlbum"])}')],
    )


def gerar_site(defs: dict[str, Any], *, base_url: str = BASE_URL_PADRAO) -> dict[str, str]:
    """Gera o site inteiro em memória: `{caminho_relativo: conteúdo}`.

    Custo: O(defs × tamanho do dossiê) — o mesmo que o `show` faz para um
    patch, feito para todos. Nada aqui toca o disco.
    """
    from gp100_architect.application.consulta import dossie

    raiz_fake = Path()  # dossie só usa `raiz` para caminhos de exibição
    mapa = slots(defs)
    paginas: dict[str, str] = {'style.css': _css()}

    # ── index + índice de busca ───────────────────────────────────────────────
    albums: list[tuple[str, dict[str, Any], int, int]] = []
    por_album: dict[str, list[tuple[dict[str, Any], list[tuple[str, str, str]]]]] = {}
    for song in defs['songs']:
        chave = song['idAlbum']
        album = defs['albums'][chave]
        patches_do_song = [
            (mapa[p['nome']], p['nome'], p.get('camada', '')) for p in song['patches']
        ]
        por_album.setdefault(chave, []).append((song, patches_do_song))
    for chave, musicas in por_album.items():
        album = defs['albums'][chave]
        total = sum(len(p) for _s, p in musicas)
        albums.append((chave, album, album.get('ano', 0), total))
    albums.sort(key=lambda t: (t[2], _titulo_album(t[1])))
    paginas['index.html'] = _pagina_index(albums)
    paginas['busca.json'] = _indice_busca(defs)

    # ── página por álbum ──────────────────────────────────────────────────────
    for chave, musicas in por_album.items():
        album = defs['albums'][chave]
        paginas[_url_album(chave)] = _pagina_album(chave, album, musicas)

    # ── página por patch (o dossiê é a fonte — o `show` e o site nunca divergem)
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]
        for patch in song['patches']:
            d = dossie(defs, patch['nome'], raiz=raiz_fake)
            paginas[_url_patch(patch['nome'])] = _pagina_patch(
                {
                    'slot': d.slot,
                    'nome': d.nome,
                    'musica': d.musica,
                    'banda': d.banda,
                    'ano': d.ano,
                    'camada': d.camada,
                    'captador': d.captador,
                    'receita': d.receita,
                    'cadeia': d.cadeia,
                    'spec': patch['spec'],
                    'momentos': d.momentos,
                    'ajustes': d.ajustes,
                    'stomps': d.stomps,
                    'exp1': d.exp1,
                    'ir': d.ir,
                    'album': _titulo_album(album),
                    'chaveAlbum': song['idAlbum'],
                    'arquivo': d.arquivo,
                }
            )

    # base_url entra como comentário no index (documenta onde o site vive)
    paginas['index.html'] = paginas['index.html'].replace(
        '<nav>', f'<!-- base_url: {escape(base_url)} -->\n<nav>', 1
    )
    return paginas
