# FAQ — as perguntas que o histórico responde

**Leia isto se** a sua dúvida já foi de alguém — as respostas aqui vieram das
issues e discussões do repositório, consolidadas. Os guias por público estão
em [docs/](README.md).

## Uso

**Os patches funcionam em firmware 2.0?**
Não — o formato da biblioteca é o **single fw 2.1**, verificado no aparelho.
O 2.0 do export antigo é rejeitado (doc 15). Atualize o firmware.

**Preciso gravar as IRs do banco local?**
Só para os patches que recomendam captura local (seção 📁 do `patch.md`). Sem
o WAV no slot, o patch soa com o CAB de fábrica — não quebra nada.

**Posso importar um arquivo com vários patches de uma vez?**
Ainda não — a biblioteca só gera o formato *single*. A investigação do
formato "all" está na [#83](https://github.com/lucascantarelli/gp-100-patch-architect/issues/83):
a parte de software (writer + receita) está pronta em
`reference/24-import-all.md`; falta o teste empírico no aparelho.

**Como acho um patch pelo som, não pelo nome?**
[Busca do site](https://lucascantarelli.github.io/gp-100-patch-architect/)
(client-side, por música/álbum) ou `uv run gp100 find <termo>` no repo.

## Contribuição

**Por que `patches/**` não está no git?**
ADR-0013: **derivados são construídos, não armazenados** — `data/defs/` é a
fonte única; o `.prst`/`patch.md` nascem no build (determinístico, timestamp
fixo) e no job de release. Por isso clonar não traz os XMLs: `uv run gp100 build`.

**Minha suíte falha num clone novo, mas o CI passa. Por quê?**
Não deveria mais — era o achado A1 da auditoria do DoD (testes lendo
derivado do disco); consertado no PR #102. Se reproduzir, é bug novo: abra issue.

**O que o erro "fragmento FORA do manifesto" significa?**
Criei um `data/defs/FOO.json` e não o declarei em `data/defs/_albums.json`
(o índice dos fragmentos — o validador cobra).

**Posso editar um `.prst` direto?**
Não. É derivado e o formato é byte a byte (CRLF, ordem de atributos). Edite o
defs e rode o build.

## Arquitetura

**Por que um pacote Python e não scripts?**
ADR-0001/ADR-0002: camadas (`domain` → `application` → `infrastructure` →
`interfaces`), `gp100` único, testável por pirâmide. O legado `tools/` foi
extinto na #33.

**Os agentes podem decidir sozinhos?**
Não. O contrato (ADR-0008) fixa identidade, "quando usar" e **limites
explícitos** — o `gp100-release-proposer`, por exemplo, propõe o bump com
evidência e **nunca decide**; a guarda de integridade (#63) reprova no CI
agente sem limites, caminho citado inexistente ou skill fora da curadoria.

**Por que a doc não é versionada no site?**
É — os **fontes** versionados são os `.md` do repo. O site (biblioteca e doc
de engenharia) é **gerado no deploy** e publicado sem commitar (decisões da
#11/#60): nada de derivado no git.

**Qual é o estado da 2.0?**
[Panorama na #59](https://github.com/lucascantarelli/gp-100-patch-architect/issues/59)
e auditoria do DoD (`docs/audit-dod-2.0.md`): 11/12 métricas verdes com
verificação mecânica; o que falta de verdade é a release em si.
