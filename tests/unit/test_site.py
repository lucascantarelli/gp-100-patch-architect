"""Site estático — geração em memória e contratos do gerador (issue #11).

Por que estes testes não geram nada no disco: a camada devolve
`{caminho: conteúdo}` — a escrita é responsabilidade do comando (`gp100 site`)
e o teste da geração inteira cabe em memória, como o `patch_md`.

O que está fixado aqui:
* **fonte única** — o site é derivado do defs: um patch novo aparece no índice
  de busca e ganha página sem configuração;
* **índice de busca minúsculo** — só nomes (slot/nome/música/álbum/banda/
  camada/captador), nunca conteúdo (a "tabela de parâmetros" dodefs inteiro
  viraria um JSON de MBs — o oposto do Pilar C);
* **consistência com a CLI** — o dossiê do `show` e a página do patch não
  divergem: ambos vêm de `consulta.dossie`;
* **títulos derivados** — música/álbum usam `nomes.song_display`/`display`,
  a mesma regra das tabelas do mapa (nada de `CT01` onde deveria dizer
  "Come Together").
"""

import json
from typing import Any

import pytest

from gp100_architect.application import site

pytestmark = pytest.mark.unit

# defs sintético mínimo: dois álbuns, duas músicas, três patches
DEFS: dict[str, Any] = {
    'albums': {
        'ZZ': {
            'banda': 'Banda Z',
            'album': 'Disco Z',
            'ano': 2001,
            'display': 'Disco Z (2001)',
            'pasta': 'Banda Z/Disco Z (2001)',
        },
        'AA': {
            'banda': 'Banda A',
            'album': 'Disco A',
            'ano': 1999,
            'display': 'Disco A (1999)',
            'pasta': 'Banda A/Disco A (1999)',
        },
    },
    'ir_local': {},
    'songs': [
        {
            'idAlbum': 'ZZ',
            'id': 'ZZX1',
            'song': 'Música X',
            'bpm': 100,
            'resumo': '',
            'referencias': [],
            'patches': [
                {
                    'nome': 'ZZX1BA',
                    'camada': 'Base',
                    'spec': {
                        'name': 'ZZX1BA',
                        'type': 'single',
                        'bpm': 100,
                        'volume': 50,
                        'modules': {
                            'DST': {'name': 'Blues OD', 'on': True, 'params': {'0': 55, '2': 40}},
                        },
                    },
                    'doc': {
                        'guitarra': {
                            'seletorCurto': 'neck',
                            'receita': 'Toque leve perto do braço',
                        },
                        'ajustes': ['Se sobrar agudo, High Cut 6500'],
                        'momentos': [{'nome': 'Solo', 'modulo': 'DST', 'para': 'ligado'}],
                    },
                },
                {
                    'nome': 'ZZX1SO',
                    'camada': 'Solo',
                    'spec': {
                        'name': 'ZZX1SO',
                        'type': 'single',
                        'bpm': 100,
                        'volume': 55,
                        'modules': {
                            'DST': {'name': 'Blues OD', 'on': True, 'params': {'0': 70}},
                        },
                    },
                    'doc': {'guitarra': {'seletorCurto': 'bridge'}},
                },
            ],
        },
        {
            'idAlbum': 'AA',
            'id': 'AAY1',
            'song': 'Música Y',
            'bpm': 90,
            'resumo': '',
            'referencias': [],
            'patches': [
                {
                    'nome': 'AAY1CL',
                    'camada': 'Clean',
                    'spec': {
                        'name': 'AAY1CL',
                        'type': 'single',
                        'bpm': 90,
                        'volume': 50,
                        'modules': {
                            'AMP': {'name': 'L-Star CL', 'on': True, 'params': {'1': 52}},
                        },
                    },
                    'doc': {'guitarra': {'seletorCurto': 'middle+neck'}},
                },
            ],
        },
    ],
}


@pytest.fixture(scope='module')
def paginas() -> dict[str, str]:
    return site.gerar_site(DEFS)


def test_gera_arquivos_basicos(paginas: dict[str, str]) -> None:
    assert set(paginas) >= {
        'index.html',
        'busca.json',
        'style.css',
        'album/AA.html',
        'album/ZZ.html',
        'patch/ZZX1BA.html',
        'patch/ZZX1SO.html',
        'patch/AAY1CL.html',
    }


def test_indice_de_busca_e_minuculo_e_nao_vaza_conteudo(paginas: dict[str, str]) -> None:
    """Só nomes; o conteúdo (parâmetros/momentos) fica na página do patch."""
    dados = json.loads(paginas['busca.json'])
    assert len(dados) == 3
    registro = next(i for i in dados if i['nome'] == 'ZZX1BA')
    assert registro['musica'] == 'Música X'
    assert registro['album'] == 'Disco Z (2001)'
    assert registro['banda'] == 'Banda Z'
    assert registro['camada'] == 'Base'
    assert '55' not in paginas['busca.json']  # valor de parâmetro não vaza pro índice


def test_pagina_do_patch_mostra_parametros_com_nome_oficial(paginas) -> None:
    html = paginas['patch/ZZX1BA.html']
    # rotulo_param deriva de PARAM_NAMES: se o par (módulo, modelo) é conhecido,
    # o nome oficial aparece; nunca o índice cru `pN`.
    assert 'p0' not in html and 'p2' not in html
    assert 'Blues OD' in html
    assert '55' in html and '40' in html
    assert 'Toque leve perto do braço' in html
    assert 'Se sobrar agudo, High Cut 6500' in html


def test_pagina_do_patch_casada_com_o_dossie_do_show(paginas) -> None:
    """O `show` e o site saem da mesma `consulta.dossie` — não podem divergir."""
    from gp100_architect.application.consulta import dossie

    d = dossie(DEFS, 'ZZX1BA', raiz=__import__('pathlib').Path('.'))
    html = paginas['patch/ZZX1BA.html']
    assert d.slot in html and d.cadeia in html
    assert d.nome in html and d.musica in html


def test_momentos_vao_para_a_pagina(paginas) -> None:
    html = paginas['patch/ZZX1BA.html']
    assert 'Momentos' in html and 'Solo' in html


def test_secoes_vazias_somem(paginas) -> None:
    """ZZX1SO não tem ajustes/momentos/stomps: a página não tem seção vazia."""
    html = paginas['patch/ZZX1SO.html']
    assert 'Ajustes finos' not in html
    assert 'Momentos' not in html
    assert 'Stomps' not in html


def test_escapes_de_html(paginas) -> None:
    """Título com caractere especial não quebra a página (escape de renderização)."""
    html = paginas['patch/AAY1CL.html']
    assert 'Música Y' in html
    assert '<Música' not in html.replace('<h1>', '').replace('</h1>', '')


def test_index_ordenado_por_ano_e_com_busca(paginas) -> None:
    html = paginas['index.html']
    assert html.index('Disco A (1999)') < html.index('Disco Z (2001)')
    assert 'id="q"' in html and 'busca.json' in html


def test_base_url_documentada_no_index(paginas: dict[str, str]) -> None:
    assert 'base_url:' in paginas['index.html']


def test_nada_e_escrito_no_disco(paginas: dict[str, str], tmp_path) -> None:
    """A camada devolve texto; quem grava é a CLI — contrato da camada."""
    de_novo = site.gerar_site(DEFS)
    assert de_novo == paginas  # puro e determinístico
    assert list(tmp_path.iterdir()) == []  # e nada apareceu no cwd/tmp
