"""Camada **e2e** — produto final e guardas de integridade (issue #34).

Duas famílias vivem aqui:

* **derivados** — o que o pipeline entrega ao músico (`.prst`, `patch.md`,
  momentos): provado sobre os arquivos construídos a partir do defs;
* **guardas** — a integridade que já quebrou uma vez e não pode quebrar de
  novo: índices em disco sem drift, ordem estável entre OS, o GUARDA DE
  SINCRONIA (TestH: o pipeline reproduz os derivados byte a byte num sandbox)
  e a conexão defs × disco × agentes.

É a camada mais lenta (o TestH roda o pipeline inteiro numa cópia temporária
do repositório): por isso os testes de sandbox carregam `pytest.mark.slow` —
a fatia rápida da suíte (`-m "not slow"`) continua útil no dia a dia.
"""
