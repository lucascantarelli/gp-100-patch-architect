"""Badges derivados (issue #117) — contagens de fonte única, provadas.

Por que este teste existe: os badges manuais apodreceram ("release-1.0",
"384 testes" conviveram com a realidade). O teste fixa que a derivação lê
CADA fonte certa — `git ls-files` para agentes/skills, defs para patches,
`VERSION`, `requires-python`, `fail_under` e a coleção pytest — e que o
formato é o endpoint do shields.io (o que o README consome).

Mesmo padrão da suíte: casos sintéticos em `tmp_path` (com `_rastreados`/
`_contagem_testes` falsificados — não há git em tmp) e a realidade commitada
lida, nunca alterada.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import badges

pytestmark = pytest.mark.unit


def _mensagens(arquivos: dict[str, str]) -> dict[str, str]:
    """`{nome_do_badge: message}` — parse do JSON de endpoint."""
    return {
        Path(chave).name: json.loads(conteudo)['message'] for chave, conteudo in arquivos.items()
    }


# ── casos sintéticos: cada fonte de dado, isolada ────────────────────────────


def test_sintetico_deriva_cada_badge_da_sua_fonte(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    (tmp_path / 'VERSION').write_text('9.9.9\n', encoding='utf-8')
    (tmp_path / 'pyproject.toml').write_text(
        '[project]\nrequires-python = ">=3.13,<3.14"\n[tool.coverage.report]\nfail_under = 77\n',
        encoding='utf-8',
    )
    # `types/agent-definition.ts` tem pasta após o prefixo — NÃO é agente
    monkeypatch.setattr(
        badges,
        '_rastreados',
        lambda _raiz: [
            '.agents/a.ts',
            '.agents/b.ts',
            '.agents/types/agent-definition.ts',
            '.agents/skills/x/SKILL.md',
        ],
    )
    monkeypatch.setattr(badges, '_contagem_testes', lambda _raiz: '42')
    # schema fiel ao defs real: toda música tem `patches` (dados_derivados soma)
    defs = {
        'songs': [{'id': 'A', 'patches': [{'nome': 'A1BA'}]}, {'id': 'B', 'patches': []}],
        'albums': {'X': {}, 'Y': {}, 'Z': {}},
    }

    rotulos = _mensagens(badges.gerar_badges(defs, raiz=tmp_path))

    assert rotulos['release.json'] == '9.9.9'
    assert rotulos['agentes.json'] == '2'
    assert rotulos['skills.json'] == '1'
    assert rotulos['patches.json'] == '2 músicas · 3 álbuns'
    assert rotulos['python.json'] == 'Python 3.13'
    assert rotulos['cobertura.json'] == 'piso ≥ 77%'
    assert rotulos['testes.json'] == '42'


def test_contagem_testes_acionavel_quando_fora_da_raiz(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Sem `collected` na saída, a mensagem diz o que fazer — nunca um número mentiroso."""

    class R:
        returncode = 1
        stdout = ''

    monkeypatch.setattr(
        badges.subprocess,
        'run',
        lambda *a, **kw: R(),
        raising=True,
    )
    assert 'erro' in badges._contagem_testes(tmp_path)


def test_url_endpoint_aponta_para_o_pages():
    url = badges.url_endpoint('agentes')
    assert url.startswith('https://img.shields.io/endpoint?url=')
    assert url.endswith('badges/agentes.json')


# ── a realidade commitada (o badge de fundo; UMA coleção pytest) ─────────────


def test_repo_real_badges_derivados(defs_real: dict[str, Any]):
    """7 badges do repo real: formato endpoint + contagens batendo nas fontes.

    A contagem de testes é DERIVADA — o teste prova que sai da coleção, não
    de um número memorizado (o valor muda a cada PR; o badge não apodrece).
    """
    rotulos = _mensagens(badges.gerar_badges(defs_real))
    assert set(rotulos) == {
        f'{n}.json'
        for n in ('release', 'agentes', 'skills', 'patches', 'python', 'cobertura', 'testes')
    }
    assert (
        rotulos['release.json']
        == (badges.RAIZ_PADRAO / 'VERSION').read_text(encoding='utf-8').strip()
    )
    assert rotulos['agentes.json'] == '21'
    assert rotulos['skills.json'] == '11'
    assert rotulos['patches.json'] == (
        f'{len(defs_real["songs"])} músicas · {len(defs_real["albums"])} álbuns'
    )
    assert rotulos['testes.json'].isdigit()
