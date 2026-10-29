---
description: "Task list for FAL-53: Official github/spec-kit integration with Linear workflow and Markdown sanitization"
---

# Tasks: Official `github/spec-kit` Integration with Linear Workflow & Markdown Sanitization (`FAL-53`)

**Input**: Design documents from `/specs/053-fal-53-spec-kit-linear-workflow/`

**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `.specify/memory/constitution.md`

## Phase 1: Setup (Official `github/spec-kit` Infrastructure)

**Purpose**: Install and configure the official `.specify/` runtime in the repository root and bundle it inside `skills/linear-workflow/assets/.specify/`.

- [X] T001 Install official `.specify/` directory (`scripts/python/`, `scripts/powershell/`, `templates/`, `memory/`, `workflows/`, `integrations/`) in repository root via `specify init --integration agy --script py`
- [X] T002 Define `fk_apm` engineering governance in `.specify/memory/constitution.md`
- [X] T003 Bundle `.specify/` runtime inside `skills/linear-workflow/assets/.specify/` for downstream APM consumers

---

## Phase 2: Foundational (`linear_api.py` Enhancements)

**Purpose**: Core CLI capabilities in `skills/linear-workflow/scripts/linear_api.py` required by all `speckit-*` skills.

- [X] T004 [US2] Implement `sanitize_markdown_payload()` and CLI subcommand `sanitize-markdown` in `skills/linear-workflow/scripts/linear_api.py`
- [X] T005 [US1] Implement `validate_spec_plan()` and CLI subcommand `validate-plan` supporting `.specify/feature.json` and `specs/<feature>/` in `skills/linear-workflow/scripts/linear_api.py`
- [X] T006 [US1] Implement `bootstrap_specify()` and CLI subcommand `bootstrap-specify` in `skills/linear-workflow/scripts/linear_api.py`

---

## Phase 3: User Story 1 - Replace `/fk-*` with Official `speckit-*` Skills Coupled to Linear (Priority: P1) 🎯 MVP

**Goal**: Provide the 10 official `speckit-*` skills in `skills/linear-workflow/.apm/skills/` and `.agents/skills/` coupled with Linear state transitions, 3-Stage Consent Gate, and Gitflow PR automation.

**Independent Test**: Verify all 10 `speckit-*` skills exist, legacy `fk-*` lifecycle skills are removed, and `apm install` deploys them cleanly.

- [X] T007 [US1] Remove legacy `fk-new-issue`, `fk-technical-analysis`, `fk-develop`, and `fk-fix` from `skills/linear-workflow/.apm/skills/`, `skills/linear-workflow/.apm/prompts/`, and `.agents/skills/`
- [X] T008 [P] [US1] Create `speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, and `speckit-tasks` in `skills/linear-workflow/.apm/skills/` with Linear 3-Stage Consent Gate and Pre-Render Gate
- [X] T009 [P] [US1] Create `speckit-analyze`, `speckit-checklist`, `speckit-taskstoissues`, `speckit-implement`, and `speckit-converge` in `skills/linear-workflow/.apm/skills/` with autonomous Linear `In Progress` ➔ `In Review` transitions and Gitflow PR integration
- [X] T010 [P] [US1] Create corresponding `speckit-*.prompt.md` files in `skills/linear-workflow/.apm/prompts/`
- [X] T011 [US1] Update `skills/linear-workflow/SKILL.md`, `instructions/linear-lifecycle-commands.instructions.md`, and `references/*.md` to document the `/speckit-*` + Linear workflow

---

## Phase 4: User Story 2 & Polish - Tests, Catalog Sync, and Verification

**Purpose**: Validate all scripts, skills, and APM bundles with automated unit tests.

- [X] T012 [US2] Update unit tests in `skills/linear-workflow/tests/test_linear_api.py` covering `sanitize_markdown_payload`, `validate_spec_plan`, `bootstrap_specify`, `.specify/scripts/python/*.py`, and the 10 `speckit-*` skill contracts
- [X] T013 [P] Update `README.md`, `CHANGELOG.md`, `apm.yml`, `bundles/default/apm.yml`, and run `apm install` to synchronize `.agents/skills/` and `apm.lock.yaml`
