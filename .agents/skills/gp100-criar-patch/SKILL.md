---
name: gp100-criar-patch
description: "Use quando o usuário quiser criar um patch novo para a pedaleira Valeton GP-100 (estilo, limpo/sujo, contexto de uso, captador). Conduz a entrevista do fluxo gp100-patch-architect e persiste o patch via pipeline do projeto GP-100 Patch Architect."
---

# Criar patch GP-100

Cole no chat (com o `@gp100-patch-architect` ou fale com Buffy normalmente) preenchendo o máximo que souber — o agente pergunta o que faltar:

```
Criar patch GP-100

Estilo/música/referência: {ex.: blues SRV · indie arpeggiado tipo The Cure · metal moderno}
Limpo ou sujo: {clean / crunch / distorção / fuzz}
Contexto de uso: {gravar em casa com fone / banda / prática}
Captador pretendido: {bridge / middle / neck / tanto faz}
Efeitos desejados (opcional): {ex.: chorus no limpo, delay pontuado, wah no solo}
IR de terceiros: {quero uma IR gratuita / usar CAB de fábrica / tanto faz}
BPM (se rítmico): {ex.: 120}
Observações: {qualquer detalhe extra}
```

Exemplo preenchido:
```
Criar patch GP-100
Estilo: blues SRV
Limpo ou sujo: crunch com solos mais sujos
Contexto: gravar em casa com fone
Captador: bridge
Efeitos: reverb de mola e um tap delay leve
IR: tanto faz (CAB de fábrica)
BPM: 96
Observações: não pode sumir na mix de backing
```

> **Precedência**: dentro do projeto GP-100 Patch Architect, `knowledge.md` e
> `reference/` vencem esta skill em qualquer divergência. Fonte canônica do
> fluxo: `prompts/criar-patch.md` no repositório.
