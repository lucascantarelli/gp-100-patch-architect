"""Suíte completa — a pirâmide pytest (issue #34).

    tests/unit/         regras puras, sem disco (rápidos)
    tests/integration/  casos de uso sobre o dado real (defs commitado)
    tests/contract/     formato .prst e CLI gp100 — a especificação dos contratos
    tests/e2e/          produto final e guardas de integridade (TestH incluso)
    tests/fixtures/     factories de defs/patch sintéticos

Markers: unit · integration · contract · e2e · slow (fonte: conftest.py).
Regra transversal: NENHUM teste escreve no repositório — tmp_path sempre;
com --guarda-repo (padrão no CI) o fim da sessão audita o working tree.
"""
