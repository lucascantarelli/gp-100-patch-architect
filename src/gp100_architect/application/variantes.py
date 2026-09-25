"""Variante experimental **-USERIR** — refinamento opcional do patch (issue #10).

O canônico é inegociável: CAB de fábrica, funciona em qualquer GP-100 sem
carregar IR. A variante troca **apenas** o CAB do canônico pelo slot de User IR
declarado em `ir_local` para o gabinete alvo (`captura` + `slot`) — quem valida
no aparelho empacota a variante **sem risco de divergir do canônico**, porque
os dois nascem do mesmo spec no mesmo build.

É **derivação, não decisão**: nenhum campo novo no defs. Se o gabinete do patch
não tem captura no `ir_local`, não há variante — silencioso por design (a
política dos 4 passos permanece; a variante é camada opcional de refinamento).

Convenções (iguais ao `ir_library.py`, catálogo de IRs):

* sufixo do nome de arquivo: ``-USERIR`` (nome de painel NÃO muda — o display
  da GP-100 tem 12 chars e o canônico já pode usar os 12);
* a pasta é a mesma do canônico: a variante é refinamento **deste** patch.

Camada: application — nenhuma função lê disco, nenhuma imprime.
"""

from __future__ import annotations

import copy
from typing import Any

from gp100_architect.application.artefatos import PatchGerado
from gp100_architect.domain.errors import SpecInvalido
from gp100_architect.domain.validation import SLOT_IR_LOCAL
from gp100_architect.infrastructure.prst.codec import gerar_xml

__all__ = ['SUFIXO', 'gerar_variante', 'tem_captura']

SUFIXO = '-USERIR'


def tem_captura(ir_local: dict[str, Any], cab: str) -> bool:
    """O gabinete tem captura com slot declarado no `ir_local`?"""
    par = ir_local.get(cab)
    return isinstance(par, dict) and bool(par.get('captura')) and bool(par.get('slot'))


def _slot_para_indice(slot: str, cab: str) -> int:
    """`"User IR 5"` → `4` (o formato `.prst` usa índice 0-based do slot).

    Usa a MESMA regex do validador do domínio (`SLOT_IR_LOCAL`): uma só
    definição do formato — o defs reprova no carregamento, a aplicação reprova
    na derivação; nenhuma das duas aceita variação que a outra deixe passar.
    """
    casa = SLOT_IR_LOCAL.fullmatch(slot)
    if not casa:
        raise SpecInvalido(
            f"ir_local.{cab}.slot: {slot!r} não segue o formato 'User IR <N>' "
            '(N de 1 a 20) — corrija o defs; a variante -USERIR deriva daqui'
        )
    return int(casa.group(1)) - 1


def gerar_variante(
    base: PatchGerado,
    spec: dict[str, Any],
    *,
    ir_local: dict[str, Any],
    ir_index: dict[str, list[str]],
    templates: dict[tuple[str, str], dict[str, Any]],
    build_time: str | None = None,
) -> PatchGerado | None:
    """Deriva a variante `-USERIR` do patch canônico, **em memória**.

    `base` é o `PatchGerado` canônico e `spec`, o spec **final** que o gerou
    (author/notes já resolvidos). Devolve `None` quando o gabinete do patch não
    tem captura no banco local — sem variante, sem aviso (política dos 4
    passos: a variante é refinamento opcional).

    Diferença do spec: **um campo** (`ir_cab_user_slot`), derivado do slot de
    `ir_local`. O `ppName` no painel é o nome **canônico** — a variante é a
    substituta direta dele em palco, no mesmo slot do pedal; quem navega pelo
    display não precisa adivinhar o que carregou.
    """
    cab = spec.get('modules', {}).get('CAB', {}).get('name')
    if not tem_captura(ir_local, str(cab)):
        return None
    par = ir_local[str(cab)]

    slot = str(par['slot'])
    indice = _slot_para_indice(slot, str(cab))

    spec_var = copy.deepcopy(spec)
    spec_var['ir_cab_user_slot'] = indice
    prst = gerar_xml(spec_var, templates, build_time=build_time)

    documentacao = _render_doc(
        base=base,
        cab=str(cab),
        captura=str(par['captura']),
        slot=slot,
        ir_index=ir_index,
    )
    return PatchGerado(
        nome=f'{base.nome}{SUFIXO}',
        musica=base.musica,
        camada=base.camada,
        slot=base.slot,
        pasta=base.pasta,
        documentacao=documentacao,
        prst=prst,
    )


def _render_doc(
    base: PatchGerado,
    *,  # TODO(#90): snake_case já; nomes pt mantidos até o ciclo de revisão
    cab: str,
    captura: str,
    slot: str,
    ir_index: dict[str, list[str]],
) -> str:
    """Doc da variante: canônica com a seção 📡 reescrita para o estado com IR."""
    from gp100_architect.application.rendering import variante_md

    return variante_md.render(
        base.documentacao, nome=base.nome, cab=cab, captura=captura, slot=slot, ir_index=ir_index
    )
