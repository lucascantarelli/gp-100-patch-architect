"""Guardas de integridade — índices, ordem entre OS, órfãos e agentes.

Migração das seções F, G, I e J do `tests/test_pipeline.py` (issue #34). São
os testes que pegam as quebras **silenciosas**: índice defasado (G), ordem de
artefato dependente de SO (I — o manifesto de IRs divergiu Windows × Linux),
patch órfão fora do defs (J) e agente citado que não existe.

Marcador `e2e`: leem o repositório commitado e comparam com o que o pacote
gera hoje — nenhuma escrita.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from gp100_architect.application import indices, ir_library, nomes
from gp100_architect.domain.params import PARAM_NAMES
from gp100_architect.infrastructure.defs import carregar_e_validar
from gp100_architect.infrastructure.prst.codec import load_templates, real_param_count

pytestmark = pytest.mark.e2e


@pytest.fixture(scope='module')
def defs_real() -> dict[str, Any]:
    return carregar_e_validar()


def _travessia(defs: dict[str, Any]):
    for song in defs['songs']:
        for patch in song['patches']:
            yield song, patch


# ── F. cobertura de nomes de parâmetro (documentação técnica) ───────────────


def test_modelos_sem_nome_estao_na_allowlist(defs_real: dict[str, Any]) -> None:
    """Todo modelo ligado com params tem tabela de nomes (ou entrou na
    allowlist consciente — hoje vazia)."""
    em_uso = {
        (mod, m['name'])
        for _s, p in _travessia(defs_real)
        for mod, m in p['spec']['modules'].items()
        if m.get('on') and m.get('params')
    }
    sem_nome = em_uso - set(PARAM_NAMES)
    assert sem_nome == set(), (
        'modelos sem tabela de nomes mudaram: acrescente os nomes em '
        'PARAM_NAMES (fonte: reference/15) ou atualize a allowlist'
    )


def test_tabelas_sem_placeholder_nem_buraco() -> None:
    for (mod, nome), labels in PARAM_NAMES.items():
        assert not re.search(r'\bp\d+\b|\(p', ' '.join(labels)), f'{mod} {nome}: rótulo placeholder'
        assert all(ln.strip() for ln in labels), f'{mod} {nome}: rótulo vazio'
        assert len(set(labels)) == len(labels), f'{mod} {nome}: rótulo repetido'


def test_tabela_nao_tem_mais_nomes_que_parametros_reais() -> None:
    templates = load_templates()
    for (mod, nome), labels in PARAM_NAMES.items():
        tpl = templates.get((mod, nome))
        if not tpl:  # modelo fora do catálogo de fábrica: sem base para conferir
            continue
        reais = real_param_count(nome, tpl['params'])
        assert len(labels) <= reais, (
            f'{mod} {nome}: {len(labels)} nomes para {reais} parâmetros reais'
        )


# ── G. índices em disco = o que o gerador produz agora (sem drift) ──────────


def test_indices_em_disco_sao_os_gerados_hoje(defs_real: dict[str, Any], raiz: Path) -> None:
    manifesto = json.loads((raiz / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
    from gp100_architect.infrastructure.ir_catalog import indice_por_cab

    saidas, _total = indices.build_all(defs_real, raiz=raiz, ir_index=indice_por_cab(manifesto))

    def norm(t: str) -> str:
        return t.replace('\r\n', '\n')

    for caminho, texto in saidas.items():
        assert caminho.is_file(), f'{caminho} não existe — rode gen_indexes.py'
        assert norm(caminho.read_text(encoding='utf-8')) == norm(texto), (
            f'{caminho} está defasado — rode: uv run python tools/gen_indexes.py'
        )


def test_slots_continuos_e_alinhados(defs_real: dict[str, Any]) -> None:
    """gen_indexes e build numeram pela mesma travessia — sempre."""
    from gp100_architect.application.biblioteca import slots

    slots_gerados = slots(defs_real)
    esperado, n = {}, 0
    for song in defs_real['songs']:
        for patch in song['patches']:
            n += 1
            esperado[patch['nome']] = f'U{n:02d}'
    assert slots_gerados == esperado, 'biblioteca e índices numeram diferente'
    assert sorted(slots_gerados.values()) == [f'U{i:02d}' for i in range(1, len(slots_gerados) + 1)]


# ── I. ordem estável entre sistemas operacionais ────────────────────────────


def test_chave_de_ordenacao_e_string(raiz: Path) -> None:
    """`wav_order` devolve str — não Path, que traz o normcase do sistema."""
    ir_dir = raiz / 'impulse_responses'
    amostra = ir_dir / '25 Analog Cab IRs' / '4x12 MFB_EQ.wav'
    chave = ir_library.wav_order(amostra, ir_dir)
    assert isinstance(chave, str)
    assert chave == '25 Analog Cab IRs/4x12 MFB_EQ.wav'


def test_mfb_vem_antes_de_metal_american() -> None:
    """Ordem de code point (Linux): 'F' (70) < 'e' (101) — o caso que quebrou."""
    nomes_wav = ['4x12 Metal American_EQ.wav', '4x12 MFB_EQ.wav']
    assert sorted(nomes_wav) == ['4x12 MFB_EQ.wav', '4x12 Metal American_EQ.wav']


def test_manifesto_esta_em_ordem_de_code_point(raiz: Path) -> None:
    """O JSON commitado já sai ordenado por string em todo pack."""
    manifesto = json.loads((raiz / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
    for pack, mp in manifesto['packs'].items():
        arquivos = [f['file'] for f in mp['files']]
        assert arquivos == sorted(arquivos), f'ordem instável no pack {pack}'


# ── J. conexão defs × disco × agentes ───────────────────────────────────────


def test_todo_patch_no_disco_esta_no_defs(defs_real: dict[str, Any], raiz: Path) -> None:
    """Patch em `patches/` fora do defs é órfão: nem índice, nem teste o vê.

    A travessia do defs é a única fonte da biblioteca — pasta criada à mão (ou
    sobra de build antigo) ficaria invisível para índices, release e CLI. Num
    clone limpo (sem derivados construídos) o conjunto do disco é vazio e o
    teste passa trivialmente — a prova real acontece após o build do CI.
    """
    definidos = {patch['nome'] for _s, patch in _travessia(defs_real)}
    no_disco = {d.name for d in (raiz / 'patches').glob('*/*/*/*') if d.is_dir()}
    assert sorted(no_disco - definidos) == [], (
        'patch(s) em patches/ que não existem no defs (tools/defs/)'
    )


def test_pastas_de_musica_unicas(defs_real: dict[str, Any]) -> None:
    pastas = [nomes.song_pasta(s) for s in defs_real['songs']]
    repetidas = {p for p in pastas if pastas.count(p) > 1}
    assert repetidas == set(), f'pasta de música repetida: {repetidas}'


def test_spawnable_agents_e_reachavel(raiz: Path) -> None:
    """`spawnableAgents` só cita agente que existe, e todo agente é alcançável."""
    agents_dir = raiz / '.agents'
    arquivos = {p.stem for p in agents_dir.glob('gp100-*.ts')}
    fonte = (agents_dir / 'gp100-patch-architect.ts').read_text(encoding='utf-8')
    bloco = fonte.split('spawnableAgents: [', 1)[1].split(']', 1)[0]
    spawnaveis = set(re.findall(r"'([^']+)'", bloco))
    assert sorted(spawnaveis - arquivos) == [], (
        'o orquestrador pode invocar agente que não existe em .agents/'
    )
    assert sorted(arquivos - spawnaveis - {'gp100-patch-architect'}) == [], (
        'agente em .agents/ que o orquestrador não consegue invocar'
    )
