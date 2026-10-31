---
description: "Task list for feature implementation: Fluxo Contínuo e Autônomo do Spec Kit com Revisão Centralizada no GitHub"
---

# Tasks: Fluxo Contínuo e Autônomo do Spec Kit com Revisão Centralizada no GitHub

**Input**: Design documents from `/specs/056-autonomous-speckit-workflow/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/)  
**Linear Issue**: [FAL-60](https://linear.app/fallkey/issue/FAL-60/featworkflow-eliminar-consent-gates-entre-fases-do-speckit-e-habilitar)  
**Pull Request**: [#22 — feat(workflow): eliminar consent gates entre fases do speckit e habilitar revisao autonoma via github](https://github.com/CaioCoelhoChaves/fk_apm/pull/22)

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story mapping ([US1], [US2], [US3], [US4])

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verification of testing environment and baseline API tooling

- [ ] T001 Setup verification environment and baseline test suite in skills/linear-workflow/tests/test_linear_api.py
- [ ] T002 [P] Verify GitHub CLI (`gh`) and Linear API connectivity in skills/linear-workflow/scripts/linear_api.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and state transition helpers that MUST be verified before user stories

**⚠️ CRITICAL**: Foundational state machine and payload utilities must be ready before modifying skill instructions

- [ ] T003 Update core Linear update helpers to support continuous transition without prompt blocking in skills/linear-workflow/scripts/linear_api.py
- [ ] T004 [P] Verify UTF-8 payload sanitization and temporary file helpers in skills/linear-workflow/scripts/linear_api.py
- [ ] T005 [P] Add unit test cases for automated state advancement and non-interactive transitions in skills/linear-workflow/tests/test_linear_api.py

**Checkpoint**: Foundational helpers verified — User stories can now proceed

---

## Phase 3: User Story 1 - Execução Autônoma Entre Fases Sem Consent Gates Interativos (Priority: P1) 🎯 MVP

**Goal**: Eliminar o Consent Gate de 3 etapas com `ask_question` nos comandos de ciclo de vida (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`), permitindo execução de ponta a ponta com mutações automáticas e sincronização contínua.

**Independent Test**: Executar os comandos sequencialmente e verificar que os artefatos são gerados, comitados no PR Draft e transicionados no Linear sem nenhuma pergunta ou bloqueio síncrono no chat.

### Implementation for User Story 1

- [ ] T006 [P] [US1] Remove Consent Gate and configure autonomous Living Spec Draft PR creation in skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md
- [ ] T007 [P] [US1] Remove Consent Gate and configure autonomous Backlog card creation in skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md
- [ ] T008 [P] [US1] Remove Consent Gate and configure autonomous Planned transition in skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md
- [ ] T009 [P] [US1] Remove Consent Gate and configure autonomous technical comment upload in skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md
- [ ] T010 [P] [US1] Remove Consent Gate and configure autonomous Todo transition in skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md
- [ ] T011 [P] [US1] Remove Consent Gate and configure autonomous plan validation in skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md
- [ ] T012 [P] [US1] Remove Consent Gate and configure autonomous issue creation batching in skills/linear-workflow/.apm/prompts/speckit-taskstoissues.prompt.md
- [ ] T013 [P] [US1] Remove Consent Gate and configure autonomous issue batching in skills/linear-workflow/.apm/skills/speckit-taskstoissues/SKILL.md
- [ ] T014 [US1] Update lifecycle instruction guide removing interactive confirmation requirements in skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md

**Checkpoint**: At this point, User Story 1 is fully functional — all lifecycle phases execute autonomously without interactive question gates.

---

## Phase 4: User Story 2 - Revisão e Acompanhamento Centralizado no GitHub com Living Specs (Priority: P1)

**Goal**: Centralizar toda a governança e inspeção no GitHub Draft PR, padronizando os relatórios executivos no chat com links clicáveis diretos para o PR e Linear.

**Independent Test**: Inspecionar os relatórios emitidos ao término de cada comando garantindo links funcionais para o PR no GitHub e orientações claras de revisão assíncrona.

### Implementation for User Story 2

- [ ] T015 [P] [US2] Standardize Executive Report format with clickable Draft PR links in skills/linear-workflow/SKILL.md
- [ ] T016 [P] [US2] Document GitHub PR review guidelines and living specs lifecycle in skills/linear-workflow/references/multi-harness-commands.md
- [ ] T017 [P] [US2] Update state machine documentation asserting autonomous transitions and manual Done safeguard in skills/linear-workflow/references/states-and-labels.md

**Checkpoint**: User Story 2 complete — Developer review is centralized in GitHub with structured executive reporting.

---

## Phase 5: User Story 3 - Sincronização Autônoma do `/speckit-clarify` com Modificações do GitHub (Priority: P2)

**Goal**: Permitir que `/speckit-clarify` sincronize alterações feitas pelo desenvolvedor no GitHub (`git pull --rebase origin <branch>`), absorva comentários e refine `spec.md` autonomamente.

**Independent Test**: Modificar `spec.md` no remote, rodar `/speckit-clarify` e verificar que as modificações são preservadas, ambiguidades dirimidas e enviadas de volta ao remote.

### Implementation for User Story 3

- [ ] T018 [P] [US3] Add git pull rebase synchronization step before spec clarification in skills/linear-workflow/.apm/prompts/speckit-clarify.prompt.md
- [ ] T019 [P] [US3] Configure autonomous ambiguity resolution and push to remote Draft PR in skills/linear-workflow/.apm/skills/speckit-clarify/SKILL.md
- [ ] T020 [US3] Add unit tests for git pull rebase clarify synchronization flow in skills/linear-workflow/tests/test_linear_api.py

**Checkpoint**: User Story 3 complete — `/speckit-clarify` seamlessly integrates remote GitHub modifications.

---

## Phase 6: User Story 4 - Atualização Constitucional e Harmonização dos Manifestos de Skills (Priority: P2)

**Goal**: Ratificar a Constituição na versão 1.2.0, atualizar manifestos de skills, compilação de bundle e changelog.

**Independent Test**: Verificar conformidade constitucional, compilação do bundle APM e integridade do CHANGELOG.md sob `## [Unreleased]`.

### Implementation for User Story 4

- [ ] T021 [P] [US4] Elevate constitution to v1.2.0 ratifying continuous autonomous pipeline and manual Done in .specify/memory/constitution.md
- [ ] T022 [P] [US4] Synchronize constitution template asset to v1.2.0 in skills/linear-workflow/assets/.specify/memory/constitution.md
- [ ] T023 [P] [US4] Update skill description and prompt declarations in apm.yml
- [ ] T024 [P] [US4] Update documentation tables and skill references in README.md
- [ ] T025 [P] [US4] Add Unreleased entries in CHANGELOG.md documenting removal of consent gates and GitHub review workflow

**Checkpoint**: User Story 4 complete — Governance, constitutions, manifests, and documentation are unified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validation across the entire suite, bundle compilation, and quickstart scenario checks

- [ ] T026 Execute complete unit test suite across all packages in skills/linear-workflow/tests/test_linear_api.py
- [ ] T027 [P] Validate multi-harness bundle compilation with APM in apm.yml
- [ ] T028 Validate quickstart verification scenarios in specs/056-autonomous-speckit-workflow/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — executes first.
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) — BLOCKS all user stories.
- **User Story 1 (Phase 3 - P1)**: Depends on Foundational completion. Delivers the core autonomous pipeline without consent gates.
- **User Story 2 (Phase 4 - P1)**: Depends on Foundational completion. Can run in parallel with US1 or immediately follow it.
- **User Story 3 (Phase 5 - P2)**: Depends on US1 prompt structure. Adds remote Git rebase integration to clarify.
- **User Story 4 (Phase 6 - P2)**: Depends on US1/US2/US3 definitions to finalize constitution, manifest, and changelog.
- **Polish (Phase 7)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Independent of other stories; foundational to the workflow.
- **User Story 2 (P1)**: Shares lifecycle reporting standard with US1.
- **User Story 3 (P2)**: Builds upon the clarified prompt architecture established in US1.
- **User Story 4 (P2)**: Formalizes the governance and documentation across all stories.

---

## Parallel Execution Examples

### User Story 1 (Prompts & Skills in Parallel)
```bash
# Launch prompt updates simultaneously:
Task: "Remove Consent Gate and configure autonomous Living Spec Draft PR creation in skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md"
Task: "Remove Consent Gate and configure autonomous Planned transition in skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md"
Task: "Remove Consent Gate and configure autonomous Todo transition in skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md"
Task: "Remove Consent Gate and configure autonomous issue creation batching in skills/linear-workflow/.apm/prompts/speckit-taskstoissues.prompt.md"
```

### User Story 4 (Governance & Manifests in Parallel)
```bash
# Update constitution and asset simultaneously:
Task: "Elevate constitution to v1.2.0 ratifying continuous autonomous pipeline and manual Done in .specify/memory/constitution.md"
Task: "Synchronize constitution template asset to v1.2.0 in skills/linear-workflow/assets/.specify/memory/constitution.md"
Task: "Update skill description and prompt declarations in apm.yml"
Task: "Update documentation tables and skill references in README.md"
Task: "Add Unreleased entries in CHANGELOG.md documenting removal of consent gates and GitHub review workflow"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (Autonomous execution of lifecycle commands)
4. **STOP and VALIDATE**: Verify commands execute without prompting `ask_question`
5. Proceed to US2, US3, US4 incrementally.

### Incremental Delivery

1. Setup + Foundational -> Pipeline utilities verified.
2. User Story 1 -> Elimination of Consent Gates across all commands (MVP!).
3. User Story 2 -> GitHub Draft PR review guidelines and Executive Report standardization.
4. User Story 3 -> `/speckit-clarify` remote GitHub rebase sync.
5. User Story 4 -> Constitution v1.2.0, APM bundle, README, and CHANGELOG.md.
6. Polish -> End-to-end test suite and quickstart scenarios validation.
