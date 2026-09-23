#!/usr/bin/env python3
""".github/scripts/audit_workflows.py — linter de endurecimento dos próprios workflows.

Por que este script existe: o projeto já tem um guarda para os DADOS (a suíte
`tests/` roda o pipeline numa cópia temporária e compara com o commitado), mas
nada vigiava quem define o PODER do CI —
um PR que altere um workflow sem revisão muda o que o token pode fazer. Hoje
nenhum job escreve no repositório (`ci.yml` roda com `contents: read` e o
`release.yml` só cria tag), e é exatamente essa propriedade que o auditor impede
de regredir em silêncio.

Mesma filosofia do resto do repo: stdlib pura, veredito binário e mensagem que
diz o que corrigir.

Uso:  python .github/scripts/audit_workflows.py
      0 = tudo dentro das regras (avisos não reprovam) · 1 = violação

Regras que REPROVAM:
  1. `permissions:`      — todo workflow declara o bloco no topo (piso mínimo).
                           Sem ele o token herda o default do repositório, que
                           pode ser de escrita.
  2. `timeout-minutes:`  — todo job declara. Job sem timeout pode pendurar a
                           fila por 6 horas (o default do GitHub) consumindo
                           minutos e travando o merge.
  3. Interpolação em `run:` — contexto não confiável (título de issue/PR, nome
                           de branch ou de arquivo) dentro do shell é
                           script injection.
  4. `pull_request_target` — dá segredos e token de escrita a código de fork.
  5. Runner flutuante (`*-latest`) — a imagem do runner troca por decisão do
                           GitHub, sem nenhum commit aqui: o label de Ubuntu
                           migra para a 26 em out/2026 e o job passa a rodar em
                           outra toolchain do dia para a noite. A regra existe
                           porque esse aviso ("ubuntu-latest will migrate")
                           aparecia no CI e ninguém o lia.
  6. Action de primeira parte em runtime depreciado — o GitHub força actions
                           que declaram `node20` a rodar em `node24` e emite
                           "Node.js 20 is deprecated" a cada job. A tabela
                           `NODE24_MINIMO` guarda o major que já declara
                           `using: node24`, verificado no `action.yml` de cada
                           tag — não é chute de calendário.
  7. Action de TERCEIRO sem SHA fixo — tag móvel é reescrevível por quem
                           publica a Action (cadeia de suprimentos): a
                           `astral-sh/setup-uv@v7` entrou assim no PR #35 e o
                           CodeQL abriu alerta no review — que foi mergeado
                           sem ser lido. A regra deixa de ser aviso e passa a
                           reprovar: primeiro fixa-se o commit, depois o
                           auditor impede a regressão. Como obter o SHA:
                           `gh api repos/<owner>/<repo>/git/ref/tags/<tag>`
                           (dereferencie se `type` for `tag`).

  8. `permissions:` — o NOME do escopo e o NÍVEL têm de ser válidos, no bloco do
                           topo e em cada job. Um nome inexistente invalida o
                           arquivo INTEIRO: o GitHub cria um "workflow file
                           issue" a cada push e nenhum job roda (nem os que
                           não têm nada a ver com o escopo). Foi o que
                           aconteceu com o `project-automation.yml`, que
                           declarava `repository-project: write` (sem o "s") e
                           ficava vermelho em todo push sem ter executado um
                           único passo desde que foi criado — e o GitHub
                           exibe o nome do workflow como o próprio caminho
                           quando isso acontece (é o sinal no `gh workflow
                           list`). Escopo novo na plataforma? Confira em
                           docs.github.com → "Workflow syntax for GitHub
                           Actions" → permissions e acrescente aqui (a lista
                           é fechada de propósito: é ela que transforma typo
                           em erro de CI).

Regra que AVISA (não reprova):
  9. Action de PRIMEIRA PARTE (`actions/*`, `github/*`) sem SHA. São mantidas
     no major de propósito — o Dependabot acompanha e o GitHub é o publicador.
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent.parent
WORKFLOWS = ROOT / '.github' / 'workflows'

# Contexto que vem de fora do repositório: interpolar isso em `run:` permite
# injetar comando via título de issue/PR ou nome de branch.
UNTRUSTED = re.compile(
    r'\$\{\{\s*(?:'
    r'github\.event\.(?:issue|pull_request|comment|review|discussion)\.\w+'
    r'|github\.head_ref'
    r'|github\.event\.workflow_run'
    r')\b')

SHA_PINNED = re.compile(r'@[0-9a-f]{40}$')
JOB_KEY = re.compile(r'^  ([A-Za-z0-9_-]+):\s*$')
USES = re.compile(r'^\s*(?:- )?uses:\s*(\S+)')
RUNNER = re.compile(r'^\s*runs-on:\s*(\S+)')
MAJOR = re.compile(r'^v(\d+)')

# Label de runner que flutua: "<algo>-latest". A imagem por trás dele é decisão
# do GitHub, não do repositório.
RUNNER_FLUTUANTE = re.compile(r'^[a-z0-9._-]+-latest$')

# Owners de primeira parte: mantidos no major (Dependabot acompanha). Action de
# outro owner tem de vir fixada por commit SHA — a tag pode ser reescrita.
PRIMEIRA_PARTE = {'actions', 'github'}

# Escopos aceitos em `permissions:` (workflow syntax). Fechado de propósito:
# `repository-project` (singular) invalidava o arquivo inteiro. Note que
# `repository-projects` cobre Projects *clássicos* do repositório — Project v2
# de usuário não se acessa por aqui: aquele token vem de secret (PAT).
ESCOPOS_DE_PERMISSAO = {
    'actions', 'attestations', 'checks', 'contents', 'deployments',
    'discussions', 'id-token', 'issues', 'models', 'packages', 'pages',
    'pull-requests', 'repository-projects', 'security-events', 'statuses',
}
NIVEIS_DE_PERMISSAO = {'read', 'write', 'none'}

PERMISSOES = re.compile(r'^(\s*)permissions:\s*(\S*)\s*$')
ESCOPO = re.compile(r'\s*([A-Za-z0-9_-]+):\s*([^\s#]+)')

# Menor major de cada action de primeira parte que já declara `using: node24`
# (lido do `action.yml` da tag). Abaixo disso, o runner força a action a rodar
# em Node 24 e emite aviso de depreciação a cada job. Action fora desta tabela é
# ignorada — a regra não inventa política para o que não foi verificado.
NODE24_MINIMO = {
    'actions/checkout': 5,
    'actions/setup-python': 6,
    'actions/setup-node': 5,
    'actions/cache': 5,
    'actions/dependency-review-action': 5,
    'github/codeql-action': 4,
}


def checar_permissoes(linhas: list[str]) -> list[tuple[int, str]]:
    """Valida TODO bloco `permissions:` (topo e por job) — nomes e níveis.

    Percorre o arquivo inteiro em vez de olhar só o topo: o `project-automation`
    tinha o escopo inválido no bloco do topo, mas um job com permissão inválida
    invalida o arquivo do mesmo jeito.
    """
    falhas: list[tuple[int, str]] = []
    i = 0
    while i < len(linhas):
        m = PERMISSOES.match(linhas[i])
        if not m:
            i += 1
            continue
        indent, inline = len(m.group(1)), m.group(2)
        if inline:  # forma curta: `permissions: read-all` / `write-all` / `{}`
            if inline not in ('read-all', 'write-all', '{}'):
                falhas.append((i + 1, f'`permissions: {inline}` inválido — use '
                                      f'`read-all`, `write-all` ou um escopo por linha'))
            i += 1
            continue
        i += 1
        while i < len(linhas) and linhas[i].strip():
            if len(linhas[i]) - len(linhas[i].lstrip()) <= indent:
                break  # voltou ao nível do bloco: fim das permissões
            mc = ESCOPO.match(linhas[i])
            if mc:
                escopo, nivel = mc.group(1), mc.group(2).strip('\'"')
                if escopo not in ESCOPOS_DE_PERMISSAO:
                    falhas.append((i + 1, f'`{escopo}: {nivel}` — "{escopo}" não é um '
                                          f'escopo válido: ele invalida o ARQUIVO '
                                          f'INTEIRO (o workflow nunca roda). Escopos '
                                          f'aceitos: {", ".join(sorted(ESCOPOS_DE_PERMISSAO))}'))
                elif nivel not in NIVEIS_DE_PERMISSAO:
                    falhas.append((i + 1, f'`{escopo}: {nivel}` — nível inválido: use '
                                          f'{", ".join(sorted(NIVEIS_DE_PERMISSAO))}'))
            i += 1
    return falhas


def audit(path: Path):
    """Audita um workflow e devolve (falhas, avisos) — listas de (linha, texto)."""
    linhas = path.read_text(encoding='utf-8', errors='replace').splitlines()
    falhas, avisos = [], []

    # ── 8. nomes e níveis de permissão (topo e por job) ─────────────────────
    falhas.extend(checar_permissoes(linhas))

    # ── 1. permissions no topo (coluna 0) ────────────────────────────────────
    if not any(re.match(r'^permissions:', l) for l in linhas):
        falhas.append((1, 'sem `permissions:` no topo — o token herda o default do '
                          'repositório; declare o piso (ex.: `contents: read`)'))

    # ── 2 e 3. varredura por job ─────────────────────────────────────────────
    em_jobs, job, job_linha = False, None, 0
    jobs = []                                    # [(nome, linha_inicial, [linhas])]
    for i, l in enumerate(linhas, start=1):
        if re.match(r'^jobs:', l):
            em_jobs = True
            continue
        if not em_jobs:
            continue
        m = JOB_KEY.match(l)
        if m:
            if job is not None:
                jobs.append((job, job_linha, corpo))
            job, job_linha, corpo = m.group(1), i, []
        elif job is not None:
            corpo.append((i, l))
    if job is not None:
        jobs.append((job, job_linha, corpo))

    for nome, linha, corpo in jobs:
        if not any(re.match(r'^\s+timeout-minutes:', l) for _, l in corpo):
            falhas.append((linha, f"job `{nome}` sem `timeout-minutes` — usa o "
                                  f"default de 6 h do GitHub"))

    # ── 3. injeção em run: ──────────────────────────────────────────────────
    em_run, run_indent = False, 0
    for i, l in enumerate(linhas, start=1):
        m = re.match(r'^(\s*)run:\s*[|>]?', l)
        if m:
            em_run, run_indent = True, len(m.group(1))
            continue
        if em_run:
            if l.strip() and len(l) - len(l.lstrip()) <= run_indent:
                em_run = False
            elif UNTRUSTED.search(l):
                falhas.append((i, f'contexto não confiável interpolado em `run:` '
                                  f'(script injection): {l.strip()[:60]}'))

    # ── 4 a 7 e 9. gatilho proibido, runner, runtime e pinagem ───────────────
    for i, l in enumerate(linhas, start=1):
        if re.match(r'^\s*(pull_request_target|workflow_run):', l):
            falhas.append((i, 'gatilho `pull_request_target`/`workflow_run` — dá '
                              'segredos e escrita a código de fork'))

        # 5. runner flutuante. Ignora lista/expressão (`[self-hosted, linux]`,
        #    `${{ matrix.os }}`): só o label simples é verificável aqui.
        mr = RUNNER.match(l)
        if mr:
            label = mr.group(1).strip('"\'')
            if RUNNER_FLUTUANTE.match(label):
                falhas.append((i, f'runner `{label}` flutua — a imagem troca sem '
                                  f'commit neste repositório; fixe a versão '
                                  f'(ex.: `ubuntu-24.04`)'))

        m = USES.match(l)
        if m:
            alvo = m.group(1)
            if alvo.startswith('./') or alvo.startswith('docker://'):
                continue                          # local / imagem: fora do escopo

            # 6. runtime. `owner/repo/caminho@ref` → `owner/repo`.
            repo = '/'.join(alvo.split('@')[0].split('/')[:2])
            ref = alvo.split('@')[1] if '@' in alvo else ''
            minimo = NODE24_MINIMO.get(repo)
            mv = MAJOR.match(ref)
            if minimo is not None and mv and int(mv.group(1)) < minimo:
                falhas.append((i, f'`{alvo}` ainda declara Node 20 (depreciado) — '
                                  f'use `{repo}@v{minimo}` ou maior'))

            if not SHA_PINNED.search(alvo):
                owner = repo.split('/')[0].lower()
                if owner in PRIMEIRA_PARTE:
                    avisos.append((i, f'`{alvo}` não está fixado por SHA '
                                      f'(primeira parte: aceito no major)'))
                else:
                    falhas.append((i, f'`{alvo}` é Action de TERCEIRO sem SHA — '
                                      f'fixe o commit e deixe a tag em '
                                      f'comentário (`{repo}@<sha> # vN`)'))
    return falhas, avisos


def main():
    """Audita todos os workflows e imprime o relatório; 1 se houver violação."""
    arquivos = sorted(WORKFLOWS.glob('*.y*ml'))
    if not arquivos:
        print(f'⚠️  nenhum workflow em {WORKFLOWS} — nada a auditar.')
        return 0

    total_falhas = total_avisos = 0
    for path in arquivos:
        falhas, avisos = audit(path)
        total_falhas += len(falhas)
        total_avisos += len(avisos)
        estado = '❌' if falhas else '✅'
        print(f'{estado} {path.relative_to(ROOT).as_posix()}')
        for linha, texto in falhas:
            print(f'     L{linha}: {texto}')
        for linha, texto in avisos:
            print(f'     ⚠️  L{linha}: {texto}')

    print()
    if total_falhas:
        print(f'❌ {total_falhas} violação(ões) em {len(arquivos)} workflow(s) — '
              f'corrija antes do merge.')
        return 1
    print(f'✅ {len(arquivos)} workflow(s) dentro das regras de endurecimento'
          + (f' ({total_avisos} aviso(s) de pinagem por SHA).' if total_avisos else '.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
