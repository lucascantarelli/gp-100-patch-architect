---
name: gp100-ajustar-patch
description: "Use quando o usuário testou um patch GP-100 na pedaleira e voltou com reclamações concretas (muito agudo, cauda engolida, riff some na banda). Mapeia cada reclamação pela tabela de troubleshooting do reference/12-workflow.md e propõe mudanças mínimas (1–2 parâmetros), atualizando o defs via pipeline."
---

# Ajustar patch GP-100 existente

Depois de testar o patch na pedaleira, descreva o que sentiu — quanto mais concreto, melhor o ajuste:

```
Ajustar patch {ID ou pasta em patches/}

O que testei: {riff/música, captador, drum se usou}
O que senti:
- {ex.: muito agudo no fone}
- {ex.: a cauda das notas está sendo engolida}
- {ex.: o riff some quando entra o backing}
O que quero: {ex.: mais corpo, menos brilho, sustain maior}
Manter: {o que está bom e não deve mudar}
```

O agente vai:
1. Mapear cada reclamação para módulo/parâmetro (tabela de troubleshooting em `reference/12-workflow.md`).
2. Propor mudanças **mínimas** (1–2 parâmetros por problema).
3. Atualizar o **fragmento do álbum (`tools/defs/<CHAVE>.json`)** (campos `spec`/`doc` do patch) e rodar o pipeline — o `patch.md`, o `.prst` e o changelog do patch são gerados a partir dele; devolver a receita de digitação só dos itens alterados.

Exemplo preenchido:
```
Ajustar patch BL-CRN-D01
O que testei: shuffle em A com drum 17, captador bridge
O que senti: agulha demais nos agudos; quando paro de tocar o chiado continua
O que quero: menos brilho e ruído parado menor
Manter: o drive e o reverb estão ótimos
```

> **Precedência**: dentro do projeto, `knowledge.md` e `reference/` vencem esta
> skill (a tabela do doc 12 é a fonte do mapeamento). Fonte canônica:
> `prompts/ajustar-patch.md`. O agente `gp100-ab-tester` conduz a entrevista
> guiada deste fluxo.
