# Implementation Plan: Modernização do linear-workflow com Ciclo de Draft PRs e Sync de Boards

**Branch**: `feat/FAL-58-modernizar-linear-workflow-draft-prs` | **Date**: 2026-10-29 | **Spec**: [spec.md](specs/054-linear-draft-prs-lifecycle/spec.md) | **Linear Issue**: [FAL-58](https://linear.app/fallkey/issue/FAL-58/featworkflow-modernizar-linear-workflow-com-ciclo-draft-prs-e)

**Input**: Feature specification from `specs/054-linear-draft-prs-lifecycle/spec.md`

---

## Summary

Modernizar integralmente a skill `linear-workflow` e padronizar o ciclo de vida do Spec Kit (`github/spec-kit`) no ecossistema `fk_apm`. A nova arquitetura implementa o ciclo de *Living Specs* via GitHub Draft PRs abertos imediatamente na fase de especificação (`/speckit-specify`), acoplados a uma esteira rigorosa de 6 estados no Linear (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`), isolamento de execução por Git Worktrees efêmeros acionados via argumento obrigatório `<CARD-ID>`, subcomandos de sincronização de quadros (`sync-boards` e `setup-board`) em `linear_api.py`, e expurgo completo de referências legadas.

---

## Technical Context

**Language/Version**: Python 3.8+ (Standard Library: `urllib.request`, `json`, `subprocess`, `pathlib`, `re`, `unittest`)  
**Primary Dependencies**: Zero dependências externas de runtime (padrão arquitetural `fk_apm`). GitHub CLI (`gh`) e Git local para operações de versionamento e PRs.  
**Storage**: N/A (Linear GraphQL API como fonte de verdade remota; arquivos Markdown locais em `specs/<feature>/`).  
**Testing**: Python `unittest` (`python -m unittest skills/linear-workflow/tests/test_linear_api.py`).  
**Target Platform**: Multi-plataforma (Windows PowerShell e POSIX/Linux/macOS) compatível com Google Antigravity, Claude Code, Cursor, Copilot e OpenCode.  
**Project Type**: Tooling CLI / Package de Skills & Prompts de IA.  
**Performance Goals**: Tempo de execução de subcomandos de inspeção/sincronização < 3 segundos.  
**Constraints**: Zero mutação automatizada para o estado `Done`; zero quebra de escape de shell via payloads de arquivo UTF-8 obrigatórios; execução determinística em worktree efêmero.  
**Scale/Scope**: Múltiplos times e projetos no Linear; 10 comandos de ciclo de vida do Spec Kit.

---

## Constitution Check

*GATE: Checked against `.specify/memory/constitution.md`*

| Princípio Constitucional | Status | Justificativa / Validação |
| :--- | :---: | :--- |
| **I. Multi-Harness Parity & Bundled Distribution** | ✅ PASS | Todos os scripts operam com a biblioteca padrão do Python 3.8+ e os templates de prompt são distribuídos para todos os 5 harnesses suportados. |
| **II. Spec-Driven Linear Lifecycle (Official `github/spec-kit`)** | ✅ PASS | O fluxo implementa a esteira canônica de 6 estágios (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`), com bloqueio estrito de transição automatizada para `Done`. |
| **III. Zero Shell-Escaping Corruption (File-First Payloads)** | ✅ PASS | Uso exclusivo de `--description-file` e `--comment-file` associados a `sanitize_markdown_payload`. Proibição total de markdown inline em argumentos. |
| **IV. Deterministic Verification & Test Coverage** | ✅ PASS | 100% de cobertura dos novos subcomandos e estados através de testes unitários automatizados em `test_linear_api.py`. |
| **V. Semantic Versioning & Keep a Changelog** | ✅ PASS | Atualização mapeada para `## [Unreleased]` no `CHANGELOG.md` no padrão Conventional Commits. |

---

## 1. Diagnóstico e Contexto

### Estado Atual e Gaps Identificados
1. **Ausência de Versionamento Inicial de Specs**: Anteriormente, a branch Gitflow e o Pull Request só eram gerados tardiamente durante a implementação (`/speckit-implement`), deixando especificações e análises técnicas isoladas localmente na máquina do desenvolvedor sem visibilidade da equipe (*dark specs*).
2. **Discrepância na Esteira do Linear**: Os times do Linear utilizavam a coluna legada `Technical Analysis` com posicionamento fracionário (`0.5`) e indefinição de responsabilidade entre planejamento e tarefas executáveis, sem uma coluna explícita para `Planned`.
3. **Acoplamento do Workspace Local**: Comandos executados em paralelo ou sobre outros cards forçavam chaveamentos de branch ou poluição do workspace ativo do desenvolvedor, gerando risco de commits em branches erradas.
4. **Resquícios de Terminologia Legada**: Permaneciam referências a comandos obsoletos do pipeline legado (`/fk-*`) na documentação e prompts da skill.

---

## 2. Arquitetura da Solução & Desenho Técnico

### Visão Geral da Arquitetura
A modernização estrutura-se em 4 pilares coesos:

```
[Developer / Agent]
        │
        ├── 1. /speckit-specify ─────────► Git Branch + GitHub Draft PR + Linear Card (Backlog)
        │
        ├── 2. /speckit-plan <CARD-ID> ──► Ephemeral Worktree ─► plan.md ─► Linear (Planned)
        │
        ├── 3. /speckit-tasks <CARD-ID> ─► Ephemeral Worktree ─► tasks.md ─► Linear (Todo)
        │
        ├── 4. /speckit-implement ───────► Ephemeral Worktree ─► Code/Tests ─► gh pr ready ─► Linear (In Review)
        │
        ├── 5. /speckit-converge ────────► Ephemeral Worktree ─► Fixes/Push ─► Linear (In Review)
        │
        └── 6. sync-boards / setup-board ► Linear GraphQL API ─► Reconciliação Idempotente de Estados
```

### Detalhamento dos Componentes

1. **Ciclo de Living Specs com Draft PRs**:
   - `/speckit-specify` cria a branch `feat/<issue-id>-<slug>`, realiza commit inicial de `spec.md`, envia ao remote com `git push -u origin <branch>` e dispara `gh pr create --draft`. A URL gerada é gravada no corpo do card do Linear em `Backlog`.
   - `/speckit-plan`, `/speckit-tasks` e `/speckit-converge` versionam seus artefatos progressivamente na mesma branch com Conventional Commits (`docs(plan): ...`, `docs(tasks): ...`).
2. **Máquina de Estados Padronizada (6 Estágios)**:
   - `Backlog` (tipo `backlog`, cor `#BEC2C8`, pos `0.0`): Concepção inicial.
   - `Planned` (tipo `unstarted`, cor `#F2C94C`, pos `1.0`): Arquitetura e análise de impacto concluídas.
   - `Todo` (tipo `unstarted`, cor `#4EA7FC`, pos `2.0`): Checklist de tarefas decomposto e validado.
   - `In Progress` (tipo `started`, cor `#F2994A`, pos `3.0`): Execução autônoma de código/testes ou aplicação de review fixes.
   - `In Review` (tipo `started`, cor `#BB87FC`, pos `4.0`): Pull Request pronto para revisão da equipe.
   - `Done` (tipo `completed`, cor `#56D364`, pos `5.0`): Exclusivamente manual por humano após merge.
   - `Canceled` (tipo `canceled`, cor `#828282`, pos `6.0`): Cancelamento de demanda.
3. **Mecanismo de Sincronização de Boards (`sync-boards` & `setup-board`)**:
   - Em `linear_api.py`, queries GraphQL recuperam todos os times e seus estados.
   - `sync-boards` detecta o estado legado `Technical Analysis` e aplica mutação `workflowStateUpdate` para renomeá-lo para `Planned`, preservando o histórico de todos os cards existentes.
   - Suporte completo a `--dry-run` para auditoria sem efeitos colaterais.
4. **Isolamento via Git Worktree Efêmero**:
   - Argumento obrigatório `<CARD-ID>` em todos os comandos pós-especificação. Se omitido, aborta imediatamente com instrução clara.
   - Se o workspace atual não estiver na branch do card, cria `.worktrees/<CARD-ID>`, executa a operação, sincroniza com o remote e executa `git worktree remove --force` e `git worktree prune`.
5. **Limpeza e Governança**:
   - Expurgar referências a `/fk-*` de todas as instruções, prompts, templates e referências do repositório.

---

## 3. Checklist de Arquivos Impactados

- [ ] `skills/linear-workflow/scripts/linear_api.py` (modificar: implementar subcomandos sync-boards e setup-board, bloqueio de Done e suporte ao estado Planned)
- [ ] `skills/linear-workflow/tests/test_linear_api.py` (modificar: novos casos de teste unitário cobrindo sync-boards, setup-board, bloqueio de Done e Planned)
- [ ] `skills/linear-workflow/SKILL.md` (modificar: documentação da esteira de 6 estágios, ciclo draft prs e expurgo de referências legadas)
- [ ] `skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md` (modificar: atualizar regras de transição e comando parametrizado)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md` (modificar: criação da branch e Draft PR no specify)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-clarify.prompt.md` (modificar: argumento obrigatório de card e commits no Draft PR)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md` (modificar: argumento obrigatório de card e transição para Planned)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md` (modificar: argumento obrigatório de card e transição para Todo)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-implement.prompt.md` (modificar: argumento de card, promoção gh pr ready e avanço para In Review)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-converge.prompt.md` (modificar: argumento de card e ciclo In Review -> In Progress -> In Review)
- [ ] `skills/linear-workflow/references/states-and-labels.md` (modificar: tabela dos 6 estados oficiais e cores)
- [ ] `skills/linear-workflow/references/multi-harness-commands.md` (modificar: sintaxe de comandos parametrizados)
- [ ] `specs/054-linear-draft-prs-lifecycle/research.md` (criar: artefato de pesquisa Fase 0)
- [ ] `specs/054-linear-draft-prs-lifecycle/data-model.md` (criar: modelo de dados e máquina de estados Fase 1)
- [ ] `specs/054-linear-draft-prs-lifecycle/contracts/linear_api_cli.md` (criar: contratos de interface CLI Fase 1)
- [ ] `specs/054-linear-draft-prs-lifecycle/quickstart.md` (criar: guia de validação executável Fase 1)
- [ ] `.specify/memory/constitution.md` (modificar: ratificar o ciclo de Living Specs e máquina de estados)

---

## 4. Estratégia de Testes

### 4.1 Testes Unitários (`unittest`)
- `test_sync_boards_dry_run`: Testa o subcomando `sync-boards` com `--dry-run`, simulando respostas GraphQL e conferindo o payload de ações propostas.
- `test_sync_boards_rename_legacy`: Testa a migração de `Technical Analysis` para `Planned`.
- `test_setup_board_idempotency`: Testa a criação idempotente de estados em times novos.
- `test_block_done_transition`: Testa a rejeição categórica de chamadas `update-issue` solicitando `--state "Done"`.
- `test_planned_state_transition`: Testa o avanço de cards para `Planned` com payload sanitizado.
- `test_validate_plan_with_planned`: Testa que `validate-plan` valida corretamente as 5 seções do plano de arquitetura.

### 4.2 Testes de Integração e Verificação Estática
- Execução completa da suíte: `python -m unittest skills/linear-workflow/tests/test_linear_api.py`.
- Validação estática dos artefatos: `python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-58`.
- Inspeção real no Linear: `python skills/linear-workflow/scripts/linear_api.py sync-boards --dry-run`.

---

## 5. Plano Gitflow

- **Branch de Trabalho**: `feat/FAL-58-modernizar-linear-workflow-draft-prs`
- **Branch Base**: `develop`
- **Pull Request Associado**: [#20 — feat(FAL-58): modernizar linear-workflow com ciclo draft prs e sincronizacao de boards](https://github.com/CaioCoelhoChaves/fk_apm/pull/20) (Draft)
- **Commits Convencionais**:
  - `docs(spec): add specification for FAL-58`
  - `docs(plan): add implementation plan and phase 1 design artifacts for FAL-58`
  - `feat(workflow): implement sync-boards and setup-board in linear_api.py`
  - `test(workflow): add unit tests for sync-boards, setup-board and state transitions`
  - `docs(skills): update prompts, instructions and expunge legacy fk-* references`
- **Rito de Finalização**: Promoção do PR Draft para pronto via `gh pr ready 20`, revisão humana e merge em `develop`. Transição manual para `Done` no Linear.
