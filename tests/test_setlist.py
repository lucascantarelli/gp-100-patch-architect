"""Testes da cola de palco (issue #15) — leitura do defs commitado; --out
grava em tmpdir (nenhuma escrita no repositório).
"""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

if sys.version_info[:2] < (3, 14):
    raise SystemExit('Este projeto roda Python 3.14 APENAS (ver tools/defs_schema.py).')

import gp100_setlist as sl  # noqa: E402
from gen_indexes import load_defs  # noqa: E402
# o script usa `carregar_e_validar`; a suíte legada chamava `load_defs` — mantida
# aqui para não reescrever os testes históricos (são migrados no #34)
sl.load_defs = load_defs
# a regra da distância também foi para o domínio (issue #28): o módulo legado
# não a define mais; a suíte histórica testa comportamento, não localização
from gp100_architect.domain.setlist import distancia as _distancia  # noqa: E402

sl.distancia = _distancia


class TestBiblioteca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = sl.Biblioteca(sl.load_defs())

    def test_resolver_por_nome_e_por_id(self):
        por_nome = self.lib.resolver('Come Together')
        por_id = self.lib.resolver('CT01')
        self.assertEqual(por_nome[0]['id'], por_id[0]['id'])

    com_secoes = ['CT01', 'STH01', 'OHB01', 'SMOO1', 'SLT01']

    def test_padrao_e_um_patch_com_secao(self):
        for sid in self.com_secoes:
            _, patch = self.lib.resolver(sid)
            self.assertTrue(patch['nome'].startswith(sid))

    def test_secao_explicita_por_dois_pontos(self):
        _, patch = self.lib.resolver('SMOO1:SO')
        self.assertEqual(patch['nome'], 'SMOO1SO')

    def test_patch_completo_aceito(self):
        musica, patch = self.lib.resolver('CT01VOX')
        self.assertEqual(patch['nome'], 'CT01VOX')
        self.assertEqual(musica['id'], 'CT01')

    def test_desconhecido_morre_com_systemexit(self):
        with self.assertRaises(SystemExit):
            self.lib.resolver('Não Existe Nada Disso')

    def test_secao_inexistente_sugere_as_disponiveis(self):
        with self.assertRaises(SystemExit) as ctx:
            self.lib.resolver('SMOO1:XX')
        self.assertIn('RI', str(ctx.exception))

    def test_catalogo_cobre_a_biblioteca(self):
        linhas = self.lib.catalogo()
        self.assertEqual(len(linhas), 58)


class TestChaveEDistancia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = sl.Biblioteca(sl.load_defs())

    def test_chave_tem_9_posicoes_pre_a_rvb(self):
        _, patch = self.lib.resolver('SMOO1:RI')
        self.assertEqual(len(sl.chave(patch)), 9)

    def test_iguais_zero_diferentes(self):
        _, p = self.lib.resolver('SMOO1:RI')
        self.assertEqual(sl.distancia(sl.chave(p), sl.chave(p)), 0)

    def test_distancia_conta_modelo_e_estado(self):
        a = {'spec': {'modules': {'PRE': {'name': 'COMP', 'on': False},
                                  'DST': {'name': 'X', 'on': True}}}}
        b = {'spec': {'modules': {'PRE': {'name': 'COMP', 'on': True},
                                  'DST': {'name': 'Y', 'on': True}}}}
        self.assertEqual(sl.distancia(sl.chave(a), sl.chave(b)), 2)


class TestOtimizacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = sl.Biblioteca(sl.load_defs())

    def itens(self, ids):
        return [self.lib.resolver(i) for i in ids]

    def test_comeca_na_primeira_e_termina_sem_repeticao(self):
        itens = self.itens(['CT01', 'STH01', 'MNY01', 'PMH01'])
        plano = sl.otimizar(itens)
        self.assertEqual(plano[0], itens[0])
        self.assertEqual(len({m['id'] for m, _ in plano}), len(itens))

    def test_vizinho_mais_proximo_escolhido(self):
        itens = self.itens(['SLT01', 'CT01', 'SCH01'])  # Nirvanas idênticos
        plano = sl.otimizar(itens)
        # começa no default (RI), vai ao Nirvana idêntico (0 trocas) e só
        # então cruza para os Beatles
        self.assertEqual([p['nome'] for _, p in plano],
                         ['SLT01RI', 'SCH01RI', 'CT01RIF'])

    def test_total_trocas_nunca_pior_que_ordem_dada(self):
        itens = self.itens(['CT01', 'PMH01', 'SLT01', 'STH01', 'MNY01'])
        ordem_dada = sum(sl.distancia(sl.chave(itens[i][1]), sl.chave(itens[i + 1][1]))
                         for i in range(len(itens) - 1))
        plano = sl.otimizar(itens)
        otimizado = sum(sl.distancia(sl.chave(plano[i][1]), sl.chave(plano[i + 1][1]))
                        for i in range(len(plano) - 1))
        self.assertLessEqual(otimizado, ordem_dada)


class TestDifCadeia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = sl.Biblioteca(sl.load_defs())

    def test_nada_muda_entre_nirvanas(self):
        _, ri = self.lib.resolver('SLT01:RI')
        _, so = self.lib.resolver('SLT01:SO')
        self.assertEqual(sl.dif_cadeia(ri, so), [])

    def test_modelo_diferente_aparece(self):
        _, ba = self.lib.resolver('STH01:BA')
        _, so = self.lib.resolver('STH01:SO')
        diffs = sl.dif_cadeia(ba, so)
        self.assertTrue(any('DST' in d and 'Green OD' in d for d in diffs))

    def test_ligar_desligar_aparece(self):
        _, ri = self.lib.resolver('SMOO1:RI')
        _, fl = self.lib.resolver('SMOO1:FL')
        diffs = sl.dif_cadeia(ri, fl)
        self.assertTrue(any('DST' in d for d in diffs))


class TestRelatorios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = sl.Biblioteca(sl.load_defs())
        itens = [cls.lib.resolver(i) for i in ['CT01', 'SLT01', 'STH01']]
        cls.plano = sl.otimizar(itens)
        cls.total = sum(sl.distancia(sl.chave(cls.plano[i][1]),
                                     sl.chave(cls.plano[i + 1][1]))
                        for i in range(len(cls.plano) - 1))

    def test_markdown_tem_slot_e_trocas(self):
        md = sl.plano_markdown(self.plano, self.total, self.lib.slots)
        self.assertIn('| # | Slot | Música | Patch |', md)
        self.assertIn('`SLT01RI`', md)
        self.assertIn('U', md)  # slots vêm do slot_map

    def test_json_bate_com_o_plano(self):
        out = sl.plano_json(self.plano, self.total, self.lib.slots)
        self.assertEqual(len(out['itens']), len(self.plano))
        self.assertEqual(out['itens'][0]['patch'], self.plano[0][1]['nome'])
        self.assertEqual(out['itens'][0]['slot'], 'U01')  # slot real, não morto

    def test_out_grava_em_tmpdir(self):
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / 'cola.md'
            rc = sl.main(['CT01', 'SLT01', '--out', str(destino)])
            self.assertEqual(rc, 0)
            self.assertIn('Cola de palco', destino.read_text(encoding='utf-8'))

    def test_list_nao_explode(self):
        self.assertEqual(sl.main(['--list']), 0)

    def test_repetida_rejeitada(self):
        with self.assertRaises(SystemExit):
            sl.main(['CT01', 'CT01'])

    def test_patch_fora_do_repertorio_rejeitado(self):
        with self.assertRaises(SystemExit):
            sl.main(['CT01', '--patch', 'SMOO1:RI'])

    def test_cabecalho_conta_trocas_reais(self):
        """Regressão: main() media dicts (sempre 0); deve medir chaves de cadeia."""
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / 'cola.md'
            sl.main(['CT01', 'SMOO1', '--out', str(destino)])
            texto = destino.read_text(encoding='utf-8')
            self.assertRegex(texto, r'\b[1-9]\d* troca')  # zero é bug aqui


if __name__ == '__main__':
    unittest.main()
