"""Derivados do pipeline: `.prst`, patch.md, momentos e concordância mapa × doc.

Migração das seções B–E do `tests/test_pipeline.py` (issue #34): nos legados
eles liam `patches/**` do disco; desde o ADR-0013 os derivados não são mais
commitados — então este módulo CONSTRÓI o produto a partir do defs commitado
(fixture de sessão, em memória via `biblioteca.gerar`) e prova o resultado:

* **C. `.prst`** — formato single fw 2.1: sem `<ppIRInfo>`, com `<ppCtrl>` e
  `<ppEXP1>`, 9 módulos na ordem PRE..RVB, `ppName` = nome do patch, 15 params
  por módulo;
* **B. fonte única de IR** — o mapa do álbum e a seção 📡 do patch.md dão a
  MESMA resposta (divergiram nos 38 patches do Pulse: um dizia "fábrica", o
  outro mandava carregar o banco local);
* **D. patch.md** — as 9 seções obrigatórias, zero HTML cru, zero rótulo
  placeholder e a guitarra antes do técnico;
* **E. momentos** — liga/desliga válido: módulo existe, estado é o inverso do
  atual e nunca toca AMP/CAB.

Marcador `e2e` (produto final); lento por natureza (gera a biblioteca inteira),
mas sem subprocess — o guarda de sincronia (TestH) é que roda o pipeline
inteiro em `test_guardas.py`.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import biblioteca, indices, nomes
from gp100_architect.application.artefatos import PatchGerado
from gp100_architect.domain.chain import CHAIN
from gp100_architect.infrastructure.defs import carregar_e_validar
from gp100_architect.infrastructure.ir_catalog import carregar as carregar_catalogo
from gp100_architect.infrastructure.ir_catalog import indice_por_cab
from gp100_architect.infrastructure.prst.codec import CHAIN_POS, load_templates

pytestmark = pytest.mark.e2e

# o mesmo GP100_BUILD_TIME que o CI usa: @time estável entre runs
BUILD_TIME = '1700000000000'

SECOES = [
    '## 🎸 1. Sua guitarra agora',
    '## 🔧 2. Ajustes finos',
    '## 📡 3. Impulse Response',
    '## 🎛️ 4. Modos de atuação',
    '## 🔊 5. Objetivo do som',
    '## 📚 6. Referência real',
    '## 🎛️ 7. Cadeia e parâmetros',
    '## 💾 8. Carregar na pedaleira',
    '## 🚫 9. Evite com este patch',
]


@pytest.fixture(scope='module')
def defs_real() -> dict[str, Any]:
    return carregar_e_validar()


@pytest.fixture(scope='module')
def ir_index(raiz: Path) -> dict[str, list[str]]:
    manifesto = carregar_catalogo(raiz / 'tools' / 'ir-library.json')
    return indice_por_cab(manifesto) if manifesto else {}


@pytest.fixture(scope='module')
def templates() -> dict[tuple[str, str], dict[str, Any]]:
    return load_templates()


@pytest.fixture(scope='module')
def gerados(
    defs_real: dict[str, Any],
    ir_index: dict[str, list[str]],
    templates: dict[tuple[str, str], dict[str, Any]],
    tmp_path_factory: pytest.TempPathFactory,
) -> list[PatchGerado]:
    """A biblioteca inteira, gerada em memória a partir do defs commitado."""
    return biblioteca.gerar(
        defs_real,
        raiz=tmp_path_factory.mktemp('derivados'),
        ir_index=ir_index,
        templates=templates,
        build_time=BUILD_TIME,
    )


@pytest.fixture(scope='module')
def por_nome(gerados: list[PatchGerado]) -> dict[str, PatchGerado]:
    return {g.nome: g for g in gerados}


@pytest.fixture(scope='module')
def saidas_indices(
    defs_real: dict[str, Any],
    ir_index: dict[str, list[str]],
    tmp_path_factory: pytest.TempPathFactory,
) -> dict[Path, str]:
    """Os índices (MAPA-DO-ALBUM.md × álbum + README) montados em memória."""
    saidas, _total = indices.build_all(
        defs_real, raiz=tmp_path_factory.mktemp('indices'), ir_index=ir_index
    )
    return saidas


def travessia(defs: dict[str, Any]) -> Iterator[tuple[dict[str, Any], dict[str, Any]]]:
    return biblioteca.travessia(defs)


def ler_mapa(defs: dict[str, Any], song: dict[str, Any], saidas: dict[Path, str]) -> list[str]:
    """Linhas da tabela 'Música → patches' do mapa do álbum da música."""
    album = defs['albums'][song['idAlbum']]
    alvo = (Path('patches') / album['pasta'] / 'MAPA-DO-ALBUM.md').as_posix()
    for caminho, texto in saidas.items():
        if caminho.as_posix().endswith(alvo):
            return texto.splitlines()
    raise AssertionError(f'MAPA-DO-ALBUM.md do álbum {album["pasta"]} não foi gerado')


# ── C. .prst — o arquivo que vai para a pedaleira ───────────────────────────


def test_formato_single_firmware_2_1(gerados: list[PatchGerado]) -> None:
    total = 0
    for g in gerados:
        root = ET.fromstring(g.prst.decode('utf-8'))
        assert root.tag == 'GP-100'
        info = root.find('preset_info')
        assert info is not None and info.get('firmware') == '2.1', g.nome
        assert info.get('count') == '1', g.nome  # single
        assert root.find('ppIRInfo') is None, (
            f'{g.nome}: ppIRInfo é do export "all" — o importador recusa'
        )
        presets = root.find('presets')
        assert presets is not None
        assert presets.get('ppName') == g.nome
        assert presets.find('ppCtrl') is not None, g.nome
        assert presets.find('ppEXP1') is not None, g.nome
        effects = presets.findall('Effect')
        assert len(effects) == len(CHAIN), g.nome
        assert [e.get('effectModuleName') for e in effects] == list(reversed(CHAIN)), g.nome
        for e in effects:
            assert e.get('x') == str(CHAIN_POS[e.get('effectModuleName')]), g.nome
            assert e.get('effectState') in ('0', '1'), g.nome
            for i in range(15):
                assert e.get(f'params_{i}') is not None, (
                    f'{g.nome}: {e.get("effectName")} sem params_{i}'
                )
        total += 1
    assert total == len(gerados) > 0


def test_par_prst_e_documentacao_para_todo_patch(gerados: list[PatchGerado]) -> None:
    """ADR-0013: o par `<NOME>.prst` + `patch.md` é o produto — nenhum faltando."""
    for g in gerados:
        assert g.documentacao.startswith('# '), g.nome
        assert g.prst.startswith(b'<'), g.nome


# ── B. fonte única de IR — mapa e doc dão a mesma resposta ──────────────────


def test_mapa_concorda_com_a_secao_de_ir(
    defs_real: dict[str, Any], saidas_indices: dict[Path, str], por_nome: dict[str, PatchGerado]
) -> None:
    marcador = re.compile(r'`(?:\S+ )?([A-Z0-9]{4,12})`')  # nome do patch no mapa
    divergencias: list[str] = []
    for song in defs_real['songs']:
        linhas = [ln for ln in ler_mapa(defs_real, song, saidas_indices) if ln.startswith('| **')]
        linha = next((ln for ln in linhas if nomes.song_display(song) in ln), None)
        assert linha is not None, f'{song["id"]}: linha da música não está no mapa'
        cells = [c.strip() for c in linha.strip().strip('|').split('|')]
        patches_col, ir_col = cells[1].split(' · '), cells[3].split(' · ')
        assert len(patches_col) == len(song['patches']), (
            f'{song["id"]}: nº de patches do mapa ≠ defs'
        )
        for i, patch in enumerate(song['patches']):
            nome = marcador.search(patches_col[i])
            assert nome is not None, f'mapa: não li o nome em {patches_col[i]!r}'
            assert nome.group(1) == patch['nome'], f'{song["id"]}: ordem do mapa'
            # o patch.md recomenda o banco local?
            doc = por_nome[patch['nome']].documentacao
            local_no_doc = '### 📁 Melhor opção no nosso banco' in doc
            local_no_mapa = ir_col[i].startswith('📁')
            if local_no_doc != local_no_mapa:
                divergencias.append(
                    f'{patch["nome"]}: patch.md '
                    f'{"recomenda o banco" if local_no_doc else "diz fábrica"} x mapa '
                    f'{"recomenda o banco" if local_no_mapa else "diz fábrica"}'
                )
    assert divergencias == [], 'mapa e patch.md discordam sobre a IR:\n  ' + '\n  '.join(
        divergencias
    )


def test_ir_local_do_defs_aponta_para_captura_existente(
    defs_real: dict[str, Any], raiz: Path
) -> None:
    import json

    manifesto = json.loads((raiz / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
    cabs = {
        Path(f['file']).parts[-2].replace(' Mics', '')
        for pack in manifesto['packs'].values()
        for f in pack['files']
    }
    for cab, par in defs_real['ir_local'].items():
        assert par['captura'] in cabs, (
            f"ir_local['{cab}'] aponta para captura ausente: {par['captura']}"
        )
        assert re.fullmatch(r'User IR ([1-9]|1[0-9]|20)', par['slot'])


# ── D. patch.md — a documentação entregue ao músico ─────────────────────────


def test_secoes_obrigatorias_e_markdown_puro(gerados: list[PatchGerado]) -> None:
    for g in gerados:
        doc = g.documentacao
        for secao in SECOES:
            assert secao in doc, f'{g.nome}: falta a seção {secao!r}'
        for tag in ('<div', '<br', '<details', '<summary', '</div'):
            assert tag not in doc, f'{g.nome}: HTML cru {tag} no Markdown'
        assert '# {' not in doc, f'{g.nome}: f-string não interpolada'


def test_sem_rotulo_placeholder(gerados: list[PatchGerado]) -> None:
    """Nem `(pN)` nem `pN` solto: todo slot setado tem nome oficial do manual."""
    ruins = []
    for g in gerados:
        achados = re.findall(r'\(p\d+\)|\bp\d+\b', g.documentacao)
        if achados:
            ruins.append(f'{g.nome}{achados[:3]}')
    assert ruins == [], f'rótulo placeholder nos docs: {ruins}'


def test_guitarra_vem_antes_do_tecnico(gerados: list[PatchGerado]) -> None:
    for g in gerados:
        doc = g.documentacao
        assert doc.index(SECOES[0]) < doc.index(SECOES[6]), (
            f'{g.nome}: dados técnicos antes da guitarra'
        )
        assert doc.index(SECOES[2]) < doc.index(SECOES[3]), (
            f'{g.nome}: IR deve vir antes dos modos de atuação'
        )


# ── E. momentos — liga/desliga em tempo real (seção 4) ──────────────────────


def test_momentos_sao_validos(defs_real: dict[str, Any]) -> None:
    encontrados = 0
    for _song, patch in travessia(defs_real):
        mods = patch['spec']['modules']
        for mo in patch['doc'].get('momentos', []):
            encontrados += 1
            assert mo['nome'] and mo['quando'], f'{patch["nome"]}: momento sem nome/quando'
            for nome_mod, estado in mo['mods']:
                assert nome_mod in mods, f'{patch["nome"]}: {nome_mod} não existe'
                assert nome_mod not in ('AMP', 'CAB'), (
                    f'{patch["nome"]}: toggle de AMP/CAB é proibido'
                )
                atual = mods[nome_mod].get('on', False)
                assert atual != (estado == 'ON'), f'{patch["nome"]}: {nome_mod} já está {estado}'
    assert encontrados > 0, 'nenhum momento declarado no defs'


def test_momentos_aparecem_no_doc(
    defs_real: dict[str, Any], por_nome: dict[str, PatchGerado]
) -> None:
    for _song, patch in travessia(defs_real):
        mo = patch['doc'].get('momentos')
        doc = por_nome[patch['nome']].documentacao
        assert '🎭 Momentos desta música' in doc, patch['nome']
        for m in mo or []:
            for nome_mod, estado in m['mods']:
                assert f'**{nome_mod} → {estado}**' in doc, (
                    f'{patch["nome"]}: momento {nome_mod} {estado} fora do doc'
                )
