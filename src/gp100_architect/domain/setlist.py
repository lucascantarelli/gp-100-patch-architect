"""Setlist — regras puras de cola de palco: assinatura de cadeia, distância
entre patches e ordenação por vizinho mais próximo.

Trazido de `tools/gp100_setlist.py` (issue #28, delta do PR #35): o script
continua sendo o consumidor (I/O, resolução de pedidos, relatórios) — aqui
ficam só as regras que **pensam** sobre a biblioteca, sem I/O nem dependência
de formato. Mesmo contrato do resto do domínio: funções puras, entrada já
validada, nenhum print.

A assinatura é `((modelo, ligado) por posição, PRE → RVB)`: igual posição com
igual par = zero trocas no device; a distância entre dois patches é o número
de posições em que a assinatura difere. A ordenação por vizinho mais próximo
não é ótima (TSP) — é **explicável**: a cola mostra exatamente o que muda a
cada passo, e para repertório (10–30 músicas) o ganho de um solver real nunca
justificou perder isso.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from gp100_architect.domain.chain import CHAIN

__all__ = ['ItemSetlist', 'assinatura', 'dif_cadeia', 'distancia', 'otimizar', 'trocas_totais']

Assinatura = tuple[tuple[str, bool], ...]

# ordem canônica das posições de módulo no defs (a mesma da cadeia; o defs
# históricamente grava `modules` nesta ordem — assinatura comparável por índice)
_ORDEM = CHAIN


def assinatura(patch: Mapping[str, Any]) -> Assinatura:
    """`((modelo, ligado) por posição, PRE → RVB)` — o que custa troca no device.

    Posição sem módulo setado assina `( '', False )`: trocar "nada" por algo é
    troca, e a ordem das posições é a da cadeia (o defs grava nesta ordem).
    """
    modules = (patch.get('spec') or {}).get('modules') or {}
    return tuple(
        (str(modules.get(m, {}).get('name', '')), bool(modules.get(m, {}).get('on', False)))
        for m in _ORDEM
    )


def distancia(a: Assinatura, b: Assinatura) -> int:
    """Trocas concretas entre dois patches: posições com assinatura diferente."""
    return sum(1 for x, y in zip(a, b, strict=True) if x != y)


def dif_cadeia(atual: Mapping[str, Any], proximo: Mapping[str, Any]) -> list[str]:
    """O que o músico precisa mexer: `['DST: Blues OD → La Charger', 'MOD: ligar A-Chorus']`.

    Mensagem acionável (regra do projeto): nome do módulo, de → para ou
    ligar/desligar — nunca um diff de dict cru.
    """
    mods_atual = (atual.get('spec') or {}).get('modules') or {}
    mods_prox = (proximo.get('spec') or {}).get('modules') or {}
    diffs: list[str] = []
    for modulo in _ORDEM:
        va = mods_atual.get(modulo) or {}
        vb = mods_prox.get(modulo) or {}
        nome_a, nome_b = str(va.get('name', '')), str(vb.get('name', ''))
        if nome_a != nome_b:
            de = nome_a if nome_a else '(vazio)'
            para = nome_b if nome_b else '(vazio)'
            diffs.append(f'{modulo}: {de} → {para}')
        elif nome_a and bool(va.get('on', False)) != bool(vb.get('on', False)):
            diffs.append(f'{modulo}: {"ligar" if vb.get("on") else "desligar"} {nome_a}')
    return diffs


def trocas_totais(plano: Sequence[tuple[Mapping[str, Any], Mapping[str, Any]]]) -> int:
    """Soma de trocas ao longo do plano `(música, patch)` — o placar da cola."""
    total = 0
    for i in range(1, len(plano)):
        total += distancia(assinatura(plano[i - 1][1]), assinatura(plano[i][1]))
    return total


ItemSetlist = tuple[Mapping[str, Any], Mapping[str, Any]]  # (song, patch) do defs


def otimizar(itens: Sequence[ItemSetlist]) -> list[ItemSetlist]:
    """Vizinho mais próximo: da primeira música, sempre o par mais parecido.

    Mantém o primeiro item na primeira posição (o show abre com o que o músico
    escalou) e não repete música. Exato o suficiente para repertório e
    explicável — ver o módulo docstring para o porquê de não ser TSP.
    """
    if not itens:
        return []
    restantes = list(itens)
    plano = [restantes.pop(0)]
    while restantes:
        atual = assinatura(plano[-1][1])
        melhor = min(restantes, key=lambda it: (distancia(atual, assinatura(it[1])),))
        restantes.remove(melhor)
        plano.append(melhor)
    return plano


# referência para consumidores que querem iterar posições com rótulo
def modulos_da_assinatura(assinatura_patch: Assinatura) -> Iterable[tuple[str, tuple[str, bool]]]:
    """Pares `(módulo, (modelo, ligado))` na ordem da cadeia."""
    return zip(_ORDEM, assinatura_patch, strict=True)
