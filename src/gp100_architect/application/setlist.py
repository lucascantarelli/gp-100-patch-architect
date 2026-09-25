"""Cola de palco — regras puras e orquestração (issue #49, regras da #28).

Migração de `tools/gp100_setlist.py` (refatoração #28/#35), reunida num único
módulo na limpeza pós-2.0.0: a resolução de pedidos ("Smooth", "SMOO1:SO",
"CT01VOX"), o catálogo e os relatórios (texto/JSON) e as REGRAS puras
(assinatura, distância, otimizador, dif) vivem juntos — quem só quer as regras
importa as funções direto; a CLI expõe o fluxo completo. Agentes consomem o
`--json` (shape estável).

Fontes únicas: slots vêm de `biblioteca.slots` (a numeração do MAPA-DO-ALBUM;
regra "nunca recalcule um slot" do agente de cola de palco).

A assinatura é `((modelo, ligado) por posição, PRE → RVB)`: igual posição com
igual par = zero trocas no device; a distância entre dois patches é o número
de posições em que a assinatura difere. A ordenação por vizinho mais próximo
não é ótima (TSP) — é **explicável**: a cola mostra exatamente o que muda a
cada passo, e para repertório (10–30 músicas) o ganho de um solver real nunca
justificou perder isso.

Camada: application — devolve dados; quem imprime é a CLI.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from gp100_architect.application.biblioteca import slots
from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.errors import EntradaInvalida

__all__ = [
    'BibliotecaSetlist',
    'ItemSetlist',
    'assinatura',
    'dif_cadeia',
    'distancia',
    'otimizar',
    'plano_json',
    'plano_markdown',
    'trocas_totais',
]

# sufixo padrão quando o músico pede a música sem seção: o patch 'tocável'
# (riff/base/ambiente) — explicitável com MUSICA:SUFIXO ou pelo nome completo.
SUFIXOS_PADRAO = frozenset({'RI', 'RI1', 'BA', 'AM'})

Assinatura = tuple[tuple[str, bool], ...]

# ordem canônica das posições de módulo no defs (a mesma da cadeia; o defs
# históricamente grava `modules` nesta ordem — assinatura comparável por índice)
_ORDEM = CHAIN

ItemSetlist = tuple[Mapping[str, Any], Mapping[str, Any]]  # (song, patch) do defs


# ── regras puras: o que custa troca no device ───────────────────────────────


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


# ── orquestração: resolver pedidos, catálogo e relatórios ───────────────────


class BibliotecaSetlist:
    """Índices de consulta do defs: por id de música, nome e patch.

    A resolução de pedidos é leitura de índice; a matemática do plano é toda
    da seção de regras acima (`otimizar`, `trocas_totais`, `dif_cadeia`).
    """

    def __init__(self, defs: dict[str, Any]) -> None:
        self.defs = defs
        self.slots = slots(defs)
        self.por_id = {s['id'].upper(): s for s in defs['songs']}
        self.por_nome = {s['song'].upper(): s for s in defs['songs']}
        self.por_patch = {p['nome'].upper(): (s, p) for s in defs['songs'] for p in s['patches']}

    def resolver(self, pedido: str) -> ItemSetlist:
        """'SMOO1' | 'smooth' | 'SMOO1SO' | 'SMOO1:SO' | 'CT01VOX' → (song, patch).

        Música sem seção usa o sufixo padrão (RI/BA/AM); se não houver, o
        primeiro patch do defs. Erro de domínio com sugestões acionáveis.
        """
        p = pedido.strip()
        if not p:
            raise EntradaInvalida('pedido vazio — informe a música (ex.: "Money")')
        base, sufixo = (x.strip() for x in p.split(':', 1)) if ':' in p else (p, None)
        musica = self.por_id.get(base.upper()) or self.por_nome.get(base.upper())
        if musica is None:
            # não é música: pode ser o patch inteiro (CT01VOX)
            hit = self.por_patch.get(p.upper())
            if hit:
                return hit
            dicas = ', '.join(sorted(self.por_id)[:8])
            raise EntradaInvalida(
                f'"{pedido}" não é música nem patch conhecido — músicas (ex.): {dicas}… '
                'use --list para o catálogo completo.'
            )
        if sufixo:
            alvo = sufixo.upper()
            for patch in musica['patches']:
                if patch['sufixo'].upper() == alvo or patch['nome'].upper() == alvo:
                    return musica, patch
            secoes = ', '.join(x['sufixo'] for x in musica['patches'])
            raise EntradaInvalida(f'{musica["id"]} não tem seção "{sufixo}" (há: {secoes})')
        for patch in musica['patches']:
            if patch['sufixo'].upper() in SUFIXOS_PADRAO:
                return musica, patch
        return musica, musica['patches'][0]

    def catalogo(self) -> list[tuple[str, str, str, str]]:
        """Linhas do --list: (id, música, álbum, patches com sufixo)."""
        albums = self.defs['albums']
        linhas = []
        for s in self.defs['songs']:
            a = albums[s['idAlbum']]
            rotulo = a['album'] if isinstance(a, dict) else a
            patches = ', '.join(f'{p["nome"]} ({p["sufixo"]})' for p in s['patches'])
            linhas.append((s['id'], s['song'], rotulo, patches))
        return linhas


def resolver_repertorio(
    lib: BibliotecaSetlist, pedidos: list[str], forcar: list[str], manter_ordem: bool
) -> list[ItemSetlist]:
    """Resolve o repertório com `--patch` aplicado; valida duplicatas/extras.

    `forcar` são pedidos `MUSICA:SUFIXO` que sobrescrevem a seção da música
    já escalada. Erros de domínio: música repetida, `--patch` órfão.
    """
    sobrescrever: dict[str, ItemSetlist] = {}
    for p in forcar:
        musica, patch = lib.resolver(p)
        sobrescrever[musica['id'].upper()] = (musica, patch)

    itens: list[ItemSetlist] = []
    vistos: set[str] = set()
    for pedido in pedidos:
        musica, patch = lib.resolver(pedido)
        chave = musica['id'].upper()
        if chave in sobrescrever:
            _m, patch = sobrescrever.pop(chave)
        if chave in vistos:
            raise EntradaInvalida(f'música repetida no repertório: {musica["song"]}')
        vistos.add(chave)
        itens.append((musica, patch))
    if sobrescrever:
        raise EntradaInvalida(
            '--patch para música fora do repertório: ' + ', '.join(sorted(sobrescrever))
        )
    return itens if manter_ordem else otimizar(itens)


def plano_json(
    plano: Sequence[ItemSetlist],
    total_trocas: int,
    mapa_slots: dict[str, str],
) -> dict[str, Any]:
    """Shape estável do `--json` (contrato para agentes): trocas_totais + itens."""
    itens = []
    for pos, (musica, patch) in enumerate(plano):
        anterior = plano[pos - 1][1] if pos else None
        itens.append(
            {
                'ordem': pos + 1,
                'slot': mapa_slots[patch['nome']],
                'musica': musica['song'],
                'patch': patch['nome'],
                'trocas': [] if anterior is None else dif_cadeia(anterior, patch),
            }
        )
    return {'trocas_totais': total_trocas, 'itens': itens}


def plano_markdown(
    plano: Sequence[ItemSetlist],
    total_trocas: int,
    mapa_slots: dict[str, str],
    titulo: str = 'Cola de palco',
) -> str:
    """Relatório em Markdown — o mesmo formato que a cola impressa sempre teve."""
    linhas = [
        f'# 🎤 {titulo}',
        '',
        f'**{len(plano)} músicas · {total_trocas} troca(s) de módulo no total** — '
        'slots da numeração da biblioteca (U01…), a mesma do MAPA-DO-ALBUM.',
        '',
        '| # | Slot | Música | Patch | Trocas ao entrar |',
        '|---|---|---|---|---|',
    ]
    for pos, (musica, patch) in enumerate(plano):
        anterior = plano[pos - 1][1] if pos else None
        slot = mapa_slots[patch['nome']]
        emoji = patch.get('emoji', '') or ''
        trocas = (
            '— (primeira)'
            if anterior is None
            else (', '.join(dif_cadeia(anterior, patch)) or 'nenhuma')
        )
        linhas.append(
            f'| {pos + 1} | **{slot}** | {emoji} {musica["song"]} | `{patch["nome"]}` | {trocas} |'
        )
    linhas += [
        '',
        '> Gerado por `gp100 setlist` — reordene e rode de novo se a sequência '
        'do show mandar mais que a economia de trocas.',
        '',
    ]
    return '\n'.join(linhas)
