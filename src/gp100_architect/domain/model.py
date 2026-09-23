"""Modelo de domínio do defs — o mínimo tipado que as regras precisam.

Fronteira deliberada: o `patches-defs.json` é a fonte única e continuam sendo
`spec`/`doc` dicts crus onde o consumidor é o gerador do `.prst`. Este modelo
existe para as regras que **pensam** sobre a biblioteca (setlist, índices,
release), onde trafegar dict solto vira bug de chave digitada errado.

Contrato: `from_dict` pressupõe defs já validado (`domain.validation`) — não
repete validação nem inventa default para campo obrigatório.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

__all__ = ['Album', 'Modulo', 'Patch', 'Song']


@dataclass(frozen=True, slots=True)
class Album:
    """Um álbum do defs — a pasta de destino dos patches e o dossiê de fontes."""

    id: str
    banda: str
    album: str
    ano: int
    pasta: str
    rig: str
    display: str = ''

    @classmethod
    def from_dict(cls, id_album: str, dado: Mapping[str, Any]) -> Album:
        return cls(
            id=id_album,
            banda=str(dado['banda']),
            album=str(dado['album']),
            ano=int(dado['ano']),
            pasta=str(dado['pasta']),
            rig=str(dado['rig']),
            display=str(dado.get('display', '')),
        )


@dataclass(frozen=True, slots=True)
class Modulo:
    """Um módulo dentro do `spec` de um patch: modelo, on/off e params."""

    nome: str
    ligado: bool
    params: Mapping[int, float] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, dado: Mapping[str, Any]) -> Modulo:
        params = dado.get('params') or {}
        return cls(
            nome=str(dado.get('name', '')),
            ligado=bool(dado.get('on', True)),
            params={int(k): float(v) for k, v in params.items()},
        )


@dataclass(frozen=True, slots=True)
class Patch:
    """Um patch da biblioteca — nome de painel, camada e cadeia de módulos."""

    nome: str
    sufixo: str
    camada: str
    tipo: str
    modulos: Mapping[str, Modulo]

    @property
    def usados(self) -> tuple[str, ...]:
        """Módulos com modelo definido, na ordem da cadeia (assinatura da setlist)."""
        from gp100_architect.domain.chain import CHAIN

        return tuple(m for m in CHAIN if self.modulos.get(m, Modulo('', False)).nome)

    @classmethod
    def from_dict(cls, dado: Mapping[str, Any]) -> Patch:
        spec = dado.get('spec') or {}
        modules = spec.get('modules') or {}
        return cls(
            nome=str(dado['nome']),
            sufixo=str(dado.get('sufixo', '')),
            camada=str(dado.get('camada', '')),
            tipo=str(spec.get('type', '')),
            modulos={mod: Modulo.from_dict(m) for mod, m in modules.items()},
        )


@dataclass(frozen=True, slots=True)
class Song:
    """Uma música do defs com seus patches (um patch = uma entrada de painel)."""

    id: str
    nome: str
    id_album: str
    bpm: float
    patches: tuple[Patch, ...] = ()
    resumo: str = ''

    @classmethod
    def from_dict(cls, dado: Mapping[str, Any]) -> Song:
        return cls(
            id=str(dado['id']),
            nome=str(dado['song']),
            id_album=str(dado['idAlbum']),
            bpm=float(dado['bpm']),
            patches=tuple(Patch.from_dict(p) for p in dado.get('patches', ())),
            resumo=str(dado.get('resumo', '')),
        )


def albuns_do_defs(defs: Mapping[str, Any]) -> dict[str, Album]:
    """Conveniência para os casos de uso: `{id: Album}` a partir do defs cru."""
    return {k: Album.from_dict(k, v) for k, v in (defs.get('albums') or {}).items()}


def songs_do_defs(defs: Mapping[str, Any]) -> tuple[Song, ...]:
    """Músicas tipadas na ordem do defs (a ordem é significativa nos índices)."""
    lista: Sequence[Mapping[str, Any]] = defs.get('songs') or ()
    return tuple(Song.from_dict(s) for s in lista)
