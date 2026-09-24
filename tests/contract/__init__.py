"""Camada **contract** — os contratos externos do produto (issue #34).

Dois tipos de contrato vivem aqui:

* o **formato `.prst`** (round-trip e bytes determinísticos, issue #29) —
  qualquer divergência impede a importação na pedaleira;
* a **CLI `gp100`** via CliRunner (issues #48/#49) — o `--json` com shape
  estável é a interface que agentes e automação consomem (issue #91).

Mudar algo aqui é breaking change por definição — os testes são a especificação.
"""
