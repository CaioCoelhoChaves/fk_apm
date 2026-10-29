# Implementation Plan: Official `github/spec-kit` Integration with Linear Workflow & Markdown Sanitization (`FAL-53`)

**Branch**: `feat/FAL-53-spec-driven-development-linear-workflow` (`053-fal-53-spec-kit-linear-workflow`) | **Date**: 2026-10-29 | **Spec**: [spec.md](file:///C:/Users/caioc/Projects/fk_packages/fk_apm/specs/053-fal-53-spec-kit-linear-workflow/spec.md)

**Input**: Feature specification from `/specs/053-fal-53-spec-kit-linear-workflow/spec.md`

## Summary

Integrate the official `github/spec-kit` package (`.specify/` runtime scripts, templates, memory constitution, and the 10 `speckit-*` Antigravity/APM skills) directly into `skills/linear-workflow` (and therefore into `bundles/default`), replacing the legacy `/fk-*` commands (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`, `/fk-fix`) with `/speckit-*` commands coupled with Linear card state transitions (`Backlog`, `Todo`, `In Progress`, `In Review`), the 3-Stage Consent Gate with Pre-Render Gate, and `sanitize_markdown_payload()` in `linear_api.py`.

## Technical Context

**Language/Version**: Python 3.8+ (standard library only for `linear_api.py` and `.specify/scripts/python/*.py`) + Markdown/YAML (APM skills and prompts)

**Primary Dependencies**: `github/spec-kit` (`specify-cli` v0.7.0 scaffolded `.specify/` runtime), Linear GraphQL API (`linear_api.py`), GitHub CLI (`gh`), APM CLI (`apm-cli`)

**Storage**: File-based (`specs/<feature>/spec.md`, `plan.md`, `tasks.md`, `.specify/feature.json`, `.specify/memory/constitution.md`)

**Testing**: Python `unittest` (`skills/linear-workflow/tests/test_linear_api.py`)

**Target Platform**: Cross-platform (Windows PowerShell & POSIX shells across Antigravity, Claude Code, Cursor, GitHub Copilot, OpenCode)

**Project Type**: AI Agent Skills & Bundles Monorepo (`fk_apm`)

**Performance Goals**: Zero external pip dependency overhead at runtime (`urllib.request` + stdlib); deterministic CLI execution `< 1s` for local validation scripts.

**Constraints**: Zero inline multi-line Markdown in shell commands (`--description-file`, `--comment-file`, `--body-file` mandatory); `Done` column transition strictly manual by the developer.

**Scale/Scope**: 10 `speckit-*` sub-skills inside `skills/linear-workflow`, `.specify/` runtime assets, `linear_api.py` CLI enhancements, and unit test suite.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Multi-Harness Parity & Bundled Distribution**: PASS — `.specify/scripts/python/` and `skills/linear-workflow/assets/.specify/` provide cross-platform Python scripts and templates distributed via `bundles/default`.
- **II. Spec-Driven Linear Lifecycle**: PASS — `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`, `/speckit-checklist`, `/speckit-taskstoissues`, `/speckit-implement`, `/speckit-converge`, and `/speckit-constitution` replace `/fk-*` and enforce Linear state transitions.
- **III. Zero Shell-Escaping Corruption**: PASS — `sanitize_markdown_payload()` in `linear_api.py` + mandatory `--description-file`, `--comment-file`, and `--body-file`.
- **IV. Deterministic Verification & Test Coverage**: PASS — Covered by `skills/linear-workflow/tests/test_linear_api.py`.
- **V. Semantic Versioning & Keep a Changelog**: PASS — Recorded under `## [Unreleased]` in `CHANGELOG.md`.

## 1. Diagnóstico e Contexto

1. **Substituição de `/fk-*` pelo pacote oficial `github/spec-kit`**: O fluxo anterior usava comandos customizados (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`, `/fk-fix`). Com a integração real do `github/spec-kit` (`specify init --integration agy --script py`), o repositório passa a utilizar a estrutura oficial `.specify/` e os 10 comandos `/speckit-*` acoplados às movimentações de card do Linear.
2. **Corrupção de Markdown em chamadas CLI**: Argumentos inline com backticks e quebras de linha em PowerShell/Bash corrompiam descrições e comentários no Linear e PRs no GitHub. A solução combina `--description-file`, `--comment-file` e `--body-file` com `sanitize_markdown_payload()` no `linear_api.py`.
3. **Pre-Render Gate no Consent Gate**: Garante que no Stage 1 o agente renderize no chat o **Título Revisado**, a **Descrição Atualizada** e o **Executive Briefing** completo antes de invocar `ask_question` no Stage 2, mantendo zero mutação no Linear até a aprovação explícita no Stage 3.

## 2. Arquitetura da Solução & Desenho Técnico

| Comando Spec Kit | Substitui | Artefatos Spec Kit | Transição Linear & Consent Gate |
| :--- | :--- | :--- | :--- |
| `/speckit-constitution` | — | `.specify/memory/constitution.md` | Governança arquitetural do repositório |
| `/speckit-specify` | `/fk-new-issue` | `specs/<feature>/spec.md`, `checklists/requirements.md` | **3-Stage Consent Gate** (Pre-Render Gate no chat ➔ `ask_question` ➔ cria card(s) em **`Backlog`** com `--description-file`) |
| `/speckit-clarify` | *(refinamento)* | Atualiza `specs/<feature>/spec.md` | Perguntas estruturadas de desambiguação; sincroniza `spec.md` com o card Linear se aplicável |
| `/speckit-plan` | `/fk-technical-analysis` (Fase 1) | `specs/<feature>/plan.md`, `research.md`, `data-model.md`, `quickstart.md` | Investiga codebase, valida contra `.specify/memory/constitution.md` e gera o plano técnico |
| `/speckit-tasks` | `/fk-technical-analysis` (Fase 2 / Gate `Todo`) | `specs/<feature>/tasks.md` | Gera `tasks.md`, roda `validate-plan`, executa **3-Stage Consent Gate** (Pre-Render do Executive Briefing + Título Revisado + Descrição Atualizada ➔ `ask_question` ➔ move card para **`Todo`**) |
| `/speckit-analyze` | *(auditoria)* | Relatório de consistência read-only | Valida alinhamento entre `spec.md`, `plan.md`, `tasks.md` e `constitution.md` |
| `/speckit-checklist` | *(qualidade)* | `specs/<feature>/checklists/<domain>.md` | Gera checklists de qualidade de requisitos ("unit tests for English") |
| `/speckit-taskstoissues` | `/fk-new-issue` (de `tasks.md`) | `specs/<feature>/tasks.md` ➔ Issues | Converte tarefas de `tasks.md` em cards atômicos no Linear em **`Backlog`** após **3-Stage Consent Gate** |
| `/speckit-implement` | `/fk-develop` | Executa `tasks.md` (`- [X]`) | **Autônomo (Sem Consent Gate)**: move card para **`In Progress`**, cria branch Gitflow, implementa tasks e testes, abre PR (`gh pr create --body-file`) e move card para **`In Review`** |
| `/speckit-converge` | `/fk-fix` | Atualiza `tasks.md` (`## Phase N: Convergence`) | **Autônomo (Sem Consent Gate)**: lê reviews/comentários do PR e gaps da spec, move card para **`In Progress`**, aplica correções na branch do PR, comenta no PR (`--body-file`) e retorna card para **`In Review`** |

## 3. Checklist de Arquivos Impactados

- [x] `.specify/memory/constitution.md`
- [x] `.specify/scripts/python/*` & `.specify/scripts/powershell/*` & `.specify/templates/*`
- [x] `skills/linear-workflow/assets/.specify/*` (cópia empacotada para distribuição via `bundles/default`)
- [x] `skills/linear-workflow/scripts/linear_api.py` (`sanitize_markdown_payload`, `validate-plan`, `bootstrap-specify`)
- [x] `skills/linear-workflow/.apm/skills/speckit-*/SKILL.md` (10 skills oficiais enriquecidas com integração Linear)
- [x] `skills/linear-workflow/.apm/prompts/speckit-*.prompt.md` (10 prompts correspondentes)
- [x] `skills/linear-workflow/SKILL.md`, `instructions/linear-lifecycle-commands.instructions.md`, `references/*.md`
- [x] `skills/linear-workflow/tests/test_linear_api.py`
- [x] `CHANGELOG.md`, `README.md`, `apm.yml`, `bundles/default/apm.yml`, `apm.lock.yaml`

## 4. Estratégia de Testes

- Executar `python -m unittest discover -s skills/linear-workflow/tests -p "test_*.py" -v` cobrindo:
  - `sanitize_markdown_payload()` (remoção de `\"`, preservação de code blocks e backticks, normalização de `\r\n` e `\n` literais).
  - `validate_spec_plan()` e CLI `validate-plan` com `.specify/feature.json` e `specs/053-fal-53-spec-kit-linear-workflow/`.
  - `bootstrap_specify()` copiando `skills/linear-workflow/assets/.specify` para diretórios consumidores.
  - Verificação de contrato das 10 skills `speckit-*` em `skills/linear-workflow/.apm/skills/` e `.agents/skills/`.
- Executar `python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks`.

## 5. Plano Gitflow

- **Branch**: `feat/FAL-53-spec-driven-development-linear-workflow` (base: `main`)
- **Commits**: Conventional Commits 1.0.0 referenciando `(FAL-53)`
- **Pull Request**: PR #19 atualizado via `gh pr edit 19 --body-file` e card `FAL-53` avançado para `In Review`.
