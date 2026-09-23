# Contribuindo com o GP-100 Patch Architect

Obrigado pelo interesse. Este projeto tem uma característica que muda tudo:
**metade dele é saída de script**. Os arquivos em `patches/**` são *gerados* a
partir de `tools/defs/` (schema v2: fragmentos por álbum), e o CI reprova quem editar o gerado à mão.
Antes de commitar na `develop`, leia a seção [O pipeline é obrigatório](#-o-pipeline-é-obrigatório).

Ao participar, você concorda com o [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
Para vulnerabilidades, **não** abra issue: siga o [`SECURITY.md`](SECURITY.md).

---

## 🧰 Ambiente de desenvolvimento

Tempo de setup: ~2 minutos, com um comando (`ADR-0001`).

| Requisito | Versão | Usado por |
|---|---|---|
| **Python** | 3.14 (apenas) | pipeline, pacote `src/gp100_architect`, testes |
| **uv** | qualquer recente | ambiente, dependências de dev, comandos (`uv run …`) |
| **Node.js** | 26 (20+ funciona) | typecheck dos agentes em `.agents/` |
| **Git** | qualquer | — |

```bash
git clone https://github.com/lucascantarelli/gp-100-patch-architect.git
cd gp-100-patch-architect
uv sync             # cria .venv, instala o lockfile e o pacote (editável)
uv run gp100 --version
node --version      # v26.x (só para o typecheck dos agentes)
```

O `tools/` legado continua rodando com a **stdlib pura** (`python tools/x.py`
funciona sem instalar nada); o ambiente uv existe para os gates de qualidade
e para a CLI oficial. Detalhes e comandos do dia a dia:
[`DEVELOPMENT.md`](DEVELOPMENT.md).

> **💡 Assinatura dos dados:** `tools/defs/` é a **fonte única** de
> músicas, álbuns, patches e IRs recomendadas. Os scripts são renderizadores —
> nenhum deles tem lista de músicas ou de cabs dentro do código. Acrescentar
> dado é editar o defs, nunca o gerador.

Páginas do manual sob demanda (opcional; requer `pymupdf` e o `manual.pdf`
local, que não é versionado):

```bash
pip install pymupdf
python tools/render_manual_page.py 21        # página impressa NN = arquivo NN+2
```

## ✅ Antes de commitar na `develop`: rode exatamente o que o CI roda

```bash
# 1. Suíte completa (156 testes) com cobertura do pacote
uv run pytest -q --cov --cov-report=term-missing

# 2. Gates de qualidade (pacote)
uv run ruff check . && uv run ruff format --check . && uv run mypy

# 3. Typecheck dos 19 agentes
npx -y -p typescript@5.9.2 tsc --noEmit -p tsconfig.json
```

Opcional, mas recomendado: `uv run pre-commit install` — os hooks rodam lint e
formatação antes do commit (o veredito continua sendo o CI).

E, **se você mexeu em dados** (música, camada, patch, momento, pack de IR ou
cab):

```bash
# 3. Pipeline completo, na ordem do CI
python tools/ir_library.py \
  && python tools/add_pulse_defs.py \
  && python tools/add_wishkah_defs.py \
  && python tools/add_santana_defs.py \
  && python tools/add_momentos.py \
  && python tools/build_song_patches.py \
  && python tools/gen_indexes.py
```

O guarda de sincronia vive na suíte (`TestH_DadosEmSincronia`): ela roda o
pipeline numa cópia temporária do repositório e compara com o commitado — se
reprovar, o teste lista os arquivos divergentes. Suíte verde = PR coerente.

## 🔁 O pipeline é obrigatório

Este fluxo já quebrou em produção uma vez (ver a história do `TestB_FonteUnica_IR`
no [`README.md`](README.md)), então o CI trata esquecimento como falha de build:

| Você mexeu em | Obrigatório rodar |
|---|---|
| `tools/defs/` (álbum, música, patch, momento) | `build_song_patches.py` → `gen_indexes.py` |
| Novos packs de IR em `impulse_responses/` | `ir_library.py` |
| Scripts em `tools/` | a suíte + o pipeline inteiro (a saída tem de continuar idêntica) |

**Nunca edite à mão** um arquivo gerado: `patches/**/*.prst`, `patches/**/patch.md`,
`patches/**/MAPA-DO-ALBUM.md`, `patches/README.md`,
`tools/ir-library.json`, `reference/16-ir-library.md` (o defs deixou de ser saída de script no schema v2 — ele É a fonte).
Sua edição será apagada na próxima execução do pipeline e reprovada pelo guarda.

### ℹ️ O spec vai direto ao codec — sem intermediário em disco

Desde o ADR-0013, o `build_song_patches.py` passa o spec **in-memory** ao codec
(`src/gp100_architect/infrastructure/prst/`): o antigo `spec.json` intermediário
**não existe mais** nem em disco. Para comparar parâmetros entre duas versões,
leia o defs (`tools/defs/`, a fonte) — o `.prst` muda o `preset_info/@time` a
cada build, o defs não. Nada em `patches/**` é escrito à mão: tudo é derivado do
defs e vigiado pelo guarda de sincronia.

### ⚠️ O catálogo de IRs não é regenerável sem o pack

O **banco** de IRs (`impulse_responses/**`) não é versionado — licença de terceiro.
O **catálogo** (`tools/ir-library.json` + `reference/16-ir-library.md`) é, porque é
insumo da documentação: é dele que sai o caminho exato da captura citado na seção 📡
no `patch.md` e o marcador 📁 no `MAPA-DO-ALBUM.md` de cada álbum.

Consequência para o seu PR: se você rodar `ir_library.py` **sem** o pack completo
que gerou o catálogo commitado, 97 docs perderiam a recomendação do banco local.
Como o `patch.md` e o mapa cairiam para "fábrica" juntos, a suíte passaria — então
o próprio script reprova a rodada
(`python tools/ir_library.py --force` só quando a remoção for intencional).

Regra prática: **não inclua `tools/ir-library.json` nem `reference/16-ir-library.md`
no PR** a menos que esteja reindexando o banco de propósito, e diga isso na descrição.

## 🎸 Acrescentando conteúdo (o caminho mais comum)

### Um patch novo para uma música existente

1. Abra o fragmento do álbum (`tools/defs/<CHAVE>.json`) e localize a música.
2. Acrescente a camada no array de patches da música. O `nome` no painel é
   `MÚSICA+CAMADA` e tem **máximo 12 caracteres** (`STH01BA`, `CT01RIF`).
3. Preencha o dossiê do rig com **fontes** — o projeto exige lastro pesquisável,
   não "achismo" de timbre.
4. Rode o pipeline completo (bloco acima).
5. Confira a seção 📡 do `patch.md` gerado: ela precisa obedecer à [política de
   IR](#-política-de-ir) — fábrica → banco local → internet → fábrica.

> **Pelo agente**, este caminho é o mesmo: `@gp100-patch-architect` entrevista,
> consulta as skills, valida com o `gp100-patch-validator` e **acrescenta o item no
> `tools/defs/`** — ele não escreve em `patches/**` (ver `knowledge.md`,
> regra 8). O que você revisa no PR é o **defs** e os derivados que o pipeline gerou.

### Um álbum inteiro novo

1. Crie o seeder `tools/add_<album>_defs.py` seguindo `add_pulse_defs.py`
   (o padrão é o seeder encadear `add_momentos`).
2. Crie `tools/defs/<CHAVE>.json` com `idAlbum`, `album` (`banda`, `ano`, `pasta`,
   `titulo`, o dossiê de rig e o `ir_local` de cada cab usado.
3. Encadeie o novo seeder no `PIPELINE` de `tests/test_pipeline.py` —
   um seeder fora da lista simplesmente não roda no guarda de sincronia.
4. Rode o pipeline, revise os `MAPA-DO-ALBUM.md` gerados e a numeração de slots.

## 🚦 Regras de ouro (revisão bloqueia o que violar)

Estas são as invariantes que a suíte testa. Um PR que as quebre não passa:

- **Patches por música, nunca compartilhados.** Cada faixa tem seu conjunto e
  cada camada tem seu patch; nome no painel `MÚSICA+CAMADA`, ≤ 12 caracteres.
- **Camadas separadas só quando o timbre muda de verdade** — e todo toggle ganha
  um **momento documentado** (a GP-100 liga/desliga módulos em tempo real).
- **NomES de parâmetro 100% oficiais** (manual do firmware V2.0). **Zero rótulo
  `pN`** na documentação: slots internos que o editor não expõe não são setados
  nem rotulados.
- **Precedência do catálogo fw 2.0/2.1** sobre o manual impresso V1.8 —
  ver `reference/15-firmware2-effects.md`.
- **NR obrigatório com ganho ≥ 55**; **um** efeito espacial dominante por patch.
- **`.prst` sempre no formato single fw 2.1** com CAB de fábrica. IR de terceiro
  é **documentada**, nunca embutida (ver política abaixo).
- **O spec não vira arquivo** — vai in-memory do defs ao codec (ADR-0013): não
  existe intermediário em disco, logo nada a versionar ou empacotar.

## 📡 Política de IR

Escrita em `knowledge.md` e achatada em testes (`TestB_FonteUnica_IR`). Toda
seção 📡 de `patch.md` segue **esta ordem**, sem pular etapa:

1. **O que o `.prst` usa agora** — CAB de fábrica; funciona ao importar, sem
   nenhum passo manual.
2. **Melhor captura no banco local** — arquivo exato em `impulse_responses/`,
   slot de User IR sugerido e passo a passo.
3. **Download gratuito** — só quando nem fábrica nem banco cobrem o gabinete
   real; monte o link e o caminho.
4. **Fallback garantido** — o CAB de fábrica, sempre.

Duas regras que não se negociam: **não embutimos WAV de terceiro no repositório**
(licença alheia — ver [`NOTICE.md`](NOTICE.md)) e **não pesquisamos na internet**
se a captura já existe no banco local.

## 📝 Padrão de commits — Conventional Commits

Formato: `<tipo>(<escopo>): <descrição no imperativo, minúscula, sem ponto final>`

| Tipo | Quando usar |
|---|---|
| `feat` | Conteúdo ou capability nova (patch, camada, álbum, flag) |
| `fix` | Correção de dado errado, bug de script ou de doc |
| `data` | Regeneração de dados do pipeline (use com moderação) |
| `docs` | Só documentação: `README`, `reference/`, `knowledge.md` |
| `refactor` | Reorganização sem mudar a saída gerada |
| `test` | Suíte em `tests/` |
| `ci` | Workflows em `.github/workflows/` |
| `chore` | Manutenção (deps, gitignore, tooling) |

```bash
git commit -m "feat(pulse): adiciona camada de solo em Time"
git commit -m "fix(ir): corrige cab recomendado no mapa do Abbey Road"
git commit -m "docs(contributing): detalha o fluxo de commit"
```

Breaking change: `feat(prst)!: ...` ou um rodapé `BREAKING CHANGE:` explicando a
migração. O `tools/gen_changelog.py` lê este padrão para montar o `CHANGELOG.md`
e sugerir o próximo bump de versão — commit fora do padrão **não aparece** no
changelog.

## 🌊 Fluxo de trabalho — develop → main

Duas branches, papéis claros:

| Branch | Papel | Push direto | Protegida |
|---|---|---|---|
| `develop` | onde o trabalho acontece — todo desenvolvimento novo entra aqui | ✅ sim | não |
| `main` | o que foi publicado — só recebe release aprovada; o merge aqui dispara a Release | ❌ não | ✅ sim |

```bash
git switch develop && git pull

# ... edite os defs, rode o pipeline e a suíte ...

git add tools/defs/ reference/
git commit -m "feat(pulse): adiciona camada de solo em Time"
git push
```

| Passo | Exigência |
|---|---|
| Commits na `develop` | Conventional Commit (é o que alimenta o `CHANGELOG.md` no release) |
| CI | roda a cada push na `develop` — o `🚦 Veredito do CI` precisa estar verde |
| `main` | só recebe código pelo PR de release (`develop` → `main`); contribuição externa abre PR contra a `develop` |
| Checks | `🚦 Veredito do CI` verde é obrigatório — não há merge com CI vermelho |

O CI roda no **push para `develop` e `main`** e em **todo PR**: o push na
`develop` é a checagem primeira (quebrou, conserta lá), e o PR de release roda
de novo sobre o merge ref antes de entrar na `main`.

### Publicando uma versão (a `main` só é alimentada por release aprovada)

Na `develop`, prepara a versão; quando a release for aprovada, o PR alimenta a `main`:

```bash
git switch develop && git pull
python tools/gen_changelog.py --version 1.1.0 --write   # prepende a seção no CHANGELOG.md
printf '%s\n' 1.1.0 > VERSION
git commit -am "chore(release): v1.1.0"
git push

# quando a release for aprovada:
gh pr create --base main --head develop --title "chore(release): v1.1.0"
gh pr merge --merge
```

Repare: **`develop` → `main` é merge commit** (e sem `--delete-branch`, que
apagaria a `develop`). Não é capricho — um squash na entrada da `main` juntaria
a release inteira num commit e as mudanças que alimentam o changelog ficariam só
na `develop`. Com merge commit a `main` contém a história da `develop`, e a
`develop` continua sendo ancestral dela: não há nada para sincronizar de volta a
cada release.

No merge para a `main`, o [`release.yml`](.github/workflows/release.yml) roda
sozinho: empacota os ZIPs, cria a tag `v1.1.0` e publica a Release. **A versão é
decidida por quem escreveu o PR, não por tempo decorrido** — e um merge que não
subiu o `VERSION` não publica nada (é um no-op verde).

Deixe o PR em **draft** enquanto o pipeline estiver instável. Ao abrir, ele já
vem com o [`PULL_REQUEST_TEMPLATE`](.github/PULL_REQUEST_TEMPLATE.md): marque as
caixas de verdade, são elas que o revisor vai conferir.

### Abrindo o PR — a informação vem no comando

Um PR aberto sem label, sem milestone e sem assignee não é um PR: é um diff à
procura de dono. O card no Project, o corte por milestone e o "quem puxa" vivem
desses três campos — então eles entram no **comando** que abre o PR, não na
memória de quem abriu:

```bash
gh pr create --base develop --fill \
  --title "feat(agents): gp100-setlist" \
  --label "type: feature" --label "scope: agents" --label "size: M" --label "priority: p2-medium" \
  --milestone "v2.0.0 — Formato, site e escala" \
  --assignee @me \
  --body "... Closes #48"
```

Regra prática dos rótulos: **um** `type:`, **um ou mais** `scope:`/`area:`, **um**
`size:` (se `size: XL`, provavelmente são dois PRs) e **um** `priority:` quando a
ordem importa. O guardian cobra em cada push: label ausente **reprova**; sem
milestone e sem assignee ele **avisa** (o aviso aparece nos checks, não some).

**A branch do PR morre no merge.** O repositório está com *Automatically delete
head branches* ligado (`delete_branch_on_merge`), então o merge pela interface já
limpa a branch. Pela CLI, diga isso explicitamente:

```bash
gh pr merge 38 --merge --delete-branch   # develop: a branch do trabalho morre aqui
gh pr merge 39 --merge                   # develop → main: NUNCA com --delete-branch
```

A exceção é o PR de release (`develop` → `main`): ali a branch de origem **é** a
`develop`, e apagá-la levaria a linha de trabalho inteira. Branch que ficou para
trás não precisa de arqueologia: `git fetch --prune && git branch --merged
origin/develop` mostra o que já entrou e pode sair.

## 👀 Revisão

Um PR é aprovado quando:

1. O `ci-gate` está verde (`test-suite`, `quality`, `typecheck`).
2. **O review foi lido** — checks verdes não são aprovação (ver checklist abaixo).
3. O diff **não** contém arquivo gerado editado à mão nem lixo de regeneração.
4. Documentação e `reference/` acompanham a mudança — dado novo sem doc é
   revisão incompleta.
5. As regras de ouro acima valem no PR.
6. Nada de binário de terceiro no diff (WAV de pack pago, PDF de fabricante).

Se você não tiver certeza sobre um ponto, **abra a PR em draft e pergunte** — é
mais barato que discutir depois do merge.

### ✅ Antes de mergear (quem mergeia)

`gh pr checks` mostra **checks**, não **review**. Aconteceu neste repositório:
o PR #35 foi mergeado com o `ci-gate` verde e dois comentários de review do
CodeQL apontando Action de terceiro sem pinagem — alerta que só apareceu dias
depois, no painel de segurança. O ritual é:

```bash
# 1. Checks verdes
gh pr checks <n>

# 2. Review lido — reviews, comentários inline e a conversa toda
gh api repos/{owner}/{repo}/pulls/<n>/reviews --jq '.[] | "\(.user.login) [\(.state)]\n\(.body)"'
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | "\(.user.login) @ \(.path):\(.line)\n\(.body)"'
gh pr view <n> --comments

# 3. Alertas de segurança (inclusive os que viraram comentário de review)
gh api repos/{owner}/{repo}/code-scanning/alerts?state=open
```

Regra de leitura: **comentário de review aberto é bloqueio**, mesmo com CI
verde — inclusive quando vem de bot (`github-advanced-security`, CodeQL,
Dependabot). Se o achado não for resolvido no PR, ele precisa de issue de
acompanhamento **antes** do merge, citada no corpo.

> **Se o review veio de bot e está vazio** (ex.: cota do Copilot esgotada), isso
> não é aprovação: revise você mesmo o diff e diga no PR quem revisou.

## 🔒 Segurança e o escopo de escrita do CI

**Nenhum workflow escreve no repositório.** O `ci.yml` roda inteiro com
`permissions: contents: read` e o `release.yml` só cria tag (proteção de branch
não governa tag). Consequências práticas para quem contribui:

- Quem acrescenta música, camada, patch, efeito, momento de toggle ou pack de IR
  **roda o pipeline localmente e commita os derivados** — o CI reprova com o
  comando exato de conserto, e a correção é sempre do autor, nunca do bot.
- Se algum job um dia voltar a commitar no `main`, o push será rejeitado pela
  branch protection: o repositório não abre exceção de escrita para o CI.
- Usar IA para editar arquivos é permitido e comum aqui — mas **revise o diff**.

## 📄 Licença

Ao contribuir, você aceita que sua contribuição seja licenciada sob o
[`LICENSE`](LICENSE) do projeto (MIT). O que o MIT **não** cobre — marcas, títulos
de música, manual do fabricante e packs de IR — está em [`NOTICE.md`](NOTICE.md).
Não envie material de terceiros cuja licença não permita redistribuição.
