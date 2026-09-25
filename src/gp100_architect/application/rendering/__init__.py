"""Renderização de documentos da biblioteca (issue #30).

Templates puros: recebem dados já carregados e devolvem texto. Nada aqui lê
disco, imprime ou importa da infraestrutura — é o que permite testar a documentação
sem gerar arquivo e o que a UI/API futura reaproveita.

* `patch_md` — o `patch.md` de um patch (as 9 seções + receita de digitação).
* `variante_md` — o `patch.md` da variante -USERIR (seção de IR reescrita).

Convenção de import: direto do submodule (`from gp100_architect.application.rendering
import patch_md`) — este `__init__` não reexporta.
"""
