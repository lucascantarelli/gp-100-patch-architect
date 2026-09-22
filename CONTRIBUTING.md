# Contribuindo com o GP-100 Patch Architect

Obrigado pelo interesse. Este projeto tem uma característica que muda tudo:
**metade dele é saída de script**. Os arquivos em `patches/**` são *gerados* a
partir de `tools/patches-defs.json`, e o CI reprova quem editar o gerado à mão.
Antes de abrir um PR, leia a seção [O pipeline é obrigatório](#-o-pipeline-é-obrigatório).

Ao participar, você concorda com o [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
Para vulnerabilidades, **não** abra issue: siga o [`SECURITY.md`](SECURITY.md).

---

## 🧰 Ambiente de desenvolvimento

Tempo de setup: ~2 minutos. Não há dependências para instalar.

| Requisito | Versão | Usado por |
|---|---|---|
| **Python** | 3.14 (3.11+ funciona) | `tools/`, `tests/` — **só a biblioteca padrão** |
| **Node.js** | 26 (20+ funciona) | typecheck dos agentes em `.agents/` |
| **Git** | qualquer | — |

```bash
git clone https://github.com/lucascantarelli/gp-100-patch-architect.git
cd gp-100-patch-architect

# Não existe requirements.txt, package.json nem venv obrigatório:
# os scripts usam a stdlib; o typecheck puxa o TypeScript via npx.
python --version    # 3.14.x
node --version      # v26.x
```

> **💡 Assinatura dos dados:** `tools/patches-defs.json` é a **fonte única** de
> músicas, álbuns, patches e IRs recomendadas. Os scripts são renderizadores —
> nenhum deles tem lista de músicas ou de cabs dentro do código. Acrescentar
> dado é editar o defs, nunca o gerador.

Páginas do manual sob demanda (opcional; requer `pymupdf` e o `manual.pdf`
local, que não é versionado):

```bash
pip install pymupdf
python tools/render_manual_page.py 21        # página impressa NN = arquivo NN+2
```

## ✅ Antes de abrir um PR: rode exatamente o que o CI roda

```bash
# 1. Suíte de testes (28 testes, stdlib pura)
python -m unittest discover -s tests -v

# 2. Typecheck dos 17 agentes
npx -y -p typescript@5.9.2 tsc --noEmit -p tsconfig.json
```

E, **se você mexeu em dados** (música, camada, patch, momento, pack de IR ou
cab):

```bash
# 3. Pipeline completo, na ordem do CI, + veredito de sincronia
python tools/ir_library.py \
  && python tools/add_pulse_defs.py \
  && python tools/add_momentos.py \
  && python tools/build_song_patches.py \
  && python tools/gen_indexes.py \
  && python tools/check_data_freshness.py
```

O último comando é o guarda: ele compara **disco × HEAD** e, se reprovar, imprime
o comando exato de conserto. Se ele passar, seu PR está coerente.

## 🔁 O pipeline é obrigatório

Este fluxo já quebrou em produção uma vez (ver a história do `TestB_FonteUnica_IR`
no [`README.md`](README.md)), então o CI trata esquecimento como falha de build:

| Você mexeu em | Obrigatório rodar |
|---|---|
| `tools/patches-defs.json` (álbum, música, patch, momento) | `add_pulse_defs.py` → `add_momentos.py` → `build_song_patches.py` → `gen_indexes.py` |
| Novos packs de IR em `impulse_responses/` | `ir_library.py` |
| Scripts em `tools/` | a suíte + o pipeline inteiro (a saída tem de continuar idêntica) |

**Nunca edite à mão** um arquivo gerado: `patches/**/*.prst`, `patches/**/patch.md`,
`patches/**/spec.json`, `patches/**/MAPA-DO-ALBUM.md`, `patches/README.md`,
`tools/patches-defs.json`, `tools/ir-library.json`, `reference/16-ir-library.md`.
Sua edição será apagada na próxima execução do pipeline e reprovada pelo guarda.

### ⚠️ O catálogo de IRs não é regenerável sem o pack

O **banco** de IRs (`impulse_responses/**`) não é versionado — licença de terceiro.
O **catálogo** (`tools/ir-library.json` + `reference/16-ir-library.md`) é, porque é
insumo da documentação: é dele que sai o caminho exato da captura citado na seção 📡
no `patch.md` e o marcador 📁 no `MAPA-DO-ALBUM.md` de cada álbum.

Consequência para o seu PR: se você rodar `ir_library.py` **sem** o pack completo
que gerou o catálogo commitado, 62 docs perderiam a recomendação do banco local.
Como o `patch.md` e o mapa cairiam para "fábrica" juntos, a suíte passaria — então
o próprio script reprova a rodada
(`python tools/ir_library.py --force` só quando a remoção for intencional).

Regra prática: **não inclua `tools/ir-library.json` nem `reference/16-ir-library.md`
no PR** a menos que esteja reindexando o banco de propósito, e diga isso na descrição.

## 🎸 Acrescentando conteúdo (o caminho mais comum)

### Um patch novo para uma música existente

1. Abra `tools/patches-defs.json` e localize o álbum e a música.
2. Acrescente a camada no array de patches da música. O `nome` no painel é
   `MÚSICA+CAMADA` e tem **máximo 12 caracteres** (`STH01BA`, `CT01RIF`).
3. Preencha o dossiê do rig com **fontes** — o projeto exige lastro pesquisável,
   não "achismo" de timbre.
4. Rode o pipeline completo (bloco acima).
5. Confira a seção 📡 do `patch.md` gerado: ela precisa obedecer à [política de
   IR](#-política-de-ir) — fábrica → banco local → internet → fábrica.

### Um álbum inteiro novo

1. Crie o seeder `tools/add_<album>_defs.py` seguindo `add_pulse_defs.py`
   (o padrão é o seeder encadear `add_momentos`).
2. Adicione o álbum em `tools/patches-defs.json` com `banda`, `ano`, `pasta`,
   `titulo`, o dossiê de rig e o `ir_local` de cada cab usado.
3. Encadeie o novo seeder no `PIPELINE` de `tools/check_data_freshness.py` e no
   passo de dados de [`.github/workflows/ci.yml`](.github/workflows/ci.yml) —
   um seeder fora da lista simplesmente não roda no CI.
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
- **`spec.json` não vai ao pacote de release** — é insumo do gerador, não do
  músico.

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
(licença alheia — ver [`LICENSE`](LICENSE)) e **não pesquisamos na internet** se
a captura já existe no banco local.

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

## 🌊 Fluxo de trabalho — GitHub Flow

O `main` é protegido: **nada de push direto**. Todo trabalho entra por PR.

```bash
git switch main && git pull
git switch -c feat/solo-time-pulse

# ... edite os defs, rode o pipeline e a suíte ...

git add tools/patches-defs.json patches/ reference/
git commit -m "feat(pulse): adiciona camada de solo em Time"
git push -u origin feat/solo-time-pulse
gh pr create --fill
```

| Passo | Exigência |
|---|---|
| Título do PR | Conventional Commit (vira a linha do `CHANGELOG.md`) |
| Base | `main` |
| Merge | **squash** — um PR, um commit limpo na história |
| Branch | apagada automaticamente após o merge |
| Checks | `🚦 Veredito do CI` verde é obrigatório — não há merge com CI vermelho |

Deixe o PR em **draft** enquanto o pipeline estiver instável. Ao abrir, ele já
vem com o [`PULL_REQUEST_TEMPLATE`](.github/PULL_REQUEST_TEMPLATE.md): marque as
caixas de verdade, são elas que o revisor vai conferir.

## 👀 Revisão

Um PR é aprovado quando:

1. O `ci-gate` está verde (`data-pipeline`, `test-suite`, `typecheck`).
2. O diff **não** contém arquivo gerado editado à mão nem lixo de regeneração.
3. Documentação e `reference/` acompanham a mudança — dado novo sem doc é
   revisão incompleta.
4. As regras de ouro acima valem no PR.
5. Nada de binário de terceiro no diff (WAV de pack pago, PDF de fabricante).

Se você não tiver certeza sobre um ponto, **abra a PR em draft e pergunte** — é
mais barato que discutir depois do merge.

## 🔒 Segurança e o auto-commit do CI

O job `data-pipeline` tem permissão de **escrita** e, em push no `main`, commita
os dados regenerados sozinho. Consequências práticas para quem contribui:

- Usar IA para editar arquivos é permitido e comum aqui — mas **revise o diff**:
  o bot publica o que o pipeline produziu.
- PR vindo de fork **não** dispara o auto-commit (fork não tem escrita); nesse
  caso o guarda reprova e mostra o comando de conserto, para você rodar local.

## 📄 Licença

Ao contribuir, você aceita que sua contribuição seja licenciada sob o
[`LICENSE`](LICENSE) do projeto (MIT). Não envie material de terceiros cuja
licença não permita redistribuição.
