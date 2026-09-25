"""Camada de aplicação — casos de uso que orquestram domínio e infraestrutura.

O que entra aqui (PKG-004…006, na ordem do roadmap 2.0):

* `validar_defs`   — relatório acionável para a CLI (hoje só o domínio existe)
* `montar_setlist` — a cola de palco (`application.setlist`, issue #49)
* `consultar_defs` — busca/diff/export usados pela CLI e, depois, pela API

Contrato da camada: recebe **dados já carregados** ou caminhos explícitos,
devolve resultados tipados e nunca imprime — quem fala com o humano é a
interface (CLI hoje, API/UI na 2.1). Assim a UI futura reusa o caso de uso sem
herdar `print` e código de saída do terminal.
"""
