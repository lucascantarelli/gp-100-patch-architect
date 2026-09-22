<!--
Título do PR: use Conventional Commit — ele vira a linha do CHANGELOG.md.
  feat(pulse): adiciona camada de solo em Time
  fix(ir): corrige cab recomendado no mapa do Abbey Road
  docs(contributing): detalha o fluxo de commit
Detalhes em CONTRIBUTING.md. Abra em draft enquanto o pipeline estiver instável.
Base: `develop` — só o PR de release (develop -> main) vai contra a `main`.
-->

## O que muda

<!-- Duas ou três frases. O que o usuário final ganha com isso? -->

## 🗂 Gestão (o guardian valida)

- [ ] Issue vinculada abaixo com **`Closes #N`** — o fechamento é automático pelo
      merge; nenhuma issue é fechada à mão
- [ ] **Milestone** associado ao PR (`gh pr edit --milestone "vX.Y.Z"` ou na sidebar)
- [ ] **Labels** aplicadas: `type: …` · `scope: …` · `size: XS–XL` (uma de cada;
      prioridade e status ficam no board)
- [ ] Card no **[Project v2](https://github.com/users/lucascantarelli/projects/1/views/1)**
      — ao abrir, a automação move para `In Progress`/`In Review`; no merge, para `Done`

Closes #

## Tipo de mudança

- [ ] `feat` — conteúdo ou capability nova (patch, camada, álbum, flag)
- [ ] `fix` — correção de dado, script ou doc
- [ ] `docs` — só documentação
- [ ] `refactor` — reorganização sem mudar a saída do pipeline
- [ ] `ci` — workflows
- [ ] `chore` — manutenção
- [ ] **Breaking change** — detalhe abaixo

---

## ✅ Checklist

### Pipeline e testes

- [ ] Rodei o pipeline completo e commitei a saída:
      `ir_library.py` → `add_pulse_defs.py` → `add_momentos.py` → `build_song_patches.py` → `gen_indexes.py`
- [ ] `python -m unittest discover -s tests -v` passa — a suíte inclui o guarda de
      sincronia (pipeline numa cópia temporária × commitado)
- [ ] `npx -y -p typescript@5.9.2 tsc --noEmit -p tsconfig.json` passa (se toquei em `.agents/`)
- [ ] **Não editei à mão** arquivo gerado: `patches/**/*.prst`, `patch.md`,
      `MAPA-DO-ALBUM.md`, `patches/README.md`, `tools/patches-defs.json`,
      `tools/ir-library.json`, `reference/16-ir-library.md`
- [ ] Se acrescentei um seeder, encadeei em `PIPELINE` (`tests/test_pipeline.py`) —
      seeder fora da lista não roda no guarda de sincronia

### Invariantes do projeto

- [ ] Todo patch novo é **por música** (não compartilhado) e o nome no painel tem **≤ 12 caracteres**
- [ ] Toda mudança de timbre de verdade virou **camada separada**, com **momento de toggle** documentado
- [ ] **Zero rótulo `pN`** em qualquer texto — nomes de parâmetro são os oficiais do manual V2.0
- [ ] Catálogo **fw 2.0/2.1** tem precedência sobre o manual impresso V1.8
- [ ] NR presente com **ganho ≥ 55**; **um** efeito espacial dominante por patch
- [ ] `.prst` continua no formato **single fw 2.1** com **CAB de fábrica**
- [ ] IR de terceiro está **documentada**, nunca embutida (seção 📡 na ordem:
      fábrica → banco local → internet gratuito → fábrica)
- [ ] A seção 📡 do `patch.md` e o `MAPA-DO-ALBUM.md` **concordam** sobre a IR
      (é a divergência que o `TestB_FonteUnica_IR` pega)

### Documentação e licença

- [ ] `README.md` / `reference/` / `knowledge.md` atualizados se o comportamento ou o
      catálogo mudaram
- [ ] Dossiê de rig novo tem **fontes linkadas** — nada de timbre por impressão pessoal
- [ ] Não comitei binário de terceiro (WAV de pack pago, PDF de fabricante, `manual.pdf`)
- [ ] `VERSION` / `CHANGELOG.md` só mudam em PR de release

### Revisão

- [ ] Descrevi como **verifiquei** que funciona (o que você ouviu/rodou, não só "deve funcionar")
- [ ] Sei que o CI **não escreve no repositório**: se o teste de sincronia reprovar
      por dado defasado, sou eu que rodo o pipeline e commito os derivados

---

## Breaking change / migração

<!-- Só se marcou breaking change: o que quebra, quem é afetado e como migrar. -->

## Notas para o revisor

<!-- Onde olhar primeiro, o que ficou em dúvida, o que deixou fora de propósito. -->
