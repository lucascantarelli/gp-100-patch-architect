# Prompt — Ajustar patch existente

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
3. Atualizar `patch.md` + changelog e devolver a receita de digitação só dos itens alterados.

Exemplo preenchido:
```
Ajustar patch BL-CRN-D01
O que testei: shuffle em A com drum 17, captador bridge
O que senti: agulha demais nos agudos; quando paro de tocar o chiado continua
O que quero: menos brilho e ruído parado menor
Manter: o drive e o reverb estão ótimos
```
