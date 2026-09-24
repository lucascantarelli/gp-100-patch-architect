"""Seção 📡 da variante -USERIR — edição do doc canônico (issue #10).

A variante NÃO re-renderiza o `patch.md`: ela nasce do documento canônico com
**uma seção reescrita** — a 📡 (Impulse Response). No canônico, ela instrui o
passo opcional de carregar IR; na variante a IR já está no `.prst`, então a
seção vira o pré-requisito do slot + ajuste fino. Todo o resto (guitarra,
cadeia, momentos, protocolo) é idêntico por construção — é isso que garante
que variante e canônico nunca divergem em conteúdo.

As regexes são ancoradas no texto exato que `patch_md.build_ir_section`
produz. Se o canônico mudar, os testes da variante quebram aqui primeiro —
de propósito: edição estrutural exige atualização consciente.

Camada: application/rendering — função pura, nenhuma leitura de disco.
"""

from __future__ import annotations

import re

from gp100_architect.application.rendering.patch_md import ir_mixes
from gp100_architect.domain.errors import SpecInvalido

__all__ = ['render']

# prefixo do título da seção 📡 no doc canônico (o sufixo pode evoluir; o
# "## 📡 3." é a assinatura estrutural da seção no documento prático-primeiro)
_TITULO_CANONICO = '## 📡 3. Impulse Response'


def render(
    documentacao: str,
    *,
    nome: str,
    cab: str,
    captura: str,
    slot: str,
    ir_index: dict[str, list[str]],
) -> str:
    """Doc da variante: canônico com a seção 📡 trocada pelo estado com IR.

    `documentacao` é o `patch.md` canônico inteiro; `nome`, o nome do patch
    (sem sufixo); `cab`/`captura`/`slot`, os dados do `ir_local` do gabinete;
    `ir_index`, o índice do banco local (sem o arquivo exato, o passo 1 instrui
    carregar a captura sem caminho).
    """
    arquivo = ir_mixes(captura, ir_index) if ir_index.get(captura) else None
    nova = _secao_user_ir(nome=nome, cab=cab, captura=captura, slot=slot, arquivo=arquivo)
    padrao = re.compile(rf'{re.escape(_TITULO_CANONICO)}[^\n]*\n.*?(?=\n### 🌍)', re.DOTALL)
    nova_doc, substituicoes = padrao.subn(nova, documentacao, count=1)
    if substituicoes != 1:
        raise SpecInvalido(
            f'{nome}: patch.md canônico sem a seção 📡 no formato esperado — '
            'patch_md.build_ir_section mudou; atualize o _secao_user_ir do variante_md'
        )
    return nova_doc


def _secao_user_ir(*, nome: str, cab: str, captura: str, slot: str, arquivo: str | None) -> str:
    """A seção 📡 da variante: IR já no `.prst`, slot é pré-requisito."""
    num = slot.split()[-1]
    passo_1: tuple[str, ...]
    if arquivo:
        passo_1 = (
            f'1. No **GP-100 Edits** → IR Manager, carregue no **{slot}** o arquivo:',
            f'   `impulse_responses/Origin Effects - IR-Cab Library V3/44.1kHz Origin Effects '
            f'IR Cab Library/{captura}/{arquivo}`',
        )
    else:
        passo_1 = (
            f'1. No **GP-100 Edits** → IR Manager, carregue no **{slot}** a captura '
            f'**{captura}** do banco `impulse_responses/`:',
        )
    return '\n'.join(
        [
            '## 📡 3. Impulse Response (CAB) — variante com User IR',
            '',
            f'**O que está no arquivo `.prst` agora**: a captura **{captura}** no **{slot}** '
            f'do banco de User IRs. Este arquivo é a **variante experimental** de `{nome}` — '
            f'mesma cadeia, mesmos parâmetros; a única diferença é o CAB apontar para a IR '
            f'do slot em vez do gabinete de fábrica `{cab}`.',
            '',
            f'> ⚠️ **Experimental**: valide no aparelho antes de levar ao palco. O canônico '
            f'`{nome}.prst` (CAB de fábrica) continua funcionando em qualquer GP-100, sem '
            f'carregar IR — a variante é refinamento, não substituição obrigatória.',
            '',
            '### ✅ Pré-requisito — a IR no slot',
            '',
            'A variante **só reproduz a captura** com o arquivo certo carregado no slot '
            '(o `.prst` guarda o número do slot, não o áudio):',
            '',
            *passo_1,
            f'2. Importe **{nome}-USERIR.prst** — o bloco CAB já aponta para **User IR {num}**; '
            'nada para trocar no patch.',
            '3. Afine no próprio CAB: **High Cut 6000–8500 Hz** a gosto (fizz → baixe), '
            '**Level** comece em 0 e compare com o bypass.',
            '',
        ]
    )
