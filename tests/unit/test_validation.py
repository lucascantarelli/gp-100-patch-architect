"""Validação do defs: o defs real passa, e cada erro diz onde e como corrigir.

Padrão do projeto (herdado do doc 21): a asserção não é "deu erro", é "o
relatório aponta o caminho JSON e a correção" — mensagem sem instrução é bug
do validador, não do usuário.
"""

from typing import Any

import pytest

from gp100_architect.domain.validation import Erros, validar

pytestmark = pytest.mark.unit


def relatorio(defs: dict[str, Any]) -> str:
    erros: Erros = validar(defs)
    assert not erros.ok(), 'esperava problema e o defs passou'
    return erros.relatorio()


def primeiro_patch(defs: dict[str, Any]) -> dict[str, Any]:
    return defs['songs'][0]['patches'][0]


def defs_minimo() -> dict[str, Any]:
    """Um defs do menor tamanho possível que passa em todas as regras."""
    return {
        'meta': {'projeto': 'teste'},
        'albums': {
            'AR': {
                'banda': 'Banda',
                'album': 'Álbum',
                'ano': 2026,
                'display': 'Banda — Álbum',
                'pasta': 'Banda',
                'rig': 'reference/15',
            }
        },
        'ir_local': {},
        'songs': [
            {
                'id': 'TEST1',
                'song': 'Teste',
                'idAlbum': 'AR',
                'bpm': 120,
                'resumo': 'música de teste',
                'referencias': [],
                'patches': [
                    {
                        'nome': 'TEST1BA',
                        'sufixo': 'BA',
                        'camada': 'Base',
                        'spec': {
                            'name': 'TEST1BA',
                            'type': 'Rock',
                            'modules': {'CAB': {'name': 'D', 'on': True}},
                        },
                        'doc': {
                            'guitarra': 'qualquer',
                            'teste': 'qualquer',
                            'irNota': 'fábrica',
                            'ajustes': [],
                            'evite': [],
                        },
                    }
                ],
            }
        ],
    }


# ── o que tem de passar ─────────────────────────────────────────────────────


def test_defs_minimo_e_valido():
    erros = validar(defs_minimo())
    assert erros.ok(), erros.relatorio()


def test_defs_commitado_e_valido(defs_mutavel: dict[str, Any]):
    erros = validar(defs_mutavel)
    assert erros.ok(), erros.relatorio()


# ── topo ────────────────────────────────────────────────────────────────────


def test_defs_vazio_acusa_os_tres_blocos_obrigatorios():
    texto = relatorio({})
    assert 'albums: ausente' in texto or 'albums' in texto
    for caminho in ('albums', 'songs', 'ir_local'):
        assert f'✗ {caminho}' in texto
    assert 'declare songs' in texto


# ── estruturais (defs real mutado) ──────────────────────────────────────────


def test_id_album_inexistente_aponta_ids_validos(defs_mutavel: dict[str, Any]):
    defs_mutavel['songs'][0]['idAlbum'] = 'ZZ'
    texto = relatorio(defs_mutavel)
    assert "songs[0].idAlbum: 'ZZ' não existe em albums" in texto
    assert 'ids válidos: ' in texto


def test_bpm_fora_do_range(defs_mutavel: dict[str, Any]):
    defs_mutavel['songs'][0]['bpm'] = 400
    assert 'fora do range 30–300' in relatorio(defs_mutavel)


def test_nome_de_painel_acima_de_12_chars_sugere_renomear(defs_mutavel: dict[str, Any]):
    patch = primeiro_patch(defs_mutavel)
    patch['nome'] = 'NOMEMUITOLONGO'
    texto = relatorio(defs_mutavel)
    assert 'máx. 12 (limite do painel da GP-100)' in texto


def test_camada_desconhecida_lista_as_validas(defs_mutavel: dict[str, Any]):
    primeiro_patch(defs_mutavel)['sufixo'] = 'ZZ'
    texto = relatorio(defs_mutavel)
    assert "'ZZ' não é uma camada conhecida" in texto
    assert 'BA' in texto and 'SO' in texto


def test_genero_invalido(defs_mutavel: dict[str, Any]):
    primeiro_patch(defs_mutavel)['spec']['type'] = 'Reggae'
    assert 'não é gênero válido' in relatorio(defs_mutavel)


def test_modulo_fora_da_cadeia(defs_mutavel: dict[str, Any]):
    primeiro_patch(defs_mutavel)['spec']['modules']['VOX'] = {'name': 'Harmony', 'on': True}
    assert 'módulo fora da cadeia fixa' in relatorio(defs_mutavel)


def test_patch_sem_cab(defs_mutavel: dict[str, Any]):
    primeiro_patch(defs_mutavel)['spec']['modules'].pop('CAB', None)
    assert 'todo patch single fw 2.1 declara CAB' in relatorio(defs_mutavel)


def test_doc_sem_guitarra(defs_mutavel: dict[str, Any]):
    primeiro_patch(defs_mutavel)['doc'].pop('guitarra')
    assert 'doc.guitarra: obrigatório' in relatorio(defs_mutavel)


def test_ir_local_orfao(defs_mutavel: dict[str, Any]):
    defs_mutavel['ir_local']['CAB Inexistente'] = {'captura': 'x', 'slot': 'User IR 9'}
    texto = relatorio(defs_mutavel)
    assert 'nenhum patch usa este CAB' in texto
    assert 'remova a entrada' in texto


# ── parâmetros (defs mínimo, mutação cirúrgica) ─────────────────────────────


def com_modulo(modulo: str, modelo: str, params: dict[str, Any]) -> dict[str, Any]:
    """Defs mínimo com um módulo extra já setado — mutação cirúrgica isolada."""
    defs = defs_minimo()
    defs['songs'][0]['patches'][0]['spec']['modules'][modulo] = {
        'name': modelo,
        'on': True,
        'params': params,
    }
    return defs


def test_indice_de_parametro_invalido():
    assert 'índice inválido' in relatorio(com_modulo('DLY', 'Sweet', {'15': 50}))


def test_param_nao_numerico_e_rejeitado():
    assert 'valor não numérico' in relatorio(com_modulo('DLY', 'Sweet', {'0': 'alto'}))


def test_bool_nao_passa_como_parametro():
    """`True` é `int` em Python — aceitar bool seria um furo silencioso."""
    assert 'valor não numérico' in relatorio(com_modulo('NR', 'Gate 1', {'0': True}))


def test_tempo_em_ms_tem_limite_proprio():
    texto = relatorio(com_modulo('DLY', 'Sweet', {'1': 4000}))
    assert 'Time=4000 ms fora de 0–1000' in texto


def test_percentual_acima_de_100_acusa_range_do_modelo():
    assert 'Mix=130' in relatorio(com_modulo('DLY', 'Sweet', {'0': 130}))


# ── momentos de toggle ──────────────────────────────────────────────────────


def test_toggle_de_amp_e_proibido(defs_mutavel: dict[str, Any]):
    patch = primeiro_patch(defs_mutavel)
    patch['doc']['momentos'] = [{'nome': 'Refrão', 'mods': [['AMP', 'OFF']], 'quando': 'no refrão'}]
    assert 'toggle de AMP/CAB é proibido' in relatorio(defs_mutavel)


def test_estado_de_toggle_precisa_ser_on_ou_off(defs_mutavel: dict[str, Any]):
    patch = primeiro_patch(defs_mutavel)
    patch['doc']['momentos'] = [
        {'nome': 'Refrão', 'mods': [['MOD', 'LIGADO']], 'quando': 'no refrão'}
    ]
    assert "estado 'LIGADO' inválido" in relatorio(defs_mutavel)


def test_momento_sem_campo_obrigatorio(defs_mutavel: dict[str, Any]):
    patch = primeiro_patch(defs_mutavel)
    patch['doc']['momentos'] = [{'nome': 'Refrão', 'mods': [['MOD', 'ON']]}]
    assert 'momentos[0].quando: obrigatório' in relatorio(defs_mutavel)
