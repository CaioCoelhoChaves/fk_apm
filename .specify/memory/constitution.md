<!--
Sync Impact Report
- Version change: N/A -> 1.0.0
- Added sections: Core Principles (I-V), Linear & Gitflow Governance, Quality & Security Gates, Governance
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: None
-->

# fk_apm Constitution

## Core Principles

### I. Multi-Harness Parity & Bundled Distribution
Every skill and workflow distributed in `fk_apm` MUST maintain functional parity across supported AI coding harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, and OpenCode). Runtime assets (including `.specify/` scripts, templates, and `linear_api.py`) MUST be self-contained and cross-platform (Windows PowerShell and POSIX shells via Python 3.8+ standard library scripts).

### II. Spec-Driven Linear Lifecycle (Official `github/spec-kit` Integration)
All planning, specification, technical analysis, implementation, and review convergence MUST flow through the official `github/spec-kit` artifact pipeline (`specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `checklists/`) coupled with Linear issue state transitions:
- `/speckit-specify` & `/speckit-taskstoissues`: Specification & issue creation in `Backlog` (with 3-Stage Consent Gate).
- `/speckit-clarify`: Structured ambiguity resolution on `spec.md`.
- `/speckit-plan` & `/speckit-tasks`: Architectural plan and task breakdown advancing the Linear card to `Todo` (with 3-Stage Consent Gate and Pre-Render Gate).
- `/speckit-implement`: Autonomous execution moving the card to `In Progress`, creating the Gitflow branch, completing `tasks.md`, opening the Pull Request, and advancing the card to `In Review` (no Consent Gate).
- `/speckit-converge`: Autonomous PR review & spec convergence moving the card to `In Progress`, applying fixes on the PR branch, and returning the card to `In Review` (no Consent Gate).
- `Done` transitions are strictly manual by the developer after merging the PR.

### III. Zero Shell-Escaping Corruption (File-First Payloads)
Agents and CLI scripts MUST NEVER pass multi-line Markdown or strings containing backticks (`` ` ``) or quotes inline via shell arguments (`--description "..."`, `--comment "..."`, `--body "..."`). All Linear mutations and GitHub PR operations MUST use UTF-8 file-based flags (`--description-file`, `--comment-file`, `--body-file`) and pass through `sanitize_markdown_payload()` in `linear_api.py`.

### IV. Deterministic Verification & Test Coverage (NON-NEGOTIABLE)
Every modification to CLI scripts (`linear_api.py`, `.specify/scripts/python/*.py`), skill contracts, or bundle manifests MUST be accompanied by deterministic automated unit tests (`unittest`) and validated with `apm compile` / `apm install` before opening or updating a Pull Request.

### V. Semantic Versioning & Keep a Changelog
All notable changes MUST be recorded under `## [Unreleased]` in `CHANGELOG.md` following Keep a Changelog 1.1.0 and Semantic Versioning 2.0.0, mapped from Conventional Commits 1.0.0 (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).

## Linear & Gitflow Governance

- **Branch Naming**: `<type>/<ISSUE-KEY>-<slug>` (e.g., `feat/FAL-53-spec-driven-development-linear-workflow`), branched from `develop` (or `main`/`master` in single-trunk repositories).
- **Conventional Commits**: `<type>(<scope>): <description> (<ISSUE-KEY>)`.
- **3-Stage Consent Gate (Planning & Technical Analysis Only)**:
  1. **Stage 1 (Pre-Render Gate — Zero Mutation)**: Render the full Executive Briefing (`Título Revisado`, `Descrição Atualizada`, and the 5 architectural sections) or proposed issue table directly in chat before calling any question tool or mutating Linear.
  2. **Stage 2 (Interactive Confirmation)**: Prompt the user via native question tool (`ask_question` / `AskUserQuestion`) with a self-contained summary and options `["(Recommended) Sim, aprovar", "Editar..."]`.
  3. **Stage 3 (Atomic Execution)**: Persist changes to Linear via `linear_api.py` using UTF-8 temporary files and idempotent comment deduplication (10-minute window).

## Quality & Security Gates

- **No Secrets in Repository**: `LINEAR_API_KEY` MUST only be read from environment variables or gitignored `.env` files.
- **Pre-Implementation Validation**: `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` and `python skills/linear-workflow/scripts/linear_api.py validate-plan` MUST pass before `/speckit-implement` transitions a card to `In Review`.

## Governance

This Constitution supersedes ad-hoc workflow habits across `fk_apm`. Amendments require updating `.specify/memory/constitution.md` via `/speckit-constitution`, incrementing the semantic version below, and verifying template compatibility across `skills/linear-workflow`.

**Version**: 1.0.0 | **Ratified**: 2026-10-29 | **Last Amended**: 2026-10-29
