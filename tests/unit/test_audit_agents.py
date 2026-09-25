"""Guarda de integridade de agentes e skills (issue #63) — casos sintéticos e reais.

Por que este teste existe: a classe de erro que o guarda caça (caminho citado
que não existe, contrato ADR-0008 incompleto, skill fora da curadoria do doc 23)
quebrava em silêncio — o `tsc` não a vê e o CI só falhava quando o agente já
estava em produção com o usuário. O teste fixa cada regra com um caso sintético
em `tmp_path` e a realidade commitada (21 agentes, 11 skills e os pares
canônicos skill ↔ prompt do doc 23).

Mesmo padrão do `test_audit_workflows.py`: nenhum teste escreve no repositório;
os casos sintéticos vivem em `tmp_path` e a realidade é lida, nunca alterada.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit

RAIZ = Path(__file__).resolve().parents[2]


def carregar() -> ModuleType:
    """Importa `.github/scripts/audit_agents.py` (script fora de pacote)."""
    caminho = RAIZ / '.github' / 'scripts' / 'audit_agents.py'
    spec = importlib.util.spec_from_file_location('audit_agents', caminho)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


auditor = carregar()


# ── fábricas de casos sintéticos ─────────────────────────────────────────────

AGENTE_OK = """const definition = {{
  id: 'teste',
  displayName: 'Teste',
  model: 'm',
  toolNames: ['read_files'],
  spawnerPrompt: `Use quando precisar testar. Nunca edita patches.`,
  systemPrompt: `Fonte: {fonte}. NÃO inventa nomes.`,
}}
export default definition
"""


def mundo(
    tmp_path: Path,
    agentes: dict[str, str],
    skills: dict[str, str],
    rastreados: frozenset[str] | None = None,
):
    """Monta um repo sintético e roda o audit() nele."""
    (tmp_path / 'reference').mkdir(exist_ok=True)
    pasta_skills = tmp_path / '.agents' / 'skills'
    pasta_skills.mkdir(parents=True, exist_ok=True)
    for nome, texto in agentes.items():
        (tmp_path / '.agents' / nome).write_text(texto, encoding='utf-8')
    for nome, texto in skills.items():
        pasta = pasta_skills / nome
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / 'SKILL.md').write_text(texto, encoding='utf-8')
    rastreados = (
        rastreados
        if rastreados is not None
        else frozenset(f'.agents/{n}' for n in agentes)
        | frozenset(f'.agents/skills/{n}/SKILL.md' for n in skills)
    )
    return auditor.audit(agentes, {n: pasta_skills / n for n in skills}, rastreados)


# ── regra 1 · caminhos citados ────────────────────────────────────────────────


def test_caminho_inexistente_reprova(tmp_path: Path) -> None:
    falhas, _ = mundo(
        tmp_path,
        {'a.ts': AGENTE_OK.format(fonte='reference/09-x.md')},
        {},
        rastreados=frozenset({'.agents/a.ts'}),
    )
    assert any('reference/09-x.md' in f and 'não existe' in f for f in falhas)


def test_caminho_existente_passa(tmp_path: Path) -> None:
    falhas, _ = mundo(
        tmp_path,
        {'a.ts': AGENTE_OK.format(fonte='reference/12-workflow.md')},
        {},
        rastreados=frozenset({'.agents/a.ts', 'reference/12-workflow.md'}),
    )
    assert not any('reference/12-workflow.md' in f for f in falhas)


def test_pasta_citada_como_fonte_passa(tmp_path: Path) -> None:
    """`data/defs/` é citação legítima: existe se houver arquivo dentro dela."""
    falhas, _ = mundo(
        tmp_path,
        {'a.ts': AGENTE_OK.format(fonte='data/defs/')},
        {},
        rastreados=frozenset({'.agents/a.ts', 'data/defs/SN.json'}),
    )
    assert not any('data/defs' in f for f in falhas)


def test_convencao_de_numero_de_doc_resolve(tmp_path: Path) -> None:
    """`reference/15` vence se existir o doc que começa com `15-` (convenção da casa)."""
    falhas, _ = mundo(
        tmp_path,
        {'a.ts': AGENTE_OK.format(fonte='reference/15')},
        {},
        rastreados=frozenset({'.agents/a.ts', 'reference/15-firmware2-effects.md'}),
    )
    assert not falhas


def test_manual_pdf_gitignored_e_citacao_legitima(tmp_path: Path) -> None:
    """Obtido fora do repo de propósito (licença); .gitignore documenta como obter."""
    falhas, _ = mundo(
        tmp_path,
        {'a.ts': AGENTE_OK.format(fonte='manual.pdf')},
        {},
        rastreados=frozenset({'.agents/a.ts'}),
    )
    assert not any('manual.pdf' in f for f in falhas)


def test_spawnavel_inexistente_avisa_mas_nao_reprova(tmp_path: Path) -> None:
    falhas, avisos = mundo(
        tmp_path,
        {
            'a.ts': AGENTE_OK.format(fonte='knowledge.md').replace(
                "toolNames: ['read_files'],",
                "toolNames: ['read_files'],\n  spawnableAgents: ['gp100-fantasma'],",
            )
        },
        {},
        rastreados=frozenset({'.agents/a.ts', 'knowledge.md'}),
    )
    assert not falhas
    assert any('gp100-fantasma' in a for a in avisos)


# ── regra 2 e 3 · contrato ADR-0008 ──────────────────────────────────────────


def test_contrato_incompleto_reprova_listando_o_que_falta(tmp_path: Path) -> None:
    texto = AGENTE_OK.format(fonte='knowledge.md').replace("displayName: 'Teste',", '')
    falhas, _ = mundo(tmp_path, {'a.ts': texto}, {}, rastreados=frozenset({'.agents/a.ts'}))
    assert any('displayName' in f and 'ADR-0008' in f for f in falhas)


def test_agente_sem_limites_reprova(tmp_path: Path) -> None:
    texto = AGENTE_OK.format(fonte='knowledge.md')
    texto = texto.replace('Nunca edita patches.', 'edita patches')
    texto = texto.replace('NÃO inventa nomes.', 'inventa nomes.')
    falhas, _ = mundo(tmp_path, {'a.ts': texto}, {}, rastreados=frozenset({'.agents/a.ts'}))
    assert any('limites explícitos' in f for f in falhas)


def test_id_duplicado_reprova(tmp_path: Path) -> None:
    falhas, _ = mundo(
        tmp_path,
        {
            'a.ts': AGENTE_OK.format(fonte='knowledge.md'),
            'b.ts': AGENTE_OK.format(fonte='knowledge.md'),
        },
        {},
        rastreados=frozenset({'.agents/a.ts', '.agents/b.ts'}),
    )
    assert any('duplicado' in f for f in falhas)


# ── regras 4 e 5 · skills: frontmatter e doc 23 ──────────────────────────────


SKILL_OK = '---\nname: teste\ndescription: Use quando testar.\n---\n\n# Teste\n'


def test_skill_sem_frontmatter_reprova(tmp_path: Path) -> None:
    falhas, _ = mundo(tmp_path, {}, {'teste': '# sem frontmatter'}, rastreados=frozenset())
    assert any('frontmatter' in f and 'name' in f for f in falhas)


def test_name_divergente_da_pasta_reprova(tmp_path: Path) -> None:
    falhas, _ = mundo(
        tmp_path,
        {},
        {'teste': SKILL_OK.replace('name: teste', 'name: outro')},
        rastreados=frozenset(),
    )
    assert any('diverge da pasta' in f for f in falhas)


def test_skill_fora_do_doc23_reprova(tmp_path: Path) -> None:
    """Skill no disco, mas fora da curadoria: reprova (doc 23 é fonte única)."""
    pasta = tmp_path / '.agents' / 'skills' / 'teste'
    pasta.mkdir(parents=True)
    (pasta / 'SKILL.md').write_text(SKILL_OK, encoding='utf-8')
    falhas, _ = auditor.audit(
        {},
        {'teste': pasta},
        frozenset({'.agents/skills/teste/SKILL.md'}),
        registradas={'outra-skill'},
    )
    assert any('não registrada no doc 23' in f for f in falhas)


def test_doc23_registrando_skill_inexistente_reprova(tmp_path: Path) -> None:
    falhas, _ = auditor.audit(
        {},
        {},
        frozenset(),
        registradas={'fantasma'},
    )
    assert any('não existe no disco' in f and 'fantasma' in f for f in falhas)


def test_skill_orfa_avisa_mas_nao_reprova(tmp_path: Path) -> None:
    """Aviso, não reprova: consumo pode ser gatilho automático (doc 23)."""
    # gp100-criar-patch é real e ninguém a cita explicitamente → aviso no repo real.
    falhas, avisos = auditor.audit(
        {},
        {
            p.name: p
            for p in sorted((RAIZ / '.agents' / 'skills').iterdir())
            if (p / 'SKILL.md').is_file()
        },
        auditor._rastreados(RAIZ),
        registradas=auditor._registradas_no_doc(auditor._rastreados(RAIZ)),
    )
    assert not any('skills/' in f for f in falhas)
    assert avisos  # há skills sem citação explícita — e nenhuma reprova


# ── regra 6 · par canônico skill gp100-* ↔ prompts/ ─────────────────────────


def test_skill_gp100_sem_prompt_canonico_reprova(tmp_path: Path) -> None:
    """Skill `gp100-*` sem o prompt canônico no git é violação (doc 23, §4)."""
    pasta = tmp_path / 'gp100-criar-patch'
    pasta.mkdir()
    (pasta / 'SKILL.md').write_text(
        '---\nname: gp100-criar-patch\ndescription: d\n---\n# x', encoding='utf-8'
    )
    falhas, _ = auditor.audit(
        {},
        {'gp100-criar-patch': pasta},
        frozenset({'.agents/skills/gp100-criar-patch/SKILL.md'}),
        registradas={'gp100-criar-patch'},
    )
    assert any('prompt canônico' in f for f in falhas), falhas


def test_prompt_orfao_sem_skill_reprova() -> None:
    """Prompt em prompts/ sem skill gp100-* consumidora é violação (doc 23, §4)."""
    falhas, _ = auditor.audit(
        {},
        {},
        frozenset({'prompts/fluxo-novo.md'}),
        registradas=set(),
    )
    assert any('prompts/fluxo-novo.md` órfão' in f for f in falhas), falhas


def test_pares_reais_estao_sincronizados() -> None:
    """Os 4 pares canônicos do repo real: skill no disco, prompt no git, zero falha."""
    falhas, _ = auditor.audit(
        {},
        {
            p.name: p
            for p in sorted((RAIZ / '.agents' / 'skills').iterdir())
            if (p / 'SKILL.md').is_file()
        },
        auditor._rastreados(RAIZ),
        registradas=auditor._registradas_no_doc(auditor._rastreados(RAIZ)),
    )
    assert not any('prompt' in f for f in falhas), falhas


# ── a realidade commitada (o guarda de fundo) ────────────────────────────────


def test_repositorio_real_passa_sem_violacoes() -> None:
    """21 agentes + 11 skills do repo: zero falha; avisos não reprovam."""
    agentes = auditor._agentes()
    skills = {
        p.name: p
        for p in sorted((RAIZ / '.agents' / 'skills').iterdir())
        if (p / 'SKILL.md').is_file()
    }
    falhas, avisos = auditor.audit(
        agentes,
        skills,
        auditor._rastreados(RAIZ),
        registradas=auditor._registradas_no_doc(auditor._rastreados(RAIZ)),
    )
    assert len(agentes) == 21
    assert len(skills) == 11
    assert not falhas, '\n'.join(falhas)
    assert all('sem consumidor' in a for a in avisos)


def test_main_devolve_zero_no_repo_real(capsys) -> None:
    assert auditor.main() == 0
    saida = capsys.readouterr().out
    assert 'integridade da camada de IA OK' in saida
