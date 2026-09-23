"""Testes do validador defs_schema.py — mutações em memória, zero escrita.

O validador roda embutido no build (carregar_e_validar) e via CLI; aqui
validamos as mensagens acionáveis injetando erros em cópias do defs real
(padrão do projeto: nenhum teste escreve no repositório).
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import defs_schema  # noqa: E402

from gp100_architect.infrastructure.defs import carregar  # noqa: E402
DEFS = carregar(ROOT / 'tools' / 'defs')  # schema v2 (issue #8): fragmentos por álbum


def patch_por_nome(d, nome):
    """(song, patch) localizado pelo nome do painel — para mutações realistas."""
    for song in d['songs']:
        for patch in song['patches']:
            if patch['nome'] == nome:
                return song, patch
    raise KeyError(nome)


def mutar(**mudancas):
    """Cópia profunda do defs real com uma mutação aplicada por callback."""
    d = copy.deepcopy(DEFS)
    for aplicar in mudancas.values():
        aplicar(d)
    return d


class A_DadosReais(unittest.TestCase):
    """O defs commitado tem de passar — sempre."""

    def test_defs_atual_e_valido(self):
        er = defs_schema.validar(copy.deepcopy(DEFS))
        self.assertTrue(er.ok(), er.relatorio())

    def test_carregar_e_validar_retorna_def(self):
        d = defs_schema.carregar_e_validar()
        self.assertIn('songs', d)


class B_ErrosAcionaveis(unittest.TestCase):
    """Cada mutação tem de produzir erro com caminho JSON + correção."""

    def _um_erro_contem(self, defs, *termos):
        er = defs_schema.validar(defs)
        self.assertFalse(er.ok(), 'esperava erro e veio OK')
        txt = er.relatorio()
        for t in termos:
            self.assertIn(t, txt, f"'{t}' ausente no relatório:\n{txt}")

    def test_nome_maior_que_12(self):
        d = copy.deepcopy(DEFS)
        patch_por_nome(d, 'CT01RIF')[1]['nome'] = 'NOMEGRANDE134'
        self._um_erro_contem(d, '13 chars', 'máx. 12')

    def test_nome_duplicado(self):
        d = copy.deepcopy(DEFS)
        d['songs'][0]['patches'][0]['nome'] = d['songs'][1]['patches'][0]['nome']
        self._um_erro_contem(d, 'duplicado')

    def test_idalbum_desconhecido(self):
        d = copy.deepcopy(DEFS)
        d['songs'][0]['idAlbum'] = 'XX'
        self._um_erro_contem(d, 'idAlbum', 'XX', 'ids válidos')

    def test_bpm_impossivel(self):
        d = copy.deepcopy(DEFS)
        d['songs'][0]['bpm'] = 999
        self._um_erro_contem(d, 'bpm', '30–300')

    def test_modulo_fora_da_cadeia(self):
        d = copy.deepcopy(DEFS)
        d['songs'][0]['patches'][0]['spec']['modules']['ZZ'] = {'name': 'X', 'on': False}
        self._um_erro_contem(d, 'modules.ZZ', 'cadeia fixa')

    def test_toggle_de_amp_proibido(self):
        d = copy.deepcopy(DEFS)
        d['songs'][0]['patches'][0]['doc']['momentos'] = [
            {'nome': 'x', 'mods': [['AMP', 'OFF']], 'quando': 'nunca'}]
        self._um_erro_contem(d, 'momentos', 'AMP/CAB é proibido')

    def test_time_fora_de_ms(self):
        d = copy.deepcopy(DEFS)
        patch_por_nome(d, 'SMOO1SO')[1]['spec']['modules']['DLY']['params']['1'] = 5000
        self._um_erro_contem(d, 'ms fora de 0–1000')

    def test_param_nao_numerico(self):
        d = copy.deepcopy(DEFS)
        patch_por_nome(d, 'SMOO1SO')[1]['spec']['modules']['DLY']['params']['1'] = 'muito'
        self._um_erro_contem(d, 'não numérico')

    def test_genero_invalido(self):
        d = copy.deepcopy(DEFS)
        patch_por_nome(d, 'SMOO1SO')[1]['spec']['type'] = 'Samba'
        self._um_erro_contem(d, 'type', 'Samba', 'gênero válido')

    def test_ir_local_orfao(self):
        d = copy.deepcopy(DEFS)
        d['ir_local']['Cab Fantasma'] = {'captura': 'x.wav', 'slot': 'User IR 9'}
        self._um_erro_contem(d, 'ir_local.Cab Fantasma', 'nenhum patch usa')


class C_Python314(unittest.TestCase):
    def test_guarda_de_runtime_exposto(self):
        # o entry point levanta SystemExit com mensagem clara se < 3.14;
        # aqui só garantimos que a política está definida no módulo
        self.assertEqual(defs_schema.PY_OK, (3, 14))


if __name__ == '__main__':
    unittest.main()
