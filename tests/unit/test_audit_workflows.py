"""Auditor de workflows — regra 8: nome e nível de permissão válidos.

Por que este teste existe: o `project-automation.yml` declarava
`repository-project: write` (sem o "s"). Escopo inexistente invalida o arquivo
INTEIRO — o GitHub respondia "workflow file issue" a cada push e **nenhum job
daquele workflow jamais rodou**. O auditor não pegava porque só cobrava a
PRESENÇA do bloco `permissions:`; agora cobra o conteúdo, e este teste fixa o
caso real (os workflows commitados) e as formas de errar.

Mesmo padrão do resto da suíte: nenhum teste escreve no repositório — os casos
sintéticos vivem em `tmp_path`.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]
WORKFLOWS = RAIZ / '.github' / 'workflows'


def carregar() -> ModuleType:
    """Importa `.github/scripts/audit_workflows.py` (script fora de pacote)."""
    caminho = RAIZ / '.github' / 'scripts' / 'audit_workflows.py'
    spec = importlib.util.spec_from_file_location('audit_workflows', caminho)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


auditor = carregar()


def falhas(tmp_path: Path, permissions: str) -> str:
    """Texto das falhas do auditor para um workflow mínimo com esse `permissions:`."""
    arquivo = tmp_path / 'workflow.yml'
    arquivo.write_text(f'name: teste\non: push\n{permissions}\n', encoding='utf-8')
    erros, _avisos = auditor.audit(arquivo)
    return '\n'.join(texto for _, texto in erros)


def test_escopo_inexistente_reprova_com_a_consequencia(tmp_path: Path) -> None:
    """O caso do `repository-project`: não basta dizer "inválido", tem de explicar."""
    texto = falhas(tmp_path, 'permissions:\n  repository-project: write')
    assert 'repository-project' in texto
    assert 'ARQUIVO' in texto
    assert 'repository-projects' in texto  # a lista de escopos aceitos vai na mensagem


def test_escopo_correto_com_s_final_passa(tmp_path: Path) -> None:
    assert falhas(tmp_path, 'permissions:\n  repository-projects: write') == ''


def test_nivel_invalido_reprova(tmp_path: Path) -> None:
    texto = falhas(tmp_path, 'permissions:\n  contents: leitura')
    assert 'nível inválido' in texto
    assert 'read' in texto and 'write' in texto


def test_comentario_na_linha_do_nivel_nao_atrapalha(tmp_path: Path) -> None:
    """`contents: read # piso` é a forma usada em todos os workflows do repo."""
    assert falhas(tmp_path, 'permissions:\n  contents: read # piso do token') == ''


def test_shorthand_read_all_e_write_all_sao_aceitos(tmp_path: Path) -> None:
    assert falhas(tmp_path, 'permissions: read-all') == ''
    assert falhas(tmp_path, 'permissions: write-all') == ''


def test_shorthand_com_um_nivel_so_reprova(tmp_path: Path) -> None:
    texto = falhas(tmp_path, 'permissions: read')
    assert 'read-all' in texto


def test_escopo_invalido_em_job_tambem_reprova(tmp_path: Path) -> None:
    """Um job com permissão torta invalida o arquivo igual ao bloco do topo."""
    texto = falhas(
        tmp_path,
        'permissions:\n  contents: read\njobs:\n  a:\n    permissions:\n'
        '      pull-request: read\n    runs-on: ubuntu-24.04\n    timeout-minutes: 5\n',
    )
    assert 'pull-request' in texto


def test_workflows_commitados_passam_no_auditor() -> None:
    """O guarda de fundo: nenhum workflow do repositório com violação."""
    arquivos = sorted(WORKFLOWS.glob('*.y*ml'))
    assert arquivos, f'nenhum workflow em {WORKFLOWS}'
    for caminho in arquivos:
        erros, _avisos = auditor.audit(caminho)
        assert not erros, f'{caminho.name}: ' + '; '.join(t for _, t in erros)


# ── Regra 10 · teto de permissões por workflow (#62) ──────────────────────────


def falhas_com_teto(tmp_path: Path, permissions: str, nome: str) -> str:
    """Mesmo de falhas(), mas gravando o nome de arquivo que define o teto."""
    arquivo = tmp_path / nome
    arquivo.write_text(f'name: teste\non: push\n{permissions}\n', encoding='utf-8')
    erros, _avisos = auditor.audit(arquivo)
    return '\n'.join(texto for _, texto in erros)


def test_write_acima_do_teto_reprova(tmp_path: Path) -> None:
    """ci.yml tem teto contents: read — write é a superfície que a regra barra."""
    texto = falhas_com_teto(tmp_path, 'permissions:\n  contents: write', 'ci.yml')
    assert 'acima do teto' in texto
    assert 'contents: read' in texto       # o teto vai na mensagem
    assert 'TETO_PERMISSOES' in texto      # e o caminho da correção


def test_escopo_fora_do_teto_reprova(tmp_path: Path) -> None:
    """Escopo que nem existe no teto reprova, mesmo em nível read."""
    texto = falhas_com_teto(
        tmp_path, 'permissions:\n  contents: read\n  issues: write', 'ci.yml')
    assert 'fora do teto' in texto
    assert 'issues' in texto


def test_job_com_write_acima_do_teto_reprova(tmp_path: Path) -> None:
    """A elevação escondida num job é exatamente o buraco que a regra 10 fecha."""
    texto = falhas_com_teto(
        tmp_path,
        'permissions:\n  contents: read\njobs:\n  a:\n'
        '    permissions:\n      contents: write\n'
        '    runs-on: ubuntu-24.04\n    timeout-minutes: 5\n',
        'ci.yml',
    )
    assert 'acima do teto' in texto
    assert 'em job' in texto


def test_teto_respeitado_passa(tmp_path: Path) -> None:
    """`contents: read` no topo continua sendo o caso normal."""
    assert falhas_com_teto(tmp_path, 'permissions:\n  contents: read', 'ci.yml') == ''


def test_nivel_abaixo_do_teto_passa(tmp_path: Path) -> None:
    """security.yml tem pull-requests: write no teto — read está abaixo, não fere."""
    texto = falhas_com_teto(
        tmp_path,
        'permissions:\n  contents: read\n  pull-requests: read',
        'security.yml',
    )
    assert texto == ''


def test_shorthand_concede_tudo_e_fere_o_teto(tmp_path: Path) -> None:
    """read-all/write-all concedem todos os escopos — acima de qualquer teto."""
    texto = falhas_com_teto(tmp_path, 'permissions: write-all', 'release.yml')
    assert 'concede' in texto


def test_todo_workflow_commitado_tem_teto_declarado() -> None:
    """A tabela é fechada: workflow novo sem entrada reprova no main() do auditor."""
    arquivos = sorted(WORKFLOWS.glob('*.y*ml'))
    assert arquivos, f'nenhum workflow em {WORKFLOWS}'
    sem_teto = [p.name for p in arquivos if p.name not in auditor.TETO_PERMISSOES]
    assert not sem_teto, f'sem teto na TETO_PERMISSOES: {sem_teto}'


def test_escritas_concedidas_sao_as_justificadas() -> None:
    """Só há write onde a escrita É o trabalho — o mapa inteiro é o contrato."""
    escritas = {nome: {e for e, n in teto.items() if n == 'write'}
                for nome, teto in auditor.TETO_PERMISSOES.items()}
    assert escritas == {
        'ci.yml': set(),
        'security.yml': {'security-events', 'pull-requests'},
        'release.yml': {'contents'},
        'project-automation.yml': set(),
    }
