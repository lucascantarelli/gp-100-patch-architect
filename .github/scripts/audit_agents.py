#!/usr/bin/env python3
""".github/scripts/audit_agents.py — guarda de integridade da camada de IA (issue #63).

Por que este script existe: o `tsc --noEmit` pega erro de **tipo** nos agentes,
mas não pega a integridade que quebra em silêncio — agente apontando para caminho
que não existe no repositório, skill sem registro na curadoria (doc 23), agente
sem contrato completo (ADR-0008). A suíte de dados tem o TestH; a superfície de
workflows tem o `audit_workflows.py`; a camada de IA não tinha ninguém.

Mesma filosofia do resto do repo: stdlib pura, veredito binário e mensagem que
diz o que corrigir. Aviso não reprova — curadoria é decisão humana (doc 23).

Uso:  python .github/scripts/audit_agents.py
      0 = integridade OK (avisos não reprovam) · 1 = violação

Regras que REPROVAM:
  1. Caminho citado por agente e inexistente nos arquivos RASTREADOS pelo git
     (não no disco: `manual.pdf` existe na máquina e é gitignored por licença —
     o CI tem de ver o mesmo que um clone limpo). A convenção de número de doc
     (`reference/15` → `reference/15-*.md`) é resolvida antes de reprovar.
  2. Contrato do agente incompleto (ADR-0008 + #63): `id`, `displayName`,
     `model`, `toolNames`, `spawnerPrompt` (o "quando usar") e `systemPrompt`
     ou `instructionsPrompt`, com limites explícitos (NUNCA/Jamais/não…).
  3. `id` duplicado entre agentes — o Freebuff resolve agente por id.
  4. Skill sem frontmatter `name`/`description` ou com `name` divergente da
     pasta (o gatilho da skill resolve pelo `name`).
  5. Divergência entre o disco e o doc 23 (a curadoria passa por ele, §4.3):
     skill no disco sem registro lá, ou registrada sem existir no disco.

Regra que AVISA (não reprova):
  6. Skill sem consumidor explícito — nenhum agente/skill/prompt a cita. O
     consumo pode ser por gatilho automático da ferramenta (é o modelo das
     skills do GP-100); o guarda ilumina, o humano decide (doc 23).
  7. `spawnableAgents` citando agente inexistente — hoje só o orquestrador usa
     o campo; tratado como aviso até a primeira ocorrência real virar regra.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):  # console Windows cp1252 -> UTF-8
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(__file__).parent.parent.parent
AGENTS = ROOT / '.agents'
SKILLS = AGENTS / 'skills'
PROMPTS = ROOT / 'prompts'
DOC_CURADORIA = ROOT / 'reference' / '23-skills-curation.md'

# Obtidos fora do repositório de propósito (gitignored) — a citação é legítima:
# `.gitignore` documenta como obter. Fora desta lista, caminho citado tem de
# estar rastreado pelo git.
FORA_DO_GIT = {'manual.pdf'}

# ── Contrato do agente (ADR-0008; issue #63) ─────────────────────────────────
CAMPOS_OBRIGATORIOS = ('id', 'displayName', 'model', 'toolNames', 'spawnerPrompt')
PROMPTS_EXIGIDOS = ('systemPrompt', 'instructionsPrompt')
LIMITES = re.compile(r'\b(?:NUNCA|Nunca|nunca|JAMAIS|Jamais|jamais|NÃO|Não|não|Nem|nem)\b')

# Caminho citado em texto (backticks, aspas ou cru). Captura conservadora: só
# caminhos relativos com pasta conhecida — nada de URL, `~`, template ou caminho
# de pacote que o checkout não resolve como arquivo.
PADRAO_CAMINHO = re.compile(
    r'(?:^|[\s(`"\'\[])(('
    r'data/[\w./-]+|reference/[\w./-]+|\.agents/[\w./-]+|prompts/[\w./-]+|'
    r'\.github/[\w./-]+|templates/[\w./-]+|docs/[\w./-]+|'
    r'patches/[\w./-]+|knowledge\.md|ARCHITECTURE\.md|CONTRIBUTING\.md|'
    r'DEVELOPMENT\.md|SECURITY\.md|NOTICE\.md|CHANGELOG\.md|master_prompt\.md|'
    r'manual\.pdf|tsconfig\.json|pyproject\.toml'
    r'))(?:[\s`)"\',.;:\]]|$)'
)

NUM_DOC = re.compile(r'^reference/(\d{2})$')


def _caminhos_citados(texto: str) -> set[str]:
    """Caminhos de repositório citados no texto (candidatos a existir no git)."""
    return {m.group(1).rstrip('.,;:') for m in PADRAO_CAMINHO.finditer(texto)}


def _rastreados(raiz: Path) -> frozenset[str]:
    """Arquivos rastreados pelo git (`git ls-files`) — a realidade do clone limpo."""
    r = subprocess.run(
        ['git', 'ls-files'], cwd=str(raiz), capture_output=True, text=True,
        encoding='utf-8', errors='replace',
    )
    if r.returncode != 0:
        raise SystemExit(f'❌ `git ls-files` falhou dentro de {raiz} — rode o '
                         'guarda na raiz de um clone do repositório.')
    return frozenset(linha for linha in r.stdout.splitlines() if linha)


def _citação_existe(rel: str, rastreados: frozenset[str]) -> bool:
    """A citação resolve no repositório? (arquivo, pasta, doc por número, fora do git)"""
    if rel in FORA_DO_GIT:
        return True
    if rel in rastreados:
        return True
    if any(caminho.startswith(rel.rstrip('/') + '/') for caminho in rastreados):
        return True  # pasta citada como fonte ("data/defs/", "reference/")
    m = NUM_DOC.match(rel)
    if m:  # convenção do projeto: "reference/15" = o doc que começa com "15-"
        prefixo = f'reference/{m.group(1)}-'
        return any(caminho.startswith(prefixo) for caminho in rastreados)
    return False


def _agentes() -> dict[str, str]:
    """Lê os agentes `.agents/*.ts`; erro se a pasta sumir."""
    arquivos = sorted(AGENTS.glob('*.ts'))
    if not arquivos:
        raise SystemExit(f'❌ nenhum agente em {AGENTS} — a camada de IA sumiu?')
    return {p.name: p.read_text(encoding='utf-8', errors='replace') for p in arquivos}


def _skill_frontmatter(caminho: Path) -> dict[str, str]:
    """Frontmatter `name`/`description` de um SKILL.md ({} se ausente)."""
    texto = caminho.read_text(encoding='utf-8', errors='replace')
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', texto, flags=re.DOTALL)
    if not m:
        return {}
    campos: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        kv = re.match(r'^(\w[\w-]*):\s*(.+)$', linha.strip())
        if kv:
            campos[kv.group(1)] = kv.group(2).strip('\'"')
    return campos


def _registradas_no_doc(rastreados: frozenset[str]) -> set[str]:
    """Nomes de skills versionadas citadas no doc de curadoria (doc 23)."""
    if not DOC_CURADORIA.is_file():
        raise SystemExit(f'❌ curadoria não encontrada: {DOC_CURADORIA} — o doc 23 '
                         'é a fonte única do inventário de skills (issue #63).')
    texto = DOC_CURADORIA.read_text(encoding='utf-8', errors='replace')
    return {
        nome
        for nome in re.findall(r'`([a-z0-9][a-z0-9-]*)`', texto)
        if f'.agents/skills/{nome}/SKILL.md' in rastreados
    }


def _consumidores_de_skill(skills: dict[str, Path]) -> dict[str, set[str]]:
    """Quem cita cada skill: agentes, outras skills e prompts canônicos."""
    textos: dict[str, str] = _agentes()
    for pasta in sorted(SKILLS.iterdir()):
        md = pasta / 'SKILL.md'
        if pasta.is_dir() and md.is_file():
            textos[f'skills/{pasta.name}'] = md.read_text(encoding='utf-8', errors='replace')
    if PROMPTS.is_dir():
        for p in sorted(PROMPTS.glob('*.md')):
            textos[f'prompts/{p.name}'] = p.read_text(encoding='utf-8', errors='replace')
    citacoes: dict[str, set[str]] = {nome: set() for nome in skills}
    for fonte, texto in textos.items():
        for nome in skills:
            if nome != fonte.removeprefix('skills/') and re.search(
                rf'[\s(`"\']({re.escape(nome)})[\s`)"\'\].,;:!?]', texto
            ):
                citacoes[nome].add(fonte)
    return citacoes


def _extrair_string_campo(texto: str, campo: str) -> str:
    """Valor string de um campo template-literal do `.ts` (sem interpretar TS)."""
    m = re.search(rf'\b{campo}\s*:\s*`', texto)
    if not m:
        return ''
    inicio = m.end()
    fim = texto.find('`', inicio)
    return texto[inicio:fim] if fim != -1 else ''


def _ids_spawnaveis(texto: str) -> list[str]:
    m = re.search(r'spawnableAgents\s*:\s*\[(.*?)\]', texto, flags=re.DOTALL)
    if not m:
        return []
    return re.findall(r"'([a-z0-9-]+)'", m.group(1))


def audit(
    agentes: dict[str, str],
    skills: dict[str, Path],
    rastreados: frozenset[str],
    registradas: set[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Devolve (falhas, avisos) — mensagens prontas com arquivo e o que corrigir."""
    falhas: list[str] = []
    avisos: list[str] = []
    registradas = _registradas_no_doc_cache if registradas is None else registradas

    # ── 1 e 7. caminhos citados por agente (prompts e spawnáveis) ────────────
    ids_conhecidos = {
        m.group(1)
        for s in agentes.values()
        if (m := re.search(r"\bid:\s*'([a-z0-9-]+)'", s))
    }
    for nome, texto in agentes.items():
        for campo in ('systemPrompt', 'instructionsPrompt', 'spawnerPrompt'):
            alvo = _extrair_string_campo(texto, campo)
            for rel in _caminhos_citados(alvo):
                if not _citação_existe(rel, rastreados):
                    falhas.append(
                        f'{nome} ({campo}): cita `{rel}` e o caminho não existe no '
                        'repositório — corrige o caminho ou cria o arquivo'
                    )
        for alvo_id in _ids_spawnaveis(texto):
            if alvo_id not in ids_conhecidos:
                avisos.append(
                    f'{nome}: `spawnableAgents` cita `{alvo_id}` e não há agente '
                    'com esse id — o spawn falha em runtime'
                )

    # ── 2, 3. contrato do agente (ADR-0008) ──────────────────────────────────
    ids_vistos: dict[str, str] = {}
    for nome, texto in agentes.items():
        faltando = [
            c for c in CAMPOS_OBRIGATORIOS + PROMPTS_EXIGIDOS
            if not re.search(rf'\b{c}\s*:', texto)
        ]
        # "systemPrompt OU instructionsPrompt" basta (agentes folha não têm os dois)
        if 'systemPrompt' in faltando and 'instructionsPrompt' in faltando:
            faltando = [c for c in faltando if c not in PROMPTS_EXIGIDOS] + [
                'systemPrompt ou instructionsPrompt'
            ]
        else:
            faltando = [c for c in faltando if c not in PROMPTS_EXIGIDOS]
        prompts = ' '.join(
            _extrair_string_campo(texto, c) for c in PROMPTS_EXIGIDOS
        )
        if not LIMITES.search(prompts):
            faltando.append('limites explícitos (NUNCA/não…) em algum prompt')
        if faltando:
            falhas.append(
                f'{nome}: contrato incompleto (ADR-0008) — falta: {", ".join(faltando)}'
            )
        m = re.search(r"\bid:\s*'([a-z0-9-]+)'", texto)
        if m:
            aid = m.group(1)
            if aid in ids_vistos:
                falhas.append(
                    f'{nome}: id `{aid}` duplicado (já em {ids_vistos[aid]}) — '
                    'o Freebuff resolve agente por id'
                )
            ids_vistos[aid] = nome

    # ── 4, 5, 6. skills: frontmatter, name×pasta, doc 23, órfãos ─────────────
    citacoes = _consumidores_de_skill(skills)
    for nome, caminho in sorted(skills.items()):
        fm = _skill_frontmatter(caminho / 'SKILL.md')
        faltando = [c for c in ('name', 'description') if c not in fm]
        if faltando:
            falhas.append(
                f'skills/{nome}/SKILL.md: frontmatter sem {", ".join(faltando)} '
                '— o gatilho da skill depende dele'
            )
        if 'name' in fm and fm['name'] != nome:
            falhas.append(
                f'skills/{nome}/SKILL.md: `name: {fm["name"]}` diverge da pasta '
                f'`{nome}` — o gatilho resolve pelo name'
            )
        if nome not in registradas:
            falhas.append(
                f'skills/{nome}: no disco mas não registrada no doc 23 — toda '
                'mudança de inventário passa pela curadoria (doc 23, §4.3)'
            )
        if not citacoes[nome]:
            avisos.append(
                f'skills/{nome}: sem consumidor explícito (agente/skill/prompt) — '
                'pode ser gatilho automático; curadoria confere no doc 23'
            )
    for nome in sorted(registradas - set(skills)):
        falhas.append(
            f'doc 23 registra `skills/{nome}` e ela não existe no disco — '
            'ou o caminho mudou, ou a curadoria ficou para trás'
        )

    return falhas, avisos


_registradas_no_doc_cache: set[str] = set()


def main() -> int:
    """Audita agentes e skills; 1 se houver violação (avisos não reprovam)."""
    global _registradas_no_doc_cache
    agentes = _agentes()
    skills = {
        p.name: p
        for p in sorted(SKILLS.iterdir())
        if p.is_dir() and (p / 'SKILL.md').is_file()
    }
    rastreados = _rastreados(ROOT)
    _registradas_no_doc_cache = _registradas_no_doc(rastreados)
    falhas, avisos = audit(agentes, skills, rastreados)

    print(f'🤖 {len(agentes)} agente(s) · {len(skills)} skill(s) — guarda de '
          'integridade da camada de IA (issue #63)')
    for f in falhas:
        print(f'  ❌ {f}')
    for a in avisos:
        print(f'  ⚠️  {a}')
    print()
    if falhas:
        print(f'❌ {len(falhas)} violação(ões) — corrija antes do merge.')
        return 1
    print('✅ integridade da camada de IA OK'
          + (f' ({len(avisos)} aviso(s) — curadoria humana).' if avisos else '.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
