"""I/O da infraestrutura — cabeçalho de WAV e escrita de artefatos (issue #30).

Duas garantias que só o disco prova:

* `inspecionar` lê o cabeçalho de verdade (e não derruba a rodada quando o
  arquivo está corrompido — o catálogo registra a falha);
* `escrever_texto` respeita o fim de linha pedido (CRLF nos `.md` da
  biblioteca) e `escrever_bytes` grava o `.prst` sem traduzir nada.
"""

from __future__ import annotations

import wave
from pathlib import Path

import pytest

from gp100_architect.infrastructure import escrita
from gp100_architect.infrastructure.wav import BITS_GP100, LIMITE_SAMPLES, inspecionar

pytestmark = pytest.mark.unit


def _wav(
    caminho: Path, *, frames: int = 1000, taxa: int = 44100, canais: int = 1, largura: int = 3
) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho), 'wb') as w:
        w.setnchannels(canais)
        w.setsampwidth(largura)
        w.setframerate(taxa)
        w.writeframes(b'\x00' * (frames * canais * largura))
    return caminho


def test_inspecionar_aprova_o_formato_da_gp100(tmp_path: Path):
    info = inspecionar(_wav(tmp_path / 'Cab' / 'ok.wav'))
    assert info == {
        'rate': 44100,
        'channels': 1,
        'bits': BITS_GP100,
        'duration_ms': 23,
        'compatible': True,
        'over_1024': False,
    }
    assert BITS_GP100 == 24
    assert LIMITE_SAMPLES == 1024


def test_inspecionar_marca_incompativel_e_cauda_longa(tmp_path: Path):
    estereo = inspecionar(_wav(tmp_path / 'estereo.wav', canais=2))
    assert estereo['compatible'] is False and estereo['channels'] == 2

    vinte_bits = inspecionar(_wav(tmp_path / '16bits.wav', largura=2))
    assert vinte_bits['compatible'] is False and vinte_bits['bits'] == 16

    quarenta_e_oito = inspecionar(_wav(tmp_path / '48k.wav', taxa=48000))
    assert quarenta_e_oito['compatible'] is False and quarenta_e_oito['rate'] == 48000

    longa = inspecionar(_wav(tmp_path / 'longa.wav', frames=LIMITE_SAMPLES + 1))
    assert longa['over_1024'] is True and longa['compatible'] is True


def test_inspecionar_wav_corrompido_nao_derruba_a_rodada(tmp_path: Path):
    ruim = tmp_path / 'ruim.wav'
    ruim.write_bytes(b'nao e wav nenhum')
    info = inspecionar(ruim)
    assert info['compatible'] is False
    assert info.get('error')


def test_inspecionar_arquivo_ausente_nao_derruba_a_rodada(tmp_path: Path):
    info = inspecionar(tmp_path / 'nao-existe.wav')
    assert info['compatible'] is False and 'error' in info


def test_escrever_texto_respeita_o_fim_de_linha(tmp_path: Path):
    crlf = tmp_path / 'a' / 'b' / 'patch.md'
    escrita.escrever_texto(crlf, '# título\nlinha\n', crlf=True)
    assert crlf.read_bytes() == '# título\r\nlinha\r\n'.encode()

    lf = tmp_path / 'c' / 'manifesto.json'
    escrita.escrever_texto(lf, '{\n}\n')
    assert lf.read_bytes() == b'{\n}\n'


def test_escrever_bytes_preserva_os_bytes_do_codec(tmp_path: Path):
    alvo = tmp_path / 'x' / 'PATCH.prst'
    # CRLF cru: write_text traduziria no Windows e corromperia o .prst
    dados = b'<?xml version="1.0" encoding="UTF-8"?>\r\n<x/>'
    escrita.escrever_bytes(alvo, dados)
    assert alvo.read_bytes() == dados
