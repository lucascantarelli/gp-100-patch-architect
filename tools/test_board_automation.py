#!/usr/bin/env python3
"""Teste do project-automation.yml: executa o job de status EXATAMENTE como o runner.

Recria o passo "Aplica o estado no campo Kanban" com GH_TOKEN=PROJECT_TOKEN:
resolve campo/item/opção por GraphQL puro e aplica via item-edit. O mesmo
token que o runner usará; mesmo `gh` que o ubuntu-24.04 (actions/runner).

Uso (PowerShell):
    $env:GH_TOKEN="<PAT>"
    uv run python tools/test_board_automation.py --evento converted_to_draft
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any
from urllib.request import Request, urlopen

OWNER = 'lucascantarelli'
REPO = 'gp-100-patch-architect'
PROJECT_NUMBER = 7
PR = 73

ESTADOS = {'In Progress': '3d3a5dfb', 'In Review': 'fb9247a3', 'Done': '5c727ec2'}


def _post(gh_token: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
    req = Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': variables}).encode(),
        headers={'Authorization': f'Bearer {gh_token}', 'Content-Type': 'application/json'},
    )
    with urlopen(req) as resp:
        dados: dict[str, Any] = json.load(resp)
    if erros := dados.get('errors'):
        sys.exit(f'GraphQL erros: {erros}')
    resultado: dict[str, Any] = dados['data']
    return resultado


def _run(gh_token: str, args: list[str]) -> str:
    env = {**os.environ, 'GH_TOKEN': gh_token}
    out = subprocess.run(args, capture_output=True, text=True, env=env)
    if out.returncode != 0:
        sys.exit(f'`{" ".join(args)}` falhou: {out.stderr.strip()}')
    return out.stdout.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--evento', required=True, choices=['converted_to_draft', 'ready_for_review', 'closed']
    )
    args = ap.parse_args()

    gh_token = os.environ.get('GH_TOKEN', '')
    if not gh_token:
        sys.exit('defina GH_TOKEN com o PAT (o mesmo valor do secret PROJECT_TOKEN)')
    valor = {
        'converted_to_draft': 'In Progress',
        'ready_for_review': 'In Review',
        'closed': 'Done',
    }[args.evento]

    # Idêntico ao workflow novo: resolve TUDO por GraphQL puro.
    data = _post(
        gh_token,
        """
    query($owner: String!, $n: Int!, $repo: String!, $pr: Int!) {
      user(login: $owner) {
        projectV2(number: $n) {
          id
          field(name: "Kanban") { ... on ProjectV2SingleSelectField { id } }
          item(number: $pr) { ... on ProjectV2Item { id } }
        }
      }
      repository(owner: $owner, name: $repo) { pullRequest(number: $pr) { id } }
    }""",
        {'owner': OWNER, 'n': PROJECT_NUMBER, 'repo': REPO, 'pr': PR},
    )
    proj: dict[str, Any] = data['user']['projectV2']
    campo_id, item_id, pr_id = (
        proj['field']['id'],
        proj['item']['id'],
        data['repository']['pullRequest']['id'],
    )

    add = _run(
        gh_token,
        [
            'gh',
            'api',
            'graphql',
            '-f',
            'query=mutation($p:ID!,$i:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$i}){item{id}}}',
            '-f',
            f'p={proj["id"]}',
            '-f',
            f'i={pr_id}',
        ],
    )
    item_id = json.loads(add)['data']['addProjectV2ItemById']['item']['id']

    upd = _post(
        gh_token,
        """
    mutation($p: ID!, $i: ID!, $f: ID!, $o: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $p, itemId: $i, fieldId: $f,
        value: { singleSelectOptionId: $o }
      }) { projectV2Item { id } }
    }""",
        {'p': proj['id'], 'i': item_id, 'f': campo_id, 'o': ESTADOS[valor]},
    )
    item_final = upd['updateProjectV2ItemFieldValue']['projectV2Item']['id']
    print(f'OK: PR #{PR} → {valor} (item {item_final[:20]}…)')


if __name__ == '__main__':
    main()
