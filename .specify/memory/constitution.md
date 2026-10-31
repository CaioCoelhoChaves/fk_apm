<!--
Sync Impact Report
- Version change: 1.1.0 -> 1.2.0
- Ratified Continuous Autonomous Spec Kit Pipeline across all lifecycle phases (/speckit-specify, /speckit-plan, /speckit-tasks, /speckit-taskstoissues, /speckit-implement, /speckit-converge)
- Eliminated synchronous in-chat Consent Gates between phases, centralizing review and governance on GitHub Living Spec Draft PRs
- Ratified remote Git rebase synchronization in /speckit-clarify (git pull --rebase origin <branch>)
- Reaffirmed strictly manual Done transition safeguard by human developer after PR merge
-->

# fk_apm Constitution

## Core Principles

### I. Multi-Harness Parity & Bundled Distribution
Every skill and workflow distributed in `fk_apm` MUST maintain functional parity across supported AI coding harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, and OpenCode). Runtime assets (including `.specify/` scripts, templates, and `linear_api.py`) MUST be self-contained and cross-platform (Windows PowerShell and POSIX shells via Python 3.8+ standard library scripts).

### II. Living Specs, Continuous Autonomous Pipeline & 6-Stage State Machine (Official `github/spec-kit` Integration)
All planning, specification, technical analysis, implementation, and review convergence MUST flow through the official `github/spec-kit` artifact pipeline (`specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `checklists/`) coupled with Linear issue state transitions, Living Specs via GitHub Draft PRs, and ephemeral worktree isolation:
- `/speckit-specify <descrição>`: Creates Gitflow branch, opens GitHub Draft PR (`gh pr create --draft`), links PR URL in Linear card, and places card in `Backlog` autonomously without in-chat consent gates.
- `/speckit-clarify <CARD-ID>`: Mandatory `<CARD-ID>` argument, executes in ephemeral worktree (`.worktrees/<CARD-ID>`), synchronizes remote developer modifications via `git pull --rebase origin <branch>`, resolves ambiguities, and pushes spec commits to the Draft PR.
- `/speckit-plan <CARD-ID>`: Mandatory `<CARD-ID>` argument, executes in ephemeral worktree, generates `plan.md` (with 5 mandatory sections), `research.md`, `data-model.md`, `quickstart.md`, pushes commits to Draft PR, and advances card from `Backlog` ➔ `Planned` autonomously without in-chat consent gates.
- `/speckit-tasks <CARD-ID>`: Mandatory `<CARD-ID>` argument, executes in ephemeral worktree, generates `tasks.md`, validates with `validate-plan`, pushes commits to Draft PR, and advances card from `Planned` ➔ `Todo` autonomously without in-chat consent gates.
- `/speckit-implement <CARD-ID>`: Mandatory `<CARD-ID>` argument, autonomous execution without Consent Gate: moves card from `Todo` ➔ `In Progress`, executes `tasks.md` marking items `[X]`, runs tests, promotes PR to ready (`gh pr ready`), and advances card to `In Review`.
- `/speckit-converge <CARD-ID>`: Mandatory `<CARD-ID>` argument, autonomous execution without Consent Gate: moves card from `In Review` ➔ `In Progress`, applies PR review fixes on PR branch, pushes commits, comments on PR, and returns card to `In Review`.
- `Done` transitions are strictly manual by the developer after merging the PR. Agents and tools MUST NOT move cards to `Done`.

### III. Zero Shell-Escaping Corruption (File-First Payloads)
Agents and CLI scripts MUST NEVER pass multi-line Markdown or strings containing backticks (`` ` ``) or quotes inline via shell arguments (`--description "..."`, `--comment "..."`, `--body "..."`). All Linear mutations and GitHub PR operations MUST use UTF-8 file-based flags (`--description-file`, `--comment-file`, `--body-file`) and pass through `sanitize_markdown_payload()` in `linear_api.py`.

### IV. Deterministic Verification & Test Coverage (NON-NEGOTIABLE)
Every modification to CLI scripts (`linear_api.py`, `.specify/scripts/python/*.py`), skill contracts, or bundle manifests MUST be accompanied by deterministic automated unit tests (`unittest`) and validated with `apm compile` / `apm install` before opening or updating a Pull Request.

### V. Semantic Versioning & Keep a Changelog
All notable changes MUST be recorded under `## [Unreleased]` in `CHANGELOG.md` following Keep a Changelog 1.1.0 and Semantic Versioning 2.0.0, mapped from Conventional Commits 1.0.0 (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).

## Linear & Gitflow Governance

- **Branch Naming**: `<type>/<CARD-ID>-<slug>` (e.g., `feat/FAL-58-modernizar-linear-workflow-draft-prs`), branched from `develop` (or `main`/`master` in single-trunk repositories).
- **Conventional Commits**: `<type>(<scope>): <description> (<CARD-ID>)`.
- **Continuous Autonomous Pipeline & Centralized GitHub Review**:
  1. **Zero In-Chat Consent Gates**: Lifecycle commands execute autonomously without synchronous question gates (`ask_question` / `AskUserQuestion`).
  2. **Living Specs on GitHub**: Review and validation are conducted by the developer directly on the GitHub Draft PR via code diffs, Markdown previews, and PR discussions.
  3. **Atomic State Advancement**: Linear state transitions (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`) occur via `linear_api.py` using UTF-8 temporary files and idempotent comment deduplication (10-minute window).
  4. **Strict Manual Done Safeguard**: The transition to `Done` is exclusively manual by the developer after merging the PR.

## Quality & Security Gates

- **No Secrets in Repository**: `LINEAR_API_KEY` MUST only be read from environment variables or gitignored `.env` files.
- **Pre-Implementation Validation**: `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` and `python skills/linear-workflow/scripts/linear_api.py validate-plan <CARD-ID>` MUST pass before `/speckit-implement` transitions a card to `In Review`.

## Governance

This Constitution supersedes ad-hoc workflow habits across `fk_apm`. Amendments require updating `.specify/memory/constitution.md` via `/speckit-constitution`, incrementing the semantic version below, and verifying template compatibility across `skills/linear-workflow`.

**Version**: 1.2.0 | **Ratified**: 2026-10-31 | **Last Amended**: 2026-10-31
