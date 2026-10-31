# Data Model: Fluxo Contínuo e Autônomo do Spec Kit

Este documento detalha as entidades lógicas, máquinas de estado, relacionamentos e contratos de dados que regem a execução contínua e autônoma do Spec Kit integrada ao Linear e ao GitHub.

---

## 1. Entidades Principais

### 1.1 Lifecycle Command Execution
Representa uma invocação de comando de ciclo de vida do Spec Kit pelo desenvolvedor ou agente.

- **command_name**: `String` (ex: `/speckit-specify`, `/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`, `/speckit-implement`, `/speckit-converge`).
- **card_id**: `String` — Identificador do card no Linear no padrão `^[A-Z]{2,10}-\d+$` (ex: `FAL-60`). Obrigatório para todos os comandos exceto `/speckit-specify` inicial.
- **branch_name**: `String` — Nome canônico da branch Gitflow no formato `<type>/<CARD-ID>-<slug>` (ex: `feat/FAL-60-autonomous-speckit-github-review`).
- **worktree_path**: `Path` — Diretório isolado efêmero em `.worktrees/<CARD-ID>`.
- **is_autonomous**: `Boolean` (sempre `true`) — Execução contínua sem gates síncronos de confirmação (`ask_question`).
- **pull_request_url**: `String (URL)` — Link permanente para o Pull Request no GitHub associado à branch.

### 1.2 Linear Issue State Machine
Reflete a evolução determinística da issue no Linear ao longo da esteira autônoma.

```text
                  +-------------------------------------------------+
                  |                                                 |
                  v                                                 |
[Backlog (0.0)] -----> [Planned (1.0)] -----> [Todo (2.0)] -----> [In Progress (3.0)]
(specify/clarify)          (plan)                 (tasks)            (implement /
                                                                      converge)
                                                                         |
                                                                         v
                                                                  [In Review (4.0)]
                                                                    (PR ready)
                                                                         |
                                                            (Strictly Manual Developer)
                                                                         |
                                                                         v
                                                                   [Done (5.0)]
```

#### Transições Determinísticas de Estado:
| De | Para | Disparado Por | Condição de Guarda / Ação Autônoma |
|---|---|---|---|
| (Novo) | `Backlog` | `/speckit-specify` | Artefatos criados, branch criada, Draft PR aberto via `gh pr create --draft`. |
| `Backlog` | `Backlog` | `/speckit-clarify` | `git pull --rebase origin <branch>`, resolução de ambiguidades, commit & push no Draft PR. |
| `Backlog` | `Planned` | `/speckit-plan` | Artefatos de arquitetura gerados, commit & push no Draft PR, comentário técnico registrado. |
| `Planned` | `Todo` | `/speckit-tasks` | `tasks.md` gerado, validação estática de plano aprovada, commit & push no Draft PR. |
| `Todo` | `In Progress` | `/speckit-implement` | Worktree criado, branch checkout, tarefas iniciadas. |
| `In Progress` | `In Review` | `/speckit-implement` | Tarefas concluídas `[X]`, testes aprovados, Draft PR promovido para Ready (`gh pr ready`). |
| `In Review` | `In Progress` | `/speckit-converge` | Feedbacks do PR recebidos, tarefas de convergência iniciadas. |
| `In Progress` | `In Review` | `/speckit-converge` | Correções aplicadas, testes aprovados, comentário no PR postado. |
| `In Review` | `Done` | **Humano** | **Estritamente manual pelo desenvolvedor após merge do PR**. Agentes proibidos. |

### 1.3 Living Spec & GitHub Pull Request Entity
Representa o Draft Pull Request criado na especificação e enriquecido progressivamente.

- **pr_number**: `Integer`
- **draft**: `Boolean` (`true` durante specify, plan, tasks; `false` após promoção por `/speckit-implement`)
- **head_branch**: `String` (`feat/<CARD-ID>-<slug>`)
- **base_branch**: `String` (`develop` ou `main`)
- **tracked_artifacts**: `List<Path>`
  - `specs/<feature>/spec.md`
  - `specs/<feature>/checklists/requirements.md`
  - `specs/<feature>/plan.md`
  - `specs/<feature>/research.md`
  - `specs/<feature>/data-model.md`
  - `specs/<feature>/quickstart.md`
  - `specs/<feature>/contracts/*`
  - `specs/<feature>/tasks.md`
- **review_comments**: Threads de revisão no PR onde o desenvolvedor realiza seus apontamentos assíncronos.

---

## 2. Modelos de Comunicação e Payloads

### 2.1 Executive Chat Report (Chat UI Payload)
Estrutura do relatório conciso emitido pelo agente ao final de cada comando (substituindo o antigo Consent Gate):

```markdown
## [Comando Executado] Concluído

- **Card Linear**: [{CARD-ID}]({linear_url}) — Estado: `{State}`
- **GitHub Pull Request**: [#{pr_number} — {title}]({pr_url}) ({draft_mode})
- **Branch**: `{branch_name}`
- **Artefatos Gerados/Atualizados**:
  - `specs/{feature}/...`

> Para revisar e comentar alterações, acesse diretamente o [Pull Request no GitHub]({pr_url}).
> Próximo comando: `{proximo_comando}`
```

### 2.2 Linear Update Mutation Payload
Payload processado via arquivo temporário UTF-8 por `linear_api.py update-issue`:

- **issue_id**: UUID ou Key da issue
- **state**: Nome canônico do estado de destino (`Planned`, `Todo`, `In Progress`, `In Review`)
- **title**: Título sanitizado da issue
- **description_file**: Caminho para arquivo com a descrição atualizada da issue
- **comment_file**: Caminho para arquivo com o briefing técnico ou log executivo da transição
