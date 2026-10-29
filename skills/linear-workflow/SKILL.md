---
name: linear-workflow
description: Synchronize Spec-Driven Development (official github/spec-kit package) and planning tasks with Linear issue tracking across any project and harness (Google Antigravity, Claude Code, Cursor, Copilot, OpenCode). Provides the 10 official /speckit-* lifecycle commands (/speckit-constitution, /speckit-specify, /speckit-clarify, /speckit-plan, /speckit-tasks, /speckit-analyze, /speckit-checklist, /speckit-taskstoissues, /speckit-implement, /speckit-converge) coupled with Linear state transitions, the mandatory 3-stage Consent Gate with Pre-Render Gate for specification/planning (/speckit-specify, /speckit-plan, /speckit-tasks, /speckit-taskstoissues), autonomous implementation (/speckit-implement) and PR review convergence (/speckit-converge), atomic state advancement (advancing to In Review upon PR opening), comment idempotency (10-minute deduplication window), deterministic Markdown sanitization, and manual-only developer transitions for 'Done'.
allowed-tools: Read,Glob,Grep,Bash
---

# Linear Workflow + Official `github/spec-kit`: Spec-Driven Task Tracking & Consent Gate

A standardized workflow for AI coding agents that integrates the official [`github/spec-kit`](https://github.com/github/spec-kit) package (`.specify/` runtime scripts, templates, memory constitution, and the 10 `/speckit-*` commands) directly with Linear issue management and Gitflow PR automation. Supports native Linear MCP servers and provides a standalone zero-dependency Python CLI helper (`scripts/linear_api.py`) for GraphQL API execution, `.specify/` bootstrapping (`bootstrap-specify`), static plan validation (`validate-plan`), and deterministic Markdown sanitization (`sanitize-markdown`).

---

## Core Non-Negotiable Standards

1. **Zero Hardcoded Secrets & Dynamic Credential Resolution**:
   - Never hardcode tokens or API keys into prompts, code, or configuration files.
   - Dynamically discover credentials in priority order:
     1. Linear MCP server tools (`linear_issue_search`, `linear_create_issue`, etc.), if present.
     2. Environment variable: `LINEAR_API_KEY` or `LINEAR_TOKEN`.
     3. Project-level `.linear.json`, `.linearrc`, or `.env`.
   - If no credentials exist, warn the user once and continue the development task without blocking.

2. **Non-Blocking Project Fallback**:
   - If the project does not exist in Linear, **never halt or abort** the user's task.
   - Proceed with Spec Kit specification, planning, or implementation normally.
   - Inform the user clearly at the start or completion that the project is not tracked in Linear.

3. **Lifecycle State Machine & Responsabilidades de Transição**:
   - Enforce the official state progression:
     `Backlog` ➔ `Technical Analysis` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done` (plus `Canceled` or `Duplicate`).
   - **Transições do Agente (Anti-Estagnação)**:
     - Especificação e Criação de Cards (`/speckit-specify`, `/speckit-taskstoissues`): Agente gera `specs/<feature>/spec.md` e cria o(s) card(s) em **`Backlog`** (após Consent Gate em 3 etapas).
     - Conclusão de Análise Técnica e Plano (`/speckit-plan` + `/speckit-tasks`): Agente gera `plan.md` e `tasks.md`, valida com `validate-plan` e move de `Technical Analysis` / `Backlog` ➔ **`Todo`** com comentário estruturado (após Consent Gate em 3 etapas).
     - Início de Implementação (`/speckit-implement`): Agente move imediatamente de `Todo` ➔ **`In Progress`** (sem Consent Gate) e cria a branch Gitflow.
     - Conclusão de Implementação (PR Aberto em `/speckit-implement`): Agente move obrigatoriamente de `In Progress` ➔ **`In Review`** com link do PR e sumário técnico.
     - Convergência e Correções de Code Review (`/speckit-converge`): Agente move de `In Review` ➔ **`In Progress`** (início da convergência/fix, sem Consent Gate) ➔ **`In Review`** (após commits, push e comentário no PR).
   - **Rito Exclusivamente Manual a partir de `In Review`**:
     - A partir de **`In Review`**, o controle é **exclusivamente manual pelo desenvolvedor**.
     - **`Done`**: O desenvolvedor move manualmente para **`Done`** após revisar o PR no GitHub, validar os testes e realizar o merge. O agente **NUNCA** move o card para `Done`.

4. **Mandatory 3-Stage Protocol (*Consent Gate*) for Specification/Planning & Autonomous Execution Exception**:
   - For specification, planning, and task decomposition commands (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`), the agent must strictly follow this protocol across all harnesses:
     - **Stage 1 (Initial Presentation, Pre-Render Gate & Questions)**: The agent prepares the spec/plan/tasks in workspace and chat, raising options and doubts with the developer. **Zero mutation**: No API calls altering Linear (`update-issue`, `create-issue`, `create-comment`) are permitted in this stage. Only read queries (`get-issue`, `search-issues`, `list-states`, `list-projects`) are allowed. **Pre-Render Gate (Proibição de Consent Gate Cego)**: It is **strictly forbidden** to invoke `ask_question` / `AskUserQuestion` without first rendering the complete proposal (full task/card decomposition table in `/speckit-specify` / `/speckit-taskstoissues`, or the **Título Revisado**, **Descrição Atualizada**, and all **5 mandatory sections** Executive Briefing in `/speckit-plan` / `/speckit-tasks`) in the visible text of the chat message.
     - **Stage 2 (Consent Gate - Interactive Prompt with Concise Summary & Options)**: After rendering the full proposal visibly in chat and resolving questions, the agent presents the consent confirmation using the **native question tool** of the active harness (`ask_question` in Antigravity, `AskUserQuestion` in Claude Code / Cursor / Copilot), embedding a **concise summary of the plan/analysis directly inside the `question` field**:
       - **Opções Estruturadas**:
         1. `(Recommended) Sim, aprovar`: Avança atomicamente para a Stage 3.
         2. `Editar...`: Permite texto livre para o desenvolvedor informar o que deseja ajustar. O agente recebe o feedback, **retorna à Stage 1**, ajusta os artefatos em `specs/<feature>/` e apresenta novamente antes de acionar um novo Consent Gate.
     - **Stage 3 (Atomic Execution - Move Card + Update Title/Description + Register Comment)**: Only after affirmative developer response (`Sim, aprovar`), execute the closing actions atomically on Linear (`create-issue` with `--description-file` or `update-issue` with `--state "Todo"`, `--title`, `--description-file`, and `--comment-file`).
   - ⚠️ **Execução Autônoma para `/speckit-implement` e `/speckit-converge` (Sem Consent Gate)**:
     - Os comandos de implementação (`/speckit-implement`) e convergência/review fix (`/speckit-converge`) rodam **sem Consent Gate**.
     - **`/speckit-implement`**: Ao ser invocado, o agente lê `specs/<feature>/tasks.md` e `plan.md`, transiciona imediatamente o card para `In Progress`, cria a branch Gitflow, implementa todas as tasks marcando `[X]`, executa os testes e avança o card para `In Review` ao abrir o PR no GitHub. Dúvidas devem ser levantadas ao desenvolvedor somente em casos excepcionais de bloqueio real; se não for bloqueante, o agente decide tecnicamente, registra a premissa assumida e prossegue.
     - **`/speckit-converge`**: Lê o feedback de review do PR aberto (e/ou lacunas de convergência entre `spec.md`, `plan.md`, `tasks.md` e o código), move o card para `In Progress`, adiciona/executa as tasks corretivas na branch existente, comenta no PR e retorna o card para `In Review` sem requerer aprovação prévia.

5. **Comment Idempotency & AIG Compliance**:
   - In accordance with Linear's official [Agent Interaction Guidelines (AIG)](https://linear.app/developers/agents):
     - Clearly signal agent identity: prefix all comments with `🤖 **AI Agent Update**:`.
     - Align with Linear Git automation: use the standard branch format `<type>/<identifier>-<slug>` (e.g. `feat/FAL-53-spec-driven-development-linear-workflow`).
     - **Idempotency Protection**: `scripts/linear_api.py` inspects recent card comments to prevent duplicate comments with identical body/payload within a 10-minute window.

6. **Parent Project, Subproject & Tooling Component Labeling**:
   - Detect when a repository represents a subproject of a unified Linear project or a standalone tooling/skills package:
     - **`Front`**: Aplicações e pacotes de interface gráfica (Flutter, React, Vue, Angular, Next.js, Web, Mobile).
     - **`Back`**: Serviços, APIs e servidores de backend (Spring Boot, Node.js API, Java, Python FastAPI/Django/Flask, Go, Rust).
     - **`Feature` ou Sem Tag (Omissão de `--label`)**: Repositórios de tooling, pacotes de skills/prompts de IA (como `fk_apm`), CLIs, automações, bibliotecas agnósticas ou infraestrutura. Nesses repositórios, **não force `Back`** pela mera presença de scripts auxiliares em Python ou Shell; aplique `--label "Feature"` ou omita `--label`.

7. **Shell Backtick & Markdown Payload Safety (`--description-file`, `--comment-file`, `--body-file`)**:
   - **Mandatory File-First Standard**: Write Markdown descriptions, comments, and PR bodies to temporary UTF-8 files and pass `--description-file "<path>"`, `--comment-file "<path>"`, and `--body-file "<path>"`.
   - **Deterministic Markdown Sanitizer (`sanitize_markdown_payload`)**: `scripts/linear_api.py` automatically runs `sanitize_markdown_payload` on all descriptions and comments before GraphQL execution (and exposes the `sanitize-markdown` CLI subcommand), normalizing `\r\n` to `\n`, stripping invalid ASCII control characters, aligning Markdown table pipes, and auto-closing unclosed fenced code blocks (```` ``` ````).
   - **Explicit Prohibition**: **Never** pass Markdown containing backticks (`` ` ``), code blocks, or double quotes directly via inline `--description "..."`, `--comment "..."`, or `--body "..."`.

8. **Official `github/spec-kit` Architecture (`.specify/` & `specs/<feature>/`)**:
   - **Bundled `.specify/` Runtime & Bootstrap**:
     - The official `github/spec-kit` runtime (`.specify/scripts/python/*.py`, `.specify/scripts/powershell/*.ps1`, `.specify/templates/*.md`, `.specify/memory/constitution.md`, `.specify/workflows/`) lives at `<repo-root>/.specify/` and is bundled inside `skills/linear-workflow/assets/.specify/`.
     - In any consumer repository where `.specify/` is not yet initialized, run `python skills/linear-workflow/scripts/linear_api.py bootstrap-specify` to install `.specify/` without overwriting an existing `constitution.md`.
   - **Repository Constitution (`.specify/memory/constitution.md`)**: Architectural principles and governance constraints live in `.specify/memory/constitution.md` (managed via `/speckit-constitution`).
   - **Feature Artifacts (`specs/<feature>/` & `.specify/feature.json`)**:
     - `specs/<feature>/spec.md`: User stories (P1, P2, P3...), functional requirements (`FR-###`), success criteria (`SC-###`), and acceptance scenarios (created by `/speckit-specify` and refined by `/speckit-clarify`).
     - `specs/<feature>/plan.md`: Implementation plan containing `Summary`, `Technical Context`, `Constitution Check`, and the **5 Mandatory Linear Sections** (`1. Diagnóstico e Contexto`, `2. Arquitetura da Solução & Desenho Técnico`, `3. Checklist de Arquivos Impactados`, `4. Estratégia de Testes`, `5. Plano Gitflow`), generated by `/speckit-plan`.
     - `specs/<feature>/tasks.md`: Dependency-ordered implementation checklist (`- [ ] T001 [P] [US1] ...`) generated by `/speckit-tasks`, executed by `/speckit-implement`, and extended by `/speckit-converge`.
     - `specs/<feature>/checklists/`: Requirement quality checklists (`requirements.md` and domain checklists via `/speckit-checklist`).
   - **Static Validation (`check_prerequisites.py` & `validate-plan`)**:
     - Run `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` and `python skills/linear-workflow/scripts/linear_api.py validate-plan --issue-key <issue-key>` before advancing a card to `Todo` or `In Review`.

---

## Official `/speckit-*` Lifecycle Commands Reference (Replaces `/fk-*`)

| Official Command | Legacy Equivalent | Spec Kit Artifacts | Linear State Transition | Execution Mode |
| :--- | :--- | :--- | :--- | :--- |
| **`/speckit-constitution`** | — | `.specify/memory/constitution.md` | — | Interactive / Governance |
| **`/speckit-specify`** | `/fk-new-issue` | `specs/<feature>/spec.md`, `checklists/requirements.md` | Cria card(s) em **`Backlog`** | **3-Stage Consent Gate** (com Pre-Render Gate) |
| **`/speckit-clarify`** | — | Atualiza `specs/<feature>/spec.md` | Sincroniza descrição do card (se aplicável) | Perguntas estruturadas (máx. 5) |
| **`/speckit-plan`** | `/fk-technical-analysis` (Fase 1) | `specs/<feature>/plan.md`, `research.md`, `data-model.md`, `quickstart.md` | Prepara análise técnica com as 5 seções obrigatórias | **3-Stage Consent Gate** (ao avançar para `Todo`) |
| **`/speckit-tasks`** | `/fk-technical-analysis` (Fase 2) | `specs/<feature>/tasks.md` | `Technical Analysis` / `Backlog` ➔ **`Todo`** | **3-Stage Consent Gate** (com Pre-Render Gate & `validate-plan`) |
| **`/speckit-analyze`** | — | Relatório de consistência read-only | — | Auditoria estática entre `spec.md`, `plan.md`, `tasks.md` e `constitution.md` |
| **`/speckit-checklist`** | — | `specs/<feature>/checklists/<domain>.md` | — | Checklist de qualidade de requisitos |
| **`/speckit-taskstoissues`** | `/fk-new-issue` (de `tasks.md`) | `specs/<feature>/tasks.md` ➔ Issues | Cria cards atômicos em **`Backlog`** | **3-Stage Consent Gate** |
| **`/speckit-implement`** | `/fk-develop` | Executa `tasks.md` (`- [X]`) | `Todo` ➔ **`In Progress`** ➔ **`In Review`** | **Autônomo (SEM Consent Gate)** |
| **`/speckit-converge`** | `/fk-fix` | `tasks.md` (`## Phase N: Convergence`) | `In Review` ➔ **`In Progress`** ➔ **`In Review`** | **Autônomo (SEM Consent Gate)** |
| *(Transição Manual)* | — | Merge do PR | `In Review` ➔ **`Done`** | **Exclusivamente Manual pelo Desenvolvedor** |

> **Compatibilidade Sintática**: Se o usuário invocar os nomes legados (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`, `/fk-fix`) ou comandos em linguagem natural, mapeie automaticamente para o comando `/speckit-*` correspondente acima.

---

## Tool Execution Matrix (Spec Kit CLI + Linear CLI/MCP)

| Operation | Spec Kit Python Script (`.specify/scripts/python/`) | Linear CLI (`python skills/linear-workflow/scripts/linear_api.py`) |
| :--- | :--- | :--- |
| **Bootstrap `.specify/`** | — | `python <skill-dir>/scripts/linear_api.py bootstrap-specify` |
| **Create Feature Spec** | `python .specify/scripts/python/create_new_feature.py --json --number <N> --short-name "<slug>" "<desc>"` | `python <skill-dir>/scripts/linear_api.py create-issue --team-id "<tid>" --project-id "<pid>" --title "<title>" --state "Backlog" --description-file "<path>"` |
| **Setup Plan** | `python .specify/scripts/python/setup_plan.py --json` | `python <skill-dir>/scripts/linear_api.py get-issue "<key-or-id>"` |
| **Setup Tasks** | `python .specify/scripts/python/setup_tasks.py --json` | `python <skill-dir>/scripts/linear_api.py validate-plan --issue-key "<key>"` |
| **Check Prerequisites** | `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks` | — |
| **Atomic Update** | — | `python <skill-dir>/scripts/linear_api.py update-issue "<id>" [--state "<state>"] [--title "<title>"] [--description-file "<path>"] [--comment-file "<path>"]` |
| **Sanitize Markdown** | — | `python <skill-dir>/scripts/linear_api.py sanitize-markdown "<file.md>" [--in-place]` |

---

## References

- [references/multi-harness-commands.md](references/multi-harness-commands.md) for cross-harness architecture (Antigravity, Claude, Cursor, Copilot, OpenCode) and APM primitives.
- [references/states-and-labels.md](references/states-and-labels.md) for full state definitions, subproject rules, and AIG compliance.
- [references/configuration.md](references/configuration.md) for API key setup and MCP integration.
- [github/spec-kit Official Repository](https://github.com/github/spec-kit)
- [Linear Developers: Agent Interaction Guidelines (AIG)](https://linear.app/developers/agents)
