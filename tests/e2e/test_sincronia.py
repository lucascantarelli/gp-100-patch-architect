"""GUARDA DE SINCRONIA (TestH) — o pipeline reproduz os derivados? (issues #34/#33)

Migração de `TestH_DadosEmSincronia` (`tests/test_pipeline.py`), o teste que
era o job `data-pipeline` do CI. Prova duas coisas:

* **determinismo** — o pipeline (`application.pipeline`, in-process desde a
  #33), rodado sobre uma cópia temporária do repositório (SEM patches/),
  reproduz byte a byte o que está em `patches/**` e nos arquivos fixos
  (`data/ir-library.json`, `reference/16-ir-library.md`); a normalização
  ignora `preset_info/@time`, equipara CRLF/LF e NÃO mascara mudança de
  parâmetro;
* **cobertura do guarda** — todo arquivo que o pipeline escreve está sob
  vigilância (quem gera um arquivo novo tem de ensinar o guarda a vê-lo).

Pega as duas formas de drift: "editei o defs e esqueci de regenerar" e "editei
à mão um arquivo gerado". Em um clone limpo (o CI), o commitado é o HEAD; na
sua máquina, é o working tree — o teste reprova antes do commit, sem sujar
nada (o @time muda só no sandbox).

ADR-0013: os derivados não são commitados; o CI os constrói ANTES do pytest e
quem precisa deles no dia a dia roda `gp100 build` ou baixa o ZIP da Release
(issue #82).

Marcadores por teste: a normalização é `unit` (rápida, roda em toda fatia), a
cobertura do guarda é `e2e` e o sandbox é `e2e` + `slow` — módulo inteiro
marcado slow tiraria a normalização da fatia `-m "not slow"`.
"""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

import pytest

from gp100_architect.application import pipeline
from gp100_architect.infrastructure.defs import carregar_e_validar

# O que o pipeline escreve: patches/** (essas extensões) + os 2 arquivos fixos.
SUFIXOS_DE_ARTEFATO = {'.prst', '.md', '.json'}
ARTEFATO_IGNORADO: set[str] = set()  # (antes: spec.json — eliminado no ADR-0013)
SUFIXO_VARIANTE = '-USERIR'  # issue #10: variante experimental, FORA do guarda
# (não é commitada; a prova local dela é test_variantes_userir_sao_deterministicas)
ARTEFATOS_FIXOS = (
    'data/ir-library.json',  # pipeline · passo ir_library
    'reference/16-ir-library.md',  # pipeline · passo ir_library
)
# O sandbox precisa espelhar TUDO que o pipeline lê — e NADA do que ele produz.
# patches/ fica FORA de propósito (ADR-0013): ela não é mais commitada, e é
# justamente o que o teste prova — um clone limpo constrói todos os derivados.
# O pipeline é in-process (o pacote já está importado), então src/ não entra.
PASTAS_DO_SANDBOX = ('data', 'reference', 'impulse_responses')

_TIME_RE = re.compile(r'time="\d+"')


def normaliza(texto: str) -> str:
    """Texto comparável: ignora `preset_info/@time` e equipara fim de linha."""
    return _TIME_RE.sub('time="T"', texto.replace('\r\n', '\n'))


def primeira_diferenca(velho: str, novo: str) -> str:
    """Descrição curta da primeira linha divergente (para o relatório do teste)."""
    va, nb = normaliza(velho).splitlines(), normaliza(novo).splitlines()
    for i, (a, b) in enumerate(zip(va, nb, strict=False), start=1):
        if a != b:
            return f'linha {i}: -{a.strip()[:70]} · +{b.strip()[:70]}'
    return f'{abs(len(va) - len(nb))} linha(s) a mais/menos'


def artefatos(raiz: Path) -> dict[str, str]:
    """{caminho posix relativo: texto} de toda a saída do pipeline sob `raiz`.

    Variantes experimentais `*-USERIR.*` (issue #10) ficam de fora: não são
    commitadas e só existem em máquinas que rodaram o build com --with-user-ir.
    """
    textos: dict[str, str] = {}
    for p in (raiz / 'patches').rglob('*'):
        if (
            p.is_file()
            and p.suffix in SUFIXOS_DE_ARTEFATO
            and p.name not in ARTEFATO_IGNORADO
            and not p.stem.endswith(SUFIXO_VARIANTE)
        ):
            textos[p.relative_to(raiz).as_posix()] = p.read_text(encoding='utf-8', errors='replace')
    for rel in ARTEFATOS_FIXOS:
        f = raiz / rel
        if f.is_file():
            textos[rel] = f.read_text(encoding='utf-8', errors='replace')
    return textos


def artefatos_variantes(raiz: Path) -> dict[str, str]:
    """{caminho posix relativo: texto} só das variantes -USERIR (issue #10)."""
    textos: dict[str, str] = {}
    for p in (raiz / 'patches').rglob('*'):
        if p.is_file() and p.stem.endswith(SUFIXO_VARIANTE) and p.suffix in SUFIXOS_DE_ARTEFATO:
            textos[p.relative_to(raiz).as_posix()] = p.read_text(encoding='utf-8', errors='replace')
    return textos


def _monta_sandbox(raiz: Path, destino: Path) -> Path:
    """Cópia do que o pipeline lê (nada do que ele escreve — ADR-0013)."""
    destino.mkdir(parents=True)
    for nome in PASTAS_DO_SANDBOX:
        origem = raiz / nome
        if origem.is_dir():
            shutil.copytree(
                origem,
                destino / nome,
                ignore=shutil.ignore_patterns('__pycache__', '*.pyc'),
            )
    return destino


def _aponta_defs_do_sandbox(monkeypatch: pytest.MonkeyPatch, sandbox: Path) -> None:
    """`GP100_DEFS` → fragmentos do SANDBOX (o pipeline lê de lá, não do repo)."""
    monkeypatch.setenv('GP100_DEFS', str(sandbox / 'data' / 'defs'))


# ── normalização (as regras de comparação em si) ────────────────────────────


@pytest.mark.unit
def test_time_do_prst_nao_conta_como_mudanca() -> None:
    a = '<preset_info time="1789773232829" firmware="2.1" product="GP-100"/>'
    b = '<preset_info time="1" firmware="2.1" product="GP-100"/>'
    assert normaliza(a) == normaliza(b)


@pytest.mark.unit
def test_crlf_e_lf_sao_equivalentes() -> None:
    assert normaliza('a\r\nb') == normaliza('a\nb')


@pytest.mark.unit
def test_parametro_diferente_nao_e_mascarado() -> None:
    a = '<Effect effectName="Sweet" params_0="25" params_1="400"/>'
    b = '<Effect effectName="Sweet" params_0="31" params_1="400"/>'
    assert normaliza(a) != normaliza(b)
    assert 'linha 1' in primeira_diferenca(a, b)


@pytest.mark.unit
def test_passos_do_pipeline_sao_a_ordem_do_guarda() -> None:
    """A constante simbólica da CLI bate com a execução in-process (issue #33)."""
    from gp100_architect.interfaces.cli.main import PIPELINE

    assert pipeline.PIPELINE_PASSOS == ('ir_library', 'patches', 'indices')
    assert PIPELINE == pipeline.PIPELINE_PASSOS


# ── cobertura do guarda ─────────────────────────────────────────────────────


@pytest.mark.e2e
def test_artefatos_cobertos_sao_so_saida_de_script(raiz: Path) -> None:
    gerados = ('patches/README.md', 'data/ir-library.json', 'reference/16-ir-library.md')
    monitorados = set(artefatos(raiz))
    for rel in gerados:
        assert rel in monitorados, f'{rel} deveria ser monitorado'
    for rel in (
        'README.md',
        'knowledge.md',
        'reference/03-amp.md',
        'reference/16-ir-library.md.bak',
        'CONTRIBUTING.md',
        'src/gp100_architect/application/pipeline.py',
        'impulse_responses/README.md',
    ):
        assert rel not in monitorados, f'{rel} não deveria ser monitorado'


@pytest.mark.e2e
def test_toda_saida_do_pipeline_esta_coberta(raiz: Path) -> None:
    """Se o gerador escreve um arquivo, ele tem que entrar no guarda de sincronia."""
    defs = carregar_e_validar()
    monitorados = set(artefatos(raiz))
    for song in defs['songs']:
        album = defs['albums'][song['idAlbum']]
        for patch in song['patches']:
            for nome in (f'{patch["nome"]}.prst', 'patch.md'):
                rel = (
                    Path('patches')
                    / album['pasta']
                    / (song.get('pasta') or song['song'])
                    / patch['nome']
                    / nome
                ).as_posix()
                assert rel in monitorados, f'{rel} fora do guarda de sincronia'


# ── o teste que era o job `data-pipeline` ───────────────────────────────────


@pytest.mark.slow
@pytest.mark.e2e
def test_pipeline_reproduz_todos_os_artefatos_commitados(
    raiz: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """O pipeline inteiro sobre uma cópia temporária do repo × o working tree.

    In-process desde a #33: `pipeline.executar` roda os três passos sobre o
    sandbox (defs lido via `GP100_DEFS`), e o resultado tem de reproduzir o
    que está no working tree — byte a byte, salvo o `@time`.
    """
    with tempfile.TemporaryDirectory(prefix='gp100-sandbox-') as tmp:
        sandbox = _monta_sandbox(raiz, Path(tmp) / 'repo')
        _aponta_defs_do_sandbox(monkeypatch, sandbox)
        codigo = pipeline.executar(sandbox)
        assert codigo == 0, f'pipeline falhou no sandbox (código {codigo})'
        commitado, produzido = artefatos(raiz), artefatos(sandbox)

    problemas = []
    for rel in sorted(set(commitado) | set(produzido)):
        if rel not in produzido:
            problemas.append(f'[removido ] {rel}: o pipeline não reproduz este arquivo')
        elif rel not in commitado:
            problemas.append(f'[novo     ] {rel}: gerado no sandbox, mas não está commitado')
        elif normaliza(commitado[rel]) != normaliza(produzido[rel]):
            problemas.append(
                f'[diferente] {rel}: {primeira_diferenca(commitado[rel], produzido[rel])}'
            )
    assert problemas == [], (
        'artefato(s) gerado(s) fora de sincronia com o commit — rode o pipeline '
        'inteiro e commite os derivados:\n  '
        + '\n  '.join(problemas[:20])
        + ('\n  … e mais' if len(problemas) > 20 else '')
    )


@pytest.mark.slow
@pytest.mark.e2e
def test_variantes_userir_sao_deterministicas(raiz: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A variante -USERIR (issue #10) não é commitada, então o guarda de
    determinismo não a cobre — este teste cobre: o build com --with-user-ir,
    rodado DUAS vezes no sandbox com GP100_BUILD_TIME fixo, produz bytes
    idênticos (a variante segue o mesmo contrato do canônico).
    """
    monkeypatch.setenv('GP100_BUILD_TIME', '1688207360000')
    with tempfile.TemporaryDirectory(prefix='gp100-sandbox-') as tmp:
        sandbox = _monta_sandbox(raiz, Path(tmp) / 'repo')
        _aponta_defs_do_sandbox(monkeypatch, sandbox)
        rodadas: list[dict[str, str]] = []
        for _ in range(2):
            codigo = pipeline.executar(sandbox, passos=('patches',), com_variante=True)
            assert codigo == 0, f'build --with-user-ir falhou no sandbox (código {codigo})'
            rodadas.append(artefatos_variantes(sandbox))
    assert rodadas[0], 'nenhuma variante -USERIR gerada no sandbox'
    assert rodadas[0] == rodadas[1], 'variantes -USERIR não determinísticas entre dois builds'
