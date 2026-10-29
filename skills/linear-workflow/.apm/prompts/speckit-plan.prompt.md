---
name: "speckit-plan"
description: "Execute the Spec Kit implementation planning workflow (specs/<feature>/plan.md, research.md, data-model.md) coupled with Linear Technical Analysis (5 mandatory sections & 3-Stage Consent Gate to Todo). coupled with Linear Technical Analysis & Planned state."
compatibility: "Requires spec-kit project structure with .specify/ directory and linear-workflow CLI"
metadata:
  author: "github-spec-kit + fk_apm"
  source: "templates/commands/plan.md"
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before planning)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_plan` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

### Mandatory `<CARD-ID>` Validation & Ephemeral Worktree Isolation
- The user **MUST** provide `<CARD-ID>` (e.g. `/speckit-plan FAL-58`).
- If `<CARD-ID>` is missing or invalid (`^[A-Z]{2,10}-\d+$`), **ABORT** immediately:
  `Uso obrigatório: /speckit-plan <CARD-ID>`
- If current workspace is not on the card's branch (`feat/<CARD-ID>-*`), execute in ephemeral worktree `.worktrees/<CARD-ID>`.

1. **Setup**: Run `python3 .specify/scripts/python/setup_plan.py --json` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, FEATURE_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `.specify/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Re-evaluate Constitution Check post-design

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_plan`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_plan` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- When constructing command invocations from hook command names, replace dots (`.`) with hyphens (`-`). For example, `speckit.git.commit` → `/speckit-git-commit`.
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Linear Technical Analysis Integration & 5 Mandatory Sections (`plan.md`)

> **Cross-Platform Python Execution**: On Windows, `python` is preferred over `python3` (`python .specify/scripts/python/setup_plan.py --json`). If `.specify/` is missing in a consumer repo, run `python skills/linear-workflow/scripts/linear_api.py bootstrap-specify` first.

When `/speckit-plan` is executed for a Linear issue (`FAL-XX` or any `<TEAM>-<NUMBER>`, replacing `/fk-technical-analysis`):

1. **Query Linear Card Context**:
   - Run `python skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"` to inspect the current title, description, labels, state, and comments.
   - Ensure `specs/<feature>/spec.md` exists (if not, create/initialize it via `.specify/scripts/python/create_new_feature.py` using the Linear issue number and slug).

2. **Include the 5 Mandatory Architectural Sections in `IMPL_PLAN` (`plan.md`)**:
   In addition to `Summary`, `Technical Context`, and `Constitution Check`, `plan.md` **MUST** include these 5 sections (verified by `linear_api.py validate-plan`):
   - `## 1. Diagnóstico e Contexto`: Root cause or architectural context based on codebase inspection.
   - `## 2. Arquitetura da Solução & Desenho Técnico`: Data flow, contracts, patterns, and design decisions.
   - `## 3. Checklist de Arquivos Impactados`: Real repository file paths to create, modify, or remove (`- [ ] path/to/file.ext`).
   - `## 4. Estratégia de Testes`: Unit, integration, and contract tests to add/run.
   - `## 5. Plano Gitflow`: Target branch `<type>/<issue-key>-<slug>` and base branch (`develop` or `main`).

3. **Advance Card to `Planned` via 3-Stage Consent Gate**:
   - Commit the generated plan artifacts (`plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`) to the Draft PR: `git commit -m "docs(plan): technical plan and architecture for <CARD-ID>"` and `git push`.
   - Advance the Linear card from `Backlog` ➔ **`Planned`** executing the **3-Stage Consent Gate**:
     - **Stage 1 (Pre-Render Gate — Zero Mutation on Linear)**: Output in chat the **Executive Briefing** containing **Título Revisado**, **Descrição Atualizada**, and the 5 mandatory architectural sections **before** calling any question tool.
     - **Stage 2 (Interactive Confirmation)**: Call `ask_question` / `AskUserQuestion` with a self-contained summary embedded in `question` and options `["(Recommended) Sim, aprovar", "Editar..."]`.
     - **Stage 3 (Atomic Execution on Linear)**: Write the updated description and Executive Briefing comment to UTF-8 temporary files and execute:
       ```bash
       python skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
         --state "Planned" \
         --title "<titulo-revisado>" \
         --description-file ".tmp-plan-desc.md" \
         --comment-file ".tmp-plan-briefing.md"
       ```
   - Suggest next step: `Próximo passo: /speckit-tasks <CARD-ID>`

## Completion Report

Command ends after Phase 1 design. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

3. **Create quickstart validation guide** → `quickstart.md`:
   - Document runnable validation scenarios that prove the feature works end-to-end
   - Include prerequisites, setup commands, test/run commands, and expected outcomes
   - Use links or references to contracts and data model details instead of duplicating them
   - Do not include full implementation code, model/service/controller bodies, migrations, or complete test suites
   - Keep this artifact as a validation/run guide; implementation details belong in `tasks.md` and the implementation phase

**Output**: data-model.md, /contracts/*, quickstart.md

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation
- ERROR on gate failures or unresolved clarifications

## Done When

- [ ] Plan workflow executed and design artifacts generated
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported to user with branch, plan path, and generated artifacts

