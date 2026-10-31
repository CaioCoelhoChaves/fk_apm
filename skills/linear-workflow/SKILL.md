---
name: linear-workflow
description: Synchronize Spec-Driven Development (official github/spec-kit package) and planning tasks with Linear issue tracking across any project and harness (Google Antigravity, Claude Code, Cursor, Copilot, OpenCode). Provides the 10 official /speckit-* lifecycle commands (/speckit-constitution, /speckit-specify, /speckit-clarify, /speckit-plan, /speckit-tasks, /speckit-analyze, /speckit-checklist, /speckit-taskstoissues, /speckit-implement, /speckit-converge) coupled with Linear state transitions (Backlog ➔ Planned ➔ Todo ➔ In Progress ➔ In Review ➔ Done), Living Specs with GitHub Draft PRs opened at spec inception, board synchronization and provisioning (sync-boards, setup-board), isolated execution via ephemeral Git worktrees (.worktrees/<CARD-ID>) requiring mandatory <CARD-ID> arguments, autonomous continuous lifecycle pipeline without in-chat consent gates, centralized GitHub PR review with Living Specs, autonomous implementation (/speckit-implement) and PR review convergence (/speckit-converge), atomic state advancement (advancing to In Review upon PR ready promotion), comment idempotency (10-minute deduplication window), deterministic Markdown sanitization, and manual-only developer transitions for 'Done'.
allowed-tools: Read,Glob,Grep,Bash
---

# Linear Workflow + Official `github/spec-kit`: Spec-Driven Task Tracking & Consent Gate

A standardized workflow for AI coding agents that integrates the official [`github/spec-kit`](https://github.com/github/spec-kit) package (`.specify/` runtime scripts, templates, memory constitution, and the 10 `/speckit-*` commands) directly with Linear issue management, Living Specs with GitHub Draft PRs, and Gitflow PR automation. Supports native Linear MCP servers and provides a standalone zero-dependency Python CLI helper (`scripts/linear_api.py`) for GraphQL API execution, board synchronization (`sync-boards`), board provisioning (`setup-board`), `.specify/` bootstrapping (`bootstrap-specify`), static plan validation (`validate-plan`), and deterministic Markdown sanitization (`sanitize-markdown`).

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

3. **Canonical 6-Stage Lifecycle State Machine & Responsabilidades de Transição**:
   - Enforce the official 6-stage progression:
     `Backlog` (pos 0.0) ➔ `Planned` (pos 1.0) ➔ `Todo` (pos 2.0) ➔ `In Progress` (pos 3.0) ➔ `In Review` (pos 4.0) ➔ `Done` (pos 5.0) (plus `Canceled` at pos 6.0).
   - **Transições Autônomas do Agente (Anti-Estagnação & Zero In-Chat Consent Gates)**:
     - Especificação e Criação de Cards (`/speckit-specify`, `/speckit-taskstoissues`): Cria branch Gitflow, abre Draft PR via `gh pr create --draft`, vincula URL ao card e coloca em **`Backlog`** de forma 100% autônoma.
     - Conclusão do Plano de Arquitetura (`/speckit-plan <CARD-ID>`): Gera `plan.md` (com as 5 seções obrigatórias), `research.md`, `data-model.md`, comita no PR Draft e avança de `Backlog` ➔ **`Planned`** com **Título Revisado** e **Descrição Atualizada** usando `--title`, `--description-file` e `--comment-file` de forma 100% autônoma.
     - Decomposição de Tarefas e Prontidão (`/speckit-tasks <CARD-ID>`): Gera `tasks.md`, valida com `validate-plan`, comita no PR Draft e avança de `Planned` ➔ **`Todo`** com **Título Revisado** e **Descrição Atualizada** usando `--title`, `--description-file` e `--comment-file` de forma 100% autônoma.
     - Início de Implementação (`/speckit-implement <CARD-ID>`): Agente move imediatamente de `Todo` ➔ **`In Progress`** (sem Consent Gate) e executa as tasks.
     - Conclusão de Implementação (`/speckit-implement <CARD-ID>`): Promove o PR de Draft para pronto via `gh pr ready <num>` e move obrigatoriamente de `In Progress` ➔ **`In Review`**.
     - Convergência e Correções de Code Review (`/speckit-converge <CARD-ID>`): Agente move de `In Review` ➔ **`In Progress`** (início da convergência/fix, sem Consent Gate), aplica os fixes na branch, comenta no PR e retorna para **`In Review`**.
   - **Rito Exclusivamente Manual para `Done`**:
     - O estado **`Done`** é de controle **exclusivamente manual pelo desenvolvedor**.
     - O desenvolvedor move manualmente para **`Done`** após revisar o PR no GitHub, validar os testes e realizar o merge. O agente **NUNCA** move o card para `Done`. A CLI rejeita tentativas com erro.

4. **Isolamento Operacional por Git Worktree Efêmero (`.worktrees/<CARD-ID>`)**:
   - Todos os comandos pós-especificação (`/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`) exigem o identificador `<CARD-ID>` obrigatório no formato `^[A-Z]{2,10}-\d+$`.
   - Se o workspace atual não estiver na branch do card, instancia um worktree efêmero em `.worktrees/<CARD-ID>`, executa os artefatos/código, faz commit e push para o remote e remove o worktree ao concluir.

5. **Continuous Autonomous Pipeline & Centralized GitHub Review (Zero In-Chat Consent Gates)**:
   - Toda a esteira de especificação, planejamento e decomposição (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`) opera com **100% de autonomia**:
     - **Zero In-Chat Consent Gates**: O agente NUNCA invoca ferramentas de perguntas síncronas de consentimento (`ask_question`, `AskUserQuestion`) entre as fases técnicas.
     - **Living Specs & Centralized GitHub Review**: A revisão, governança e alinhamento do desenvolvedor ocorrem diretamente no GitHub através do Draft Pull Request criado no início da especificação. O desenvolvedor inspeciona os diffs de Markdown, comenta no PR ou edita diretamente na branch.
     - **Executive Briefing & Links no Chat**: Ao término de cada comando, o agente renderiza no chat um relatório executivo estruturado com links clicáveis diretos para o Pull Request no GitHub, o card no Linear e orientações claras para o próximo comando.
     - **Mutações Atômicas via Arquivos UTF-8**: Todas as alterações de título, descrição ou comentários no Linear utilizam arquivos temporários UTF-8 (`--title`, `--description-file`, `--comment-file`), prevenindo problemas de escape de shell.

6. **Parent Project, Subproject & Tooling Component Labeling**:
   - Detect when a repository represents a subproject of a unified Linear project or a standalone tooling/skills package:
     - **`Front`**: Aplicações e pacotes de interface gráfica (Flutter, React, Vue, Angular, Next.js, Web, Mobile).
     - **`Back`**: Serviços, APIs e servidores de backend (Spring Boot, Node.js API, Java, Python FastAPI/Django/Flask, Go, Rust).
     - **`Feature` ou Sem Tag (Omissão de `--label`)**: Repositórios de tooling, pacotes de skills/prompts de IA (como `fk_apm`), CLIs, automações, bibliotecas agnósticas ou infraestrutura. Nesses repositórios, **não force `Back`** pela mera presença de scripts auxiliares em Python ou Shell; aplique `--label "Feature"` ou omita `--label`.

7. **Comment Idempotency & AIG Compliance**:
   - Prefixo obrigatório `🤖 **AI Agent Update**:`.
   - Janela de desduplicação de 10 minutos para comentários idênticos.

8. **Shell Backtick & Markdown Payload Safety (`--description-file`, `--comment-file`, `--body-file`)**:
   - Nunca passe Markdown inline. Sempre use arquivos UTF-8 e passe por `sanitize_markdown_payload`.

9. **Provisionamento e Sincronização de Boards (`sync-boards` & `setup-board`)**:
   - `python skills/linear-workflow/scripts/linear_api.py sync-boards [--team-id <UUID>] [--dry-run]`: Reconcilia times existentes, migra `Technical Analysis` para `Planned`, e alinha cores/posições.
   - `python skills/linear-workflow/scripts/linear_api.py setup-board --team-id <UUID> [--force]`: Provisiona os 6 estados canônicos (+ Canceled) de forma idempotente.

10. **Cards Operacionais Manuais & Isolamento Total de Código (`/fk-new-manual-issue`)**:
   - Destinado exclusivamente a demandas estritamente operacionais e humanas (registro em serviços, pagamentos, consoles de lojas de aplicativos, alinhamentos).
   - Cria cards no Linear diretamente na coluna `Backlog` com a etiqueta `manual`.
   - **Zero Git Mutations**: Proibição estrita de criar branches Git (`feat/*`), criar worktrees, alterar código ou abrir Pull Requests.
   - Suporta criação individual e em lote via CLI (`--batch-file`). Opera sob o **3-Stage Consent Gate** com Pre-Render Gate tabular no chat.

---

## Official `/speckit-*` Lifecycle Commands Reference

| Comando Oficial | Argumentos | Artefatos Spec Kit | Transição Linear | Modo de Execução |
| :--- | :--- | :--- | :--- | :--- |
| **`/speckit-constitution`** | — | `.specify/memory/constitution.md` | — | Interativo / Governança |
| **`/speckit-specify`** | `<descrição>` | `specs/<feature>/spec.md` | Cria card em **`Backlog`** + Draft PR | **Autônomo (Cria Draft PR e card)** |
| **`/speckit-clarify`** | `<CARD-ID>` | `specs/<feature>/spec.md` | Sync de spec no Draft PR | **Autônomo (Sync git pull rebase)** |
| **`/speckit-plan`** | `<CARD-ID>` | `plan.md`, `research.md`, `data-model.md` | `Backlog` ➔ **`Planned`** | **Autônomo (Avança para Planned)** |
| **`/speckit-tasks`** | `<CARD-ID>` | `specs/<feature>/tasks.md` | `Planned` ➔ **`Todo`** | **Autônomo (Avança para Todo)** |
| **`/speckit-analyze`** | `[<CARD-ID>]` | Relatório de consistência | — | Auditoria estática read-only |
| **`/speckit-checklist`** | `[<CARD-ID>]` | `checklists/<domain>.md` | — | Checklist de qualidade de requisitos |
| **`/speckit-taskstoissues`**| `[<CARD-ID>]` | `tasks.md` ➔ Sub-cards | Cria sub-cards em **`Backlog`** | **Autônomo (Cria sub-cards)** |
| **`/speckit-implement`** | `<CARD-ID>` | Executa `tasks.md` (`[X]`) | `Todo` ➔ **`In Progress`** ➔ **`In Review`** | **Autônomo (SEM Consent Gate)** |
| **`/speckit-converge`** | `<CARD-ID>` | Fixes de review em `tasks.md` | `In Review` ➔ **`In Progress`** ➔ **`In Review`** | **Autônomo (SEM Consent Gate)** |
| **`/fk-new-manual-issue`** | `[<descrição>]` | — | Cria card(s) em **`Backlog`** com tag `manual` | **3-Stage Consent Gate** (Zero Git / Zero PR) |
