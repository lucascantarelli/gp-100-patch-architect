# Changelog

Todas as mudanças relevantes deste projeto, por versão.
Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) · versionamento: [SemVer](https://semver.org/lang/pt-BR/).

> A partir da v1.0.1, este arquivo é **gerado** por `tools/gen_changelog.py` a
> partir dos commits, e as entradas são prependidas pelo workflow
> [`Release`](.github/workflows/release.yml). Não edite à mão.
>
> A v1.0.0 abaixo é a **baseline escrita à mão**: a história anterior a esta
> automação não seguia Conventional Commits, então ela não é derivável. Daqui
> para frente, o título do PR (que vira o commit do squash) é o que alimenta o
> changelog — ver [CONTRIBUTING.md](CONTRIBUTING.md).

## [1.0.0] — 2026-09-21

Primeira versão publicável da biblioteca e do pipeline.

### ✨ Funcionalidades

- **62 patches em 42 músicas**, divididos em 4 álbuns: *Abbey Road* (Beatles),
  *Apostrophe (')* (Frank Zappa, com *Uncle Remus*), *Cheap Thrills*
  (Big Brother & The Holding Company, com *Piece of My Heart*) e *Pulse*
  (Pink Floyd — 24 músicas → 38 patches, ordem do álbum em U25–U62).
- **Formato `.prst` single, firmware 2.1**, validado estruturalmente contra o
  export que importou no aparelho (sem `ppIRInfo`, com `ppCtrl`/`ppEXP1`, cadeia
  x=0–8, 15 parâmetros por módulo).
- **17 agentes** em `.agents/` — orquestrador + uma skill por bloco da cadeia
  (PRE, DST, AMP, CAB/IR, EQ, MOD, NR, DLY, RVB, globais) + skills de apoio.
- **Pipeline reprodutível**: `patches-defs.json` como fonte única; regenerar não
  altera parâmetros (só o `preset_info/@time` do export real).
- **Empacotamento de release** (`tools/build_release.py`): ZIP da biblioteca
  completa + um ZIP por álbum, com as notas da Release.

### 📊 Dados e patches

- **Biblioteca local de IRs indexada**: 291 WAVs da Origin Effects IR-Cab Library
  V3 em 9 gabinetes + 25 Analog Cab IRs.
- **Catálogo real do firmware 2.0/2.1** extraído de export de fábrica
  (`tools/factory-catalog.json`, 99 presets · 117 modelos), com precedência sobre
  o manual impresso V1.8.
- **Manual V1.8 transcrito** página a página em `reference/00–17`.

### 🐞 Correções

- **Divergência mapa × `patch.md` sobre IR**: o `MAPA-DO-ALBUM.md` recomendava
  CAB de fábrica enquanto o `patch.md` mandava carregar uma IR do banco nos 38
  patches do Pulse. A causa era a duplicação da tabela de IRs; hoje
  `tools/patches-defs.json` é a fonte única e o teste `TestB_FonteUnica_IR`
  reprova a regressão.
- **Ordem de artefatos dependente do SO**: a comparação de `Path` usa `normcase`
  (minúsculas no Windows, identidade no Linux), o que fazia o manifesto de IRs
  divergir entre a máquina e o CI. A ordenação passou a ser por string (ordem de
  code point), travada por `TestI_OrdemEstavel`.
- **Zero rótulo `pN`** na documentação: os 40 `patch.md` do Pulse e as 28 menções
  em ajustes/evite passaram a usar os nomes oficiais do manual V2.0.

### 📚 Documentação

- **Guia de governança completo**: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `.editorconfig`,
  `CODEOWNERS`, templates de issue e de PR.
- **Endurecimento de CI/CD**: workflow `Security` (CodeQL em Python e TypeScript,
  revisão de dependências e auditoria de permissões dos workflows) e workflow
  `Release` (SemVer, changelog e publicação automatizadas).
- **`README.md`** com badges, arquitetura, instalação, uso e FAQ.

### 🔐 Segurança

- **Conteúdo de terceiros fora do versionamento**: os packs de IR e o
  `manual.pdf` deixaram de ser versionados (licença alheia não concede
  redistribuição). O catálogo gerado permanece no repositório, por ser insumo da
  documentação dos patches.
- **Guarda contra encolhimento do catálogo**: `ir_library.py` reprova a rodada
  que removeria packs citados pela documentação, em vez de degradar 62 docs em
  silêncio.
