# Guia do usuário — do zero ao patch na pedaleira

**Leia isto se** você só quer **usar** os patches: tocar a biblioteca na sua
GP-100, gravar as IRs do banco local e importar os `.prst` sem tropeçar. Você
NÃO precisa ler arquitetura, ADRs nem o pipeline — volte ao
[README](https://github.com/lucascantarelli/gp-100-patch-architect) quando quiser
entender como funciona.

## 1 · Instalar

1. Instale o **Node.js 18+** (macOS/Windows/Linux) e o CLI do agente:
   `npm install -g freebuff`
2. Abra o agente dentro da pasta do projeto: `freebuff`
3. **Sem chave de API e sem Python** para usar a biblioteca pronta — o Python
   só é necessário para gerar patches novos (veja o [guia do contribuidor](guia-contribuidor.md)).

## 2 · Baixar os patches

O jeito navegável: **[site da biblioteca](https://lucascantarelli.github.io/gp-100-patch-architect/)**
— busca por música/álbum, página por patch com cadeia, parâmetros oficiais e
momentos. Os `.prst` e `patch.md` de cada patch se baixam do **GitHub Release**
(`Releases` → `gp100-patches-v<versão>.zip`), com o layout
`<Banda>/<Álbum>/<Música>/<NOME>/`.

## 3 · Gravar as IRs do banco local (uma vez)

Alguns patches recomendam capturas do banco local (a seção 📁 do `patch.md`):

1. Baixe o pack indicado na [doc 17](../reference/17-free-ir-packs.md)
2. Coloque o WAV no cartão SD em `USER IMPULSE` no slot indicado
   (`User IR 1`–`User IR 20` — o mapa de qual slot cada gabinete usa está no
   patch e no `MAPA-DO-ALBUM.md`)
3. Se o slot ficar vazio, o patch soa com o CAB de fábrica — não quebra nada

## 4 · Subir um patch na pedaleira

1. Copie o `.prst` para a raiz do cartão SD (formato FAT32)
2. No aparelho: **Import** → selecione o arquivo → confirme
3. Se o GP-100 Edits for o canal: `File → Import` e escolha o `.prst`

## 5 · Se a importação recusar: `tone-mismatch`

O erro `tone-mismatch` na validação (ou "Wrong patch file type" na pedaleira)
significa formato incompatível:

- **Use o `.prst` do Release da versão que casa com seu firmware 2.1** — o
  formato do projeto é o single fw 2.1 verificado no aparelho
- Não edite o XML à mão: CRLF e ordem de atributos são contrato
- Dúvida se o arquivo está íntegro? `uv run gp100 verify` (requer o setup do
  [guia do contribuidor](guia-contribuidor.md))

---

**Próximo passo**: escolha um patch no
[site](https://lucascantarelli.github.io/gp-100-patch-architect/) (comece por
**Smooth — Santana**, o mais documentado) e toque. Quer **criar** patch novo?
Vá para o [guia do contribuidor](guia-contribuidor.md).
