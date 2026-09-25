# Investigação do import "all" — um arquivo por biblioteca? (issue #83)

Premissa do [ADR-0013](../docs/decisions/0013-modelo-de-artefatos-em-escala.md)
que faltava verificar: o firmware distingue export *single* de *all* (é a
origem do erro `Wrong patch file type (single/all)`), mas **nunca testamos se
o aparelho/GP-100 Edits importam um arquivo "all" gerado por nós**. Em escala,
um "all" válido por álbum muda a adoção: o músico importa 1 arquivo em vez de N.

## O que já está pronto (parte de software)

- **Writer do formato**: [`all_writer.py`](../src/gp100_architect/infrastructure/prst/all_writer.py)
  — `gerar_xml_all(specs, templates, user_irs=…)`; reuso total do codec single
  (cada bloco `<presets>` é **byte a byte** o do single correspondente — prova
  no teste `test_bloco_preset_e_byte_a_byte_o_do_single`).
- **Reader** já lê "all" (era treinado no export de fábrica): round-trip
  provado em `tests/unit/test_all_writer.py`.
- **Receita derivada** (single repetido + três diferenças):
  `count="N"` no `<preset_info>`; N blocos `<presets>`; `<ppIRInfo>` com os
  20 slots `ppIRInfo0..19` (`ppIRNum = 168820736+i`, `ppIRCRC`/`ppIRCRCType` —
  slots sem IR informado saem com CRC "0"), opcional quando a biblioteca não
  tem IR local. Mesma serialização: UTF-8, CRLF, firmware 2.1, timestamp
  determinístico.

**Gerar os candidatos de teste** (da raiz do repo; cria 3 arquivos na pasta atual
— 1 patch, 2 patches e 1 patch com `<ppIRInfo>`):

```bash
uv run python -c "
from pathlib import Path
from gp100_architect.application import biblioteca
from gp100_architect.infrastructure.defs import carregar_e_validar
from gp100_architect.infrastructure.prst.all_writer import gerar_xml_all_de_singles
from gp100_architect.infrastructure.prst.codec import load_templates
from gp100_architect.infrastructure.ir_catalog import carregar, indice_por_cab
defs = carregar_e_validar()
manifesto = carregar(Path('data/ir-library.json'))
gerados = biblioteca.gerar(defs, raiz=Path('dist/all-test'), ir_index=indice_por_cab(manifesto), templates=load_templates(Path('data/factory-catalog.json')))
singles = [g.prst for g in gerados[:2]]
Path('all-1-patch.prst').write_bytes(gerar_xml_all_de_singles(singles[:1]))
Path('all-2-patches.prst').write_bytes(gerar_xml_all_de_singles(singles))
Path('all-1-patch-irinfo.prst').write_bytes(gerar_xml_all_de_singles(singles[:1], user_irs=[{'crc': '12345', 'crc_type': '1'}]))
print('3 candidatos gerados —', gerados[0].nome, gerados[1].nome)
"
```

## Protocolo de teste (mantenedor — requer acesso físico)

1. **GP-100 Edits (desktop)**: importar `all-1-patch.prst` → registrar: aceita?
   O patch aparece com nome/params corretos? Repetir com `all-2-patches.prst`.
2. **Aparelho (cartão SD)**: mesmo arquivo, segundo canal. Registrar igual.
3. **`<ppIRInfo>`**: importar `all-1-patch-irinfo.prst` — o CRC "fake" é
   aceito/ignorado/recusado? (o doc 15 adverte: o editor recalcula ao carregar
   IRs novas; o aparelho pode tratar CRC "0" como slot vazio).
4. **Limites, se aceitar**: N máximo por arquivo? Nomes/ordem preservados?
   IRs locais sobrevivem ao import?
5. **Registrar** o veredito nesta seção (fotos/vídeo no PR da conclusão).

## Veredito

_(a preencher com o resultado empírico — aceito com receita final ou recusado
com evidência; os critérios de aceite da #83 seguem daqui.)_

| Candidato | GP-100 Edits | Aparelho | Observação |
|---|---|---|---|
| `all-1-patch.prst` | — | — | |
| `all-2-patches.prst` | — | — | |
| `all-1-patch-irinfo.prst` | — | — | |

**Se importável**: abrir issue de implementação (writer no empacotamento da
release do ADR-0013 — um ZIP com 1 arquivo por álbum em vez de N).
**Se não importável**: atualizar a tabela do ADR-0013 (premissa resolvida:
single apenas) e encerrar a #83.
