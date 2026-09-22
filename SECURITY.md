# Política de Segurança

## Versões suportadas

Este projeto é um **pipeline de geração de dados + uma biblioteca de patches**,
distribuído pela branch `main` e por Releases tagueadas. Não há branch de
manutenção: apenas a versão mais recente recebe correções.

| Versão | Suporte |
|---|---|
| `1.x` (`main` e última Release) | ✅ corrigida ativamente |
| Anteriores | ❌ sem suporte — atualize |

## Como reportar uma vulnerabilidade

**Não abra issue pública para vulnerabilidades.** Use um dos canais privados:

1. **GitHub Security Advisories** — aba
   [`Security` → `Report a vulnerability`](https://github.com/lucascantarelli/gp-100-patch-architect/security/advisories/new)
   (canal preferencial: mantém o relatório, o patch e o aviso no mesmo lugar).
2. **E-mail** — `lucascantarelli@users.noreply.github.com` com o assunto
   `[SECURITY] gp-100-patch-architect`.

Inclua, quando possível:

- Descrição do problema e impacto concreto
- Passos mínimos para reproduzir (comando, arquivo de entrada, versão)
- Versão afetada (`VERSION` ou tag da Release)
- Sistema operacional e versão do Python/Node
- Sugestão de correção, se você tiver uma

### Prazo de resposta

| Etapa | Prazo-alvo |
|---|---|
| Confirmação de recebimento | 72 horas |
| Avaliação inicial (severidade e escopo) | 7 dias |
| Correção ou plano de mitigação | 30 dias |
| Divulgação coordenada | após a correção, com crédito a quem reportar (se desejado) |

Pedimos que você aguarde a correção antes de qualquer divulgação pública.
Damos crédito pelo achado nas Release Notes, salvo se você preferir anonimato.

## Escopo — o que conta como vulnerabilidade aqui

Este repositório é, em boa parte, **dados e documentação**. O que é tratado
como questão de segurança:

| Dentro do escopo | Por quê |
|---|---|
| Execução de código arbitrário nos scripts de `tools/` | Entrada hostil em `patches-defs.json`, caminhos de arquivo ou WAVs malformados |
| Traversal de caminho / escrita fora do repositório | Nomes de pasta/patch vindos dos defs são usados para montar caminhos |
| XML/`Entity Expansion` nos `.prst` | Os geradores leem e escrevem XML; XXE ou billion-laughs em entrada de terceiros |
| Escrita automatizada no branch principal | Nenhum workflow declara `contents: write` para empurrar em branch; um PR que introduza um job capaz de commitar no `main` é um achado válido |
| Segredos expostos no histórico ou nos logs | Tokens, credenciais ou chaves em qualquer arquivo versionado |
| Cadeia de suprimentos das GitHub Actions | Actions não fixadas por SHA ou workflow com permissões largas demais |
| Runner ou runtime de Action obsoleto | Runner em label mutável (`-latest`) troca de imagem sem commit aqui, e Action que ainda declara Node 20 recebe aviso de depreciação a cada job |
| Injeção em workflows (`${{ }}` de contexto não confiável) | Título de issue/PR, nome de branch ou de arquivo interpolado em `run:` |

## Fora do escopo

Não são tratados como vulnerabilidades de segurança deste projeto:

- **Acurácia sonora dos patches.** "O timbre não ficou igual ao disco" é
  discussão de conteúdo — abra uma issue comum ou um PR com a correção.
- **Compatibilidade com o hardware.** Divergência entre a documentação e o
  comportamento real da GP-100 em um firmware específico é issue, não CVE.
- **Licenciamento de conteúdo de terceiros** (marcas, títulos de música, packs
  de IR, manual da Valeton) — ver o [`NOTICE.md`](NOTICE.md).
  Correções de atribuição são bem-vindas como PR.
- **Packs de IR que você baixou.** Este repositório não distribui IRs de
  terceiros; a origem e a licença de cada pack são responsabilidade de quem
  baixa. Veja [`impulse_responses/README.md`](impulse_responses/README.md).

## Controles já habilitados no repositório

| Controle | Estado |
|---|---|
| Secret scanning + push protection | ✅ habilitados |
| Dependabot (alertas + security updates) | ✅ habilitado |
| CodeQL (SAST) | ✅ via [`security.yml`](.github/workflows/security.yml) |
| Revisão de dependências em PR | ✅ via [`security.yml`](.github/workflows/security.yml) |
| Aferição de permissões dos workflows | ✅ via [`security.yml`](.github/workflows/security.yml) |
| Runner fixo (`ubuntu-24.04`) e Actions em runtime suportado | ✅ via [`audit_workflows.py`](.github/scripts/audit_workflows.py), que **reprova** label de runner mutável e Action de primeira parte abaixo do `node24` |
| Verificação de integridade dos dados em cada push/PR | ✅ via [`ci.yml`](.github/workflows/ci.yml) |
| Branch protection em `main` e `develop` (PR + check obrigatórios, sem exceção de bypass) | ✅ aplicar com [`setup_repo.sh`](setup_repo.sh) |

## Boas práticas para quem contribui

- Nunca comite credenciais, tokens ou `.env` — o push protection bloqueia os
  padrões conhecidos, mas ele não é a sua única linha de defesa.
- Não embuta binários de terceiros (WAVs de packs pagos, PDFs de fabricante)
  no repositório: eles são obtidos localmente e ficam no `.gitignore`.
- Rode a suíte antes de abrir PR: `python -m unittest discover -s tests -v`.
- Ao usar o agente para editar arquivos, revise o diff — o pipeline é
  reprodutível (só `preset_info/@time` varia) e o guarda de frescor reprova
  artefato gerado fora do commit, mas quem decide o que entra é a sua revisão.
