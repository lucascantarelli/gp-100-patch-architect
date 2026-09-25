"""Linter de consistência de docs (issue #58) — casos sintéticos e reais.

Mesmo padrão de `test_audit_workflows.py`/`test_audit_agents.py`: cada regra
com fixture sintética (`tmp_path`) + guardas sobre a realidade commitada.
A varredura E2E sobre o repo inteiro não é teste da suíte (consulta a API do
GitHub — nondeterminística); o CI a executa como gate.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO = RAIZ / '.github' / 'scripts' / 'audit_docs.py'

_spec = importlib.util.spec_from_file_location('audit_docs', CAMINHO)
audit_docs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_docs)

pytestmark = pytest.mark.unit


class ApiFake:
    """API do GitHub em memória — o estado que os testes declaram."""

    def __init__(
        self, issues: dict[int, str] | None = None, milestones: list[str] | None = None
    ) -> None:
        self.issues = issues or {}
        self.milestones_lista = milestones or ['v1.0.0', 'v2.0.0']
        self.ok = True

    def issue_existe(self, n: int) -> bool:
        return n in self.issues

    def issue_state(self, n: int) -> str | None:
        return self.issues.get(n)

    def milestones(self) -> list[str]:
        return self.milestones_lista


def _rodar(cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(CAMINHO)],
        capture_output=True,
        encoding='utf-8',
        errors='replace',
        timeout=300,
        cwd=cwd or RAIZ,
    )
    return r.returncode, r.stdout + r.stderr


# ── issues citadas: existência e estado reivindicado ────────────────────────


def test_issue_inexistente_reprova(tmp_path: Path) -> None:
    prosa = 'Ver o detalhe em #9999.\n'
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_issues(tmp_path / 'd.md', prosa, ApiFake(), violas, avisos)
    assert any('#9999' in v and 'NÃO existe' in v for v in violas)


def test_estado_errado_reprova(tmp_path: Path) -> None:
    api = ApiFake(issues={41: 'closed', 42: 'open'})
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_issues(
        tmp_path / 'd.md', 'A #41 está aberta e a #42 fechada.\n', api, violas, avisos
    )
    assert len(violas) == 2  # as duas reivindicações estão invertidas


def test_estado_certo_passa_e_faixa_reprova(tmp_path: Path) -> None:
    api = ApiFake(issues=dict.fromkeys(range(41, 44), 'closed'))
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_issues(
        tmp_path / 'd.md',
        'Epics #41–#43 fechadas. A #42 foi entregue.\n',
        api,
        violas,
        avisos,
    )
    assert violas == []


def test_sem_rede_degrada_para_aviso(tmp_path: Path) -> None:
    api = ApiFake()
    api.ok = False
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_issues(tmp_path / 'd.md', 'Citando #41 aqui.\n', api, violas, avisos)
    assert violas == [] and avisos


def test_url_nao_vira_citacao_de_issue(tmp_path: Path) -> None:
    prosa = 'Veja https://exemplo.com/pagina#41 e [x](doc.md#ancora).\n'
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_issues(tmp_path / 'd.md', prosa, ApiFake(), violas, avisos)
    assert violas == []


# ── caminhos citados ─────────────────────────────────────────────────────────


def test_caminho_inexistente_reprova(tmp_path: Path, raiz: Path) -> None:
    prosa = 'A regra vive em `data/nao-existe-nem-um-dia.json`.\n'
    achados = audit_docs.verificar_caminhos(tmp_path / 'd.md', raiz, prosa, set(), lambda p: False)
    assert len(achados) == 1 and 'data/nao-existe' in achados[0]


def test_caminho_do_historico_passa(tmp_path: Path, raiz: Path) -> None:
    """`tools/…` extinto é citação legítima — existiu no git."""
    prosa = 'Antes: `python tools/gp100.py`.\n'
    achados = audit_docs.verificar_caminhos(
        tmp_path / 'd.md', raiz, prosa, set(), lambda p: p == 'tools/gp100.py'
    )
    assert achados == []


def test_abreviacao_de_doc_por_numero_passa(tmp_path: Path, raiz: Path) -> None:
    prosa = 'A decisão está no `reference/19` e no doc `reference/18`.\n'
    achados = audit_docs.verificar_caminhos(tmp_path / 'd.md', raiz, prosa, set(), lambda p: False)
    assert achados == []


def test_nomes_de_modelo_e_sintaxe_nao_sao_caminhos(tmp_path: Path, raiz: Path) -> None:
    prosa = (
        'Modelo `z-ai/glm-5.3-flash`; parâmetro `Mode(STD/Jumbo)`; '
        'JSONPath `preset_info/@time`; action `astral-sh/setup-uv@v7`; '
        'atalho solto `defs/`.\n'
    )
    achados = audit_docs.verificar_caminhos(tmp_path / 'd.md', raiz, prosa, set(), lambda p: False)
    assert achados == []


# ── links relativos ──────────────────────────────────────────────────────────


def test_link_quebrado_reprova(tmp_path: Path, raiz: Path) -> None:
    prosa = 'Veja [o guia](docs/nao-existe.md) e [o repo](../fora.md).\n'
    violas, _avisos = audit_docs.verificar_links(tmp_path / 'd.md', raiz, prosa)
    assert len(violas) == 2


def test_link_de_issue_do_github_nao_e_caminho(tmp_path: Path, raiz: Path) -> None:
    prosa = 'Discutido em [e12](../../issues/42) e [blob](../blob/main/README.md).\n'
    violas, _ = audit_docs.verificar_links(tmp_path / 'd.md', raiz, prosa)
    assert violas == []


# ── milestones citados ───────────────────────────────────────────────────────


def test_milestone_fantasma_reprova(tmp_path: Path) -> None:
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_milestones(
        tmp_path / 'd.md',
        'Trabalho no milestone v9.9.9-fantasma.\n',
        ApiFake(),
        violas,
        avisos,
    )
    assert len(violas) == 1 and 'v9.9.9' in violas[0]


def test_milestone_real_com_descritor_passa(tmp_path: Path) -> None:
    violas: list[str] = []
    avisos: list[str] = []
    audit_docs.verificar_milestones(
        tmp_path / 'd.md',
        'Milestone `v2.0.0 — Formato, site e escala` fecha a iteração.\n',
        ApiFake(milestones=['v2.0.0 — Formato, site e escala']),
        violas,
        avisos,
    )
    assert violas == []


# ── comandos em blocos de doc ────────────────────────────────────────────────


def test_comando_gp100_inexistente_reprova(tmp_path: Path) -> None:
    falhas = audit_docs.verificar_comandos(['uv run gp100 frobnicate --destino x'], rodar=True)
    assert len(falhas) == 1 and 'frobnicate' in falhas[0]


def test_comandos_reais_do_repo_passam() -> None:
    falhas = audit_docs.verificar_comandos(
        [
            'uv run gp100 build --quiet\nuv run gp100 site --destino dist/site',
            'gh pr view 102 --json state\ngh issue comment 64 --body-file x.md',
        ],
        rodar=True,
    )
    assert falhas == []


def test_grupo_historico_com_barra_nao_e_comando() -> None:
    """ADR-0003 planejou `find/show/diff` — grupo, não comando a validar."""
    falhas = audit_docs.verificar_comandos(['gp100 find/show/diff   consulta'], rodar=True)
    assert falhas == []


# ── estrutura do documento ───────────────────────────────────────────────────


def test_cerca_preserva_numeracao_de_linha(tmp_path: Path, raiz: Path) -> None:
    texto = 'linha 1\n\n```bash\ncd fantasma\n```\n\n`data/nao-existe.json`\n'
    prosa, cercas = audit_docs._separa_cercas(texto)
    achados = audit_docs.verificar_caminhos(tmp_path / 'd.md', raiz, prosa, set(), lambda p: False)
    assert cercas and ':7' in achados[0]


def test_caminho_dentro_de_cerca_nao_e_promessa(tmp_path: Path, raiz: Path) -> None:
    prosa, _ = audit_docs._separa_cercas('```\nsrc/fantasma/inexistente.py\n```\n')
    achados = audit_docs.verificar_caminhos(tmp_path / 'd.md', raiz, prosa, set(), lambda p: False)
    assert achados == []


def test_excecao_historica_e_consciente() -> None:
    assert audit_docs.EXCETO['docs/audit-2.0.md'] == {'estado', 'issue'}
    assert audit_docs.EXCETO['reference/22-dead-code-analysis.md'] == {'caminho'}


# ── guardas sobre a realidade commitada ──────────────────────────────────────


def test_repo_real_esta_verde() -> None:
    """O critério de aceite da #58: zero falso positivo na develop."""
    codigo, saida = _rodar()
    assert codigo == 0, saida[-1500:]
    assert '78 docs consistentes' in saida or 'docs consistentes' in saida


def test_clone_raso_degrada_caminho_para_aviso(tmp_path: Path) -> None:
    """Regressão do CI real: checkout com fetch-depth 1 não vê o histórico e
    citar `tools/…` extinto virava violação FALSA. Num clone raso, a
    verificação de caminhos degrada a aviso (mesma filosofia do offline)."""
    repo = tmp_path / 'repo'
    repo.mkdir()

    def _git(*args: str) -> None:
        subprocess.run(['git', *args], cwd=repo, capture_output=True, check=True)

    _git('init', '-q')
    (repo / 'HISTORIA.md').write_text('Antes: `tools/legacy.py`.\n', encoding='utf-8')
    _git('-c', 'user.name=t', '-c', 'user.email=t@t', 'add', '-A')
    _git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'init')
    (repo / '.git' / 'shallow').write_text('', encoding='utf-8')  # simula fetch-depth 1

    codigo, saida = _rodar(cwd=repo)
    assert codigo == 0, saida[-1500:]
    assert 'clone raso' in saida


def test_merge_de_release_ve_a_historia_completa(tmp_path: Path) -> None:
    """Regressão do PR de release (#107): num merge develop→main, o `git log
    -- <caminho>` SEM --full-history simplifica pelo primeiro parent e os
    commits da develop que criaram o caminho ficam invisíveis — citação
    histórica legítima virava violação falsa."""
    repo = tmp_path / 'repo'
    repo.mkdir()

    def _git(*args: str) -> None:
        subprocess.run(['git', *args], cwd=repo, capture_output=True, check=True)

    cfg = ['-c', 'user.name=t', '-c', 'user.email=t@t']
    _git('init', '-q', '-b', 'main')
    (repo / 'ANTES.md').write_text('início\n', encoding='utf-8')
    _git(*cfg, 'add', '-A')
    _git(*cfg, 'commit', '-qm', 'base')

    _git('checkout', '-qb', 'develop')
    (repo / 'tools').mkdir()
    (repo / 'tools' / 'legado.py').write_text('x\n', encoding='utf-8')
    (repo / 'DOC.md').write_text('citando `tools/legado.py`\n', encoding='utf-8')
    _git(*cfg, 'add', '-A')
    _git(*cfg, 'commit', '-qm', 'feat: cria tools/legado.py e cita no DOC')

    _git('checkout', '-q', 'main')
    (repo / 'OUTRO.md').write_text('main\n', encoding='utf-8')
    _git(*cfg, 'add', '-A')
    _git(*cfg, 'commit', '-qm', 'chore: main anda sozinha')
    # identidade no merge também: o runner do CI não tem user.name/email globais
    _git(*cfg, 'merge', '-q', '--no-ff', 'develop', '-m', 'merge de release')

    codigo, saida = _rodar(cwd=repo)
    assert codigo == 0, saida[-1500:]
    assert 'tools/legado.py' not in saida


def test_entrada_no_ci_e_no_pre_commit() -> None:
    ci = (RAIZ / '.github' / 'workflows' / 'ci.yml').read_text(encoding='utf-8')
    assert 'audit_docs.py' in ci
    pc = (RAIZ / '.pre-commit-config.yaml').read_text(encoding='utf-8')
    assert 'audit_docs.py' in pc
