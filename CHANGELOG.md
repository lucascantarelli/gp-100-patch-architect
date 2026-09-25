# Changelog

Todas as mudanças relevantes deste projeto, por versão.
Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) · versionamento: [SemVer](https://semver.org/lang/pt-BR/).

> Gerado por `gp100 release` / `gp100 changelog` a partir dos commits
> (Conventional Commits) — **não edite à mão**. Quem publica roda
> `gen_changelog.py --version X.Y.Z --write` antes de subir o `VERSION`;
> o workflow `Release` só valida e publica.
>
> A v1.0.0 é a **baseline escrita à mão**: a história anterior a esta
> automação não seguia Conventional Commits, então ela não é derivável.
> Daqui para frente, o título do PR (que vira o commit do squash) é o que
> alimenta o changelog — ver CONTRIBUTING.md.

## [2.0.0] — 2026-09-24

### ✨ Funcionalidades

- **#61**: guias por público + FAQ + exemplos comentados (#106)
- **#60**: site de documentação em MkDocs Material publicado pelo CI (#105)
- **#12**: Are You Experienced (Jimi Hendrix) - 7o album do defs, 103 patches (#104)
- **#58,#83**: linter de consistência de docs + writer do formato all (parte software) (#103)
- **#56**: agente de versionamento - propoe o bump via gp100 changelog, nunca decide (#101)
- **#90**: fase 1 - catalogo JSON no pipeline do site (shapes estaveis = contrato) (#100)
- **#63**: guarda de integridade de agentes e skills no CI (#98)
- **#11**: site da biblioteca — gp100 site + Pages (busca client-side, sem backend) (#99)
- **#48,#49**: CLI do pacote com consulta e produção — shims delegam (#94)
- **#10**: variante experimental -USERIR gerável com --with-user-ir (#92)
- **#9**: stomps FS-A/FS-B e pedal de expressão (EXP1) formais no schema
- **#8**: schema v2 — defs dividido por álbum, seeders aposentados e derivados fora do git
- **#29**: codec .prst vira biblioteca em infrastructure/ com testes de contrato
- **automation**: issue fechada move o card para Done — fim dos cards zumbis
- **ci**: teto de permissões por workflow — menor privilégio verificável (#62)
- **2.0**: fundação — pacote em src/, uv, gates de qualidade e ADRs 0001–0010
- **agents**: versiona as 11 skills em .agents/skills + curadoria (doc 23)
- **review**: doc 21 — code review do código Python + correções M1/M2/B1/B5
- **agents**: gp100-setlist + gp100-ab-tester + golden set (Pilar E)
- **tools**: defs_schema.py — validação acionável do defs + Python 3.14 apenas
- **tools**: CLI unificada gp100.py — find, show, diff, export, build, verify
- **gestão**: Project v2 + guardian, templates de issue e roadmap da v2.0
- **santana**: Smooth — 4 patches com stomps (Lone Star + Soldano/Mesa)
- **nirvana**: biblioteca do From the Muddy Banks of the Wishkah — 17 músicas, 31 patches

### 🐞 Correções

- **#11**: stylesheet com profundidade relativa - index na raiz do site citava ../style.css (404 no Pages)
- **#11**: dispensa configure-pages - site estatico com links relativos nao precisa de base url
- **#11**: pages: read no job de build - configure-pages le GET /pages
- **ci**: project-automation válido, token de Project correto e auditor cobrando permissões
- **ci**: fixa a Action de terceiro por SHA e reprova a regressão no auditor
- **ci**: trava de runtime após o setup-python (python do runner era 3.12)
- **review**: timestamp determinístico no .prst e IR User sem slot fixo
- **santana**: atende o review - ir_local dos 2 CABs, chorus parametrizado no stomp e nits de doc
- **wishkah**: atende o review - sobressalentes reais, 31/31 com momentos, seletor e Tourettes

### 📚 Documentação

- **#46**: resolucao do pilar D registrada - albuns parciais contam, meta segue como trajetoria
- #63 entregue (PR #98) no roadmap - epic #45 resta #56 e #57
- link do site no README (badge + abertura + ferramentas) e badge de testes atualizado
- #11 entregue (PR #99) nos roadmaps - caminho critico agora e #90 fase 1
- #91 fechada (PR #97) nos roadmaps - caminho critico comeca no site #11
- roadmap reflete epics #41 e #42 encerrados e o novo caminho critico
- **roadmap**: grafo §3 coerente com o board — #31 obsoleta, #91 e #90 no grafo
- **#42**: roadmap pós-trio de formato — status atual e decisões A1/A2 resolvidas
- **#91**: orquestrador alinhado à #8/#30 — TestH é guarda de determinismo e build_doc mora no pacote
- **#90**: API do catálogo entra no Pilar C do roadmap
- **#8**: conserta resíduos do schema v2 — seeders fora dos docs e guarda de determinismo
- **adr-0013**: modelo de artefatos em escala — defs é a única fonte versionada
- **governança**: registra as premissas vencidas do board — views por API e gh project mascarando PAT válido
- **governança**: numeração e comentários do guardian alinhados ao fechamento real da issue
- **roadmap**: alinha os nomes dos milestones de fase ao que existe no GitHub
- contagens da v1.1.0 — 97 patches / 58 músicas / 6 álbuns
- **fluxo**: desenvolvimento na develop com push direto; main só recebe release aprovada

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
