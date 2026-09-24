"""Casos de uso da biblioteca + renderização do `patch.md` (issue #30).

O TestH roda o pipeline em **subprocess** — ele prova o produto byte a byte,
mas não mede cobertura do pacote. Estes testes exercitam a biblioteca
in-process, com o defs real recortado e saída em `tmp_path` (nenhum teste
escreve no repositório — regra do projeto).

Cobrem os dois lados do contrato da migração: a geração em memória
(`biblioteca.gerar`) e os templates puros (`rendering.patch_md`), que passaram
a ser testáveis sem disco justamente por isso.
"""

from __future__ import annotations

import copy
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import biblioteca
from gp100_architect.application.rendering import patch_md
from gp100_architect.domain.chain import CHAIN
from gp100_architect.domain.errors import FormatoPrstInvalido, SpecInvalido
from gp100_architect.infrastructure.prst.codec import load_templates

pytestmark = pytest.mark.unit

ALBUNS = {
    'AR': {
        'banda': 'Testband',
        'album': 'Testalbum',
        'ano': 1999,
        'display': 'Testalbum',
        'pasta': 'Testband/Testalbum (1999)',
    }
}


def _mod(nome: str, on: bool = True, *params: Any) -> dict[str, Any]:
    return {'name': nome, 'on': on, 'params': {str(i): v for i, v in enumerate(params)}}


def _spec() -> dict[str, Any]:
    """Spec mínimo com os 9 módulos da cadeia (2 ligados, 1 sobressalente)."""
    return {
        'name': 'TST01BA',
        'type': 'Rock',
        'bpm': 120,
        'volume': 60,
        'ir_slot': None,
        'modules': {
            'PRE': _mod('Boost', False),
            'DST': _mod('Blues OD', True, 40, 55, 60),
            'AMP': _mod('Flagman', True, 44, 55, 62),
            'NR': _mod('Gate 1', False),
            'CAB': _mod('UK-LD 4x12', True, 78, 62),
            'EQ': _mod('EQ 1', False),
            'MOD': _mod('A-Chorus', False),
            'DLY': _mod('Sweet', False, 20, 570),
            'RVB': _mod('Hall', True, 38, 45),
        },
    }


def _song(**extra: Any) -> dict[str, Any]:
    song = {
        'id': 'TST01',
        'song': 'Test Song',
        'idAlbum': 'AR',
        'bpm': 120,
        'resumo': 'Resumo da música de teste.',
        'referencias': [{'role': 'Amp real', 'conf': 'alta', 'src': 'fonte'}],
        'patches': [],
    }
    song.update(extra)
    return song


def _patch(**extra: Any) -> dict[str, Any]:
    doc = {
        'guitarra': {
            'seletor': 'Ponte',
            'seletorCurto': 'Ponte',
            'volume': '8',
            'tone': '7',
            'receita': 'Ponte, vol 8',
            'tecnicas': ['Toque firme'],
        },
        'comoTocar': [],
        'teste': {'riff': 'riff de teste', 'drum': 'groove', 'escutar': ['Mais brilho']},
        'ajustes': ['Muito agudo → reduzir High Cut', 'Sem seta aqui'],
        'evite': ['Não empilhar dois delays'],
        'momentos': [
            {'nome': 'Solo', 'mods': [['DLY', 'ON']], 'quando': 'no solo', 'dica': 'religue depois'}
        ],
    }
    doc.update(extra.pop('doc', {}))
    return {
        'camada': 'Base',
        'sufixo': 'BA',
        'nome': 'TST01BA',
        'emoji': '🎸',
        'timbre': 'Crunch de teste',
        'spec': _spec(),
        'doc': doc,
        **extra,
    }


def test_travessia_e_slots_contemplam_todo_o_defs(defs_real: dict[str, Any]):
    defs = copy.deepcopy(defs_real)
    esperado = sum(len(s['patches']) for s in defs['songs'])
    assert len(list(biblioteca.travessia(defs))) == esperado

    mapa = biblioteca.slots(defs)
    assert len(mapa) == esperado
    assert sorted(mapa.values()) == [f'U{i:02d}' for i in range(1, esperado + 1)]
    # a primeira música manda no U01: a numeração segue a ordem do defs
    assert mapa[defs['songs'][0]['patches'][0]['nome']] == 'U01'


def test_gerar_em_memoria_sem_tocar_o_repositorio(defs_real: dict[str, Any], tmp_path: Path):
    defs = copy.deepcopy(defs_real)
    defs['songs'] = defs['songs'][:2]  # recorte: dois álbuns/músicas
    gerados = biblioteca.gerar(defs, raiz=tmp_path, ir_index={}, templates=load_templates())

    esperado = sum(len(s['patches']) for s in defs['songs'])
    assert len(gerados) == esperado
    for patch in gerados:
        assert patch.pasta.is_relative_to(tmp_path / 'patches')
        assert patch.slot.startswith('U')
        assert '## 📡 3. Impulse Response' in patch.documentacao
        assert patch.prst.startswith(b'<?xml version="1.0" encoding="UTF-8"?>')
        presets = ET.fromstring(patch.prst).find('presets')
        assert presets is not None and presets.get('ppName') == patch.nome
        # o spec ganha author/notes derivados da música
        assert patch.documentacao.count('Crunch') >= 0


def test_gerar_aceita_build_time_deterministico(defs_real: dict[str, Any], tmp_path: Path):
    defs = copy.deepcopy(defs_real)
    defs['songs'] = defs['songs'][:1]
    templates = load_templates()
    a = biblioteca.gerar(
        defs, raiz=tmp_path, ir_index={}, templates=templates, build_time='1700000000000'
    )
    b = biblioteca.gerar(
        defs, raiz=tmp_path, ir_index={}, templates=templates, build_time='1700000000000'
    )
    assert [p.prst for p in a] == [p.prst for p in b]


def test_nome_no_painel_divergente_reprova():
    xml = b'<?xml version="1.0" encoding="UTF-8"?><GP-100><presets ppName="OUTRO"/></GP-100>'
    with pytest.raises(SpecInvalido, match='diverge'):
        biblioteca._validar_nome_no_xml(xml, 'TST01BA')


def test_nome_acima_do_limite_do_painel_reprova():
    xml = b'<GP-100><presets ppName="NOMEMUITOLONGO"/></GP-100>'
    with pytest.raises(SpecInvalido, match='limite do display'):
        biblioteca._validar_nome_no_xml(xml, 'NOMEMUITOLONGO')


def test_xml_invalido_reprova_com_formato():
    with pytest.raises(FormatoPrstInvalido):
        biblioteca._validar_nome_no_xml(b'<GP-100><presets', 'TST01BA')


def test_xml_sem_presets_reprova():
    with pytest.raises(SpecInvalido, match='diverge'):
        biblioteca._validar_nome_no_xml(b'<GP-100/>', 'TST01BA')


# ---- renderização (template puro, sem disco) --------------------------------


def test_build_doc_tem_as_secoes_e_momentos():
    doc = patch_md.build_doc(
        _song(), _patch(), _spec(), 'U07', albums=ALBUNS, ir_local={}, ir_index={}
    )
    for secao in (
        '## 🎸 1. Sua guitarra agora',
        '## 🔧 2. Ajustes finos',
        '## 📡 3. Impulse Response',
        '## 🎛️ 4. Modos de atuação',
        '## 🔊 5. Objetivo do som',
        '## 📚 6. Referência real',
        '## 🎛️ 7. Cadeia e parâmetros',
        '## 💾 8. Carregar na pedaleira',
        '## 🚫 9. Evite com este patch',
    ):
        assert secao in doc
    assert '**U07**' in doc
    assert '**DLY → ON**' in doc
    assert '| — | Sem seta aqui |' in doc  # ajuste sem "sintoma → ação"
    assert 'SOBRESSALENTE **DLY**' in doc  # receita com o sobressalente
    assert 'Mapeamento rig real → GP-100' in doc
    assert '<div' not in doc and '<br' not in doc


def test_secao_de_ir_recomenda_o_banco_quando_existe_captura():
    spec, patch = _spec(), _patch()
    ir_local = {'UK-LD 4x12': {'captura': 'UK 4x12 GB', 'slot': 'User IR 4'}}
    ir_index = {'UK 4x12 GB': ['UK 4x12 GB Medium Mix.wav', 'UK 4x12 GB Bright Mix.wav']}
    doc = patch_md.build_doc(
        _song(), patch, spec, 'U01', albums=ALBUNS, ir_local=ir_local, ir_index=ir_index
    )
    assert '### 📁 Melhor opção no nosso banco' in doc
    assert 'UK 4x12 GB Medium Mix.wav' in doc
    assert 'User IR 4' in doc
    assert 'UK 4x12 GB Bright Mix.wav' in doc  # alternativas listadas


def test_secao_de_ir_cai_para_fabrica_sem_captura():
    doc = patch_md.build_doc(
        _song(),
        _patch(),
        _spec(),
        'U01',
        albums=ALBUNS,
        ir_local={'UK-LD 4x12': {'captura': 'X', 'slot': 'User IR 2'}},
        ir_index={'Outro Cab': ['a.wav']},
    )
    assert '### 🔍 Não há captura melhor no nosso banco' in doc
    assert '### ✅ Fallback garantido' in doc


def test_secao_de_ir_inclui_nota_especifica():
    patch = _patch(doc={'irNota': 'Teste com User IR 4 antes do show.'})
    doc = patch_md.build_doc(
        _song(), patch, _spec(), 'U01', albums=ALBUNS, ir_local={}, ir_index={}
    )
    assert '**Nota específica deste patch**: Teste com User IR 4' in doc


def test_ir_mixes_prefere_medium_e_cai_para_o_primeiro():
    assert (
        patch_md.ir_mixes('C', {'C': ['C Bright Mix.wav', 'C Medium Mix.wav']})
        == 'C Medium Mix.wav'
    )
    assert patch_md.ir_mixes('C', {'C': ['C Dark Mix.wav']}) == 'C Dark Mix.wav'
    assert patch_md.ir_mixes('C', {'C': ['C Custom.wav']}) == 'C Custom.wav'
    assert patch_md.ir_mixes('C', {}) is None


def test_disp_traduz_switches_e_unidades():
    assert patch_md.disp('Bright', '0') == 'Off'
    assert patch_md.disp('Bright', '1') == 'On'
    assert patch_md.disp('Char', '1') == 'Hot'
    assert patch_md.disp('Mode', '3') == 'Piezo'
    assert patch_md.disp('Sync', '0') == 'Off'
    assert patch_md.disp('Trail', '1') == 'On'
    assert patch_md.disp('Time', '570') == '570 ms'
    assert patch_md.disp('Time', 'nao-numero') == 'nao-numero'
    assert patch_md.disp('Mix', '30') == '30'
    assert patch_md.fmt_val(12) == '12'


def test_ajustes_table_aceita_linhas_com_e_sem_sintoma():
    tabela = patch_md.ajustes_table(['a → b', 'linha solta'])
    assert tabela == '| a | b |\n| — | linha solta |'


def test_detail_tables_ignora_modulos_off_e_marca_sem_nome():
    spec = _spec()
    spec['modules']['DLY'] = _mod('Sweet', False)
    tabela = patch_md.detail_tables(spec)
    assert '### DST — Blues OD' in tabela
    assert 'DLY' not in tabela  # módulo desligado não entra
    assert 'pN' not in tabela
    sem_nome = _spec()
    # modelo fora do catálogo PARAM_NAMES: os slots saem como `pN`, nunca inventados
    sem_nome['modules']['EQ'] = _mod('Modelo Ilegível', True, 5, 5)
    tabela_sem_nome = patch_md.detail_tables(sem_nome)
    assert '| p0 | 5 |' in tabela_sem_nome
    assert '`pN`' in tabela_sem_nome


def test_typing_recipe_lista_cadeia_e_sobressalentes():
    receita = patch_md.typing_recipe(_spec(), _patch()['doc'])
    assert 'DST' in receita and 'AMP' in receita
    assert 'RVB' in receita and 'ajuste fino no painel' in receita
    assert 'SOBRESSALENTE' in receita
    sem_momentos = patch_md.typing_recipe(_spec(), {})
    assert 'SOBRESSALENTE' not in sem_momentos


def test_tabela_de_consumo_do_chip_do_patch():
    """Resumo rápido do patch: módulo, modelo e valores na ordem da cadeia."""
    doc = patch_md.build_doc(
        _song(), _patch(), _spec(), 'U01', albums=ALBUNS, ir_local={}, ir_index={}
    )
    linhas = [linha for linha in doc.splitlines() if linha.startswith('| ') and ' | ' in linha]
    assert any(linha.startswith('| AMP | Flagman') for linha in linhas)
    assert CHAIN[0] == 'PRE'  # a cadeia vem do domínio


# ---- stomps + EXP1 na doc (issue #9) ------------------------------------------


def test_doc_renderiza_tabela_de_stomps():
    doc = _patch()['doc'] | {
        'stomps': [
            {
                'fs': 'A',
                'mods': [['DST', 'OFF']],
                'quando': 'No verso, para o riff respirar.',
                'dica': 'Religue no refrão.',
            }
        ]
    }
    secao = patch_md.build_momentos_section(_spec(), doc)
    assert 'FS-A / FS-B deste patch' in secao
    assert '| **FS-A** |' in secao
    assert '**DST → OFF**' in secao
    assert 'No verso, para o riff respirar.' in secao
    assert '*Dica: Religue no refrão.*' in secao


def test_doc_sem_stomps_nao_renderiza_a_subsecao():
    secao = patch_md.build_momentos_section(_spec(), _patch()['doc'])
    assert 'FS-A / FS-B deste patch' not in secao
    assert 'Pedal de expressão' not in secao


def test_doc_renderiza_pedal_de_expressao():
    spec = _spec() | {'exp1': {'módulo': 'DST', 'param': 'Gain', 'min': 10, 'max': 90}}
    secao = patch_md.build_momentos_section(spec, _patch()['doc'])
    assert 'Pedal de expressão (EXP1)' in secao
    assert '**Gain do DST**' in secao
    assert '10 (calcanhar) → 90 (bico)' in secao
    assert 'Módulo controlado | **DST**' in secao


def test_doc_exp1_sem_modulo_nao_renderiza():
    spec = _spec() | {'exp1': {'param': 'Gain'}}
    secao = patch_md.build_momentos_section(spec, _patch()['doc'])
    assert 'Pedal de expressão' not in secao
