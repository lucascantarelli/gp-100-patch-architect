"""Testes da CLI gp100.py (find/show/diff/export) — leitura pura, sem escrita.

Roda junto da suíte (`unittest discover -s tests`): usa o defs e os patches
commitados; nenhum teste escreve no repositório (regra do projeto).
"""
import json
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import gp100  # noqa: E402

DEFS = json.loads((ROOT / 'tools' / 'patches-defs.json').read_text(encoding='utf-8'))


class A_Slots(unittest.TestCase):
    """Numeração de slots — tem de concordar com gen_indexes.slot_map."""

    def test_slots_batem_com_gen_indexes(self):
        from gen_indexes import slot_map
        self.assertEqual(gp100.slots(DEFS), slot_map(DEFS))

    def test_primeiro_e_ultimo(self):
        smap = gp100.slots(DEFS)
        self.assertEqual(len(smap), 97)
        self.assertEqual(min(smap.values()), 'U01')
        self.assertEqual(max(smap.values()), 'U97')


class B_Find(unittest.TestCase):
    def _run(self, argv):
        out = StringIO()
        with redirect_stdout(out):
            rc = gp100.main(argv)
        return rc, out.getvalue()

    def test_find_acha_por_musica(self):
        rc, out = self._run(['find', 'money'])
        self.assertEqual(rc, 0)
        self.assertIn('MNY01BA', out)
        self.assertIn('U50', out)

    def test_find_acha_por_banda(self):
        rc, out = self._run(['find', 'santana'])
        self.assertEqual(rc, 0)
        self.assertIn('SMOO1SO', out)

    def test_find_sem_resultado_sai_1(self):
        rc, out = self._run(['find', 'zzznada'])
        self.assertEqual(rc, 1)


class C_Show(unittest.TestCase):
    def _run(self, argv):
        out = StringIO()
        with redirect_stdout(out):
            rc = gp100.main(argv)
        return rc, out.getvalue()

    def test_show_mostra_cadeia_params_momentos(self):
        rc, out = self._run(['show', 'smoo1so'])  # case-insensitive
        self.assertEqual(rc, 0)
        self.assertIn('U96', out)
        self.assertIn('Yellow OD', out)
        self.assertIn('Gain=48', out)
        self.assertIn('MOD→ON', out)

    def test_show_patch_inexistente_falha_com_dica(self):
        with self.assertRaises(SystemExit) as ctx:
            self._run(['show', 'ZZZZZZ'])
        self.assertIn('find', str(ctx.exception))


class D_Diff(unittest.TestCase):
    def test_diff_mostra_diferencas_reais(self):
        out = StringIO()
        with redirect_stdout(out):
            rc = gp100.main(['diff', 'STH01BA', 'STH01SO'])
        texto = out.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn('volume: 60 → 62', texto)
        self.assertIn('Blues OD → Green OD', texto)

    def test_diff_de_si_mesmo_nao_mostra_diferenca(self):
        out = StringIO()
        with redirect_stdout(out):
            gp100.main(['diff', 'SMOO1SO', 'SMOO1SO'])
        self.assertNotIn('±', out.getvalue())


class E_Export(unittest.TestCase):
    def _run(self, argv):
        out = StringIO()
        with redirect_stdout(out):
            rc = gp100.main(argv)
        return rc, out.getvalue()

    def test_listar_album_em_ordem_de_slot(self):
        rc, out = self._run(['export', '--album', 'SN', '--listar'])
        self.assertEqual(rc, 0)
        linhas = [l for l in out.splitlines() if 'SMOO' in l]
        self.assertEqual([l.split()[0] for l in linhas],
                         ['U94', 'U95', 'U96', 'U97'])

    def test_album_invalido_erro_acionavel(self):
        with self.assertRaises(SystemExit) as ctx:
            self._run(['export', '--album', 'ZZ', '--listar'])
        self.assertIn('AR', str(ctx.exception))  # lista os válidos


class F_ParamNames(unittest.TestCase):
    def test_rotulo_oficial_e_usado(self):
        # família DLY no manual V2.0: Mix/Time/Fdbk (ordem dos params)
        self.assertEqual(gp100.rotulo_param('DLY', 'Sweet', 1), 'Time')
        self.assertEqual(gp100.rotulo_param('DLY', 'Sweet', 0), 'Mix')


if __name__ == '__main__':
    unittest.main()
