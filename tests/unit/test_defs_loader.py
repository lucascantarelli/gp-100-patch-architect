"""Carregador do defs (schema v2): fragmentos por álbum, sempre validados.

O ponto destes testes é a regra do achado M2 do review: **não existe carregar
sem validar**. Um defs quebrado falha na porta, com relatório, e não no meio do
pipeline longe da causa. No schema v2 (issue #8) o loader também é o guarda da
estrutura: fragmento fora do manifesto, manifesto apontando arquivo ausente,
música fora de ordem e o `idAlbum` do fragmento reprovam AQUI, com o caminho do
arquivo no relatório.

Todos os testes montam `data/defs/` em `tmp_path` — nenhum escreve no repo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.domain.errors import DefsInvalidos, Gp100Error
from gp100_architect.infrastructure import defs as carregador

pytestmark = pytest.mark.unit


# ---- fábrica de fragmentos (o mínimo que o loader e o domínio exigem) --------


def _album(**extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        'banda': 'Banda',
        'album': 'Álbum',
        'ano': 1999,
        'display': 'Álbum',
        'pasta': 'Banda/Álbum (1999)',
        'rig': 'rig do álbum',
    }
    base.update(extra)
    return base


def _song(idx: int, chave: str) -> dict[str, Any]:
    return {
        'id': f'T{idx:02d}',
        'song': f'Música {idx}',
        'idAlbum': chave,
        'bpm': 100,
        'resumo': 'resumo',
        'referencias': [],
        'patches': [
            {
                'nome': f'T{idx:02d}BA',
                'camada': 'Base',
                'sufixo': 'BA',
                'emoji': '🎸',
                'timbre': 't',
                'spec': {},
                'doc': {},
            }
        ],
    }


def _fragmento(chave: str, n_musicas: int = 1, **extra: Any) -> dict[str, Any]:
    frag: dict[str, Any] = {
        'idAlbum': chave,
        'album': _album(),
        'songs': [_song(i + 1, chave) for i in range(n_musicas)],
    }
    frag.update(extra)
    return frag


def _escrever(diretorio: Path, manifesto: list[str], *frags: dict[str, Any]) -> Path:
    diretorio.mkdir(parents=True, exist_ok=True)
    for frag in frags:
        (diretorio / f'{frag["idAlbum"]}.json').write_text(
            json.dumps(frag, ensure_ascii=False), encoding='utf-8'
        )
    (diretorio / carregador.MANIFESTO).write_text(json.dumps(manifesto), encoding='utf-8')
    return diretorio


# ---- estrutura aceita --------------------------------------------------------


def test_defs_padrao_aponta_para_o_diretorio_de_fragmentos(raiz: Path):
    assert carregador.DEFS_PADRAO == raiz / 'data' / 'defs'
    assert carregador.raiz_do_repo() == raiz


def test_consolidar_devolve_o_shape_do_monolito(tmp_path: Path):
    dir_ = _escrever(
        tmp_path / 'defs',
        ['AR', 'ZP'],
        _fragmento('AR', 2, meta={'regrasNomenclatura': ['r']}),
        _fragmento('ZP', 1, ir_local={'UK-LD 4x12': {'captura': 'C', 'slot': 'User IR 1'}}),
    )
    dados = carregador.consolidar(dir_)
    assert list(dados) == ['meta', 'albums', 'ir_local', 'songs']
    assert list(dados['albums']) == ['AR', 'ZP']  # ordem VEM do manifesto
    assert [s['idAlbum'] for s in dados['songs']] == ['AR', 'AR', 'ZP']
    assert dados['meta'] == {'regrasNomenclatura': ['r']}  # meta declarado no 1º
    assert list(dados['ir_local']) == ['UK-LD 4x12']  # ir_local por fragmento


def test_carregar_aceita_json_unico_para_diagnostico(tmp_path: Path):
    unico = tmp_path / 'defs.json'
    dados: dict[str, Any] = {'albums': {}, 'songs': [], 'ir_local': {}}
    unico.write_text(json.dumps(dados), encoding='utf-8')
    assert carregador.carregar(unico) == dados


def test_variante_de_ambiente_tem_prioridade(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """O override existe para testes trabalharem em tmpdir, nunca no repositório."""
    alvo = tmp_path / 'defs'
    _escrever(alvo, ['AR'], _fragmento('AR'))
    monkeypatch.setenv(carregador.VAR_DEFS, str(alvo))
    assert carregador.caminho_defs() == alvo
    assert carregador.carregar()['songs'][0]['idAlbum'] == 'AR'


def test_erro_de_dominio_e_previsto_e_nao_vaza_para_o_usuario_como_bug():
    assert issubclass(DefsInvalidos, Gp100Error)


# ---- o defs real passa por tudo ----------------------------------------------


def test_carregar_e_validar_no_defs_do_repo(raiz: Path):
    """O defs commitado (fragmentos) passa pela estrutura + validação do domínio."""
    dados = carregador.carregar_e_validar()
    assert dados['songs'] and dados['albums']
    # blocos contíguos por álbum, na ordem do manifesto (61 músicas / 7 álbuns)
    vistos = [
        s['idAlbum']
        for i, s in enumerate(dados['songs'])
        if i == 0 or s['idAlbum'] != dados['songs'][i - 1]['idAlbum']
    ]
    assert vistos == list(dados['albums'])


def test_diretorio_ausente_tera_mensagem_do_schema_v2(tmp_path: Path):
    with pytest.raises(DefsInvalidos) as erro:
        carregador.consolidar(tmp_path / 'nao-existe')
    assert 'schema v2' in str(erro.value)


# ---- regras do schema v2 (o loader reprova, com caminho do arquivo) ----------


def test_fragmento_fora_do_manifesto_reprova(tmp_path: Path):
    dir_ = _escrever(tmp_path / 'defs', ['AR'], _fragmento('AR'))
    (dir_ / 'ZZ.json').write_text(json.dumps(_fragmento('ZZ')), encoding='utf-8')
    with pytest.raises(DefsInvalidos) as erro:
        carregador.consolidar(dir_)
    msg = str(erro.value)
    assert 'ZZ.json' in msg and 'FORA do manifesto' in msg


def test_manifesto_sem_o_arquivo_correspondente_reprova(tmp_path: Path):
    dir_ = _escrever(tmp_path / 'defs', ['AR', 'ZP'], _fragmento('AR'))
    with pytest.raises(DefsInvalidos) as erro:
        carregador.consolidar(dir_)
    assert 'declara "ZP" mas ZP.json não existe' in str(erro.value)


def test_fragmento_com_idalbum_errado_cai_na_regra_de_orfaos(tmp_path: Path):
    """`idAlbum: ZZ` dentro de AR.json: o ARQUIVO não corresponde a nenhuma chave
    declarada (o nome do fragmento é a chave) — a regra de órfãos pega, com o
    caminho exato, e o manifesto denuncia o arquivo ausente."""
    frag = _fragmento('AR')
    frag['idAlbum'] = 'ZZ'
    dir_ = _escrever(tmp_path / 'defs', ['AR'], frag)
    with pytest.raises(DefsInvalidos) as erro:
        carregador.consolidar(dir_)
    msg = str(erro.value)
    assert 'ZZ.json' in msg and 'FORA do manifesto' in msg
    assert 'declara "AR" mas AR.json não existe' in msg


def test_fragmento_sem_musicas_cai_na_validacao_do_dominio(tmp_path: Path):
    """Estrutura íntegra + álbum sem músicas: quem reprova é o domínio (`songs`
    vazia no consolidado), com o relatório acionável de sempre."""
    quebrado = _escrever(tmp_path / 'defs', ['AR'], _fragmento('AR', n_musicas=0))
    with pytest.raises(DefsInvalidos) as erro:
        carregador.carregar_e_validar(quebrado)
    msg = str(erro.value)
    assert 'songs: ausente ou não é lista' in msg
    assert 'corrija' in msg


def test_fragmento_sem_musicas_repassa_para_o_dominio(tmp_path: Path):
    """AR.json vazio: a sequência consolidada [ZP] é subsequência válida do
    manifesto — o loader passa e quem reprova é o domínio (`songs` vazia no
    consolidado inteiro). Divisão limpa: estrutura é do loader, dados do
    domínio."""
    dir_ = _escrever(
        tmp_path / 'defs', ['AR', 'ZP'], _fragmento('AR', n_musicas=0), _fragmento('ZP', 1)
    )
    dados = carregador.consolidar(dir_)  # estrutura ok
    assert [s['idAlbum'] for s in dados['songs']] == ['ZP']
    with pytest.raises(DefsInvalidos):
        carregador.carregar_e_validar(dir_)  # domínio reprova songs vazia


def test_musicas_trocadas_entre_fragmentos_reprovam(tmp_path: Path):
    """Música do ZP dentro de AR.json: a sequência consolidada vira [ZP, ZP]
    com manifesto [AR, ZP] — o bloco AR 'desaparece' e a regra pega.

    É o modo realista de intercalação nascer: música colada no fragmento
    errado. Com 1 fragmento por álbum, o bloco de cada álbum é o conteúdo do
    seu arquivo — então bloco ausente = arquivo sem as músicas dele."""
    zumbi = {'idAlbum': 'AR', 'album': _album(), 'songs': [_song(9, 'ZP')]}
    dir_ = _escrever(tmp_path / 'defs', ['AR', 'ZP'], zumbi, _fragmento('ZP', 1))
    with pytest.raises(DefsInvalidos) as erro:
        carregador.consolidar(dir_)
    msg = str(erro.value)
    # pego NA LEITURA do fragmento, com o apontamento exato do conserto:
    assert 'AR.json' in msg and 'mova para ZP.json' in msg
    assert 'T09' in msg


def test_fragmentos_integros_passam_pela_regra_de_ordem(tmp_path: Path):
    dir_ = _escrever(tmp_path / 'defs', ['AR', 'ZP'], _fragmento('AR', 2), _fragmento('ZP', 1))
    dados = carregador.consolidar(dir_)
    assert [s['idAlbum'] for s in dados['songs']] == ['AR', 'AR', 'ZP']
