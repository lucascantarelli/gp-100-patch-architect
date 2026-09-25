"""Badges do README derivados do repositório — contagens de fonte única (#117).

Os badges do README eram editados à mão e a auditoria de workflows (#115)
provou o apodrecimento ("release-1.0" e "384 testes" conviviam com a
realidade). Aqui cada badge é **derivado**: versão do arquivo `VERSION`
(ADR-0010), agentes/skills do `git ls-files`, patches do defs validado,
Python do `requires-python` do pyproject, cobertura do `fail_under` e testes
da coleção pytest (único dado que executa o gerador — ~2s, só no deploy).

Formato: endpoint do shields.io (`schemaVersion` 1). O README cita a URL do
`badges.json` publicado no Pages; dado derivado não se edita, se regenera.

Contrato da camada: devolve `{caminho_relativo: conteúdo}` em memória e nunca
escreve no disco — quem grava é a CLI via `infrastructure.escrita` (mesmo
contrato do `site.py`).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

__all__ = ['gerar_badges', 'url_endpoint']

URL_BASE = 'https://img.shields.io/endpoint?url='
PAGES_BASE = 'https://lucascantarelli.github.io/gp-100-patch-architect/'
RAIZ_PADRAO = Path(__file__).resolve().parents[3]
_VERDE, _AMBAR = '2ea44f', 'f3a637'


def _escapar(s: str) -> str:
    """Escape do shields.io: `-` vira `--` e `_` vira `__` no label/message."""
    return s.replace('-', '--').replace('_', '__')


def _badge(label: str, message: str, cor: str) -> str:
    """JSON de endpoint do shields.io (`-`/`_` escapados por `--`/`__`)."""
    return json.dumps(
        {
            'schemaVersion': 1,
            'label': _escapar(label),
            'message': _escapar(message),
            'color': cor,
        },
        ensure_ascii=False,
    )


def _rastreados(raiz: Path) -> list[str]:
    """`git ls-files` — a realidade do clone limpo (mesma fonte do audit_agents)."""
    r = subprocess.run(
        ['git', 'ls-files'],
        cwd=str(raiz),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    if r.returncode != 0:
        raise RuntimeError(f'git ls-files falhou em {raiz} — rode na raiz de um clone.')
    return [linha for linha in r.stdout.splitlines() if linha]


def _piso_cobertura(raiz: Path) -> int:
    """Piso de cobertura declarado no pyproject (`fail_under`)."""
    config = tomllib.loads((raiz / 'pyproject.toml').read_text(encoding='utf-8'))
    return int(config['tool']['coverage']['report']['fail_under'])


def _contagem_testes(raiz: Path) -> str:
    """Coleção pytest (`--collect-only`, addopts limpos); erro vira badge acionável."""
    r = subprocess.run(
        [sys.executable, '-m', 'pytest', '--collect-only', '-o', 'addopts='],
        cwd=str(raiz),
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    m = re.search(r'(\d+) tests? collected', r.stdout)
    return m.group(1) if (r.returncode == 0 and m) else 'erro — rode `gp100 badges` na raiz'


def url_endpoint(nome: str) -> str:
    """URL de endpoint do shields.io para o badge `nome` publicado no Pages."""
    from urllib.parse import quote

    return URL_BASE + quote(PAGES_BASE + 'badges/' + nome + '.json', safe=':/?&=')


def _contagem_agentes(rastreados: list[str]) -> int:
    """Agentes = `.agents/*.ts` de topo rastreados (types/agent-definition.ts não é agente)."""
    return sum(
        1
        for c in rastreados
        if c.startswith('.agents/') and c.endswith('.ts') and '/' not in c[len('.agents/') :]
    )


def _contagem_skills(rastreados: list[str]) -> int:
    """Skills = pastas com SKILL.md rastreadas (a curadoria do doc 23 as registra)."""
    return sum(1 for c in rastreados if c.startswith('.agents/skills/') and c.endswith('/SKILL.md'))


def gerar_badges(defs: dict[str, Any], *, raiz: Path = RAIZ_PADRAO) -> dict[str, str]:
    """Badges derivados: `{badges/<nome>.json: conteúdo}` — a CLI grava no destino."""
    rastreados = _rastreados(raiz)
    versao = (raiz / 'VERSION').read_text(encoding='utf-8').strip()
    politicas = tomllib.loads((raiz / 'pyproject.toml').read_text(encoding='utf-8'))
    py = re.search(r'\d+\.\d+', politicas['project']['requires-python'])
    badges = {
        'release': _badge('release', versao, _VERDE),
        'agentes': _badge('agentes', str(_contagem_agentes(rastreados)), _VERDE),
        'skills': _badge('skills', str(_contagem_skills(rastreados)), _VERDE),
        'patches': _badge(
            'patches',
            f'{len(defs["songs"])} músicas · {len(defs["albums"])} álbuns',
            _VERDE,
        ),
        'python': _badge('gerador', f'Python {py.group(0)}' if py else '—', _AMBAR),
        'cobertura': _badge('cobertura', f'piso ≥ {_piso_cobertura(raiz)}%', _VERDE),
        'testes': _badge('testes', _contagem_testes(raiz), _VERDE),
    }
    return {f'badges/{nome}.json': conteudo for nome, conteudo in badges.items()}
