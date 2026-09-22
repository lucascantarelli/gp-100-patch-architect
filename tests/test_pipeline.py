"""
tests/test_pipeline.py — Testes do pipeline GP-100 Patch Architect.

Stdlib pura (unittest): não precisa instalar nada — roda igual no CI e na sua
máquina. Cobre as invariantes que **já quebraram uma vez** neste projeto:

  A. defs      — ids únicos, nome de patch único e ≤ 12 chars (limite do painel),
                 toda música aponta para um álbum declarado em `albums`
  B. fonte     — o mapa do álbum e a seção 📡 do patch.md CONCORDAM sobre a IR
                 (divergiram nos 38 patches do Pulse: um dizia "fábrica", o
                 outro mandava carregar o arquivo do banco local)
  C. .prst     — formato single fw 2.1 (sem ppIRInfo, com ppCtrl/ppEXP1, 9 módulos
                 na ordem PRE..RVB), ppName = nome da pasta, 15 params por módulo
  D. patch.md  — as 9 seções obrigatórias, zero HTML cru e zero rótulo
                 placeholder (nem "(pN)" nem `pN`: todo slot setado tem nome oficial)
  E. momentos  — liga/desliga válido: módulo existe, estado é o inverso do atual
                 e nunca toca AMP/CAB
  F. cobertura — todo modelo ligado num patch tem tabela de nomes; a allowlist
                 (hoje vazia) existe para um modelo novo sem nome falhar alto
  G. índices   — os arquivos em disco são exatamente o que o gerador produz hoje
                 (pega "esqueci de rodar gen_indexes.py")
  H. frescor  — GUARDA DE SINCRONIA: o pipeline, rodado inteiro numa cópia
                 temporária do repositório, tem de reproduzir EXATAMENTE o que
                 está commitado — pega "editei o defs e esqueci de regenerar" e
                 "editei à mão arquivo gerado". A normalização ignora
                 `preset_info/@time` (o único byte que muda de propósito),
                 equipara CRLF/LF e NÃO mascara mudança de parâmetro
  I. ordem    — os artefatos saem SEMPRE na mesma ordem, em qualquer sistema
                 operacional: `sorted()` sobre `Path` usa `normcase` (minúsculas
                 no Windows, identidade no Linux) e o manifesto de IRs divergia
                 entre a máquina e o CI
  J. conexão  — o agente e a biblioteca estão ligados: todo patch em `patches/**`
                 está declarado no defs (senão é órfão invisível) e todo agente que
                 o orquestrador pode invocar existe em `.agents/`

Rodar:  python -m unittest discover -s tests -v
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))

import build_song_patches as BSP          # noqa: E402  (precisa do sys.path acima)
import generate_prst as GEN                # noqa: E402
import gen_indexes as GI                   # noqa: E402
import ir_library as IRL                   # noqa: E402

DEFS = BSP.DEFS
CHAIN = BSP.CHAIN
SECOES = [
    '## 🎸 1. Sua guitarra agora',
    '## 🔧 2. Ajustes finos',
    '## 📡 3. Impulse Response',
    '## 🎛️ 4. Modos de atuação',
    '## 🔊 5. Objetivo do som',
    '## 📚 6. Referência real',
    '## 🎛️ 7. Cadeia e parâmetros',
    '## 💾 8. Carregar na pedaleira',
    '## 🚫 9. Evite com este patch',
]
# Modelos REAIS do fw 2.0 sem nome oficial de parâmetro documentado. Hoje é
# VAZIO: o manual oficial do firmware V2.0 deu nome a todos (Saturate =
# Gain/Mix/Output/H-Cut, Red Haze = Fuzz/VOL, T-Echo = Mix/Time/Fdbk) e os slots
# internos que sobravam deixaram de ser setados. Ao acrescentar um modelo novo
# com params, ele precisa entrar aqui E em PARAM_NAMES — este teste existe para a
# decisão ser consciente, não por esquecimento.
SEM_NOME_OFICIAL = set()
PATCHES_DIR = ROOT / 'patches'


def todas_as_musicas():
    """[(song, patch)] em ordem — a mesma travessia que numera os slots."""
    for song in DEFS['songs']:
        for patch in song['patches']:
            yield song, patch


def pasta_da_musica(song):
    return PATCHES_DIR / DEFS['albums'][song['idAlbum']]['pasta'] / GI.song_pasta(song)


def pasta_do_patch(song, patch):
    return pasta_da_musica(song) / patch['nome']


def ler_mapa(song):
    """Linhas da tabela 'Música → patches' do mapa do álbum da música."""
    mapa = PATCHES_DIR / DEFS['albums'][song['idAlbum']]['pasta'] / 'MAPA-DO-ALBUM.md'
    return mapa.read_text(encoding='utf-8').splitlines()


class TestA_Defs(unittest.TestCase):
    """Integridade da fonte única (tools/patches-defs.json)."""

    def test_albuns_declarados(self):
        for song in DEFS['songs']:
            self.assertIn(song['idAlbum'], DEFS['albums'],
                          f"{song['id']}: idAlbum {song['idAlbum']} não está em albums")

    def test_albuns_completos(self):
        for key, alb in DEFS['albums'].items():
            for campo in ('banda', 'album', 'ano', 'display', 'pasta'):
                self.assertTrue(alb.get(campo) not in (None, ''),
                                f"albums.{key} sem '{campo}'")
            self.assertTrue((PATCHES_DIR / alb['pasta']).is_dir(),
                            f"albums.{key}: pasta {alb['pasta']} não existe em patches/")

    def test_ids_de_musica_unicos(self):
        ids = [s['id'] for s in DEFS['songs']]
        self.assertEqual(len(ids), len(set(ids)), 'id de música repetido')

    def test_pastas_de_musica_unicas(self):
        pastas = [GI.song_pasta(s) for s in DEFS['songs']]
        repetidas = {p for p in pastas if pastas.count(p) > 1}
        self.assertEqual(repetidas, set(), f'pasta de música repetida: {repetidas}')

    def test_nomes_de_patch_unicos_e_no_limite_do_painel(self):
        nomes = [p['nome'] for _s, p in todas_as_musicas()]
        self.assertEqual(len(nomes), len(set(nomes)), 'nome de patch repetido')
        for nome in nomes:
            self.assertLessEqual(len(nome), 12, f'{nome}: mais de 12 caracteres')
            self.assertRegex(nome, r'^[A-Z0-9]+$', f'{nome}: use só A-Z e 0-9')


class TestB_FonteUnica_IR(unittest.TestCase):
    """O mapa e o patch.md têm de dar a MESMA resposta sobre a IR (bug do Pulse)."""

    def test_mapa_concorda_com_a_secao_de_ir(self):
        marcador = re.compile(r'`(?:\S+ )?([A-Z0-9]{4,12})`')   # nome do patch no mapa
        divergencias = []
        for song in DEFS['songs']:
            linhas = [l for l in ler_mapa(song) if l.startswith('| **')]
            linha = next((l for l in linhas if GI.song_display(song) in l), None)
            self.assertIsNotNone(linha, f"{song['id']}: linha da música não está no mapa")
            cells = [c.strip() for c in linha.strip().strip('|').split('|')]
            patches_col, ir_col = cells[1].split(' · '), cells[3].split(' · ')
            self.assertEqual(len(patches_col), len(song['patches']),
                             f"{song['id']}: nº de patches do mapa ≠ defs")
            for i, patch in enumerate(song['patches']):
                nome = marcador.search(patches_col[i])
                self.assertIsNotNone(nome, f'mapa: não li o nome em {patches_col[i]!r}')
                self.assertEqual(nome.group(1), patch['nome'], f"{song['id']}: ordem do mapa")
                # o patch.md recomenda o banco local?
                doc = (pasta_do_patch(song, patch) / 'patch.md').read_text(encoding='utf-8')
                local_no_doc = '### 📁 Melhor opção no nosso banco' in doc
                local_no_mapa = ir_col[i].startswith('📁')
                if local_no_doc != local_no_mapa:
                    divergencias.append(
                        f"{patch['nome']}: patch.md "
                        f"{'recomenda o banco' if local_no_doc else 'diz fábrica'} x mapa "
                        f"{'recomenda o banco' if local_no_mapa else 'diz fábrica'}")
        self.assertEqual(divergencias, [], 'mapa e patch.md discordam sobre a IR:\n  '
                         + '\n  '.join(divergencias))

    def test_ir_local_do_defs_aponta_para_captura_existente(self):
        ir_lib = GI.load_ir_library()
        self.assertIsNotNone(ir_lib, 'tools/ir-library.json não legível')
        cabs = {Path(f['file']).parts[-2].replace(' Mics', '')
                for pack in ir_lib['packs'].values() for f in pack['files']}
        for cab, par in DEFS['ir_local'].items():
            self.assertIn(par['captura'], cabs,
                          f"ir_local['{cab}'] aponta para captura ausente: {par['captura']}")
            self.assertRegex(par['slot'], r'^User IR ([1-9]|1[0-9]|20)$')


class TestC_Prst(unittest.TestCase):
    """.prst: o arquivo que vai para a pedaleira."""

    def test_formato_single_firmware_2_1(self):
        total = 0
        for song, patch in todas_as_musicas():
            prst = pasta_do_patch(song, patch) / f"{patch['nome']}.prst"
            self.assertTrue(prst.is_file(), f'{prst} não existe')
            root = ET.parse(prst).getroot()
            self.assertEqual(root.tag, 'GP-100')
            info = root.find('preset_info')
            self.assertEqual(info.get('firmware'), '2.1', f'{prst}: firmware')
            self.assertEqual(info.get('count'), '1', f'{prst}: count (single)')
            self.assertIsNone(root.find('ppIRInfo'),
                              f'{prst}: ppIRInfo é do export "all" — o importador recusa')
            presets = root.find('presets')
            self.assertEqual(presets.get('ppName'), patch['nome'], f'{prst}: ppName')
            self.assertIsNotNone(presets.find('ppCtrl'), f'{prst}: falta ppCtrl')
            self.assertIsNotNone(presets.find('ppEXP1'), f'{prst}: falta ppEXP1')
            effects = presets.findall('Effect')
            self.assertEqual(len(effects), len(CHAIN), f'{prst}: módulos')
            self.assertEqual([e.get('effectModuleName') for e in effects], list(reversed(CHAIN)),
                             f'{prst}: ordem dos <Effect> no arquivo')
            for e in effects:
                self.assertEqual(e.get('x'), str(GEN.CHAIN_POS[e.get('effectModuleName')]),
                                 f'{prst}: {e.get("effectModuleName")} com x errado')
                self.assertIn(e.get('effectState'), ('0', '1'), f'{prst}: effectState')
                for i in range(15):
                    self.assertIsNotNone(e.get(f'params_{i}'),
                                         f'{prst}: {e.get("effectName")} sem params_{i}')
            total += 1
        self.assertEqual(total, sum(len(s['patches']) for s in DEFS['songs']))

    def test_readme_da_pasta_do_patch(self):
        for song, patch in todas_as_musicas():
            pasta = pasta_do_patch(song, patch)
            # `spec.json` não entra: é intermediário, gerado pelo pipeline e não
            # versionado — num clone limpo (o job test-suite) ele não existe.
            for arquivo in ('patch.md', f"{patch['nome']}.prst"):
                self.assertTrue((pasta / arquivo).is_file(),
                                f'{patch["nome"]}: falta {arquivo} em {pasta}')


class TestD_Documentacao(unittest.TestCase):
    """Documentação entregue ao usuário."""

    def test_secoes_obrigatorias_e_markdown_puro(self):
        for song, patch in todas_as_musicas():
            doc = (pasta_do_patch(song, patch) / 'patch.md').read_text(encoding='utf-8')
            for secao in SECOES:
                self.assertIn(secao, doc, f"{patch['nome']}: falta a seção {secao!r}")
            for tag in ('<div', '<br', '<details', '<summary', '</div'):
                self.assertNotIn(tag, doc, f"{patch['nome']}: HTML cru {tag} no Markdown")
            self.assertNotIn('# {', doc, f"{patch['nome']}: f-string não interpolada")

    def test_sem_rotulo_placeholder(self):
        """Nem `(pN)` nem `pN` solto: todo slot setado tem nome oficial do manual."""
        ruins = []
        for song, patch in todas_as_musicas():
            doc = (pasta_do_patch(song, patch) / 'patch.md').read_text(encoding='utf-8')
            achados = re.findall(r'\(p\d+\)|\bp\d+\b', doc)
            if achados:
                ruins.append(f"{patch['nome']}{achados[:3]}")
        self.assertEqual(ruins, [], f'rótulo placeholder nos docs: {ruins}')

    def test_guitarra_vem_antes_do_tecnico(self):
        for song, patch in todas_as_musicas():
            doc = (pasta_do_patch(song, patch) / 'patch.md').read_text(encoding='utf-8')
            self.assertLess(doc.index(SECOES[0]), doc.index(SECOES[6]),
                            f"{patch['nome']}: dados técnicos antes da guitarra")
            self.assertLess(doc.index(SECOES[2]), doc.index(SECOES[3]),
                            f"{patch['nome']}: IR deve vir antes dos modos de atuação")


class TestE_Momentos(unittest.TestCase):
    """Liga/desliga módulos em tempo real (seção 4)."""

    def test_momentos_sao_validos(self):
        encontrados = 0
        for song, patch in todas_as_musicas():
            mods = patch['spec']['modules']
            for mo in patch['doc'].get('momentos', []):
                encontrados += 1
                self.assertTrue(mo['nome'] and mo['quando'], f"{patch['nome']}: momento sem nome/quando")
                for nome_mod, estado in mo['mods']:
                    self.assertIn(nome_mod, mods, f"{patch['nome']}: {nome_mod} não existe")
                    self.assertNotIn(nome_mod, ('AMP', 'CAB'),
                                     f"{patch['nome']}: toggle de AMP/CAB é proibido")
                    atual = mods[nome_mod].get('on', False)
                    self.assertNotEqual(atual, estado == 'ON',
                                        f"{patch['nome']}: {nome_mod} já está {estado}")
        self.assertGreater(encontrados, 0, 'nenhum momento declarado no defs')

    def test_momentos_aparecem_no_doc(self):
        for song, patch in todas_as_musicas():
            mo = patch['doc'].get('momentos')
            doc = (pasta_do_patch(song, patch) / 'patch.md').read_text(encoding='utf-8')
            if mo:
                self.assertIn('🎭 Momentos desta música', doc, patch['nome'])
                for m in mo:
                    for nome_mod, estado in m['mods']:
                        self.assertIn(f'**{nome_mod} → {estado}**', doc,
                                      f"{patch['nome']}: momento {nome_mod} {estado} fora do doc")
            else:
                self.assertIn('🎭 Momentos desta música', doc, patch['nome'])


class TestF_ParamNames(unittest.TestCase):
    """Cobertura dos nomes de parâmetro (documentação técnica)."""

    def test_modelos_sem_nome_estao_na_allowlist(self):
        em_uso = {(mod, m['name']) for _s, p in todas_as_musicas()
                  for mod, m in p['spec']['modules'].items() if m.get('on') and m.get('params')}
        sem_nome = em_uso - set(BSP.PARAM_NAMES)
        self.assertEqual(sem_nome, SEM_NOME_OFICIAL,
                         'modelos sem tabela de nomes mudaram: acrescente os nomes em '
                         'PARAM_NAMES (fonte: reference/) ou atualize SEM_NOME_OFICIAL')

    def test_tabelas_sem_placeholder_nem_buraco(self):
        for (mod, nome), labels in BSP.PARAM_NAMES.items():
            self.assertNotRegex(' '.join(labels), r'\bp\d+\b|\(p', f'{mod} {nome}: rótulo placeholder')
            self.assertTrue(all(l.strip() for l in labels), f'{mod} {nome}: rótulo vazio')
            self.assertEqual(len(set(labels)), len(labels), f'{mod} {nome}: rótulo repetido')

    def test_tabela_nao_tem_mais_nomes_que_parametros_reais(self):
        templates = GEN.load_templates()
        for (mod, nome), labels in BSP.PARAM_NAMES.items():
            tpl = templates.get((mod, nome))
            if not tpl:      # modelo fora do catálogo de fábrica: sem base para conferir
                continue
            reais = GEN.real_param_count(nome, tpl['params'])
            self.assertLessEqual(len(labels), reais,
                                 f'{mod} {nome}: {len(labels)} nomes para {reais} parâmetros reais')


class TestG_Indices(unittest.TestCase):
    """Os índices em disco são o que o gerador produz agora (sem drift)."""

    def test_mapas_e_readme_atualizados(self):
        saidas, _total = GI.build_all(DEFS)
        def norm(t):
            return t.replace('\r\n', '\n')
        for path, texto in saidas.items():
            self.assertTrue(path.is_file(), f'{path} não existe — rode gen_indexes.py')
            self.assertEqual(norm(path.read_text(encoding='utf-8')), norm(texto),
                             f'{path} está defasado — rode: python tools/gen_indexes.py')

    def test_slots_continuos_e_alinhados(self):
        slots = GI.slot_map(DEFS)
        self.assertEqual(len(slots), sum(len(s['patches']) for s in DEFS['songs']))
        self.assertEqual(sorted(slots.values()), [f'U{i:02d}' for i in range(1, len(slots) + 1)])
        # build_song_patches.main() calcula os slots pela mesma travessia
        esperado, n = {}, 0
        for song in DEFS['songs']:
            for patch in song['patches']:
                n += 1
                esperado[patch['nome']] = f'U{n:02d}'
        self.assertEqual(slots, esperado, 'gen_indexes e build_song_patches numeram diferente')


# ---- guarda de sincronia (o que era o job `data-pipeline` do CI) ---------------
# Pipeline na ordem real; rodado numa CÓPIA temporária do repositório pelo teste
# de integração abaixo. Os scripts derivam todos os caminhos de
# `Path(__file__).parent.parent`, então a cópia é autocontida (sem .git, sem
# tocar no working tree — o `preset_info/@time` muda a cada build de propósito).
PIPELINE = (
    'tools/ir_library.py',             # indexa impulse_responses/ (se baixou pack)
    'tools/add_pulse_defs.py',         # seeders de álbum (já encadeia add_momentos)
    'tools/add_momentos.py',           # momentos de toggle por patch
    'tools/build_song_patches.py',     # patch.md + .prst (+ spec.json local)
    'tools/gen_indexes.py',            # MAPA-DO-ALBUM.md + patches/README.md
)
# O que o pipeline escreve: patches/** (essas extensões) + os 3 arquivos fixos.
SUFIXOS_DE_ARTEFATO = {'.prst', '.md', '.json'}
ARTEFATO_IGNORADO = {'spec.json'}      # intermediário, fora do git
ARTEFATOS_FIXOS = (
    'tools/patches-defs.json',         # reescrito pelos seeders
    'tools/ir-library.json',           # ir_library.py
    'reference/16-ir-library.md',      # ir_library.py
)
_PASTAS_DO_SANDBOX = ('tools', 'patches', 'reference', 'impulse_responses')

_TIME_RE = re.compile(r'time="\d+"')


def normaliza(texto):
    """Texto comparável: ignora `preset_info/@time` e equipara fim de linha."""
    return _TIME_RE.sub('time="T"', texto.replace('\r\n', '\n'))


def primeira_diferenca(velho, novo):
    """Descrição curta da primeira linha divergente (para o relatório do teste)."""
    va, nb = normaliza(velho).splitlines(), normaliza(novo).splitlines()
    for i, (a, b) in enumerate(zip(va, nb), start=1):
        if a != b:
            return f'linha {i}: -{a.strip()[:70]} · +{b.strip()[:70]}'
    return f'{abs(len(va) - len(nb))} linha(s) a mais/menos'


def artefatos(raiz: Path):
    """{caminho posix relativo: texto} de toda a saída do pipeline sob `raiz`."""
    textos = {}
    for p in (raiz / 'patches').rglob('*'):
        if p.is_file() and p.suffix in SUFIXOS_DE_ARTEFATO and p.name not in ARTEFATO_IGNORADO:
            textos[p.relative_to(raiz).as_posix()] = p.read_text(encoding='utf-8', errors='replace')
    for rel in ARTEFATOS_FIXOS:
        f = raiz / rel
        if f.is_file():
            textos[rel] = f.read_text(encoding='utf-8', errors='replace')
    return textos


class TestH_DadosEmSincronia(unittest.TestCase):
    """O pipeline reproduz o commitado? (era o job `data-pipeline` do CI.)"""

    def test_time_do_prst_nao_conta_como_mudanca(self):
        a = '<preset_info time="1789773232829" firmware="2.1" product="GP-100"/>'
        b = '<preset_info time="1" firmware="2.1" product="GP-100"/>'
        self.assertEqual(normaliza(a), normaliza(b))

    def test_crlf_e_lf_sao_equivalentes(self):
        self.assertEqual(normaliza('a\r\nb'), normaliza('a\nb'))

    def test_parametro_diferente_nao_e_mascarado(self):
        a = '<Effect effectName="Sweet" params_0="25" params_1="400"/>'
        b = '<Effect effectName="Sweet" params_0="31" params_1="400"/>'
        self.assertNotEqual(normaliza(a), normaliza(b))
        self.assertIn('linha 1', primeira_diferenca(a, b))

    def test_artefatos_cobertos_sao_so_saida_de_script(self):
        gerados = ('patches/README.md',
                   'tools/patches-defs.json', 'tools/ir-library.json',
                   'reference/16-ir-library.md')
        monitorados = set(artefatos(ROOT))
        for rel in gerados:
            self.assertIn(rel, monitorados, f'{rel} deveria ser monitorado')
        for rel in ('README.md', 'knowledge.md', 'reference/03-amp.md',
                    'reference/16-ir-library.md.bak', 'CONTRIBUTING.md',
                    'tools/build_song_patches.py', 'impulse_responses/README.md'):
            self.assertNotIn(rel, monitorados, f'{rel} não deveria ser monitorado')

    def test_pipeline_declarado_existe_no_disco(self):
        for rel in PIPELINE:
            self.assertTrue((ROOT / rel).is_file(), f'pipeline cita script ausente: {rel}')

    def test_toda_saida_do_pipeline_esta_coberta(self):
        """Se o gerador escreve um arquivo, ele tem que entrar no guarda de sincronia."""
        monitorados = set(artefatos(ROOT))
        for song in DEFS['songs']:
            for patch in song['patches']:
                pasta = pasta_do_patch(song, patch)
                for nome in (f"{patch['nome']}.prst", 'patch.md'):
                    rel = (pasta / nome).relative_to(ROOT).as_posix()
                    self.assertIn(rel, monitorados, f'{rel} fora do guarda de sincronia')

    def test_pipeline_reproduz_todos_os_artefatos_commitados(self):
        """O teste que era o job `data-pipeline`: roda o pipeline inteiro numa
        cópia temporária do repositório e compara o resultado com o commitado.

        Pega as duas formas de drift: "editei o defs e esqueci de regenerar" e
        "editei à mão um arquivo gerado". Em um clone limpo (o CI), o commitado é
        o HEAD; na sua máquina, é o working tree — ou seja, o teste reprova
        antes do commit, sem sujar nada (o @time muda só no sandbox).
        """
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp) / 'repo'
            sandbox.mkdir()
            for nome in _PASTAS_DO_SANDBOX:
                origem = ROOT / nome
                if origem.is_dir():
                    shutil.copytree(origem, sandbox / nome,
                                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            for script in PIPELINE:
                r = subprocess.run([sys.executable, str(sandbox / script)], cwd=sandbox,
                                   capture_output=True, encoding='utf-8', errors='replace')
                self.assertEqual(
                    r.returncode, 0,
                    f'{script} falhou no sandbox:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
            commitado, produzido = artefatos(ROOT), artefatos(sandbox)

        problemas = []
        for rel in sorted(set(commitado) | set(produzido)):
            if rel not in produzido:
                problemas.append(f'[removido ] {rel}: o pipeline não reproduz este arquivo')
            elif rel not in commitado:
                problemas.append(f'[novo     ] {rel}: gerado no sandbox, mas não está commitado')
            elif normaliza(commitado[rel]) != normaliza(produzido[rel]):
                problemas.append(f'[diferente] {rel}: {primeira_diferenca(commitado[rel], produzido[rel])}')
        self.assertEqual(
            problemas, [],
            'artefato(s) gerado(s) fora de sincronia com o commit — rode o pipeline '
            'inteiro e commite os derivados:\n  ' + '\n  '.join(problemas[:20])
            + ('\n  … e mais' if len(problemas) > 20 else ''))


class TestI_OrdemEstavel(unittest.TestCase):
    """A ordem dos artefatos gerados não pode depender do sistema operacional.

    `sorted()` sobre `Path` compara com `normcase`: **minúsculas no Windows** e
    identidade no Linux. O manifesto de IRs saiu com `4x12 Metal American` antes
    de `4x12 MFB` aqui e o inverso no CI — mesmo gerador, resultado diferente.
    A ordenação passou a usar string (ordem de code point), igual em qualquer OS.
    """

    def test_chave_de_ordenacao_e_string(self):
        """`wav_order` devolve str — não Path, que traz o normcase do sistema."""
        amostra = IRL.IR_DIR / '25 Analog Cab IRs' / '4x12 MFB_EQ.wav'
        chave = IRL.wav_order(amostra)
        self.assertIsInstance(chave, str)
        self.assertEqual(chave, '25 Analog Cab IRs/4x12 MFB_EQ.wav')

    def test_mfb_vem_antes_de_metal_american(self):
        """Ordem de code point (Linux): 'F' (70) < 'e' (101) — o caso que quebrou."""
        nomes = ['4x12 Metal American_EQ.wav', '4x12 MFB_EQ.wav']
        self.assertEqual(sorted(nomes), ['4x12 MFB_EQ.wav', '4x12 Metal American_EQ.wav'])

    def test_manifesto_esta_em_ordem_de_code_point(self):
        """O JSON commitado já sai ordenado por string em todo pack."""
        manifesto = json.loads((ROOT / 'tools' / 'ir-library.json').read_text(encoding='utf-8'))
        for pack, mp in manifesto['packs'].items():
            arquivos = [f['file'] for f in mp['files']]
            self.assertEqual(arquivos, sorted(arquivos), f'ordem instável no pack {pack}')


class TestJ_ConexaoAgenteBiblioteca(unittest.TestCase):
    """O agente projeta o patch; o pipeline publica a biblioteca a partir do defs.

    Quando os dois se separam, sobra um patch que existe em `patches/**` mas não
    no defs — e ele é **invisível**: os índices e todos os outros testes iteram o
    defs, e só o guarda de sincronia (TestH, pipeline × commitado) o vê. Estes
    dois testes fecham essa porta.
    """

    def test_todo_patch_no_disco_esta_no_defs(self):
        """Patch em `patches/**` fora do defs é órfão: nem índice, nem teste o vê."""
        definidos = {patch['nome'] for _, patch in todas_as_musicas()}
        no_disco = {d.name for d in (ROOT / 'patches').glob('*/*/*/*') if d.is_dir()}
        self.assertEqual(sorted(no_disco - definidos), [],
                         'patch(s) em patches/ que não existem em tools/patches-defs.json')

    def test_spawnable_agents_e_reachavel(self):
        """`spawnableAgents` só cita agente que existe, e todo agente é alcançável."""
        agents_dir = ROOT / '.agents'
        arquivos = {p.stem for p in agents_dir.glob('gp100-*.ts')}
        fonte = (agents_dir / 'gp100-patch-architect.ts').read_text(encoding='utf-8')
        bloco = fonte.split('spawnableAgents: [', 1)[1].split(']', 1)[0]
        spawnaveis = set(re.findall(r"'([^']+)'", bloco))
        self.assertEqual(sorted(spawnaveis - arquivos), [],
                         'o orquestrador pode invocar agente que não existe em .agents/')
        self.assertEqual(sorted(arquivos - spawnaveis - {'gp100-patch-architect'}), [],
                         'agente em .agents/ que o orquestrador não consegue invocar')


if __name__ == '__main__':
    unittest.main(verbosity=2)
