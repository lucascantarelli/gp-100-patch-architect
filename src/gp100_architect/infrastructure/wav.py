"""Inspeção de WAV — taxa, canais, bits, duração e compatibilidade (issue #30).

Migração de `tools/ir_library.py` (`wav_info`): a leitura do cabeçalho WAV é
I/O e por isso mora aqui; a decisão do que é compatível continua explícita e
citável — mono, 24 bits e 44,1 kHz são o formato que a GP-100 aceita direto.

Um WAV ilegível não derruba a rodada: devolve `{'error': ..., 'compatible':
False}` e o catálogo registra o arquivo com a falha (é o que mantém o índice
honesto quando um pack vem corrompido).

Camada: infrastructure (o domínio nunca importa daqui).
"""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

__all__ = ['BITS_GP100', 'LIMITE_SAMPLES', 'TAXA_GP100', 'inspecionar']

TAXA_GP100 = 44100
BITS_GP100 = 24
LIMITE_SAMPLES = 1024  # ~23 ms @ 44.1 kHz — o editor apara a cauda acima disso


def inspecionar(caminho: Path) -> dict[str, Any]:
    """Cabeçalho do WAV + flags de compatibilidade com a GP-100.

    `compatible`: mono, 24 bits e 44,1 kHz — o formato aceito direto.
    `over_1024`: mais de 1024 samples (o editor apara a cauda ao carregar).
    """
    try:
        with wave.open(str(caminho)) as w:
            frames = w.getnframes()
            taxa = w.getframerate()
            canais = w.getnchannels()
            largura = w.getsampwidth()
        return {
            'rate': taxa,
            'channels': canais,
            'bits': largura * 8,
            'duration_ms': round(frames / taxa * 1000),
            'compatible': canais == 1 and largura * 8 == BITS_GP100 and taxa == TAXA_GP100,
            'over_1024': frames > LIMITE_SAMPLES,
        }
    except Exception as e:  # WAV corrompido não derruba o índice
        return {'error': str(e), 'compatible': False}
