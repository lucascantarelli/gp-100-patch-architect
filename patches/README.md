# 🎸 Biblioteca de patches — GP-100

![Organização](https://img.shields.io/badge/organização-banda%2Fálbum%2Fmúsica%2Fpatch-2ea44f?style=flat-square) ![Formato](https://img.shields.io/badge/.prst-single%20fw%202.1-2ea44f?style=flat-square) ![Patches](https://img.shields.io/badge/patches-97-e02d2d?style=flat-square)

## 🗂️ Estrutura

```
patches/
├── <Banda>/
│   └── <Álbum> (<ano>)/
│       ├── MAPA-DO-ALBUM.md            # música → patches + slots
│       └── <Música>/
│           └── <MUSICA-CAMADA>/        # 1 pasta por patch
│               ├── <MUSICA-CAMADA>.prst  # ✅ importável (single, fw 2.1)
│               └── patch.md              # documentação prática-primeiro
└── README.md
```

## 🏷️ Nomenclatura (leia-se em 2 segundos)

`MUSICA## + CAMADA` — máximo 12 caracteres (limite do painel da GP-100).

| Código | Significado | | Código | Significado |
|---|---|---|---|---|
| `BA` | base | | `FL` | fills |
| `SO` | solo | | `AR` | arpejos |
| `RI` | riff | | `AC` | acústico |
| `CL` | clean | | `SL` | slide |
| `VO` | voz-líder | | | |

Exemplos: `STH01BA` = Something 01 · Base · `CT01RIF` = Come Together 01 · Riff · `URM01SL` = Uncle Remus 01 · Slide.

> **Regra**: cada música tem patches **exclusivos**. Músicas só ganham mais de um patch quando o timbre muda de verdade entre as seções.

## 📚 Álbuns

| Banda | Álbum | Músicas | Patches | Mapa |
|---|---|---|---|---|
| 🎸 **The Beatles** | **Abbey Road (1969)** | 14 | 20 | [`MAPA-DO-ALBUM.md`](Beatles/Abbey%20Road%20(1969)/MAPA-DO-ALBUM.md) |
| 🎸 **Frank Zappa** | **Apostrophe (’) (1974)** | 1 | 2 | [`MAPA-DO-ALBUM.md`](Frank%20Zappa/Apostrophe%20(1974)/MAPA-DO-ALBUM.md) |
| 🎸 **Janis Joplin (Big Brother & The Holding Company)** | **Cheap Thrills — Piece of My Heart (1968)** | 1 | 2 | [`MAPA-DO-ALBUM.md`](Janis%20Joplin/Piece%20of%20My%20Heart%20(1968)/MAPA-DO-ALBUM.md) |
| 🎸 **Pink Floyd** | **Pulse (1995)** | 24 | 38 | [`MAPA-DO-ALBUM.md`](Pink%20Floyd/Pulse%20(1995)/MAPA-DO-ALBUM.md) |
| 🎸 **Nirvana** | **Muddy Banks (1996)** | 17 | 31 | [`MAPA-DO-ALBUM.md`](Nirvana/From%20the%20Muddy%20Banks%20(1996)/MAPA-DO-ALBUM.md) |
| 🎸 **Santana** | **Supernatural (1999)** | 1 | 4 | [`MAPA-DO-ALBUM.md`](Santana/Supernatural%20(1999)/MAPA-DO-ALBUM.md) |

## 📄 Cada patch contém

| Arquivo | O que é |
|---|---|
| `<NOME>.prst` | Arquivo **importável** no GP-100 Edits ou direto na pedaleira (single-patch, fw 2.1) |
| `patch.md` | Doc prática-primeiro: guitarra já na seção 1, ajustes finos, objetivo do som, dossiê, técnica |

## 🔧 Regenerar tudo

```bash
python tools/build_song_patches.py   # patch.md + .prst a partir de tools/patches-defs.json
python tools/gen_indexes.py          # mapas dos álbuns + este README
```

---

[`📖 README do projeto`](../README.md)
