---

description: "Task list for removing the final consent gate rite in linear-workflow speckit stages (FAL-74)"
---

# Tasks: Remoção do Rito de Aprovação Final (Consent Gate) no Linear Workflow

**Input**: Design documents from `/specs/055-remove-consent-gate-rite/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/skill-execution-modes.md`, `quickstart.md`

**Tests**: Included as requested in `plan.md` (Section 4) and `specs/055-remove-consent-gate-rite/spec.md` (`SC-002` — 100% of `skills/linear-workflow/tests/test_linear_api.py` passing).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`)
- Exact file paths are included in every task description.

---

## Phase 1: Setup (Governance & Baseline)

**Purpose**: Amend the project Constitution to v1.2.0 so all downstream skill, prompt, and test updates conform to the ratified dialogue-driven workflow.

- [X] T001 Amend Constitution from `v1.1.0` to `v1.2.0` (removing mandatory 3-Stage Consent Gate from `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` while preserving Draft PRs, Pre-Render, `Done` manual-only, and `/speckit-taskstoissues` batch gate) in `.specify/memory/constitution.md`
- [X] T002 [P] Synchronize packaged Constitution template to `v1.2.0` in `skills/linear-workflow/assets/.specify/memory/constitution.md`

---

## Phase 2: Foundational (Core Skill & Global Multi-Harness Instructions)

**Purpose**: Update the root `linear-workflow` skill contract and global multi-harness instruction file that govern all `/speckit-*` commands.

**⚠️ CRITICAL**: No user story command updates can begin until this phase is complete.

- [X] T003 Update core `linear-workflow` protocol (replacing 3-Stage Consent Gate with direct dialogue-driven execution + mandatory Pre-Render for `specify`, `plan`, `tasks` and keeping Consent Gate exclusively for `taskstoissues`) in `skills/linear-workflow/SKILL.md`
- [X] T004 [P] Update global multi-harness lifecycle instructions (`direct_dialogue_driven` for `specify`, `plan`, `tasks`, `autonomous` for `implement`, `three_stage_consent_gate` for `taskstoissues`) in `skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md`

**Checkpoint**: Core governance and global instructions ready — command-level implementation for US1 and US2 can now proceed.

---

## Phase 3: User Story 1 - Fluxo Orientado a Diálogo sem Rito de Aprovação Final (Priority: P1) 🎯 MVP

**Goal**: Remove the mandatory final approval rite (`ask_question` / `AskUserQuestion` with `"(Recommended) Sim, aprovar"` / `"Editar..."`) from `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, and `/speckit-implement` across both `.apm/skills/` and `.apm/prompts/`, enabling direct GitHub Draft PR and Linear execution after Pre-Render.

**Independent Test**: Inspect all 8 files (`SKILL.md` and `.prompt.md` for `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`) and verify via `git grep` and unit tests that none require `ask_question` / `AskUserQuestion` final approval before creating/transitioning Linear cards (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`).

### Implementation for User Story 1

- [X] T005 [P] [US1] Remove Stage 2 final approval rite and execute branch, Draft PR (`gh pr create --draft --body-file`), and `Backlog` issue creation (`--description-file`) directly after chat table Pre-Render in `skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md`
- [X] T006 [P] [US1] Synchronize multi-harness prompt for `/speckit-specify` with direct execution after Pre-Render and natural dialogue for critical ambiguities in `skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md`
- [X] T007 [P] [US1] Remove Stage 2 final approval rite and advance issue directly to `Planned` (`--title`, `--description-file`, `--comment-file`) after Draft PR commit and chat Executive Briefing Pre-Render in `skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md`
- [X] T008 [P] [US1] Synchronize multi-harness prompt for `/speckit-plan` with direct `Planned` transition after Executive Briefing Pre-Render in `skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md`
- [X] T009 [P] [US1] Remove Stage 2 final approval rite and advance issue directly to `Todo` (`--title`, `--description-file`, `--comment-file`) after `validate-plan`, Draft PR commit, and chat Executive Briefing Pre-Render in `skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md`
- [X] T010 [P] [US1] Synchronize multi-harness prompt for `/speckit-tasks` with direct `Todo` transition after `validate-plan` and Executive Briefing Pre-Render in `skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md`
- [X] T011 [P] [US1] Reinforce 100% autonomous execution without final approval rite (natural dialogue only on blocking ambiguity; `Todo` ➔ `In Progress` ➔ `In Review`; `Done` manual-only) in `skills/linear-workflow/.apm/skills/speckit-implement/SKILL.md`
- [X] T012 [P] [US1] Synchronize multi-harness prompt for `/speckit-implement` with autonomous execution and natural dialogue policy in `skills/linear-workflow/.apm/prompts/speckit-implement.prompt.md`

**Checkpoint**: All 4 target `/speckit-*` commands (8 skill/prompt files) now operate without final approval rites.

---

## Phase 4: User Story 2 - Preservação do Pre-Render, Diálogo Natural e Exceções Explícitas (Priority: P2)

**Goal**: Preserve full Pre-Render transparency in chat, UTF-8 file-first payload safety, natural dialogue refinement, and the batch 3-Stage Consent Gate in `/speckit-taskstoissues`, while updating reference docs, evals, and deterministic unit tests to enforce the new contracts.

**Independent Test**: Run `python -m unittest skills/linear-workflow/tests/test_linear_api.py` and confirm 100% pass rate, verifying Pre-Render & UTF-8 payload invariants, absence of final approval rites in the 4 target commands, multi-harness parity, and preservation of the 3-Stage Consent Gate in `speckit-taskstoissues`.

### Implementation for User Story 2

- [X] T013 [P] [US2] Update execution mode matrix (`direct_dialogue_driven`, `autonomous`, `three_stage_consent_gate`) and Pre-Render protocol documentation in `skills/linear-workflow/references/multi-harness-commands.md`
- [X] T014 [P] [US2] Update `stateDiagram-v2` and state transition table (removing Consent Gate from `specify`, `plan`, `tasks` while preserving `taskstoissues` batch gate and manual `Done`) in `skills/linear-workflow/references/states-and-labels.md`
- [X] T015 [P] [US2] Update eval 1 `expected_output` to expect direct `Backlog` creation + Draft PR after chat Pre-Render without final approval gate in `skills/linear-workflow/evals/evals.json`
- [X] T016 [US2] Update `test_skill_files_enforce_prerender_and_tooling_labels` (replacing legacy `"Proibição de Consent Gate Cego"` check) and add contract tests verifying absence of `"Sim, aprovar"` / `"Editar..."` in `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`, multi-harness parity, and preservation of 3-Stage Consent Gate in `speckit-taskstoissues` in `skills/linear-workflow/tests/test_linear_api.py`

**Checkpoint**: Reference documentation, evals, and automated contract tests fully enforce US1 and US2 invariants.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Synchronize catalog manifests, changelog, deployed `.agents/skills/` artifacts, and run final verification checks.

- [X] T017 [P] Update `linear-workflow` package description (dialogue-driven SDD without final approval rite in `specify`/`plan`/`tasks`/`implement`) in `apm.yml`
- [X] T018 [P] Update `linear-workflow` row in Individual Skills table in `README.md`
- [X] T019 [P] Document removal of final Consent Gate rite in `CHANGELOG.md` under `## [Unreleased]` (`Changed`)
- [X] T020 Run `apm install` to synchronize `skills/linear-workflow/` to `.agents/skills/` and update `apm.lock.yaml`
- [X] T021 Run `python -m unittest skills/linear-workflow/tests/test_linear_api.py` and `git grep -n "Sim, aprovar" -- skills/linear-workflow/` to verify `SC-001`, `SC-002`, and `SC-003` per `specs/055-remove-consent-gate-rite/quickstart.md`
- [X] T022 Run `python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-74` to confirm `"valid": true` across all feature artifacts

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately (`T001`, `T002` in parallel).
- **Foundational (Phase 2)**: Depends on Setup (`T001`–`T002`) — BLOCKS User Story 1 and User Story 2 (`T003`, `T004` in parallel).
- **User Story 1 (Phase 3 - P1 🎯 MVP)**: Depends on Foundational (`T003`–`T004`). All 8 command skill/prompt files (`T005`–`T012`) are independent and can execute in parallel.
- **User Story 2 (Phase 4 - P2)**: Depends on Foundational (`T003`–`T004`) and US1 completion for `T016` test validation. `T013`, `T014`, `T015` can run in parallel; `T016` runs after `T005`–`T015`.
- **Polish (Phase 5)**: `T017`, `T018`, `T019` can run in parallel after Phase 4; `T020` (`apm install`) must precede `T021` (test suite + parity verification) and `T022` (`validate-plan`).

### Parallel Opportunities

- **Phase 1**: `T001` and `T002` (different files).
- **Phase 2**: `T003` and `T004` (different files).
- **Phase 3 (US1)**: `T005` through `T012` (all 8 files are distinct `.apm/skills/` and `.apm/prompts/` files).
- **Phase 4 (US2)**: `T013`, `T014`, `T015` in parallel, followed by `T016`.
- **Phase 5 (Polish)**: `T017`, `T018`, `T019` in parallel, followed sequentially by `T020` ➔ `T021` ➔ `T022`.

---

## Parallel Example: User Story 1

```bash
# Update all 4 target command pairs in parallel after Phase 2:
Task: "T005 [P] [US1] skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md"
Task: "T006 [P] [US1] skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md"
Task: "T007 [P] [US1] skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md"
Task: "T008 [P] [US1] skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md"
Task: "T009 [P] [US1] skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md"
Task: "T010 [P] [US1] skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md"
Task: "T011 [P] [US1] skills/linear-workflow/.apm/skills/speckit-implement/SKILL.md"
Task: "T012 [P] [US1] skills/linear-workflow/.apm/prompts/speckit-implement.prompt.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`T001`–`T002` — Constitution `v1.2.0`).
2. Complete Phase 2: Foundational (`T003`–`T004` — Core `SKILL.md` + global instructions).
3. Complete Phase 3: User Story 1 (`T005`–`T012` — 4 command skill/prompt pairs).
4. **STOP and VALIDATE**: Confirm zero `"Sim, aprovar"` / `"Editar..."` occurrences in the 4 target commands.

### Incremental Delivery

1. Setup + Foundational ➔ Core governance ready.
2. Add User Story 1 ➔ All 4 `/speckit-*` stages operate without final approval rite (MVP!).
3. Add User Story 2 ➔ References, evals, and deterministic unit tests updated and passing.
4. Polish ➔ Manifests synced via `apm install`, `apm.lock.yaml` updated, `CHANGELOG.md` updated, and `validate-plan FAL-74` passing.
