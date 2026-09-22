"""Testes dos scripts hoje fora da suíte (issue #16): analyze_prst,
build_release e gen_changelog.

O projeto roda **Python 3.14 apenas** (política guardada em
`tools/defs_schema.py` e travada no CI): a suíte inteira se recusa a rodar
em runtime diferente, com a mesma mensagem acionável do validador.

Nenhum teste escreve no repositório (regra do projeto): o empacotamento
roda num tmpdir lendo os `.prst` commitados; os testes de VERSION e
CHANGELOG redirecionam as constantes de módulo para arquivos temporários.
"""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

if sys.version_info[:2] < (3, 14):
    raise SystemExit(
        f"Este projeto roda Python 3.14 APENAS — detectado "
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}.\n"
        f"O CI roda em 3.14 (ver .github/workflows/ci.yml).")

import analyze_prst  # noqa: E402
import build_release  # noqa: E402
import gen_changelog  # noqa: E402

PRST = ROOT / 'patches' / 'Santana' / 'Supernatural (1999)' / \
    'Smooth' / 'SMOO1RI' / 'SMOO1RI.prst'


class TestAnalyzePrst(unittest.TestCase):
    """parse() + analyze() sobre o .prst de Santana gerado pelo pipeline."""

    @classmethod
    def setUpClass(cls):
        cls.info, cls.irs, cls.patches = analyze_prst.parse(str(PRST))
        cls.models, cls.param_stats = analyze_prst.analyze(cls.patches)

    def test_info_tem_campos_essenciais(self):
        for campo in ('software', 'firmware', 'product', 'count'):
            self.assertIn(campo, self.info)

    def test_formato_single_fw21(self):
        self.assertEqual(self.info.get('firmware'), '2.1')

    def test_um_preset_com_nome_do_patch(self):
        self.assertEqual(len(self.patches), 1)
        self.assertEqual(self.patches[0]['name'], 'SMOO1RI')

    def test_sem_bloco_ppIRInfo_no_formato_single(self):
        # <ppIRInfo> só existe no export "all" — o formato single não o tem
        # (e o guarda de None em parse() existe exatamente por isso).
        self.assertEqual(self.irs, [])

    def test_effect_exposto_com_nome_e_params_15_slots(self):
        e = self.patches[0]['effects'][0]
        self.assertIn('module', e)
        self.assertIsInstance(e['params'], list)
        self.assertEqual(len(e['params']), 15)

    def test_analyze_conta_uso_e_param_stats_por_modelo(self):
        self.assertTrue(self.models)
        for key, m in self.models.items():
            self.assertGreater(m['count'], 0)
            self.assertEqual(len(self.param_stats[key]), 15)

    def test_fmt_stat_linhas_formadas(self):
        stat = self.param_stats[sorted(self.models)[0]]
        out = analyze_prst.fmt_stat(stat)
        self.assertTrue(all(l.startswith('  p') for l in out.splitlines()))


class TestBuildRelease(unittest.TestCase):
    """Validação SemVer, bump, coleta do defs e empacotamento em tmpdir."""

    def test_read_version_da_versao_commitada(self):
        esperado = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertEqual(build_release.read_version(), esperado)

    def test_read_version_rejeita_nao_semver(self):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td) / 'VERSION'
            fake.write_text('1.2', encoding='utf-8')  # não-SemVer
            original = build_release.VERSION_FILE
            build_release.VERSION_FILE = fake
            try:
                with self.assertRaises(SystemExit):
                    build_release.read_version()
            finally:
                build_release.VERSION_FILE = original

    def test_bump_tres_componentes(self):
        self.assertEqual(build_release.bump('1.2.3', 'major'), '2.0.0')
        self.assertEqual(build_release.bump('1.2.3', 'minor'), '1.3.0')
        self.assertEqual(build_release.bump('1.2.3', 'patch'), '1.2.4')

    def test_collect_patches_espelha_o_defs(self):
        defs = json.loads(
            (ROOT / 'tools' / 'patches-defs.json').read_text(encoding='utf-8'))
        items = build_release.collect_patches()
        n_definidos = sum(len(s['patches']) for s in defs['songs'])
        self.assertEqual(len(items), n_definidos)
        nomes = {nome for _, nome in items}
        self.assertIn('SMOO1RI', nomes)

    def test_assert_valid_prst_aceita_commitado(self):
        build_release.assert_valid_prst(PRST, 'SMOO1RI')  # não levanta

    def test_assert_valid_prst_rejeita_nome_divergente(self):
        with self.assertRaises(SystemExit):
            build_release.assert_valid_prst(PRST, 'OUTRO')

    def test_package_em_tmpdir_produz_zips_e_notas(self):
        """Empacota tudo num tmpdir lendo os .prst do repositório (só leitura)."""
        with tempfile.TemporaryDirectory() as td:
            dist = Path(td)
            orig = (build_release.DIST_DIR, build_release.PATCHES_DIR)
            build_release.DIST_DIR = dist
            build_release.PATCHES_DIR = ROOT / 'patches'
            try:
                build_release.package('9.9.9')
            finally:
                build_release.DIST_DIR, build_release.PATCHES_DIR = orig

            completo = dist / 'gp100-patches-v9.9.9.zip'
            self.assertTrue(completo.exists())
            with zipfile.ZipFile(completo) as z:
                prst = [n for n in z.namelist() if n.endswith('.prst')]
                self.assertGreater(len(prst), 0)
                self.assertTrue(
                    all(n.endswith('.prst') or n.endswith('patch.md')
                        for n in z.namelist()))
            # um zip por álbum presente
            self.assertTrue(any('Santana' in n.name for n in dist.glob('*.zip')))
            notas = dist / 'RELEASE-NOTES-v9.9.9.md'
            self.assertTrue(notas.exists())
            texto = notas.read_text(encoding='utf-8')
            self.assertIn('9.9.9', texto)
            self.assertIn('Como usar', texto)


class TestGenChangelog(unittest.TestCase):
    """Parser de Conventional Commits, seções e bump — sem escrita no repo."""

    def test_commit_re_tipos_e_escopo(self):
        m = gen_changelog.COMMIT_RE.match('feat(tools): CLI unificada')
        self.assertEqual(m.group('tipo'), 'feat')
        self.assertEqual(m.group('escopo'), 'tools')
        self.assertEqual(m.group('desc'), 'CLI unificada')
        self.assertIsNone(gen_changelog.COMMIT_RE.match('Merge pull request #17'))

    def test_breaking_por_bang(self):
        m = gen_changelog.COMMIT_RE.match('feat(pipeline)!: schema v2')
        self.assertTrue(m.group('breaking'))

    def test_breaking_footer_regex(self):
        corpo = 'descrição\n\nBREAKING CHANGE: formato do defs muda'
        nota = gen_changelog.BREAKING_FOOTER.search(corpo)
        self.assertEqual(nota.group(1), 'formato do defs muda')

    def test_coletar_rodando_git_real(self):
        # Roda `git log` de verdade sobre a história do repositório:
        # deve retornar uma lista de itens 5-upla sem crash.
        itens = gen_changelog.coletar(None)
        self.assertIsInstance(itens, list)
        for it in itens:
            self.assertEqual(len(it), 5)

    def test_bump_sugerido_tres_regras(self):
        atual = '1.2.3'
        feat = [('feat', '', 'x', '', False)]
        fix = [('fix', '', 'x', '', False)]
        brk = [('feat', '', 'x', 'mudou o formato', True)]
        self.assertEqual(gen_changelog.bump_sugerido(fix, atual), '1.2.4')
        self.assertEqual(gen_changelog.bump_sugerido(feat, atual), '1.3.0')
        self.assertEqual(gen_changelog.bump_sugerido(brk, atual), '2.0.0')

    def test_secao_ordena_e_agrupa(self):
        itens = [
            ('fix', '', 'corrige leitura', '', False),
            ('feat', 'tools', 'novo comando', '', False),
            ('feat', '', 'outra coisa', '', False),
        ]
        texto = gen_changelog.secao('1.2.3', itens, incluir_ocultos=False)
        self.assertIn('## [1.2.3]', texto)
        self.assertIn('### ✨ Funcionalidades', texto)
        self.assertIn('### 🐞 Correções', texto)
        self.assertIn('**tools**: novo comando', texto)
        self.assertNotIn('♻️ Refatoração', texto)  # oculto sem --all

    def test_secao_quebra_no_topo(self):
        itens = [('feat', '', 'x', 'quebra tudo', True)]
        texto = gen_changelog.secao('2.0.0', itens, incluir_ocultos=False)
        self.assertIn('### ⚠️ Mudanças incompatíveis', texto)
        self.assertIn('quebra tudo', texto)

    def test_secao_vazia_mensagem(self):
        texto = gen_changelog.secao('1.0.1', [], incluir_ocultos=False)
        self.assertIn('Nenhuma mudança visível', texto)

    def test_escrever_no_changelog_idempotente(self):
        with tempfile.TemporaryDirectory() as td:
            changelog = Path(td) / 'CHANGELOG.md'
            changelog.write_text(
                '# Changelog\n\npre-ambulo\n\n## [0.9.0] — 2026-01-01\n\nantigo\n',
                encoding='utf-8')
            original = gen_changelog.CHANGELOG
            gen_changelog.CHANGELOG = changelog
            try:
                bloco = '## [1.0.0] — 2026-09-22\n\n### ✨ Funcionalidades\n\n- x'
                gen_changelog.escrever_no_changelog(bloco, '1.0.0')
                gen_changelog.escrever_no_changelog(bloco, '1.0.0')  # idempotente
            finally:
                gen_changelog.CHANGELOG = original
            texto = changelog.read_text(encoding='utf-8')
            self.assertEqual(texto.count('## [1.0.0]'), 1)
            self.assertIn('## [0.9.0]', texto)

    def test_ler_versao_atual_formato_semver(self):
        self.assertRegex(gen_changelog.ler_versao_atual(), r'^\d+\.\d+\.\d+$')


if __name__ == '__main__':
    unittest.main()
