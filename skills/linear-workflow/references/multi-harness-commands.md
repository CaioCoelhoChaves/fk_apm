# Multi-Harness Command Architecture & Routing Reference (`github/spec-kit` + Linear)

This reference documents how the official `github/spec-kit` commands (`speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-taskstoissues`, `speckit-implement`, `speckit-converge`) coupled with Linear lifecycle transitions and Living Spec Draft PRs operate across multiple AI coding harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, and OpenCode) through APM primitives.

---

## 1. APM Primitives Mapping (`skills/linear-workflow/`)

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
│   │   ├── speckit-converge.prompt.md
│   │   └── fk-new-manual-issue.prompt.md
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
│       ├── speckit-converge/SKILL.md
│       └── fk-new-manual-issue/SKILL.md
├── assets/
│   └── .specify/                                      # Bundled github/spec-kit runtime
├── SKILL.md                                           # Core workflow engine
└── scripts/
    └── linear_api.py                                  # Zero-dependency Linear & Spec Kit CLI
```

---

## 2. Parameterized Command Syntax & Linear Lifecycle Roles

Todos os comandos pós-especificação exigem obrigatoriamente o identificador `<CARD-ID>` (ex: `FAL-58`).

| Comando Oficial `/speckit-*` | Parâmetro Obrigatório | Papel no Ciclo Linear | Modo de Execução & Consent Gate | Next Step Prompting |
| :--- | :--- | :--- | :--- | :--- |
| **`/speckit-specify`** | Não (`<descrição>`) | Cria `spec.md`, branch Gitflow, Draft PR no GitHub e card em **`Backlog`** | **3-Stage Consent Gate** | `Próximo passo: /speckit-clarify <CARD-ID> ou /speckit-plan <CARD-ID>` |
| **`/speckit-clarify`** | **Sim** (`<CARD-ID>`) | Refina até 5 dúvidas em `spec.md`, executa em worktree efêmero e comita no Draft PR | Perguntas interativas | `Próximo passo: /speckit-plan <CARD-ID>` |
| **`/speckit-plan`** | **Sim** (`<CARD-ID>`) | Gera `plan.md` (com 5 seções obrigatórias), executa em worktree efêmero e avança para **`Planned`** | **3-Stage Consent Gate** | `Próximo passo: /speckit-tasks <CARD-ID>` |
| **`/speckit-tasks`** | **Sim** (`<CARD-ID>`) | Gera `tasks.md`, roda `validate-plan`, executa em worktree efêmero e avança para **`Todo`** | **3-Stage Consent Gate** | `Próximo passo: /speckit-implement <CARD-ID>` |
| **`/speckit-taskstoissues`** | Opcional (`<CARD-ID>`) | Converte tarefas ou fases de `tasks.md` em sub-cards atômicos em **`Backlog`** | **3-Stage Consent Gate** | `Próximo passo: /speckit-plan <SUB-CARD-ID>` |
| **`/speckit-implement`** | **Sim** (`<CARD-ID>`) | Move para **`In Progress`**, executa tasks, roda testes, promove PR (`gh pr ready`) e avança para **`In Review`** | **Autônomo (SEM Consent Gate)** | `Próximo passo: Revisar Pull Request no GitHub e acionar /speckit-converge <CARD-ID> para feedbacks` |
| **`/speckit-converge`** | **Sim** (`<CARD-ID>`) | Move para **`In Progress`**, resolve code review na branch do PR, comita, comenta no PR e retorna para **`In Review`** | **Autônomo (SEM Consent Gate)** | `Próximo passo: Revisão final e merge manual do Pull Request pelo mantenedor` |
| **`/fk-new-manual-issue`** | Opcional (`[<descrição>]`) | Cria 1 ou múltiplos cards estritamente operacionais no Linear em **`Backlog`** com tag **`manual`** | **3-Stage Consent Gate** (Zero Git / Zero PR) | — |
| **`/speckit-constitution`** | Não | Cria ou atualiza a Constituição do projeto em `.specify/memory/constitution.md` | Interativo / Governança | — |
| **`/speckit-analyze`** | Opcional (`<CARD-ID>`) | Auditoria de consistência read-only entre `spec.md`, `plan.md`, `tasks.md` e Constituição | Read-Only | — |
| **`/speckit-checklist`** | Opcional (`<CARD-ID>`) | Gera checklists customizados de requisitos em `specs/<feature>/checklists/` | Interativo | — |

---

## 3. Isolamento por Worktree Efêmero (`.worktrees/<CARD-ID>`)

Para evitar trocas de branch no repositório de trabalho do desenvolvedor e garantir suporte multitarefa:
- Quando o workspace ativo já estiver na branch do card (`git branch --show-current == <target-branch>`), os comandos executam diretamente no diretório atual.
- Caso contrário, os comandos instanciam um worktree efêmero em `.worktrees/<CARD-ID>`, executam as operações de documentação e código, realizam commit/push para o Draft PR remoto e removem o worktree ao concluir (`git worktree remove --force`).

---

## 4. Multi-Harness Interactive Consent Gate Protocol

- **Pre-Render Gate (Proibição de Consent Gate Cego)**: Renderizar o Executive Briefing contendo **Título Revisado**, **Descrição Atualizada** e as 5 seções obrigatórias no chat antes de acionar a pergunta de consentimento.
- **Stage 2 (Consent Gate Interativo)**: Acionar a ferramenta nativa de pergunta com resumo conciso.
- **Stage 3 (Execução Atômica)**: Mutação atômica no Linear via --title, --description-file e --comment-file.


---

## 5. Cards Operacionais e Isolamento Total de Código (`/fk-new-manual-issue`)

Para atividades estritamente manuais e operacionais (sem alteração de código, branches Git ou PRs):
- O comando `/fk-new-manual-issue` opera sob o **3-Stage Consent Gate** com Pre-Render Gate tabular no chat.
- Cria cards diretamente na coluna `Backlog` com a etiqueta `manual`.
- **Garantia de Isolamento Absoluto**: Zero branches Git criadas, zero worktrees, zero commits e zero Draft PRs.
- Suporta criação individual e em lote via CLI (`--batch-file`).
