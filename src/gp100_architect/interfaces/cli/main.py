"""CLI oficial — a porta de entrada única do projeto (issues #48/#49).

Regra do adaptador: **nenhuma regra vive aqui**. O comando monta o caminho,
chama o caso de uso (`application/`) e traduz o resultado em texto, código de
saída e cor. É o que permite a API da 2.1 expor exatamente o mesmo
comportamento.

## Comandos

Consulta (#48): `find` · `show` · `diff` · `export` — sobre
`application.consulta`. Produção (#49): `build` · `verify` · `setlist` ·
`release` — sobre `application.setlist`/`release` e o pipeline do guarda
(`application.pipeline`, in-process desde a #33). Utilidades: `version` ·
`validate` · `analyze` · `manual-page` · `changelog`.

## Para agentes

Saídas `--json` com shape estável (contrato): `find`, `show`, `diff` e
`setlist --json`. Códigos de saída documentados; `build --quiet` devolve só
exit code + linha final. Consumo previsto: `gp100-patch-validator` (show
--json para o mecânico), `gp100-ab-tester` (diff), `gp100-setlist`
(setlist --json), `gp100-patch-architect` (build/verify).

Códigos de saída (contrato para automação):
    0  sucesso
    1  entrada inválida (defs quebrado, patch inexistente, versão inválida)
    2  erro de uso da CLI (o próprio Typer emite)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, TextIO

import typer
from rich.console import Console

from gp100_architect import __version__
from gp100_architect.application import consulta
from gp100_architect.application import release as release_app
from gp100_architect.application import setlist as setlist_app
from gp100_architect.application.setlist import trocas_totais
from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.errors import Gp100Error
from gp100_architect.infrastructure.defs import DEFS_PADRAO, carregar_e_validar

app = typer.Typer(
    name='gp100',
    help='Biblioteca de patches da Valeton GP-100: consulta, produção e release.',
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode='rich',
)
console = Console()
err_console = Console(stderr=True)


def _tolerante_a_encoding(stream: TextIO) -> None:
    """Um caractere que o console não escreve não pode virar traceback.

    No console legado do Windows (cp1252) um emoji de relatório derruba o
    comando com `UnicodeEncodeError` — e o usuário vê stack trace em vez de
    diagnóstico. Aqui a codificação falha para 'replace': acento (que o cp1252
    escreve) continua legível e o ideograma vira '?'. O CI e os testes usam
    stream de texto puro, que não tem `reconfigure` — por isso o getattr.
    """
    reconfigure = getattr(stream, 'reconfigure', None)
    if callable(reconfigure):
        reconfigure(errors='replace')


_tolerante_a_encoding(sys.stdout)
_tolerante_a_encoding(sys.stderr)


def _versao(valor: bool) -> None:
    """`--version` responde e sai antes de qualquer outro trabalho."""
    if valor:
        console.print(f'gp100-patch-architect {__version__}')
        raise typer.Exit()


@app.callback()
def principal(
    version: bool = typer.Option(
        False,
        '--version',
        '-V',
        callback=_versao,
        is_eager=True,
        help='Mostra a versão instalada e sai.',
    ),
) -> None:
    """Ferramentas oficiais da biblioteca GP-100."""


@app.command()
def version() -> None:
    """Mostra a versão instalada."""
    console.print(__version__)


@app.command()
def validate(
    defs_caminho: Path | None = typer.Argument(
        None,
        help='Caminho do diretório de fragmentos do defs (padrão: data/defs).',
    ),
) -> None:
    """Valida o defs e sai com 0 (válido) ou 1 (problemas acionáveis)."""
    try:
        dados = carregar_e_validar(defs_caminho)
    except Gp100Error as erro:
        err_console.print(str(erro))
        raise typer.Exit(code=1) from erro
    songs = dados.get('songs') or []
    patches = sum(len(s.get('patches') or []) for s in songs)
    # Texto sem ideograma de propósito: a saída da CLI tem de ser escrevível em
    # qualquer console que o projeto suporta (há teste para isso).
    origem = defs_caminho or DEFS_PADRAO
    console.print(
        f'[green]{Path(origem).name} válido[/green] — '
        f'{len(songs)} músicas, {patches} patches, {len(dados.get("albums") or {})} álbuns'
    )


# ── contexto compartilhado: o defs validado, uma vez por comando ───────────


def _defs() -> dict[str, Any]:
    """Defs validado — erro previsto vira saída acionável (código 1)."""
    try:
        return carregar_e_validar()
    except Gp100Error as erro:
        err_console.print(str(erro))
        raise typer.Exit(code=1) from erro


def _raiz() -> Path:
    """Raiz do repositório (código do pacote roda de qualquer cwd)."""
    return Path(__file__).resolve().parents[4]


def _erro(erro: Gp100Error) -> typer.Exit:
    """Traduz erro de domínio em saída acionável (código 1)."""
    err_console.print(str(erro))
    return typer.Exit(code=1)


# ── consulta (#48) ──────────────────────────────────────────────────────────


@app.command()
def find(
    termo: str = typer.Argument(..., help='Música, artista, álbum, captador, camada ou nome.'),
    saida_json: bool = typer.Option(False, '--json', help='Saída em JSON (shape estável).'),
) -> None:
    """Busca patches por música, artista, álbum, captador, camada ou nome."""
    defs = _defs()
    try:
        achados = consulta.buscar(defs, termo, raiz=_raiz())
    except Gp100Error as erro:
        _erro(erro)
    if saida_json:
        console.print_json(json.dumps([a.__dict__ for a in achados], ensure_ascii=False))
        raise typer.Exit(code=0 if achados else 1)
    atual = None
    for a in achados:
        if a.album != atual:
            atual = a.album
            console.print(f'\n[bold]{a.banda} — {a.album}[/bold]')
        console.print(
            f'  {a.slot}  {a.nome:<9} {a.musica:<40} {a.camada:<22} captador: {a.captador}'
        )
        console.print(f'           {a.arquivo}')
    if achados:
        console.print(f"\n{len(achados)} patch(es) para '{termo}'")
    else:
        console.print(
            f"nada encontrado para '{termo}' — tente música, banda, álbum, "
            'captador (bridge/neck) ou nome'
        )
        raise typer.Exit(code=1)


@app.command()
def show(
    nome: str = typer.Argument(..., help='Nome do patch (ex.: SMOO1SO).'),
    saida_json: bool = typer.Option(False, '--json', help='Saída em JSON (shape estável).'),
) -> None:
    """Resumo completo de um patch: cadeia, parâmetros, momentos, stomps, IR."""
    defs = _defs()
    try:
        d = consulta.dossie(defs, nome, raiz=_raiz())
    except Gp100Error as erro:
        _erro(erro)
    if saida_json:
        console.print_json(json.dumps(d.__dict__, ensure_ascii=False, default=str))
        raise typer.Exit()
    console.print(f'\n🎛️  {d.nome} ({d.slot}) — {d.musica} · {d.banda} ({d.ano})')
    console.print(f'   {d.camada}')
    console.print(f'   🎸 Captador: {d.captador} · Receita: {d.receita}')
    console.print(f'\n   Cadeia: {d.cadeia}')
    console.print('\n   Parâmetros (módulos ligados):')
    for mod, modelo, pares in d.parametros:
        console.print(f'     {mod:<4} {modelo}: {pares}')
    if d.momentos:
        console.print(f'\n   Momentos de toggle ({len(d.momentos)}):')
        for mom in d.momentos:
            mods = ', '.join(f'{a}→{b}' for a, b in mom.get('mods', []))
            console.print(f'     • {mom["nome"]} [{mods}]: {mom["quando"]}')
    if d.stomps:
        console.print(f'\n   Stomps (FS-A/FS-B) ({len(d.stomps)}):')
        for st in d.stomps:
            mods = ', '.join(f'{a}→{b}' for a, b in st.get('mods', []))
            console.print(f'     • FS-{st["fs"]}: {mods} — {st.get("quando", "")}')
    if d.ajustes:
        console.print('\n   Ajustes finos deste patch:')
        for a in d.ajustes:
            console.print(f'     • {a}')
    if d.exp1:
        console.print(
            f'\n   🎚️ EXP1: {d.exp1.get("param")} do {d.exp1.get("módulo")} '
            f'({d.exp1.get("min", 0)} → {d.exp1.get("max", 99)})'
        )
    console.print(f'\n   📡 IR: {d.ir}')
    console.print(f'   📁 {d.arquivo}')
    console.print(f'   📄 {Path(d.pasta) / "patch.md"}')


@app.command()
def diff(
    a: str = typer.Argument(..., help='Patch A (base da comparação).'),
    b: str = typer.Argument(..., help='Patch B (comparado).'),
    saida_json: bool = typer.Option(False, '--json', help='Saída em JSON (shape estável).'),
) -> None:
    """Diff legível entre dois patches, por nome oficial de parâmetro."""
    defs = _defs()
    try:
        d = consulta.diferencas(defs, a, b, raiz=_raiz())
    except Gp100Error as erro:
        _erro(erro)
    if saida_json:
        console.print_json(json.dumps(d, ensure_ascii=False))
        raise typer.Exit()
    console.print(f'\ndiff {d["a"]} → {d["b"]}\n')
    for linha in d['linhas']:
        console.print(linha)
    console.print(
        f'\n  momentos: {d["momentos"][0]} → {d["momentos"][1]} · '
        f'ajustes: {d["ajustes"][0]} → {d["ajustes"][1]}'
    )


@app.command()
def export(
    nomes_patch: list[str] = typer.Argument(None, help='Nomes de patch (opcional).'),
    album: str = typer.Option(
        None, '--album', help='Exporta um álbum inteiro (id: AR/ZP/PMH/PL/WM/SN).'
    ),
    destino: Path = typer.Option(
        None, '--destino', help='Pasta destino (default: dist/importacao-gp100).'
    ),
    listar: bool = typer.Option(False, '--listar', help='Só lista, não copia.'),
) -> None:
    """Copia .prst para a pasta de importação USB, em ordem de slot."""
    defs = _defs()
    try:
        plano = consulta.planejar_exportacao(
            defs,
            raiz=_raiz(),
            nomes_patch=list(nomes_patch or []),
            album=album,
            destino=destino,
            listar=listar,
        )
    except Gp100Error as erro:
        _erro(erro)
    from gp100_architect.application.biblioteca import slots as _slots

    smap = _slots(defs)
    if plano.listar:
        for origem, _dst in plano.itens:
            nome = origem.stem
            slot = smap.get(nome, '??')
            console.print(f'  {slot}  {nome:<9}')
        console.print(f'\n{len(plano.itens)} arquivo(s) — destino seria: {plano.destino}')
        raise typer.Exit()
    n = consulta.executar_exportacao(plano)
    console.print(
        f'✅ {n} .prst copiado(s) para {plano.destino} (prefixo = slot, ordem pronta para importar)'
    )


# ── produção (#49; pipeline in-process desde a #33) ─────────────────────────

# Ordem do guarda de determinismo (TestH): indexa IRs → gera os derivados →
# índices. Os nomes são os passos de `application.pipeline` (pipeline in-process
# desde a #33 — não há mais caminho de script).
PIPELINE = (
    'ir_library',
    'patches',
    'indices',
)


def _rodar(passos: tuple[str, ...], titulo: str, quiet: bool, com_variantes: bool) -> int:
    """Executa o pipeline in-process na raiz do repositório; para no primeiro erro."""
    if not quiet:
        console.print(f'\n▶ {titulo}')
    from gp100_architect.application import pipeline

    if quiet:
        # sem relatório passo a passo: só a linha final (contrato do agente)
        from io import StringIO

        buffer = StringIO()
        codigo = pipeline.executar(_raiz(), passos=passos, com_variante=com_variantes, out=buffer)
        if codigo != 0:
            trecho = buffer.getvalue().strip().splitlines()[-1:]  # última linha é a causa
            err_console.print(trecho[0] if trecho else f'falhou (código {codigo})')
            return codigo
        return 0
    codigo = pipeline.executar(_raiz(), passos=passos, com_variante=com_variantes)
    if codigo != 0:
        console.print(f'\n✗ falhou (código {codigo}) — corrija e rode de novo')
        return codigo
    console.print(f'\n✅ {titulo} concluído')
    return 0


@app.command()
def build(
    quiet: bool = typer.Option(
        False, '--quiet', '-q', help='Só exit code + linha final (para agentes).'
    ),
    with_user_ir: bool = typer.Option(
        False,
        '--with-user-ir',
        help='Gera também a variante experimental <NOME>-USERIR.prst dos patches '
        'com captura no ir_local (issue #10).',
    ),
) -> None:
    """Roda o pipeline completo na ordem do guarda de determinismo (TestH)."""
    codigo = _rodar(
        PIPELINE, 'pipeline completo (ordem do guarda de sincronia)', quiet, with_user_ir
    )
    if quiet and codigo == 0:
        console.print('build ok')
    raise typer.Exit(code=codigo)


@app.command()
def analyze(
    arquivo: Path = typer.Argument(..., help='Export .prst (single ou "all") a dissecar.'),
    saida_json: Path = typer.Option(
        None, '--json', help='Salva o dump completo (info, IRs, patches) no arquivo.'
    ),
) -> None:
    """Disseca um export .prst: modelos, códigos e estatísticas de params."""
    from collections import defaultdict

    from gp100_architect.domain.errors import FormatoPrstInvalido
    from gp100_architect.infrastructure.prst.reader import analyze, fmt_stat, parse

    ORDEM_CADEIA = list(CHAIN)  # seções na ordem da cadeia (PRE → RVB)
    try:
        info, irs, patches = parse(str(arquivo))
    except FormatoPrstInvalido as erro:
        _erro(erro)
    models, param_stats = analyze(patches)

    console.print(
        f'== preset_info: software={info.get("software")} firmware={info.get("firmware")} '
        f'product={info.get("product")} count={info.get("count")}'
    )
    console.print(f'== User IRs: {len(irs)} slots')

    by_module: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for (modulo, nome), dados in sorted(models.items()):
        by_module[modulo].append((nome, dados))
    for modulo in ORDEM_CADEIA:
        console.print(f'\n=== {modulo} ({len(by_module[modulo])} modelos) ===')
        for nome, dados in by_module[modulo]:
            codes = ','.join(sorted(dados['codes']))
            console.print(
                f'  {nome:24s} code={codes:12s} usado_em={dados["count"]:3d} x={sorted(dados["x"])}'
            )
            console.print(fmt_stat(param_stats[(modulo, nome)]))

    console.print(f'\n=== CATALOGO ({len(patches)} patches) ===')
    for p in patches:
        cadeia = ' '.join(f'{e["module"]}:{e["name"]}({e["state"]})' for e in p['effects'])
        console.print(
            f'  #{int(p["id"]) + 1:03d} [{p["type"]}] {p["name"]} bpm={p["bpm"]} '
            f'vol={p["volume"]} ir={p["ir_num"]}\n      {cadeia}'
        )

    if saida_json:
        dump = {'info': info, 'user_irs': irs, 'patches': patches}
        saida_json.parent.mkdir(parents=True, exist_ok=True)
        saida_json.write_text(json.dumps(dump, ensure_ascii=False, indent=1), encoding='utf-8')
        console.print(f'\nJSON salvo em {saida_json}')


@app.command()
def manual_page(
    paginas: list[int] = typer.Argument(None, help='Páginas IMPRESSAS do manual.pdf.'),
    todas: bool = typer.Option(False, '--all', help='Re-renderiza o manual inteiro.'),
) -> None:
    """Renderiza páginas do manual.pdf sob demanda (requer pymupdf)."""
    try:
        import pymupdf  # type: ignore[import-not-found]
    except ImportError as exc:
        err_console.print(
            'pymupdf não instalado — rode: uv tool install pymupdf (ou pip install --user pymupdf).'
        )
        raise typer.Exit(code=1) from exc
    raiz = _raiz()
    pdf = raiz / 'manual.pdf'
    if not pdf.exists():
        err_console.print(f'manual.pdf não encontrado em {pdf}')
        raise typer.Exit(code=1)
    out_dir = raiz / 'manual_pages'
    preview = out_dir / 'preview'
    doc = pymupdf.open(pdf)
    total = doc.page_count
    if todas:
        nums: list[int] = list(range(1, total + 1))
    elif not paginas:
        err_console.print('informe as páginas impressas (ex.: gp100 manual-page 21) ou --all')
        raise typer.Exit(code=2)
    else:
        nums = [n + 2 for n in paginas]  # impressa → página do PDF (mapa da casa)
    doc.close()
    ZOOM_ALTA = 2.0
    PREVIEW_LARGURA = 900
    for n in nums:
        if not 1 <= n <= total:
            err_console.print(f'Página {n} fora do intervalo (1..{total}).')
            raise typer.Exit(code=1)
        d = pymupdf.open(pdf)
        page = d[n - 1]
        out_dir.mkdir(parents=True, exist_ok=True)
        preview.mkdir(parents=True, exist_ok=True)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_ALTA, ZOOM_ALTA))
        png = out_dir / f'p{n:02d}.png'
        pix.save(png)
        escala = PREVIEW_LARGURA / pix.width
        prev = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM_ALTA * escala, ZOOM_ALTA * escala))
        jpg = preview / f'p{n:02d}.jpg'
        prev.save(jpg)
        d.close()
        console.print(f'✅ PDF p{n:02d} → manual_pages/p{n:02d}.png + preview/p{n:02d}.jpg')
    if not todas:
        impressas = ', '.join(str(n) for n in paginas or [])
        console.print(f'\n💡 Página impressa = arquivo p(NN+2). Renderizadas: {impressas}.')


@app.command()
def verify(
    quiet: bool = typer.Option(False, '--quiet', '-q', help='Só exit code + linha final.'),
) -> None:
    """Roda a suíte de testes — a mesma do CI (`uv run pytest -q`)."""
    if not quiet:
        console.print('\n▶ suíte de testes (a mesma do CI)')
    r = subprocess.run([sys.executable, '-m', 'pytest', '-q'], cwd=_raiz())
    if r.returncode != 0 and quiet:
        err_console.print('suíte reprovou — rode: uv run pytest -q (o relatório diz onde)')
    elif r.returncode == 0 and quiet:
        console.print('verify ok')
    raise typer.Exit(code=r.returncode)


@app.command()
def setlist(
    musicas: list[str] = typer.Argument(
        None, help='Músicas (nome ou id) e/ou seções (MUSICA:SUFIXO ou nome do patch).'
    ),
    patch: list[str] = typer.Option(
        None, '--patch', help='Força o patch de uma música (repita a flag; aceita SMOO1:SO).'
    ),
    keep_order: bool = typer.Option(
        False, '--keep-order', help='Respeita a ordem dada (não otimiza por trocas).'
    ),
    titulo: str = typer.Option('Cola de palco', '--title', help='Título do relatório.'),
    listar: bool = typer.Option(False, '--list', help='Lista músicas e patches.'),
    saida_json: bool = typer.Option(False, '--json', help='Saída em JSON (shape estável).'),
    out: Path = typer.Option(None, '--out', help='Grava o relatório em arquivo.'),
) -> None:
    """Cola de palco: ordem de slots que minimiza trocas de módulo."""
    defs = _defs()
    lib = setlist_app.BibliotecaSetlist(defs)
    if listar:
        for sid, musica, album, patches in lib.catalogo():
            console.print(f'{sid:9} | {musica:38} | {album:32} | {patches}')
        raise typer.Exit()
    if not musicas:
        err_console.print('informe o repertório (ex.: "Come Together" "Money") ou --list')
        raise typer.Exit(code=2)
    try:
        # resolver_repertorio já devolve o plano final: otimizado (vizinho mais
        # próximo, regra do domínio #28) ou na ordem dada com --keep-order
        plano = setlist_app.resolver_repertorio(lib, list(musicas), list(patch or []), keep_order)
    except Gp100Error as erro:
        _erro(erro)
    total = trocas_totais(plano)
    if saida_json:
        conteudo = json.dumps(
            setlist_app.plano_json(plano, total, lib.slots), ensure_ascii=False, indent=1
        )
    else:
        conteudo = setlist_app.plano_markdown(plano, total, lib.slots, titulo)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(conteudo + '\n', encoding='utf-8')
        console.print(f'✅ {out}')
    else:
        console.print(conteudo)


@app.command()
def changelog(
    versao: str | None = typer.Option(
        None, '--version', help='Versão da seção (default: bump sugerido).'
    ),
    escrever: bool = typer.Option(False, '--write', help='Prepende a seção no CHANGELOG.md.'),
    destino: Path = typer.Option(None, '--out', help='Grava a seção neste arquivo.'),
    tudo: bool = typer.Option(False, '--all', help='Inclui tipos ocultos (refactor, ci…).'),
) -> None:
    """Seção do CHANGELOG derivada dos commits (Conventional Commits)."""
    from gp100_architect.application import changelog as changelog_app

    raiz = _raiz()
    itens = changelog_app.coletar(changelog_app.ultima_tag(raiz), raiz=raiz)
    if versao is None:
        versao = changelog_app.bump_sugerido(itens, changelog_app.ler_versao_atual(raiz))
    elif not release_app.SEMVER_RE.match(versao):
        err_console.print(f"Versão inválida: '{versao}' — use SemVer (ex.: 1.1.0).")
        raise typer.Exit(code=1)
    bloco = changelog_app.secao(versao, itens, tudo)
    if escrever:
        changelog_app.escrever_no_changelog(bloco, versao, raiz / 'CHANGELOG.md')
        console.print(
            f'✅ CHANGELOG.md: seção [{versao}] prependida '
            f'({len(itens)} commit(s) desde {changelog_app.ultima_tag(raiz) or "o início"}).'
        )
    elif destino:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(bloco, encoding='utf-8')
        console.print(f'✅ {destino}')
    else:
        console.print(bloco)
        tag = changelog_app.ultima_tag(raiz) or 'o início da história'
        bump = changelog_app.bump_sugerido(itens, changelog_app.ler_versao_atual(raiz))
        console.print(f'--- {len(itens)} commit(s) desde {tag} · bump sugerido: v{bump}')


@app.command()
def release(
    versao: str = typer.Argument(None, help='Versão SemVer (default: lê VERSION).'),
    destino: Path = typer.Option(None, '--destino', help='Pasta de saída (default: dist/).'),
) -> None:
    """Empacota os ZIPs (completo + por álbum) e as notas da release em dist/."""
    defs = _defs()
    raiz = _raiz()
    try:
        version = release_app.validar_versao(versao) if versao else release_app.ler_versao(raiz)
        relatorio = release_app.package(
            version,
            defs=defs,
            patches_dir=raiz / 'patches',
            destino=destino or (raiz / 'dist'),
        )
    except Gp100Error as erro:
        _erro(erro)
    console.print(f'🚀 Empacotando v{version}:')
    console.print(f'  📦 {relatorio["completo"].name}: {relatorio["total"]} patches (com patch.md)')
    for alvo, n in relatorio['zips']:
        console.print(f'  📦 {alvo.name}: {n} patches')
    console.print(f'  📝 {relatorio["notas"].name}')
    console.print('✅ Pacotes em dist/ (não versionar — o CI publica na Release).')


@app.command()
def site(
    destino: Path = typer.Option(None, '--destino', help='Pasta de saída (default: dist/site).'),
    base_url: str = typer.Option(
        None, '--base-url', help='Prefixo de URL do Pages (default: /gp-100-patch-architect/).'
    ),
) -> None:
    """Gera o site estático da biblioteca (busca client-side, sem backend)."""
    from gp100_architect.application import site as site_app
    from gp100_architect.infrastructure.escrita import escrever_texto

    raiz = _raiz()
    destino = destino or (raiz / 'dist' / 'site')
    paginas = site_app.gerar_site(_defs(), base_url=base_url or site_app.BASE_URL_PADRAO)
    for relativo, conteudo in sorted(paginas.items()):
        escrever_texto(destino / relativo, conteudo)
    json_kb = len(paginas['busca.json'].encode('utf-8')) / 1024
    console.print(
        f'🌐 {len(paginas)} arquivo(s) em {destino} '
        f'({len(paginas) - 3} páginas de patch/álbum) · busca.json: {json_kb:.1f} KB'
    )
    console.print('✅ Site gerado (derivado do defs — publicável no Pages).')


@app.command()
def badges(
    destino: Path = typer.Option(None, '--destino', help='Pasta de saída (default: <raiz>/site).'),
) -> None:
    """Gera os badges derivados do repo (badges/*.json, formato endpoint do shields.io)."""
    from gp100_architect.application import badges as badges_app
    from gp100_architect.infrastructure.escrita import escrever_texto

    destino = destino or (_raiz() / 'site')
    arquivos = badges_app.gerar_badges(_defs())
    for relativo, conteudo in sorted(arquivos.items()):
        escrever_texto(destino / relativo, conteudo)
    console.print(
        f'🏷️ {len(arquivos)} badge(s) derivados em {destino / "badges"} '
        '(release, agentes, skills, patches, python, cobertura, testes).'
    )
    console.print('✅ Badges gerados (dado derivado não se edita; se regenera).')


if __name__ == '__main__':  # python -m gp100_architect.interfaces.cli.main
    app()
