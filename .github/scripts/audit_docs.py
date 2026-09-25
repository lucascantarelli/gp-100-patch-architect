#!/usr/bin/env python3
"""Linter de consistência de documentação (issue #58).

Por que este script existe: a pior classe de erro deste repositório não é
código — é **doc divergindo da realidade**. Casos já documentados: o
`CODEOWNERS` apontando arquivo inexistente, "17 agentes" quando eram 19, o
audit citando números de issue errados, o roadmap listando issues "abertas"
na fase errada e um `3.0` que só existia em texto. Nenhum desses foi pego por
máquina — todos por leitura humana, semanas depois.

Mesma filosofia do `audit_workflows.py`: stdlib pura (mais `git`/`gh` via
subprocess), veredito binário e mensagem que diz o que corrigir — com
`arquivo:linha` sempre que possível.

Uso:  python .github/scripts/audit_docs.py
      0 = consistente (avisos não reprovam) · 1 = violação

O que REPROVA:
  1. `#N` citado em doc que NÃO existe no repositório (issue/PR inexistente).
  2. Reivindicação de ESTADO errada — "#N fechada"/"aberta"/"entregue" quando
     a realidade (API do GitHub) é outra, inclusive em faixas "#A–#B abertas".
  3. **Caminho** citado que NUNCA existiu no git (nem presente, nem no
     histórico — citação histórica de `tools/…` é legítima e passa; typo não).
  4. **Link relativo** de Markdown que não resolve (o alvo não existe).
  5. **Milestone** citado que não existe ("milestone fantasma é falha").
  6. Comando de `gh`/`gp100` em bloco de doc com caminho de subcomando
     INVÁLIDO — validado com `--help` (o `gh project item-list` sem `--limit`
     teria sido pego aqui; `--help` é local, sem rede).
  7. **Contagem literal** ("N agentes/skills/patches/músicas/álbuns/testes/
     .prst") que diverge da **derivação** (`badges.dados_derivados`, ADR-0014)
     — a mesma fonte dos badges e do `/stats/`. Linha com sinal de subconjunto
     ou registro histórico (golden set, "na auditoria", "da época", versão
     antiga) não reivindica o total e passa.

O que AVISA (não reprova):
  * Âncora de link (`doc.md#seção`) que não casa com um título do alvo —
    a numeração de títulos muda com frequência; o alvo existente é o contrato.
  * Verificações remotas (1, 2 e 5) quando não há rede/token — offline o
    linter degrada para aviso em vez de reprovar (o CI SEMPRE tem rede).
  * Comando cujo binário não está instalado na máquina (CI tem tudo).

Superfície: todos os `*.md` rastreados pelo git. Blocos de código cercado são
esvaziados antes das verificações 1–5 (exemplos de caminho em docs são
legítimos) e usados APENAS pela verificação 6. URLs (`https://…`) nunca
entram no scan de `#N`.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_FALLBACK = "lucascantarelli/gp-100-patch-architect"

# Estados que um doc pode reivindicar sobre uma issue — e o que significam.
ESTADOS = {
    "fechada": "closed", "fechado": "closed", "fechadas": "closed",
    "fechados": "closed", "aberta": "open", "aberto": "open",
    "abertas": "open", "abertos": "open", "entregue": "closed",
    "entregues": "closed", "concluida": "closed", "concluída": "closed",
    "concluidas": "closed", "concluídas": "closed", "concluido": "closed",
    "concluído": "closed", "pendente": "open", "pendentes": "open",
}

RE_CITACAO = re.compile(r"(?<![\w/\)\]])#(\d{1,4})\b")
RE_URL = re.compile(r"https?://\S+")
RE_ESTADO = re.compile(
    rf"#(\d{{1,4}})\s+(?:(?:está|esta|era|foi|é|são)\s+)?({ '|'.join(ESTADOS) })\b",
    re.IGNORECASE,
)
RE_FAIXA = re.compile(
    rf"#(\d{{1,4}})\s*[–—-]\s*#?(\d{{1,4}})\s+(?:(?:está|esta|era|foi|é|são)\s+)?({ '|'.join(ESTADOS) })\b",
    re.IGNORECASE,
)
RE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
RE_MILESTONE = re.compile(r"milestone\s+[`*\"']*(v\d[\w.-]*)", re.IGNORECASE)
RE_CERCA = re.compile(r"^(```|~~~)", re.M)
PLACEHOLDER = re.compile(r"[<>*{}$@:|()\[\],…–—'\"?=]")
RE_CONT = re.compile(r"^\s*(gh|gp100|uv)\b")

# Caminho só é CANDIDATO a verificação se parecer caminho DE REPOSITÓRIO —
# a gramática é conservadora de propósito (zero falso positivo vale mais que
# pegar mais um typo): ≥ 2 segmentos, sem caractere de sintaxe/negrito/modelo,
# e (tem extensão conhecida OU começa com diretório de topo conhecido).
# `z-ai/glm-5.3-flash` (modelo), `Mode(STD/Jumbo)` (sintaxe de parâmetro),
# `preset_info/@time` (JSONPath), `astral-sh/setup-uv@v7` (action) ficam fora.
RE_CANDIDATO = re.compile(r"^\.?[A-Za-z0-9_][\w.-]*(?:/[\w.-]+)+/?$")
EXT_CONHECIDAS = {
    "md", "py", "yml", "yaml", "json", "toml", "txt", "ts", "sh", "cfg",
    "ini", "csv", "wav", "prst", "pdf", "html", "css", "js", "lock",
}
PREFIXO_CONHECIDO = {
    "src", "docs", "tests", "reference", "data", "patches", "tools",
    ".github", ".agents", "manual_pages", "impulse_responses", "dist",
    "scripts", "skills",
}
RE_ABREV_DOC = re.compile(r"^(reference|docs)/(\d{1,2})$")

# Grupos com barra num ADR histórico (`gp100 find/show/diff`) — eram três
# comandos no plano; hoje dois existem e um mudou de nome. Julgar slash a
# slash exigiria semântica: fica FORA da verificação de comandos.
RE_GRUPO_SLASH = re.compile(r"/|-e-|")

# Skills de TERCEIROS citam arquivos do ECOSSISTEMA delas (references/,
# worktrees/, state_dir/…) — não é promessa sobre ESTE repositório. Mesma
# lista de exclusão do pre-commit e do ruff.
SURFACAS_FORA = (".agents/skills/",)

# Exceções conscientes: {arquivo: {verificações que nele NÃO se aplicam}}.
# Cada entrada tem por quê — a tabela é fechada de propósito (mesmo desenho
# do TETO_PERMISSOES do auditor de workflows).
EXCETO: dict[str, set[str]] = {
    # Registro histórico de 2026-09: cita de propósito os erros da época
    # ("#29" onde era #30, issues "abertas" na fase errada). Reler o passado
    # com o veredito de hoje seria reescrever a auditoria.
    "docs/audit-2.0.md": {"estado", "issue", "contagens"},
    # Auditoria do DoD datada: as métricas congelam a época da verificação.
    "docs/audit-dod-2.0.md": {"contagens"},
    # Análise de 2026-09 sobre o legado (tools/): a proposta de prevenção
    # (`tests/test_dead_code.py`) foi SUPERADA — o código morto virou teste
    # da pirâmide e o scanner AST não sobreviveu à extinção do legado.
    "reference/22-dead-code-analysis.md": {"caminho"},
    # ADR datado: o contexto descreve a biblioteca DA ÉPOCA ("97 patches") —
    # reler com a derivação de hoje reescreveria o registro da decisão.
    "docs/decisions/0013-modelo-de-artefatos-em-escala.md": {"contagens"},
    # Demais ADRs: contexto histórico datado ("hoje a CLI é…", "no momento…")
    # — a decisão vive no tempo em que foi tomada.
    "docs/decisions/0002-camadas-pragmaticas.md": {"contagens"},
    "docs/decisions/0003-cli-typer-rich.md": {"contagens"},
    "docs/decisions/0004-ui-via-api-na-2-1.md": {"contagens"},
    "docs/decisions/0005-qualidade-ruff-mypy-pytest.md": {"contagens"},
    "docs/decisions/0008-agents-e-contrato.md": {"contagens"},
    # Golden set é POR DEFINIÇÃO um subconjunto (20 músicas / 43 patches).
    "reference/20-golden-set.md": {"contagens"},
    # Histórico de releases: cada seção congela as contagens da sua época.
    "CHANGELOG.md": {"contagens"},
}


# ── infra: git, gh, api ──────────────────────────────────────────────────────


def _git(*args: str) -> str:
    r = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    return r.stdout.strip() if r.returncode == 0 else ""


class Api:
    """API do GitHub com degradação graciosa: sem rede/token, `ok=False`."""

    def __init__(self) -> None:
        self.repo = os.environ.get("GITHUB_REPOSITORY") or self._repo_git()
        self.token = (
            os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_TOKEN")
            or self._token_gh()
        )
        self.ok = bool(self.repo and self.token)
        self._cache: dict[str, object] = {}

    @staticmethod
    def _repo_git() -> str:
        url = _git("remote", "get-url", "origin")
        m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
        return m.group(1) if m else ""

    @staticmethod
    def _token_gh() -> str:
        try:
            r = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True,
            )
            return r.stdout.strip() if r.returncode == 0 else ""
        except OSError:
            return ""

    def _get(self, caminho: str) -> tuple[int, object]:
        if caminho in self._cache:
            return 200, self._cache[caminho]
        url = f"https://api.github.com/repos/{self.repo}/{caminho}"
        req = urllib.request.Request(url, headers={"User-Agent": "audit-docs"})
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                dados = json.load(resp)
            self._cache[caminho] = dados
            return 200, dados
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self._cache[caminho] = None
            return e.code, None
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            return 0, None

    def issue_existe(self, n: int) -> bool | None:
        """True/False; None = não deu para verificar (sem rede)."""
        codigo, _ = self._get(f"issues/{n}")
        return None if codigo == 0 else codigo == 200

    def issue_state(self, n: int) -> str | None:
        _, dados = self._get(f"issues/{n}")
        if not isinstance(dados, dict):
            return None
        return str(dados.get("state")) if "state" in dados else None

    def milestones(self) -> list[str] | None:
        _, dados = self._get("milestones?state=all&per_page=100")
        if not isinstance(dados, list):
            return None
        return [str(m.get("title", "")) for m in dados]


# ── leitura dos docs ─────────────────────────────────────────────────────────


def _separa_cercas(texto: str) -> tuple[str, list[str]]:
    """Devolve (prosa com cercas VIRADAS EM LINHA VAZIA, cercas).

    Virar a linha em vazia (em vez de removê-la) preserva a NUMERAÇÃO das
    linhas da prosa — a mensagem do linter tem de apontar a linha real.
    Dentro de cercas não há docs.
    """
    prosa: list[str] = []
    cercas: list[str] = []
    atual: list[str] | None = None
    for linha in texto.splitlines():
        if RE_CERCA.match(linha):
            if atual is None:
                atual = []
                prosa.append("")  # cerca de abertura também preserva a numeração
            else:
                cercas.append("\n".join(atual))
                atual = None
                prosa.append("")  # preserva a numeração das linhas
            continue
        if atual is None:
            prosa.append(linha)
        else:
            atual.append(linha)
            prosa.append("")  # conteúdo da cerca também ocupa linha na prosa
    if atual is not None:  # cerca sem fechar — o linter não conserta isso
        cercas.append("\n".join(atual))
    return "\n".join(prosa), cercas


def _doc_com_linhas(texto: str) -> list[tuple[int, str]]:
    """Linhas (1-indexadas) da PROSA — a linha da cerca não conta para achar."""
    return list(enumerate(texto.splitlines(), start=1))


def _onde(prosa: str, trecho: str) -> int:
    """Linha 1-indexada da primeira ocorrência (0 se sumiu na fusão)."""
    m = re.search(re.escape(trecho), prosa, re.M)
    return prosa[: m.start()].count("\n") + 1 if m else 0


def tracked_markdowns(raiz: Path) -> list[Path]:
    nomes = _git("-C", str(raiz), "ls-files", "*.md").splitlines()
    return sorted(raiz / n for n in nomes if n)


# ── verificações locais (sem rede) ───────────────────────────────────────────


def _e_caminho_candidato(token: str) -> bool:
    if not RE_CANDIDATO.match(token) or PLACEHOLDER.search(token):
        return False
    segmentos = token.rstrip("/").split("/")
    if len(segmentos) < 2:  # `defs/` solto não é promessa verificável
        return False
    extensao = segmentos[-1].rpartition(".")[2].lower()
    return bool(extensao in EXT_CONHECIDAS or segmentos[0] in PREFIXO_CONHECIDO)


def _caminho_existe(raiz: Path, token: str, rastreados: set[str], existiu) -> bool:
    """Raiz, índice, histórico, layout src/ ou abreviação de doc por número."""
    rel = token.rstrip("/")
    if (raiz / rel).exists() or rel in rastreados or existiu(rel):
        return True
    # módulos citados pelo caminho interno do pacote (`domain/params.py`)
    if (raiz / "src" / "gp100_architect" / rel).exists():
        return True
    # caminho relativo à pasta dos agentes (`.agents/README.md` cita `types/…`)
    if (raiz / ".agents" / rel).exists():
        return True
    # abreviação da casa: `reference/19` → `reference/19-*.md`
    if m := RE_ABREV_DOC.match(rel):
        return bool((raiz / m.group(1)).glob(f"{m.group(2)}-*.md"))
    return False


def verificar_caminhos(
    doc: Path, raiz: Path, prosa: str, rastreados: set[str],
    existiu,
) -> list[str]:
    """Caminho candidato citado tem de existir (presente, índice ou histórico)."""
    achados: list[str] = []
    for token in set(re.findall(r"`([^`\n]+)`", prosa)):
        if not _e_caminho_candidato(token):
            continue
        if subprocess.run(
            ["git", "-C", str(raiz), "check-ignore", "-q", token],
            capture_output=True,
        ).returncode == 0:
            continue  # derivado (dist/, patches/) — citar não é prometer
        if not _caminho_existe(raiz, token, rastreados, existiu):
            linha = _onde(prosa, token)
            achados.append(
                f"{doc.name}:{linha} · caminho `{token}` nunca existiu no repo "
                "(nem presente, nem histórico) — typo ou doc de arquitetura inexistente"
            )
    return achados


# ── 7 · contagens literais × derivação (ADR-0014) ────────────────────────────

RE_CONTAGEM = re.compile(
    r"\b(?P<num>\d{1,4})\s+"
    r"(?P<unidade>agentes|skills|patches|m[uú]sicas|[aá]lbuns|testes)\b",
    re.IGNORECASE,
)
RE_CONTAGEM_PRST = re.compile(r"\b(?P<num>\d{1,4})\s+(?:`?\.)?prst`?", re.IGNORECASE)

# Linha com estes sinais NÃO reivindica o total atual: fala de subconjunto
# (golden set, "skills de efeito"), de registro histórico (auditoria antiga,
# época da migração) ou cita a divergência para corrigi-la.
CONTEXTO_NAO_TOTAL = re.compile(
    r"can[oô]nic|golden|de efeito|na auditoria|desatualizada|v\d\.\d"
    r"|conclu[ií]|encerrad|entregue|[éd]poca|extint"
    # metas e horizontes (futuro, não presente): "≥ 100 patches", "meta de 10"
    r"|meta|horizonte|≥|extra[íi]d"
    # citação de artefato antigo: "analyze_prst.py fala em '62 patches'"
    r"|fala em"
    # tag XML inline (protocolo técnico, não total): "1 patch… com <ppIRInfo>"
    r"|<[a-z]+"
    # contagens POR ÁLBUM (subconjunto): "Pulse (24 músicas / 38 patches)"
    r"|pulse|wishkah|supernatural|abbey|apostrophe|experienced|cheap thrills"
    r"|smooth|santana",
    re.IGNORECASE,
)

UNIDADE_CHAVE = {
    "agentes": "agentes",
    "skills": "skills",
    "patches": "patches",
    "prst": "patches",
    "músicas": "musicas",
    "musicas": "musicas",
    "álbuns": "albuns",
    "albuns": "albuns",
    "testes": "testes",
}


def _contagens_derivadas(raiz: Path) -> dict | None:
    """A fonte única (ADR-0014) — None se o pacote/defs não carregar (degrada).

    `badges.py` é 100% stdlib e a cadeia do loader também: o checkout entra no
    `sys.path` e a derivação roda no python do linter, sem instalar nada —
    mesmo runtime do CI (job Agentes) e da máquina local.
    """
    try:
        sys.path.insert(0, str(raiz / "src"))
        from gp100_architect.application.badges import dados_derivados
        from gp100_architect.infrastructure.defs import carregar_e_validar

        return dados_derivados(carregar_e_validar(), raiz=raiz)
    except Exception:  # noqa: BLE001 — degradar é o contrato (o CI nunca deve falhar aqui)
        return None


def verificar_contagens(doc: Path, prosa: str, derivacao: dict) -> list[str]:
    """Contagem literal citada tem de bater com a derivação (ADR-0014).

    Dispara só em dígitos + unidade conhecida, na linha SEM sinal de
    subconjunto/registro histórico (o golden set pode dizer "43 patches" —
    fala do recorte, não da biblioteca). O valor verdadeiro é o derivado;
    prosa divergente é erro nosso, não da fonte.
    """
    achados: list[str] = []
    for numero_linha, linha in enumerate(prosa.splitlines(), 1):
        if CONTEXTO_NAO_TOTAL.search(linha):
            continue
        for padrao in (RE_CONTAGEM, RE_CONTAGEM_PRST):
            for m in padrao.finditer(linha):
                unidade = (
                    m.group("unidade") if "unidade" in (m.groupdict().keys()) else "prst"
                )
                chave = UNIDADE_CHAVE.get(unidade.lower())
                esperado = derivacao.get(chave) if chave else None
                if esperado is None or str(m.group("num")) == str(esperado):
                    continue
                achados.append(
                    f'{doc.name}:{numero_linha} · "{m.group("num")} {unidade}" '
                    f"diverge da derivação ({chave}={esperado}) — rode o pipeline ou "
                    "corrija a prosa; contagem pública é derivada (ADR-0014)"
                )
    return achados


def verificar_links(
    doc: Path, raiz: Path, prosa: str
) -> tuple[list[str], list[str]]:
    """Link relativo de Markdown resolve (âncora errada é só aviso)."""
    violas: list[str] = []
    avisos: list[str] = []
    for alvo in set(RE_LINK.findall(prosa)):
        if alvo.startswith(("http:", "https:", "mailto:", "#")):
            continue
        # links internos do GitHub (`../../issues/42`, `../blob/main/…`)
        # resolvem NA PLATAFORMA — não são caminho do working tree
        if re.match(r"^(?:\.\./)+(?:issues|pull|blob|tree|releases)/", alvo):
            continue
        caminho, _, ancora = alvo.partition("#")
        destino = (doc.parent / caminho).resolve()
        if not destino.exists():
            linha = _onde(prosa, f"]({alvo})")
            violas.append(
                f"{doc.name}:{linha} · link `({alvo})` não resolve — "
                f"esperado {destino.relative_to(raiz) if destino.is_relative_to(raiz) else destino}"
            )
        elif ancora and destino.suffix == ".md":
            titulos = {slug(t) for t in _titulos(destino)}
            if titulos and slug(ancora) not in titulos:
                linha = _onde(prosa, f"]({alvo})")
                avisos.append(
                    f"{doc.name}:{linha} · âncora `#{ancora}` não casa "
                    f"com título algum de `{caminho}` (o arquivo existe)"
                )
    return violas, avisos


def _titulos(doc: Path) -> list[str]:
    try:
        return re.findall(r"^#{1,6}\s+(.+)$", doc.read_text(encoding="utf-8"), re.M)
    except OSError:
        return []


def slug(titulo: str) -> str:
    """Slug GitHub: minúsculas, espaço→'-', pontuação fora (mantém acento)."""
    t = titulo.strip().lower().replace("`", "").replace("*", "")
    return "".join(c if c.isalnum() or c in "-_" else ("-" if c.isspace() else "") for c in t)


# ── verificação de comandos (blocos de doc) ──────────────────────────────────


def _segmentos(cerca: str) -> list[str]:
    """Comandos executáveis de uma cerca, com continuações e encadeamentos."""
    linhas = cerca.replace("\\\n", " ").splitlines()
    fora: list[str] = []
    for linha in linhas:
        if linha.strip().startswith(("#", "$")) or not linha.strip():
            continue
        if not RE_CONT.match(linha.strip()):
            continue
        for parte in re.split(r"\s*(?:;|&&|\|\|)\s*", linha):
            fora.append(parte.strip())
    return fora


def verificar_comandos(cercas: list[str], rodar: bool) -> list[str]:
    """`gh <sub…>` e `gp100 <cmd>`: o caminho de subcomando tem de existir."""
    if not rodar:
        return []
    falhas: list[str] = []
    for cerca in cercas:
        for seg in _segmentos(cerca):
            tokens = seg.split()
            while tokens and re.match(r"^[A-Z_]+=.*", tokens[0]):
                tokens = tokens[1:]
            if not tokens:
                continue
            if tokens[0] == "gh" and len(tokens) > 1 and not tokens[1].startswith("-"):
                alvo, profundidade = tokens[1:3], 0
                for t in alvo:
                    if t.startswith("-"):
                        break
                    profundidade += 1
                caminho = ["gh", *alvo[:profundidade], "--help"]
                if _ajuda(caminho) is False:
                    falhas.append(f"gh {' '.join(alvo[:profundidade])} — subcomando inexistente")
            elif tokens[0] == "gp100" and len(tokens) > 1 and not tokens[1].startswith("-"):
                if RE_GRUPO_SLASH.search(tokens[1]):
                    continue  # grupo histórico (`find/show/diff`) — não é um comando
                saida = _ajuda(["uv", "run", "gp100", "--help"])
                if saida and tokens[1] not in saida:
                    falhas.append(f"gp100 {tokens[1]} — comando inexistente no CLI")
            elif tokens[:3] == ["uv", "run", "gp100"] and len(tokens) > 3 and not tokens[3].startswith("-"):
                # flags (--version, --json…) não são validadas: o help rich
                # quebra linha conforme a largura e o matching vira frágil
                saida = _ajuda(["uv", "run", "gp100", "--help"])
                if saida and tokens[3] not in saida:
                    falhas.append(f"gp100 {tokens[3]} — comando inexistente no CLI")
    return falhas


def _ajuda(argv: list[str]) -> str | False:
    """Saída de `--help` (cacheada); False = comando falhou; "" = sem binário."""
    chave = " ".join(argv)
    if chave in _AJUDA_CACHE:
        return _AJUDA_CACHE[chave]
    try:
        r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        _AJUDA_CACHE[chave] = ""
        return ""
    _AJUDA_CACHE[chave] = r.stdout if r.returncode == 0 else False
    return _AJUDA_CACHE[chave]


_AJUDA_CACHE: dict[str, str | False] = {}


# ── verificações remotas ─────────────────────────────────────────────────────


def verificar_issues(
    doc: Path, prosa: str, api: Api, violas: list[str], avisos: list[str],
) -> None:
    if not api.ok:
        avisos.append(f"{doc.name} · verificação remota de #N ignorada (sem rede/token)")
        return
    for m in RE_CITACAO.finditer(prosa):
        n = int(m.group(1))
        existe = api.issue_existe(n)
        if existe is False:
            violas.append(
                f"{doc.name}:{_onde(prosa, m.group(0))} · `#{n}` citado e NÃO existe "
                "no repositório — número errado ou referência podre"
            )
        elif existe is None:
            avisos.append(f"{doc.name} · `#{n}` não verificado (API indisponível)")
    for padrao, extra in ((RE_FAIXA, True), (RE_ESTADO, False)):
        for m in padrao.finditer(prosa):
            a, b = int(m.group(1)), int(m.group(2)) if extra else int(m.group(1))
            estado = ESTADOS[m.group(3 if extra else 2).lower()]
            if b - a > 20:
                continue
            for n in range(a, b + 1):
                real = api.issue_state(n)
                if real is None:
                    continue
                if real != estado:
                    violas.append(
                        f"{doc.name}:{_onde(prosa, m.group(0))} · `#{n}` dito "
                        f"`{estado}` mas está `{real}` na realidade"
                    )


def verificar_milestones(doc: Path, prosa: str, api: Api,
                         violas: list[str], avisos: list[str]) -> None:
    reais = api.milestones() if api.ok else None
    if reais is None:
        if RE_MILESTONE.search(prosa):
            avisos.append(f"{doc.name} · milestones não verificados (sem rede/token)")
        return
    for m in RE_MILESTONE.finditer(prosa):
        citado = m.group(1).strip().rstrip(".")
        if not re.match(r"^v\d", citado):
            continue
        nomes = {t.split(" — ")[0]: t for t in reais}
        if citado not in nomes and citado not in reais:
            violas.append(
                f"{doc.name}:{_onde(prosa, m.group(0))} · milestone `{citado}` "
                f"não existe — reais: {', '.join(sorted(nomes))}"
            )


# ── main ─────────────────────────────────────────────────────────────────────


def _clone_raso(raiz: Path) -> bool:
    """Clone sem histórico (CI costuma usar fetch-depth 1): `git log` não vê
    o passado, e citação de caminho histórico viraria violação falsa."""
    return _git("-C", str(raiz), "rev-parse", "--is-shallow-repository") == "true"


def main() -> int:
    raiz = Path(_git("rev-parse", "--show-toplevel") or ".").resolve()
    api = Api()
    rastreados = set(_git("ls-files").splitlines())
    raso = _clone_raso(raiz)
    historico: dict[str, bool] = {}

    def existiu(caminho: str) -> bool:
        if caminho not in historico:
            # --full-history: SEM ele, o git simplifica a travessia pelo
            # primeiro parent — no merge de release (a develop inteira
            # entrando na main de uma vez), commits da develop que
            # adicionaram/removeram um caminho ficam INVISÍVEIS e a citação
            # histórica legítima vira violação falsa (foi o que travou o
            # PR de release #107).
            historico[caminho] = bool(
                _git("log", "--oneline", "-1", "--full-history", "--", caminho)
            )
        return historico[caminho]

    violas: list[str] = []
    avisos: list[str] = []
    derivacao = _contagens_derivadas(raiz)
    if derivacao is None:
        avisos.append(
            "contagens: derivação indisponível (pacote/defs não carregou) — "
            "verificação de contagens degradada a aviso (ADR-0014)"
        )
    docs = tracked_markdowns(raiz)
    for doc in docs:
        rel = str(doc.relative_to(raiz)).replace("\\", "/")
        if rel.startswith(SURFACAS_FORA):
            continue  # skills de terceiros citam o ecossistema delas
        exceto = EXCETO.get(rel, set())
        texto = doc.read_text(encoding="utf-8", errors="replace")
        prosa, cercas = _separa_cercas(texto)

        if "estado" not in exceto and "issue" not in exceto:
            verificar_issues(doc, prosa, api, violas, avisos)
        if "milestone" not in exceto:
            verificar_milestones(doc, prosa, api, violas, avisos)
        if "contagens" not in exceto and derivacao is not None:
            violas.extend(verificar_contagens(doc, prosa, derivacao))
        if "caminho" not in exceto:
            if raso:
                avisos.append(
                    f"{doc.name} · verificação de caminhos degradada a aviso "
                    "(clone raso não vê o histórico — configure fetch-depth: 0)"
                )
            else:
                violas_caminho = verificar_caminhos(doc, raiz, prosa, rastreados, existiu)
                violas.extend(violas_caminho)
        violas_link, avisos_link = verificar_links(doc, raiz, prosa)
        violas.extend(violas_link)
        avisos.extend(avisos_link)
        for falha in verificar_comandos(cercas, rodar=True):
            violas.append(f"{rel} · {falha}")

    for a in avisos:
        print(f"  ⚠️  {a}")
    if violas:
        for v in violas:
            print(f"  ❌ {v}")
        print(f"\n❌ consistência dos docs: {len(violas)} violação(ões) em {len(docs)} docs")
        return 1
    print(
        f"✅ {len(docs)} docs consistentes — issues, caminhos, links, "
        f"milestones, contagens e comandos conferem"
        + (f" ({len(avisos)} aviso(s))" if avisos else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
