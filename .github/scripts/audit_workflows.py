#!/usr/bin/env python3
""".github/scripts/audit_workflows.py — linter de endurecimento dos próprios workflows.

Por que este script existe: o projeto já tem um guarda para os DADOS
(`tools/check_data_freshness.py`), mas nada vigiava a superfície que pode
**escrever** no repositório — e ela é justamente a mais sensível aqui, porque o
job `data-pipeline` tem `contents: write` e commita no `main` em push. Um PR que
consiga alterar um workflow sem revisão alterou o poder de escrita do CI.

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

Regra que AVISA (não reprova):
  5. `uses:` de terceiro sem SHA fixo. O Dependabot (`.github/dependabot.yml`)
     mantém as Actions atualizadas, então fixar por SHA é viável — mas a
     migração é gradual, e reprovar hoje deixaria todos os workflows vermelhos.
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


def audit(path: Path):
    """Audita um workflow e devolve (falhas, avisos) — listas de (linha, texto)."""
    linhas = path.read_text(encoding='utf-8', errors='replace').splitlines()
    falhas, avisos = [], []

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

    # ── 4 e 5. gatilho proibido e pinagem ──────────────────────────────────
    for i, l in enumerate(linhas, start=1):
        if re.match(r'^\s*(pull_request_target|workflow_run):', l):
            falhas.append((i, 'gatilho `pull_request_target`/`workflow_run` — dá '
                              'segredos e escrita a código de fork'))
        m = re.match(r'^\s*(?:- )?uses:\s*(\S+)', l)
        if m:
            alvo = m.group(1)
            if alvo.startswith('./') or alvo.startswith('docker://'):
                continue                          # local / imagem: fora do escopo
            if not SHA_PINNED.search(alvo):
                avisos.append((i, f'`{alvo}` não está fixado por SHA'))
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
