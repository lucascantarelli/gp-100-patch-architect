"""Writer do formato "all" da GP-100 (issue #83 — parte de software).

A premissa não verificada do ADR-0013: o firmware distingue export *single*
de *all* (origem do erro "Wrong patch file type (single/all)"), mas nunca
testamos se o aparelho/GP-100 Edits **importam** um arquivo "all" gerado por
nós. Este módulo fecha a parte de software da investigação: gera o candidato
de teste — mesmo contrato de bytes do codec single (CRLF, ordem de atributos,
timestamp determinístico), com `count="N"`, N blocos `<presets>` e o bloco
`<ppIRInfo>` (a diferença central do formato).

A linha da casa: **gerar é da aplicação, serializar é daqui** — o `<ppIRInfo>`
segue a regra do doc 15 (20 slots `ppIRInfo0..19`, `ppIRNum = 168820736+i`,
`ppIRCRC` obrigatório), e a APLICAÇÃO decide o que preencher a partir do
inventário de IRs do usuário (`data/ir-library.json`). Um "all" sem IRs locais
não precisa do bloco; os slots não cobertos ficam com CRC "0" e `ppIRCRCType`
"0" — candidato honesto para o teste de import.

Dois pontos de entrada: `gerar_xml_all` (a partir de specs, reusa o codec) e
`gerar_xml_all_de_singles` (a partir dos BYTES de singles já gerados — caminho
preferido da aplicação, pois o empacotamento já os tem em memória). Em ambos,
cada bloco `<presets>` é idêntico byte a byte ao single correspondente.

Camada: infrastructure. Funções PURAS: nenhum print, nenhum SystemExit; a
escrita em disco é da CLI.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Any

from gp100_architect.infrastructure.prst.codec import (
    BASE_IR_NUM,
    BUILD_TIME_PADRAO,
    gerar_xml,
)

__all__ = ['SLOTS_IR', 'SpecAllInvalido', 'gerar_xml_all', 'gerar_xml_all_de_singles']

SLOTS_IR = 20  # ppIRInfo0..19 (doc 15) — slots de User IR do aparelho


class SpecAllInvalido(ValueError):
    """Nenhum patch informado — o formato "all" exige ao menos um."""


def gerar_xml_all(
    specs: list[dict[str, Any]],
    templates: dict[tuple[str, str], dict[str, Any]],
    *,
    user_irs: list[dict[str, str]] | None = None,
    build_time: str | None = None,
) -> bytes:
    """Gera o XML formato "all" (N presets) a partir dos specs do codec single.

    `user_irs` (opcional) preenche o `<ppIRInfo>`: lista de dicts com `crc`
    e `crc_type` na ordem dos slots; o slot i recebe `ppIRNum = 168820736+i`.
    Slots além da lista (ou sem lista) saem com CRC "0".
    """
    if not specs:
        raise SpecAllInvalido('formato "all" sem patches: informe ao menos um spec')
    blocos = [_bloco_presets(gerar_xml(spec, templates, build_time)) for spec in specs]
    return _montar(blocos, user_irs=user_irs, build_time=build_time)


def gerar_xml_all_de_singles(
    singles: list[bytes],
    *,
    user_irs: list[dict[str, str]] | None = None,
    build_time: str | None = None,
) -> bytes:
    """Monta o formato "all" a partir dos BYTES de singles já gerados.

    Cada bloco `<presets>` é extraído dos bytes — e, por construção, idêntico
    ao single publicado. É o caminho do empacotamento futuro (`biblioteca.gerar`
    devolve os singles em memória).
    """
    if not singles:
        raise SpecAllInvalido('formato "all" sem patches: informe ao menos um single')
    return _montar([_bloco_presets(s) for s in singles], user_irs=user_irs, build_time=build_time)


def _montar(
    blocos: list[bytes],
    *,
    user_irs: list[dict[str, str]] | None,
    build_time: str | None,
) -> bytes:
    """`count=N` + `<ppIRInfo>` opcional + os blocos `<presets>`; CRLF igual ao single."""
    root = ET.Element('GP-100')
    info = ET.SubElement(root, 'preset_info')
    info.set('software', '1.2.0')
    info.set('firmware', '2.1')  # firmware atual — 2.0 no export antigo rejeita
    info.set('product', 'GP-100')
    info.set('count', str(len(blocos)))
    info.set('platform', 'WINDOWS')
    info.set('time', build_time or os.environ.get('GP100_BUILD_TIME', BUILD_TIME_PADRAO))
    _anexar_ir_info(root, user_irs)
    for bloco in blocos:
        root.append(ET.fromstring(bloco.decode('utf-8')))
    return _serializar(root)


def _anexar_ir_info(root: ET.Element, user_irs: list[dict[str, str]] | None) -> None:
    """`<ppIRInfo>` com os 20 slots do doc 15 — presente só com IRs a declarar.

    O `ppIRCRC` dos slots é dado do export de fábrica (doc 15: o editor
    recalcula ao carregar IRs novas); slots sem IR informado saem "0".
    """
    if not user_irs:
        return
    ir_info = ET.SubElement(root, 'ppIRInfo')
    ir_info.set('ppIRNumInfo', str(SLOTS_IR))
    for i in range(SLOTS_IR):
        slot = ET.SubElement(ir_info, f'ppIRInfo{i}')
        slot.set('ppIRNum', str(BASE_IR_NUM + i))
        ir = user_irs[i] if i < len(user_irs) else None
        slot.set('ppIRCRC', str(ir['crc']) if ir and ir.get('crc') is not None else '0')
        slot.set('ppIRCRCType', str(ir.get('crc_type', '0')) if ir else '0')


def _bloco_presets(single: bytes) -> bytes:
    """O bloco `<presets>…</presets>` de um XML single completo."""
    texto = single.decode('utf-8')
    inicio = texto.index('<presets')
    fim = texto.rindex('</presets>') + len('</presets>')
    return texto[inicio:fim].encode('utf-8')


def _serializar(root: ET.Element) -> bytes:
    """Mesma serialização do codec single (CRLF + cabeçalho)."""
    ET.indent(root, space='  ')
    xml = ET.tostring(root, encoding='unicode')
    linhas = '\r\n'.join(xml.splitlines()) + '\r\n'
    return ('<?xml version="1.0" encoding="UTF-8"?>\r\n\r\n' + linhas).encode('utf-8')
