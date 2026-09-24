"""Changelog derivado da história — regras puras de parsing e formatação (issue #32).

Migração de `tools/gen_changelog.py`: o que **pensa** sobre commits (regex,
seções, bump sugerido, prepend idempotente) vira biblioteca; o shim de
`tools/` fica só com argv e impressão. O changelog é **derivado da história**,
não escrito à mão — nada de dois lugares discordando sobre o que mudou.

Regras preservadas (são contrato, não detalhe):

* `desde` = última tag `v*` (ou a história inteira, na primeira release);
* tipos visíveis: feat, fix, data, docs, perf — os demais só com `--all`;
* rodapé `BREAKING CHANGE:` ou `!` antes dos dois-pontos abre a seção de
  mudanças incompatíveis e força bump MAJOR;
* merge commits e `[skip ci]` são ignorados;
* bump: breaking → MAJOR · qualquer `feat` → MINOR · senão → PATCH.

Camada: application — funções de parsing/formato são puras; as duas que tocam
o mundo (`git` e `escrever_no_changelog`) recebem raiz/caminho explícitos.
"""

from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

__all__ = [
    'BREAKING_FOOTER',
    'COMMIT_RE',
    'SECOES',
    'SKIP',
    'VISIVEIS',
    'ItemCommit',
    'bump_sugerido',
    'coletar',
    'coletar_do_log',
    'escrever_no_changelog',
    'git',
    'ler_versao_atual',
    'secao',
    'ultima_tag',
]

# tipo -> (título da seção, ordem). Ordem = como aparece no changelog.
SECOES: dict[str, tuple[str, int]] = {
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
VISIVEIS = frozenset({'feat', 'fix', 'data', 'docs', 'perf'})

COMMIT_RE = re.compile(
    r'^(?P<tipo>[a-z]+)(?:\((?P<escopo>[^)]*)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$'
)
BREAKING_FOOTER = re.compile(r'^BREAKING[ -]CHANGE:\s*(.+)$', re.MULTILINE)
SKIP = re.compile(r'\[skip ci\]', re.IGNORECASE)

# (tipo, escopo, descrição, nota de breaking, é breaking)
ItemCommit = tuple[str, str, str, str, bool]

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')


# ── I/O de git (o shim não duplica; a biblioteca centraliza) ────────────────


def git(*args: str, raiz: Path) -> str:
    """Roda um comando git no repositório e devolve o stdout (UTF-8 tolerante)."""
    r = subprocess.run(['git', *args], cwd=raiz, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(
            f'git {" ".join(args)} falhou: {r.stderr.decode("utf-8", "replace").strip()}'
        )
    return r.stdout.decode('utf-8', 'replace')


def ultima_tag(raiz: Path) -> str | None:
    """Tag `v*` mais recente alcançável, ou None (primeira release)."""
    r = subprocess.run(
        ['git', 'describe', '--tags', '--abbrev=0', '--match', 'v[0-9]*'],
        cwd=raiz,
        capture_output=True,
    )
    return r.stdout.decode().strip() or None if r.returncode == 0 else None


# ── parsing e regras (puras) ────────────────────────────────────────────────


def coletar_do_log(bruto: str) -> list[ItemCommit]:
    """Converte a saída `%H%x1f%s%x1f%b%x1e` do git em itens de changelog.

    Pura: recebe o texto bruto do log — quem roda git é o chamador (o shim ou
    `coletar`). Commits fora do padrão Conventional e `[skip ci]` não entram.
    """
    itens: list[ItemCommit] = []
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
            continue  # fora do padrão: não entra no changelog
        rodape = BREAKING_FOOTER.search(corpo)
        breaking = bool(m.group('breaking')) or bool(rodape)
        itens.append(
            (
                m.group('tipo'),
                m.group('escopo') or '',
                m.group('desc').strip(),
                rodape.group(1).strip() if rodape else '',
                breaking,
            )
        )
    return itens


def coletar(desde: str | None, *, raiz: Path) -> list[ItemCommit]:
    """Itens desde a tag (inclusive até HEAD) — roda git na `raiz` dada."""
    intervalo = f'{desde}..HEAD' if desde else 'HEAD'
    bruto = git('log', intervalo, '--no-merges', '--format=%H%x1f%s%x1f%b%x1e', raiz=raiz)
    return coletar_do_log(bruto)


def bump_sugerido(itens: list[ItemCommit], atual: str) -> str:
    """MAJOR se breaking, MINOR se houver feat, senão PATCH."""
    major, minor, patch = (int(n) for n in atual.split('.'))
    if any(i[4] for i in itens):
        return f'{major + 1}.0.0'
    if any(i[0] == 'feat' for i in itens):
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


def ler_versao_atual(raiz: Path) -> str:
    """Versão de VERSION; '0.0.0' se ausente/inválida (primeira release)."""
    arquivo = raiz / 'VERSION'
    if arquivo.exists() and SEMVER_RE.match(arquivo.read_text(encoding='utf-8').strip()):
        return arquivo.read_text(encoding='utf-8').strip()
    return '0.0.0'


def secao(version: str, itens: list[ItemCommit], incluir_ocultos: bool) -> str:
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

    por_secao: dict[tuple[str, int], list[str]] = {}
    for tipo, escopo, desc, _, _ in visiveis:
        chave = SECOES.get(tipo, (f'{tipo.capitalize()}', 99))
        por_secao.setdefault(chave, []).append(f'- {f"**{escopo}**: " if escopo else ""}{desc}')
    for (titulo, _), itens_secao in sorted(por_secao.items(), key=lambda kv: kv[0][1]):
        linhas += [f'### {titulo}', '', *itens_secao, '']
    return '\n'.join(linhas)


# ── escrita (caminho explícito; idempotente) ────────────────────────────────


def _cabecalho() -> str:
    return (
        '# Changelog\n\n'
        'Todas as mudanças relevantes deste projeto, por versão.\n'
        'Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) · '
        'versionamento: [SemVer](https://semver.org/lang/pt-BR/).\n\n'
        '> Gerado por `gp100 release` / `tools/gen_changelog.py` a partir dos commits\n'
        '> (Conventional Commits) — **não edite à mão**. Quem publica roda\n'
        '> `gen_changelog.py --version X.Y.Z --write` antes de subir o `VERSION`;\n'
        '> o workflow `Release` só valida e publica.\n'
        '>\n'
        '> A v1.0.0 é a **baseline escrita à mão**: a história anterior a esta\n'
        '> automação não seguia Conventional Commits, então ela não é derivável.\n'
        '> Daqui para frente, o título do PR (que vira o commit do squash) é o que\n'
        '> alimenta o changelog — ver CONTRIBUTING.md.\n\n'
    )


def escrever_no_changelog(bloco: str, version: str, caminho: Path) -> None:
    """Escreve a seção no CHANGELOG.md, criando o arquivo com cabeçalho se preciso.

    Idempotente: se a seção da MESMA versão já está no topo, ela é SUBSTITUÍDA
    em vez de duplicada — rodar `--write` duas vezes (ou corrigir um commit e
    rodar de novo) não deixa dois blocos `## [x.y.z]` no arquivo.
    """
    if caminho.exists():
        atual = caminho.read_text(encoding='utf-8')
        if atual.startswith('# Changelog'):
            fim = atual.find('\n## ')
            corpo = atual[fim + 1 :] if fim != -1 else ''
        else:
            corpo = atual
    else:
        corpo = ''

    marca = f'## [{version}]'
    if corpo.startswith(marca):
        proxima = corpo.find('\n## ', len(marca))
        corpo = corpo[proxima + 1 :] if proxima != -1 else ''

    caminho.write_text(f'{_cabecalho()}{bloco}\n{corpo}', encoding='utf-8')
