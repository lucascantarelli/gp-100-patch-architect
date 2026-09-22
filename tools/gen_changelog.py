"""gen_changelog.py — monta o CHANGELOG.md a partir dos Conventional Commits.

O projeto já padroniza commits (ver CONTRIBUTING.md), então o changelog é
**derivado da história**, não escrito à mão: nada de dois lugares discordando
sobre o que mudou numa versão.

Uso:
  python tools/gen_changelog.py                       # prévia + bump sugerido
  python tools/gen_changelog.py --version 1.1.0       # seção da versão p/ stdout
  python tools/gen_changelog.py --version 1.1.0 --write   # prepende no CHANGELOG.md
  python tools/gen_changelog.py --version 1.1.0 --out dist/notas.md   # seção em arquivo
  python tools/gen_changelog.py --all                 # inclui chore/ci/test (ruído)

Regras:
  - `desde` = última tag `v*` (ou a história inteira, na primeira release).
  - Tipos visíveis: feat, fix, data, docs, perf. Ocultos: chore, ci, test,
    refactor, style, build (aparecem só com `--all`).
  - Rodapé `BREAKING CHANGE:` ou `!` antes dos dois-pontos abre a seção de
    mudanças incompatíveis e força bump MAJOR.
  - Merge commits e os auto-commits do pipeline (`[skip ci]`) são ignorados.

Bump sugerido: breaking → MAJOR · qualquer `feat` → MINOR · senão → PATCH.
"""
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent
CHANGELOG = ROOT / 'CHANGELOG.md'

# tipo -> (título da seção, ordem). Ordem = como aparece no changelog.
SECOES = {
    'feat': ('✨ Funcionalidades', 1),
    'data': ('📊 Dados e patches', 2),
    'fix': ('🐞 Correções', 3),
    'perf': ('⚡ Desempenho', 4),
    'docs': ('📚 Documentação', 5),
    'refactor': ('♻️ Refatoração', 6),
    'test': ('🧪 Testes', 7),
    'ci': ('🤖 CI/CD', 8),
    'build': ('📦 Build', 9),
    'chore': ('🔧 Manutenção', 10),
    'style': ('💅 Estilo', 11),
}
VISIVEIS = {'feat', 'fix', 'data', 'docs', 'perf'}

COMMIT_RE = re.compile(
    r'^(?P<tipo>[a-z]+)(?:\((?P<escopo>[^)]*)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$')
BREAKING_FOOTER = re.compile(r'^BREAKING[ -]CHANGE:\s*(.+)$', re.MULTILINE)
SKIP = re.compile(r'\[skip ci\]', re.IGNORECASE)


def git(*args) -> str:
    """Roda um comando git no repositório e devolve o stdout."""
    r = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} falhou: "
                         f"{r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout.decode('utf-8', 'replace')


def ultima_tag() -> str | None:
    """Tag `v*` mais recente alcançável, ou None (primeira release)."""
    r = subprocess.run(['git', 'describe', '--tags', '--abbrev=0', '--match', 'v[0-9]*'],
                       cwd=ROOT, capture_output=True)
    return r.stdout.decode().strip() or None if r.returncode == 0 else None


def coletar(desde: str | None):
    """[(tipo, escopo, descrição, breaking_note)] desde a tag (inclusive até HEAD)."""
    intervalo = f'{desde}..HEAD' if desde else 'HEAD'
    # Unidade de registro: hash + assunto + corpo, separados por NUL.
    bruto = git('log', intervalo, '--no-merges', '--format=%H%x1f%s%x1f%b%x1e')
    itens = []
    for registro in bruto.split('\x1e'):
        registro = registro.strip('\n')
        if not registro:
            continue
        partes = registro.split('\x1f')
        assunto = partes[1].strip() if len(partes) > 1 else ''
        corpo = partes[2] if len(partes) > 2 else ''
        if not assunto or SKIP.search(assunto):
            continue
        m = COMMIT_RE.match(assunto)
        if not m:
            continue                          # fora do padrão: não entra no changelog
        rodape = BREAKING_FOOTER.search(corpo)
        breaking = bool(m.group('breaking')) or bool(rodape)
        itens.append((
            m.group('tipo'), m.group('escopo') or '',
            m.group('desc').strip(), rodape.group(1).strip() if rodape else '',
            breaking,
        ))
    return itens


def bump_sugerido(itens, atual: str) -> str:
    """MAJOR se breaking, MINOR se houver feat, senão PATCH."""
    major, minor, patch = (int(n) for n in atual.split('.'))
    if any(i[4] for i in itens):
        return f'{major + 1}.0.0'
    if any(i[0] == 'feat' for i in itens):
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


def ler_versao_atual() -> str:
    """Versão de VERSION; '0.0.0' se ausente/ inválida (primeira release)."""
    arquivo = ROOT / 'VERSION'
    if arquivo.exists() and re.match(r'^\d+\.\d+\.\d+$', arquivo.read_text(encoding='utf-8').strip()):
        return arquivo.read_text(encoding='utf-8').strip()
    return '0.0.0'


def secao(version: str, itens, incluir_ocultos: bool) -> str:
    """Seção em Markdown da versão (Keep a Changelog), sem o cabeçalho do arquivo."""
    linhas = [f'## [{version}] — {date.today().isoformat()}', '']
    quebras = [i for i in itens if i[4]]
    if quebras:
        linhas += ['### ⚠️ Mudanças incompatíveis', '']
        for tipo, escopo, desc, nota, _ in quebras:
            esc = f'**{escopo}**: ' if escopo else ''
            linhas.append(f'- {esc}{nota or desc} ({tipo})')
        linhas.append('')

    visiveis = itens if incluir_ocultos else [i for i in itens if i[0] in VISIVEIS]
    if not visiveis:
        linhas += ['_Nenhuma mudança visível ao usuário nesta versão._', '']
        return '\n'.join(linhas)

    por_secao = {}
    for tipo, escopo, desc, _, _ in visiveis:
        titulo = SECOES.get(tipo, (f'{tipo.capitalize()}', 99))
        por_secao.setdefault(titulo, []).append(
            f"- {f'**{escopo}**: ' if escopo else ''}{desc}")
    for (titulo, _), itens_secao in sorted(por_secao.items(), key=lambda kv: kv[0][1]):
        linhas += [f'### {titulo}', '', *itens_secao, '']
    return '\n'.join(linhas)


def escrever_no_changelog(bloco: str):
    """Prepende a seção no CHANGELOG.md, criando o arquivo com cabeçalho se preciso."""
    cabecalho = (
        '# Changelog\n\n'
        'Todas as mudanças relevantes deste projeto, por versão.\n'
        'Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) · '
        'versionamento: [SemVer](https://semver.org/lang/pt-BR/).\n\n'
        '> Gerado por `tools/gen_changelog.py` a partir dos commits '
        '(Conventional Commits). Não edite à mão.\n\n')
    if CHANGELOG.exists():
        atual = CHANGELOG.read_text(encoding='utf-8')
        if atual.startswith('# Changelog'):
            fim = atual.find('\n## ')
            corpo = atual[fim + 1:] if fim != -1 else ''
        else:
            corpo = atual
    else:
        corpo = ''
    CHANGELOG.write_text(f'{cabecalho}{bloco}\n{corpo}', encoding='utf-8')


def main():
    """Monta a seção da versão e imprime, grava em arquivo ou prepende no changelog."""
    incluir_ocultos = '--all' in sys.argv
    itens = coletar(ultima_tag())

    version = None
    if '--version' in sys.argv:
        version = sys.argv[sys.argv.index('--version') + 1]
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise SystemExit(f"Versão inválida: '{version}' — use SemVer (ex.: 1.1.0).")
    if version is None:
        version = bump_sugerido(itens, ler_versao_atual())

    bloco = secao(version, itens, incluir_ocultos)

    if '--write' in sys.argv:
        escrever_no_changelog(bloco)
        print(f'✅ CHANGELOG.md: seção [{version}] prependida '
              f'({len(itens)} commit(s) desde {ultima_tag() or "o início"}).')
    elif '--out' in sys.argv:
        destino = ROOT / sys.argv[sys.argv.index('--out') + 1]
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(bloco, encoding='utf-8')
        print(f'✅ {destino.relative_to(ROOT).as_posix()}')
    else:
        print(bloco)
        print(f'--- {len(itens)} commit(s) desde {ultima_tag() or "o início da história"}'
              f' · bump sugerido: v{bump_sugerido(itens, ler_versao_atual())}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
