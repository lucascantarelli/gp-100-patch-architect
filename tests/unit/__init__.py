"""Testes unitários do pacote `gp100` (camada de domínio + adaptadores).

Novos testes nascem aqui, em pytest; os testes históricos de pipeline seguem em
`tests/` (unittest) até a migração da suíte (PKG-009). Marque o tipo do teste
com `@pytest.mark.unit|integration|contract|e2e` — o marcador é o que permite
rodar a pirâmide em fatias no CI.
"""
