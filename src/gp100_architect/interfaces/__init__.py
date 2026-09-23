"""Interfaces — os adaptadores de entrada do sistema.

`cli/` é o adaptador de hoje. A 2.1 acrescenta `api/` (FastAPI) sobre os mesmos
casos de uso, e a UI futura consome a API — nunca os módulos internos
(ADR-0004: sem lógica nos adaptadores).
"""
