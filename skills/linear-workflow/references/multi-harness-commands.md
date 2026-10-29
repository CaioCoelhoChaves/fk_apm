# Multi-Harness Command Architecture & Routing Reference (`github/spec-kit` + Linear)

This reference documents how the official `github/spec-kit` commands (`speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-taskstoissues`, `speckit-implement`, `speckit-converge`) coupled with Linear lifecycle transitions operate across multiple AI coding harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, and OpenCode) through APM primitives.

---

## 1. APM Primitives Mapping (`skills/linear-workflow/`)

To guarantee consistent behavior across harnesses and distribute the official `github/spec-kit` package inside `bundles/default`, `skills/linear-workflow/` organizes its assets as follows:

```
skills/linear-workflow/
├── .apm/
│   ├── instructions/
│   │   └── linear-lifecycle-commands.instructions.md  # Global rule interceptor
│   ├── prompts/
│   │   ├── speckit-constitution.prompt.md
│   │   ├── speckit-specify.prompt.md
│   │   ├── speckit-clarify.prompt.md
│   │   ├── speckit-plan.prompt.md
│   │   ├── speckit-tasks.prompt.md
│   │   ├── speckit-analyze.prompt.md
│   │   ├── speckit-checklist.prompt.md
│   │   ├── speckit-taskstoissues.prompt.md
│   │   ├── speckit-implement.prompt.md
│   │   └── speckit-converge.prompt.md
│   └── skills/
│       ├── speckit-constitution/SKILL.md
│       ├── speckit-specify/SKILL.md
│       ├── speckit-clarify/SKILL.md
│       ├── speckit-plan/SKILL.md
│       ├── speckit-tasks/SKILL.md
│       ├── speckit-analyze/SKILL.md
│       ├── speckit-checklist/SKILL.md
│       ├── speckit-taskstoissues/SKILL.md
│       ├── speckit-implement/SKILL.md
│       └── speckit-converge/SKILL.md
├── assets/
│   └── .specify/                                      # Bundled github/spec-kit runtime
├── SKILL.md                                           # Core workflow engine
└── scripts/
    └── linear_api.py                                  # Zero-dependency Linear & Spec Kit CLI
```

### Deployment Targets:
- **Google Antigravity (`agy`)**:
  - `skills/` promoted to `.agents/skills/speckit-*/SKILL.md` (native slash commands `/speckit-*`).
  - `instructions/` compiled to `.agents/rules/` and `AGENTS.md`.
- **Claude Code**: `.claude/commands/` and rules in `.claude/rules/`.
- **Cursor**: `.cursor/commands/` and rules in `.cursor/rules/`.
- **GitHub Copilot**: `.github/prompts/speckit-*.prompt.md` and instructions in `.github/instructions/`.

---

## 2. Command Routing & Syntactic Tolerance Standard

| Official `/speckit-*` Command | Legacy `/fk-*` Alias | Linear Lifecycle Role | Consent Gate |
| :--- | :--- | :--- | :--- |
| `/speckit-specify` | `/fk-new-issue` | Create `specs/<feature>/spec.md` & create Linear card(s) in **`Backlog`** | **3-Stage Consent Gate** |
| `/speckit-clarify` | — | Resolve up to 5 ambiguities in `spec.md` & sync Linear description | Interactive Q&A |
| `/speckit-plan` | `/fk-technical-analysis` (Phase 1) | Generate `plan.md` (with 5 mandatory Linear sections), `research.md`, `data-model.md` | **3-Stage Consent Gate** (when advancing to `Todo`) |
| `/speckit-tasks` | `/fk-technical-analysis` (Phase 2) | Generate `tasks.md`, run `validate-plan`, and advance Linear card to **`Todo`** | **3-Stage Consent Gate** |
| `/speckit-taskstoissues` | `/fk-new-issue` (from `tasks.md`) | Convert `tasks.md` items/phases into atomic Linear cards in **`Backlog`** | **3-Stage Consent Gate** |
| `/speckit-implement` | `/fk-develop` | Move card to **`In Progress`**, create Gitflow branch, execute `tasks.md`, open PR, move card to **`In Review`** | **Autonomous (NO Consent Gate)** |
| `/speckit-converge` | `/fk-fix` | Read PR review feedback & spec gaps, move card to **`In Progress`**, fix on PR branch, comment on PR, return card to **`In Review`** | **Autonomous (NO Consent Gate)** |
| `/speckit-constitution` | — | Author/amend `.specify/memory/constitution.md` | Interactive |
| `/speckit-analyze` | — | Read-only consistency check across `spec.md`, `plan.md`, `tasks.md`, and `constitution.md` | Read-Only |
| `/speckit-checklist` | — | Generate domain requirements checklists under `specs/<feature>/checklists/` | Interactive |

---

## 3. Multi-Harness Interactive Consent Gate Protocol

### Behavioral Guarantee & Zero Mutation
- **Zero Mutation in Stage 1**: Linear state updates (`update-issue`), comment creation, and card creation (`create-issue`) are strictly forbidden prior to explicit developer confirmation in Stage 2.
- **Stage 1 (Pre-Render Gate)**: Render the full proposal visibly in the chat message before calling any question tool — either the complete card decomposition table in `/speckit-specify` / `/speckit-taskstoissues` or the **Executive Briefing** (`Título Revisado`, `Descrição Atualizada`, and the 5 mandatory sections) in `/speckit-plan` / `/speckit-tasks`.
- **Stage 2 (Interactive Consent Gate with Embedded Summary)**: Invoke the native question tool (`ask_question` / `AskUserQuestion`) with a concise summary embedded inside `question` and options `["(Recommended) Sim, aprovar", "Editar..."]`.
- **Stage 3 (Atomic Execution)**: On affirmative answer, execute Linear CLI mutations using UTF-8 temporary files (`--description-file`, `--comment-file`), automatically sanitized by `sanitize_markdown_payload`.
