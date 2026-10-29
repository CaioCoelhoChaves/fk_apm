# Feature Specification: Official `github/spec-kit` Integration with Linear Workflow & Markdown Sanitization

**Feature Branch**: `feat/FAL-53-spec-driven-development-linear-workflow` (`053-fal-53-spec-kit-linear-workflow`)

**Linear Issue**: `FAL-53`

**Created**: 2026-10-29

**Status**: Approved

**Input**: User description: "Integrate the official github/spec-kit package (.specify/ + 10 speckit-* skills) into the fk_apm development pipeline, replacing /fk-* commands with /speckit-* commands coupled to Linear card state transitions, 3-stage Consent Gate, and Markdown payload sanitization."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Official `github/spec-kit` Lifecycle Coupled with Linear (Priority: P1)

As a developer using `fk_apm` (with the `default` bundle installed), I want to use the official `/speckit-*` commands (`/speckit-constitution`, `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`, `/speckit-checklist`, `/speckit-taskstoissues`, `/speckit-implement`, `/speckit-converge`) instead of `/fk-*`, while preserving all Linear card movements (`Backlog`, `Todo`, `In Progress`, `In Review`), the 3-stage Consent Gate for planning/analysis, and autonomous execution for implementation and review fixes.

**Why this priority**: Core architectural requirement confirmed by the user — replacing `/fk-*` with the real `github/spec-kit` workflow coupled with Linear board automation in `bundles/default`.

**Independent Test**: Run `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` and verify all 10 `speckit-*` skills are deployed in `.agents/skills/` and `skills/linear-workflow/.apm/skills/` with Linear state machine integration.

**Acceptance Scenarios**:

1. **Given** a feature request or rough requirement, **When** the user invokes `/speckit-specify` (or `/speckit-taskstoissues`), **Then** the agent generates `specs/<feature>/spec.md` + `checklists/requirements.md` via `.specify/scripts/python/create_new_feature.py`, executes the 3-Stage Consent Gate (Pre-Render Gate in chat -> `ask_question` -> atomic Linear creation), and creates the Linear card(s) in `Backlog` using `--description-file`.
2. **Given** an existing Linear card and `spec.md`, **When** the user invokes `/speckit-plan` and `/speckit-tasks`, **Then** the agent generates `plan.md` and `tasks.md` via `.specify/scripts/python/setup_plan.py` and `setup_tasks.py`, validates the plan against `.specify/memory/constitution.md`, pre-renders the Executive Briefing (`Título Revisado`, `Descrição Atualizada`, and the 5 mandatory sections) in chat with zero prior Linear mutation, asks for confirmation via `ask_question`, and moves the Linear card to `Todo` via `--description-file` and `--comment-file`.
3. **Given** a Linear card ready for development with `tasks.md`, **When** the user invokes `/speckit-implement <issue-key>`, **Then** the agent autonomously (without Consent Gate) transitions the Linear card to `In Progress`, creates/switches to the Gitflow branch `<type>/<issue-key>-<slug>`, executes all tasks in `tasks.md` marking them `[X]`, opens a GitHub PR using `gh pr create --body-file`, and transitions the Linear card to `In Review`.
4. **Given** an open PR or card in `In Review` with review feedback or spec drift, **When** the user invokes `/speckit-converge <issue-key>`, **Then** the agent autonomously transitions the Linear card to `In Progress`, reads PR comments/reviews and spec gaps, appends convergence tasks to `tasks.md`, applies fixes on the PR branch, comments on the PR via `--body-file`, and returns the card to `In Review`.

---

### User Story 2 - Markdown Sanitization & Pre-Render Gate Protection (Priority: P1)

As a developer reviewing cards in Linear and PRs in GitHub, I want all Markdown descriptions and comments sent by the agent to be free of shell-escaping corruption (`\"`, broken backticks, literal `\n` strings) and I want to see the full Executive Briefing in chat before the confirmation question pops up.

**Why this priority**: Eliminates corrupted Markdown payloads on Linear/GitHub caused by inline PowerShell/Bash arguments and prevents blind approval prompts.

**Independent Test**: Run `python -m unittest discover -s skills/linear-workflow/tests -p "test_*.py" -v` to verify `sanitize_markdown_payload()` repairs corrupted sequences while preserving valid code blocks.

**Acceptance Scenarios**:

1. **Given** a Markdown payload containing escaped quotes (`\"`) or literal `\r\n` / `\n` sequences from CLI serialization, **When** `linear_api.py create-issue` or `update-issue` processes the input, **Then** `sanitize_markdown_payload()` cleans the payload before sending the GraphQL mutation to Linear.
2. **Given** a technical analysis or specification approval gate, **When** Stage 1 runs, **Then** the agent outputs the full Executive Briefing (`Título Revisado`, `Descrição Atualizada`, and 5 sections) in chat before invoking `ask_question` in Stage 2.

---

### Edge Cases

- What happens when a consumer project installs `bundles/default` via APM in a repository that does not yet have `.specify/` at the root?
  - `skills/linear-workflow/assets/.specify/` bundles the complete `.specify/` runtime (Python & PowerShell scripts, templates, memory constitution template, workflows) and `python skills/linear-workflow/scripts/linear_api.py bootstrap-specify` automatically initializes `.specify/` in the target repository without overwriting an existing `constitution.md`.
- How does the system handle legacy `/fk-*` references in user prompts?
  - `skills/linear-workflow/SKILL.md` maps any legacy `/fk-*` or natural language request directly to the corresponding `/speckit-*` workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST include the official `.specify/` directory (`scripts/python/`, `scripts/powershell/`, `templates/`, `memory/constitution.md`, `workflows/`, `integrations/`) at the repository root and bundled in `skills/linear-workflow/assets/.specify/`.
- **FR-002**: `skills/linear-workflow/.apm/skills/` and `.agents/skills/` MUST provide the 10 official `speckit-*` skills (`speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-taskstoissues`, `speckit-implement`, `speckit-converge`) replacing `fk-new-issue`, `fk-technical-analysis`, `fk-develop`, and `fk-fix`.
- **FR-003**: `linear_api.py` MUST implement `sanitize_markdown_payload()`, `validate-plan` (compatible with `.specify/feature.json` and `specs/<feature>/`), and `bootstrap-specify`.
- **FR-004**: All Linear and GitHub CLI mutations in `speckit-*` skills MUST enforce file-based UTF-8 arguments (`--description-file`, `--comment-file`, `--body-file`) and forbid inline multi-line Markdown strings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All unit tests in `skills/linear-workflow/tests/test_linear_api.py` pass (`0` failures).
- **SC-002**: `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` exits with code `0` for `specs/053-fal-53-spec-kit-linear-workflow`.
- **SC-003**: `python skills/linear-workflow/scripts/linear_api.py validate-plan --issue-key FAL-53` returns `{"valid": true}`.
- **SC-004**: `apm compile` and `apm install` succeed with all 10 `speckit-*` skills registered in `apm.lock.yaml`.

## Assumptions

- Python 3.8+ is available in the environment for running `.specify/scripts/python/*.py` and `skills/linear-workflow/scripts/linear_api.py`.
- Linear API credentials (`LINEAR_API_KEY`) are configured in `.env` or environment variables when executing live Linear transitions.
