# Tasks: Criação de Cards Manuais no Linear com comando fk-new-manual-issue

**Input**: Design documents from `specs/055-manual-linear-cards/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)  
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `data-model.md`, `contracts/`, `research.md`  
**Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)  
**Pull Request (Draft)**: [#21 — feat(skills): add fk-new-manual-issue command for manual linear cards](https://github.com/CaioCoelhoChaves/fk_apm/pull/21)  
**Branch**: `feat/FAL-59-fk-new-manual-issue`

---

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and command parsing structure

- [X] T001 Verify and prepare test harness execution environment for linear_api in skills/linear-workflow/tests/test_linear_api.py
- [X] T002 [P] Configure arguments and subparser skeleton for create-manual-issues in skills/linear-workflow/scripts/linear_api.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and helpers that MUST be complete before ANY user story can be implemented

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implement helper to resolve or create manual label with team scoping in skills/linear-workflow/scripts/linear_api.py
- [X] T004 Implement helper to resolve Backlog state identifier and ensure state enforcement in skills/linear-workflow/scripts/linear_api.py
- [X] T005 [P] Implement payload sanitization wrapper using sanitize_markdown_payload for manual issue descriptions in skills/linear-workflow/scripts/linear_api.py

**Checkpoint**: Core helpers ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Criação de Card Manual Individual via Comando (Priority: P1) 🎯 MVP

**Goal**: Permitir a criação de um único card manual no Linear com título e descrição estruturada, garantindo estado `Backlog`, tag `manual` e associação ao projeto/time ativo.

**Independent Test**: Invocar `python skills/linear-workflow/scripts/linear_api.py create-manual-issues --title "..." --description "..."` e validar o retorno JSON com `success: true`, `state: "Backlog"` e `labels: ["manual"]`.

### Tests for User Story 1 ⚠️

- [X] T006 [P] [US1] Add unit test test_create_manual_issues_single in skills/linear-workflow/tests/test_linear_api.py
- [X] T007 [P] [US1] Add unit test test_create_manual_issues_ensures_backlog_state in skills/linear-workflow/tests/test_linear_api.py
- [X] T008 [P] [US1] Add unit test test_create_manual_issues_ensures_manual_label in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 1

- [X] T009 [US1] Implement single issue creation handler in cmd_create_manual_issues in skills/linear-workflow/scripts/linear_api.py
- [X] T010 [US1] Support file-first description reading via --description-file in skills/linear-workflow/scripts/linear_api.py

**Checkpoint**: User Story 1 is functional and testable independently (MVP ready)

---

## Phase 4: User Story 2 - Criação em Lote de Múltiplos Cards Manuais (Priority: P1)

**Goal**: Permitir o cadastro atômico e sequencial de múltiplos cards operacionais a partir de arquivo JSON estruturado (`--batch-file`), retornando lista consolidada com identificadores gerados.

**Independent Test**: Criar arquivo temporário JSON com 2 ou mais issues e invocar `python skills/linear-workflow/scripts/linear_api.py create-manual-issues --batch-file ".tmp-test.json"`, verificando retorno com `count` igual ao número de itens e todos criados em `Backlog` com tag `manual`.

### Tests for User Story 2 ⚠️

- [X] T011 [P] [US2] Add unit test test_create_manual_issues_batch in skills/linear-workflow/tests/test_linear_api.py
- [X] T012 [P] [US2] Add unit test test_create_manual_issues_missing_team_or_auth in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 2

- [X] T013 [US2] Implement batch payload parsing and schema validation for --batch-file in skills/linear-workflow/scripts/linear_api.py
- [X] T014 [US2] Implement sequential batch issue creation with consolidated JSON response in skills/linear-workflow/scripts/linear_api.py

**Checkpoint**: User Story 2 is functional and supports batch creation reliably

---

## Phase 5: User Story 3 - Consent Gate Interativo com Pré-Visualização Antes da Criação (Priority: P2)

**Goal**: Disponibilizar o prompt e as declarações de skill do comando `/fk-new-manual-issue` implementando o 3-Stage Consent Gate (Pre-Render Gate tabular, confirmação interativa e execução atômica via arquivo UTF-8).

**Independent Test**: Executar o comando `/fk-new-manual-issue` em um dos harnesses suportados e validar a exibição da tabela de pré-visualização, a confirmação pelo usuário antes de qualquer mutação remota e a limpeza dos arquivos temporários.

### Implementation for User Story 3

- [X] T015 [P] [US3] Create prompt definition for fk-new-manual-issue in skills/linear-workflow/.apm/prompts/fk-new-manual-issue.prompt.md
- [X] T016 [P] [US3] Create skill declaration for fk-new-manual-issue in skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md
- [X] T017 [P] [US3] Install skill declaration into workspace in .agents/skills/fk-new-manual-issue/SKILL.md

**Checkpoint**: User Story 3 enables interactive command execution across supported harnesses

---

## Phase 6: User Story 4 - Isolamento Operacional Sem Gatilho de Pipeline de Código (Priority: P2)

**Goal**: Garantir que as diretrizes do comando `/fk-new-manual-issue` imponham isolamento absoluto de código (zero branches Git, zero worktrees, zero PRs) e registrar o comando na documentação oficial do `linear-workflow`.

**Independent Test**: Validar que após a execução do comando a árvore Git permanece inalterada (`git status` limpo) e que o comando consta nas tabelas de referência multi-harness.

### Implementation for User Story 4

- [X] T018 [US4] Enforce zero git mutations constraint and update command documentation in skills/linear-workflow/SKILL.md
- [X] T019 [P] [US4] Register /fk-new-manual-issue command in skills/linear-workflow/references/multi-harness-commands.md

**Checkpoint**: User Story 4 ensures governance constraints and full documentation coverage

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Quality verification, regression testing, and changelog tracking

- [X] T020 [P] Execute full test suite in skills/linear-workflow/tests/test_linear_api.py
- [X] T021 Validate end-to-end quickstart scenarios in specs/055-manual-linear-cards/quickstart.md
- [X] T022 Update CHANGELOG.md with Keep a Changelog entry under Unreleased

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências - inicia imediatamente.
- **Foundational (Phase 2)**: Depende do Setup - BLOQUEIA todas as user stories.
- **User Story 1 (Phase 3)**: Depende da Fase Foundational. É o núcleo do MVP.
- **User Story 2 (Phase 4)**: Depende da Fase Foundational e reutiliza a lógica de criação individual de US1.
- **User Story 3 (Phase 5)**: Depende de US1 e US2 (necessita do subcomando CLI funcional).
- **User Story 4 (Phase 6)**: Pode rodar em paralelo ou após US3 para documentação e salvaguardas de isolamento Git.
- **Polish (Phase 7)**: Depende da conclusão de todas as histórias.

### User Story Dependencies

- **US1 (P1)**: Inicia após a Fase 2 (Foundational). Não depende de outras histórias.
- **US2 (P1)**: Inicia após US1 para reutilizar o fluxo de mutação de issues.
- **US3 (P2)**: Constrói a interface de prompt e skill sobre a CLI desenvolvida em US1/US2.
- **US4 (P2)**: Validação de isolamento e documentação final do comando.

---

## Parallel Opportunities

- **Setup & Foundational**:
  - `T002` [P] pode rodar em paralelo com `T001`.
  - `T005` [P] pode rodar em paralelo com `T003` e `T004`.
- **User Story 1**:
  - Testes unitários `T006`, `T007`, `T008` podem ser escritos em paralelo.
- **User Story 2**:
  - Testes `T011` e `T012` podem ser escritos em paralelo.
- **User Story 3**:
  - `T015`, `T016` e `T017` operam em arquivos distintos e podem ser criados em paralelo.
- **User Story 4**:
  - `T019` pode ser executado em paralelo com `T018`.
- **Polish**:
  - `T020` e `T022` podem ser preparados em paralelo.

---

## Parallel Execution Examples

### Parallel Example: User Story 1 Tests
```bash
# Executar suíte de testes unitários de US1 em paralelo ou agrupados:
python -m unittest skills/linear-workflow/tests/test_linear_api.py -k test_create_manual_issues
```

### Parallel Example: User Story 3 Skill Assets
```bash
# Criação simultânea de definições em arquivos isolados:
Task: "Create prompt definition in skills/linear-workflow/.apm/prompts/fk-new-manual-issue.prompt.md"
Task: "Create skill declaration in skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md"
Task: "Install skill declaration in .agents/skills/fk-new-manual-issue/SKILL.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Executar Fase 1 (Setup) e Fase 2 (Foundational).
2. Implementar e validar testes e CLI para criação de card manual individual (Fase 3 - US1).
3. **STOP and VALIDATE**: Testar criação individual via `create-manual-issues --title ...`.
4. Card manual criado no Linear em `Backlog` com tag `manual`.

### Incremental Delivery

1. Setup + Foundational concluídos.
2. User Story 1 (Criação individual CLI) ➔ Testar e validar (MVP).
3. User Story 2 (Criação em lote JSON `--batch-file`) ➔ Testar e validar.
4. User Story 3 (Prompt e skill `/fk-new-manual-issue` multi-harness com Consent Gate).
5. User Story 4 (Garantia de isolamento Git e documentação).
6. Polish (Suíte completa de testes, validação do quickstart e CHANGELOG).

---

## Notes

- Total de tarefas: 22
- Todas as tarefas seguem estritamente o formato `- [ ] [ID] [P?] [Story?] Descrição com caminho de arquivo`.
- Mutações no Linear são realizadas estritamente em UTF-8 file-first com passagem por `sanitize_markdown_payload`.
- Zero branches Git e zero PRs são gerados para cards operacionais criados por este comando.
