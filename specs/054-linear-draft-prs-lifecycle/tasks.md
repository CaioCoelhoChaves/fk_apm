---
description: "Task list for modernizing linear-workflow with draft PRs lifecycle and board sync"
---

# Tasks: Living Specs & Draft PR Lifecycle com Linear Workflow e Sync de Boards

**Input**: Design documents from `/specs/054-linear-draft-prs-lifecycle/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `skills/linear-workflow/` and `specs/054-linear-draft-prs-lifecycle/` at repository root
- Tests: `skills/linear-workflow/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, test fixtures, and environment prerequisites

- [ ] T001 Configure test fixtures and GraphQL mock helpers for Linear teams and workflow states in skills/linear-workflow/tests/test_linear_api.py
- [ ] T002 [P] Update repository gitignore to ignore ephemeral worktrees per EphemeralWorktreeContext constraint "Padrão: `.worktrees/<CARD-ID>` (ignorado no `.gitignore`)" in .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and data structures that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Define canonical 6-stage LinearWorkflowState constants and validator quoting constraints verbatim (name: "Um de: `Backlog`, `Planned`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`", type: "Um de: `backlog`, `unstarted`, `started`, `completed`, `canceled`", position: "Valores de 0.0 a 6.0 com incrementos regulares", color: "Regex: `^#[0-9A-Fa-f]{6}$`") in skills/linear-workflow/scripts/linear_api.py
- [ ] T004 [P] Implement EphemeralWorktreeContext manager and helper functions (`create_ephemeral_worktree`, `cleanup_ephemeral_worktree`) quoting constraints verbatim (cardId: "Padrão: `^[A-Z]{2,10}-\\d+$` (obrigatório em todos os comandos)", worktreePath: "Padrão: `.worktrees/<CARD-ID>`", status: "`created`, `active`, `syncing`, `cleaned_up`, `failed`") in skills/linear-workflow/scripts/linear_api.py
- [ ] T005 [P] Implement strict transition blocker in `cmd_update_issue` returning error `{"success": false, "error": "Transição para 'Done' é restrita a humanos após merge manual de Pull Request."}` when `--state "Done"` is requested in skills/linear-workflow/scripts/linear_api.py
- [ ] T006 Add unit tests covering EphemeralWorktreeContext lifecycle and Done transition rejection in skills/linear-workflow/tests/test_linear_api.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Concepção da Spec com Draft PR Imediato e Card em Backlog (Priority: P1) 🎯 MVP

**Goal**: Criar branch Gitflow e Draft PR imediatamente na etapa de `/speckit-specify`, vincular URL do PR ao card em `Backlog`, e isolar comandos via ephemeral worktree com `<CARD-ID>` obrigatório.

**Independent Test**: Executar `/speckit-specify`, verificar criação de branch Gitflow `feat/<issue-id>-<slug>`, commit inicial `docs(spec)`, abertura de PR Draft via `gh pr create --draft`, criação do card no Linear em `Backlog` vinculado ao PR, e validação de worktree isolado no `/speckit-clarify`.

### Tests for User Story 1 ⚠️

- [ ] T007 [P] [US1] Add unit tests for LivingSpecDraftPR URL parsing and Draft PR linking in skills/linear-workflow/tests/test_linear_api.py
- [ ] T008 [P] [US1] Add unit tests verifying mandatory `<CARD-ID>` validation aborts execution with explicit syntax hint when omitted in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 1

- [ ] T009 [US1] Implement `create_draft_pr` helper and card body draft PR linking complying with LivingSpecDraftPR constraints (branchName: "Padrão: `<type>/<CARD-ID>-<slug>`", title: "Padrão: `<type>(<CARD-ID>): <descricao-curta>`", isDraft: "`true` durante `specify`, `clarify`, `plan`, `tasks`; `false` após `implement`", htmlUrl: "Padrão: `https://github.com/<owner>/<repo>/pull/<number>`") in skills/linear-workflow/scripts/linear_api.py
- [ ] T010 [US1] Update `/speckit-specify` prompt to create Gitflow branch, push to remote, open Draft PR via `gh pr create --draft`, and link PR to Linear Backlog card in skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md
- [ ] T011 [US1] Update `/speckit-specify` skill definition to match Living Spec Draft PR lifecycle in skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md
- [ ] T012 [US1] Update `/speckit-clarify` prompt to require mandatory `<CARD-ID>` argument, execute in ephemeral worktree, commit spec updates to Draft PR, and suggest `/speckit-plan <CARD-ID>` in skills/linear-workflow/.apm/prompts/speckit-clarify.prompt.md
- [ ] T013 [US1] Update `/speckit-clarify` skill definition with mandatory `<CARD-ID>` validation and next-step prompting in skills/linear-workflow/.apm/skills/speckit-clarify/SKILL.md

**Checkpoint**: User Story 1 fully functional and testable independently (MVP Complete)

---

## Phase 4: User Story 2 - Máquina de Estados Linear de 6 Estágios e Transições Controladas (Priority: P1)

**Goal**: Padronizar ciclo estrito de 6 estágios (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`), transicionar para `Planned` no plan, `Todo` no tasks, `In Progress`/`In Review` no implement.

**Independent Test**: Executar os comandos sequencialmente em uma issue de teste, validando o estado via `linear_api.py get-issue` em cada etapa e conferindo que transições diretas para `Done` são categoricamente rejeitadas.

### Tests for User Story 2 ⚠️

- [ ] T014 [P] [US2] Add unit tests for `Planned` state resolution and 6-stage transition flow in skills/linear-workflow/tests/test_linear_api.py
- [ ] T015 [P] [US2] Add unit tests verifying `validate-plan` succeeds for `Planned` state spec directories in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 2

- [ ] T016 [US2] Update `resolve_team_states` and `validate_spec_plan` in skills/linear-workflow/scripts/linear_api.py to support `Planned` (unstarted, pos 1.0) and resolve spec dirs matching card ID
- [ ] T017 [US2] Update `/speckit-plan` prompt to require `<CARD-ID>`, execute in ephemeral worktree, commit `plan.md` to Draft PR (`docs(plan): ...`), advance card to `Planned` via 3-Stage Consent Gate, and suggest `/speckit-tasks <CARD-ID>` in skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md
- [ ] T018 [US2] Update `/speckit-plan` skill definition with `Planned` state transition rules in skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md
- [ ] T019 [US2] Update `/speckit-tasks` prompt to require `<CARD-ID>`, execute in ephemeral worktree, commit `tasks.md` to Draft PR (`docs(tasks): ...`), validate with `validate-plan`, advance card to `Todo` via 3-Stage Consent Gate, and suggest `/speckit-implement <CARD-ID>` in skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md
- [ ] T020 [US2] Update `/speckit-tasks` skill definition with `Todo` transition rules in skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md
- [ ] T021 [US2] Update `/speckit-implement` prompt to require `<CARD-ID>`, move card to `In Progress`, execute in ephemeral worktree, mark PR ready via `gh pr ready`, advance card to `In Review`, and suggest `/speckit-converge <CARD-ID>` in skills/linear-workflow/.apm/prompts/speckit-implement.prompt.md
- [ ] T022 [US2] Update `/speckit-implement` skill definition with autonomous implementation and PR ready promotion rules in skills/linear-workflow/.apm/skills/speckit-implement/SKILL.md
- [ ] T023 [US2] Update references table with 6 official states, positions, and colors in skills/linear-workflow/references/states-and-labels.md

**Checkpoint**: User Stories 1 and 2 functional and testable independently

---

## Phase 5: User Story 3 - Provisionamento e Sincronização Inteligente de Boards do Linear (Priority: P2)

**Goal**: Implementar subcomandos `sync-boards` e `setup-board` em `linear_api.py` com suporte a `--dry-run`, migração de `Technical Analysis` para `Planned`, e provisionamento idempotente.

**Independent Test**: Executar `linear_api.py sync-boards --dry-run` e `linear_api.py setup-board --team-id <UUID>` validando detecção e migração sem mutações acidentais.

### Tests for User Story 3 ⚠️

- [ ] T024 [P] [US3] Add unit tests for `cmd_sync_boards` verifying team inspection, `--dry-run` safety, and `Technical Analysis` renaming in skills/linear-workflow/tests/test_linear_api.py
- [ ] T025 [P] [US3] Add unit tests for `cmd_setup_board` verifying idempotent creation of missing workflow states in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 3

- [ ] T026 [US3] Implement Linear GraphQL queries (`WorkspaceTeamsAndStates`) and mutations (`WorkflowStateCreate`, `WorkflowStateUpdate`) in skills/linear-workflow/scripts/linear_api.py
- [ ] T027 [US3] Implement `cmd_sync_boards` supporting `--team-id` and `--dry-run` to inspect teams, rename legacy states to `Planned`, and enforce positions/colors per contract in skills/linear-workflow/scripts/linear_api.py
- [ ] T028 [US3] Implement `cmd_setup_board` supporting `--team-id` and `--force` to idempotently provision canonical 6 states (+ Canceled) in skills/linear-workflow/scripts/linear_api.py
- [ ] T029 [US3] Register `sync-boards` and `setup-board` subcommands in CLI argument parser in skills/linear-workflow/scripts/linear_api.py

**Checkpoint**: Board synchronization and provisioning operational and testable independently

---

## Phase 6: User Story 4 - Convergência Autônoma e Resolução de Code Review com Draft PR (Priority: P2)

**Goal**: Implementar convergência autônoma em `/speckit-converge` com ciclo `In Review` ➔ `In Progress` ➔ correções e testes ➔ `In Review`.

**Independent Test**: Simular PR com comentários de review, executar `/speckit-converge <CARD-ID>` e conferir transições temporárias para `In Progress` e retorno para `In Review` com comentário no PR.

### Tests for User Story 4 ⚠️

- [ ] T030 [P] [US4] Add unit tests for review resolution cycle and PR comment deduplication in skills/linear-workflow/tests/test_linear_api.py

### Implementation for User Story 4

- [ ] T031 [US4] Update `/speckit-converge` prompt to require `<CARD-ID>`, move card to `In Progress`, execute in ephemeral worktree, apply review fixes, push commits, post PR completion comment, and advance card to `In Review` in skills/linear-workflow/.apm/prompts/speckit-converge.prompt.md
- [ ] T032 [US4] Update `/speckit-converge` skill definition with autonomous PR convergence workflow in skills/linear-workflow/.apm/skills/speckit-converge/SKILL.md

**Checkpoint**: Autonomous convergence operational and testable independently

---

## Phase 7: User Story 5 - Limpeza e Depreciação de Código Legado (Priority: P3)

**Goal**: Expurgar todas as menções aos fluxos legados `/fk-*` e estados obsoletos em docs, prompts, instructions e templates.

**Independent Test**: Executar busca estática garantindo zero ocorrências de menções aos fluxos legados em `skills/linear-workflow/` e templates.

### Implementation for User Story 5

- [ ] T033 [P] [US5] Expunge legacy `/fk-*` references and update lifecycle instructions in skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md
- [ ] T034 [P] [US5] Update multi-harness command reference with parameterized `<CARD-ID>` syntax and remove legacy aliases in skills/linear-workflow/references/multi-harness-commands.md
- [ ] T035 [P] [US5] Update main skill guide removing legacy references and documenting 6-stage lifecycle in skills/linear-workflow/SKILL.md
- [ ] T036 [P] [US5] Update remaining prompt templates (`speckit-taskstoissues.prompt.md`, `speckit-constitution.prompt.md`, `speckit-analyze.prompt.md`, `speckit-checklist.prompt.md`) in skills/linear-workflow/.apm/prompts/
- [ ] T037 [P] [US5] Update remaining skill definitions (`speckit-taskstoissues/SKILL.md`, `speckit-constitution/SKILL.md`, `speckit-analyze/SKILL.md`, `speckit-checklist/SKILL.md`) in skills/linear-workflow/.apm/skills/
- [ ] T038 [US5] Sync bundled assets in `skills/linear-workflow/assets/.specify/` with root `.specify/` templates and scripts

**Checkpoint**: Legacy code and references completely expunged

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements, validations, and documentation updates that affect multiple user stories

- [ ] T039 [P] Update Constitution in .specify/memory/constitution.md ratifying Living Specs, 6-stage state machine, and ephemeral worktree isolation
- [ ] T040 [P] Execute full unit test suite via `python -m unittest skills/linear-workflow/tests/test_linear_api.py` and ensure 100% pass
- [ ] T041 Run static plan validation via `python skills/linear-workflow/scripts/linear_api.py validate-plan specs/054-linear-draft-prs-lifecycle`
- [ ] T042 Run quickstart verification scenarios per specs/054-linear-draft-prs-lifecycle/quickstart.md
- [ ] T043 Document changes under `## [Unreleased]` following Keep a Changelog and Conventional Commits in CHANGELOG.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3) or in parallel if staffed
  - US1 (Living Specs Draft PR) and US2 (6-Stage State Machine) are Priority P1 and should be executed first
  - US3 (Board Sync) and US4 (Converge) are Priority P2 and can run after or alongside US1/US2
  - US5 (Legacy Cleanup) is Priority P3 and runs once the new lifecycle is in place
- **Polish (Phase 8)**: Depends on all user stories (Phase 3 to 7) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational (Phase 2). No dependencies on other stories.
- **User Story 2 (P1)**: Starts after Foundational (Phase 2). Integrates with US1 Draft PR context.
- **User Story 3 (P2)**: Starts after Foundational (Phase 2). Independently tests board mutations.
- **User Story 4 (P2)**: Starts after US1 and US2 (depends on Draft PR and `In Review` state).
- **User Story 5 (P3)**: Starts after US1-US4 to ensure all active templates reference the modernized commands.

### Within Each User Story

- Tests written first, verified to fail before implementation
- CLI helpers and core logic before prompts and skill definitions
- Prompts before skill metadata files
- Story complete and validated before moving to next priority

### Parallel Opportunities

- All Setup tasks marked `[P]` (T002) can run in parallel with T001
- Foundational tasks marked `[P]` (T004, T005) can run in parallel once T003 is scoped
- In US1: T007, T008 can run in parallel
- In US2: T014, T015 can run in parallel
- In US3: T024, T025 can run in parallel
- In US5: T033, T034, T035, T036, T037 can run in parallel across documentation and prompt files
- In Polish: T039 and T040 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch test creation for User Story 1 in parallel:
Task: "Add unit tests for LivingSpecDraftPR URL parsing and Draft PR linking in skills/linear-workflow/tests/test_linear_api.py"
Task: "Add unit tests verifying mandatory <CARD-ID> validation aborts execution with explicit syntax hint when omitted in skills/linear-workflow/tests/test_linear_api.py"

# Update prompts and skills in parallel:
Task: "Update /speckit-specify prompt in skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md"
Task: "Update /speckit-specify skill definition in skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004, T005, T006)
3. Complete Phase 3: User Story 1 (T007 through T013)
4. **STOP and VALIDATE**: Test User Story 1 independently with `gh pr create --draft` and Linear issue creation
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Core foundations ready
2. Add User Story 1 (P1) → Draft PRs open at spec inception (MVP!)
3. Add User Story 2 (P1) → 6-stage Linear state transitions (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`)
4. Add User Story 3 (P2) → Board synchronization and automated setup (`sync-boards`, `setup-board`)
5. Add User Story 4 (P2) → Autonomous PR review convergence
6. Add User Story 5 (P3) → Expunge legacy code and clean references
7. Phase 8 Polish → Comprehensive verification, quickstart validation, and changelog update
