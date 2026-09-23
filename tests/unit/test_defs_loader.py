"""Carregador do defs: valida sempre, e o caminho é apontável por ambiente.

O ponto destes testes é a regra do achado M2 do review: **não existe carregar
sem validar**. Um defs quebrado falha na porta, com relatório, e não no meio do
pipeline longe da causa.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.domain.errors import DefsInvalidos, Gp100Error
from gp100_architect.infrastructure import defs as carregador

pytestmark = pytest.mark.unit


def test_defs_padrao_aponta_para_a_fonte_unica(raiz: Path):
    assert carregador.DEFS_PADRAO == raiz / 'tools' / 'patches-defs.json'
    assert carregador.raiz_do_repo() == raiz


def test_carregar_e_validar_aceita_o_defs_commitado():
    dados = carregador.carregar_e_validar()
    assert dados['songs'] and dados['albums']


def test_variante_de_ambiente_tem_prioridade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """O override existe para testes trabalharem em tmpdir, nunca no repositório."""
    alvo = tmp_path / 'defs.json'
    alvo.write_text('{"albums": {}, "songs": [], "ir_local": {}}', encoding='utf-8')
    monkeypatch.setenv(carregador.VAR_DEFS, str(alvo))
    assert carregador.caminho_defs() == alvo


def test_defs_invalido_levanta_defs_invalidos_com_relatorio(tmp_path: Path):
    quebrado = tmp_path / 'quebrado.json'
    quebrado.write_text(json.dumps({'albums': {}, 'songs': [], 'ir_local': {}}), encoding='utf-8')
    with pytest.raises(DefsInvalidos) as erro:
        carregador.carregar_e_validar(quebrado)
    mensagem = str(erro.value)
    assert 'problema(s) no patches-defs.json' in mensagem
    assert '✗ albums' in mensagem
    # `ir_local: {}` é válido (biblioteca sem captura local) — albums vazio e
    # songs vazio são os dois problemas reais deste arquivo.
    assert erro.value.problemas == 2


def test_erro_de_dominio_e_previsto_e_nao_vaza_para_o_usuario_como_bug():
    assert issubclass(DefsInvalidos, Gp100Error)


def test_carregar_nao_valida_o_que_e_util_para_diagnostico(tmp_path: Path):
    """`carregar` é a porta de diagnóstico: entrega o JSON cru, mesmo inválido."""
    arquivo = tmp_path / 'cru.json'
    dados: dict[str, Any] = {'albums': {}}
    arquivo.write_text(json.dumps(dados), encoding='utf-8')
    assert carregador.carregar(arquivo) == dados
