"""Testes unitários do pacote — regras puras e funções isoladas (issue #34).

Novos testes nascem aqui, em pytest, marcados `unit`: sem disco, sem rede, sem
defs commitado (quem precisa do dado real está em `tests/integration/`). A
pirâmide completa: `unit` → `integration` → `contract` (CLI/formato) → `e2e`
(produto e guardas) — ver `tests/conftest.py` para os markers.
"""
