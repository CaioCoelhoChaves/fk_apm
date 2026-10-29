# Interface Contracts: Linear API CLI & Spec Kit Lifecycle Commands

**Issue**: [FAL-58](https://linear.app/fallkey/issue/FAL-58/featworkflow-modernizar-linear-workflow-com-ciclo-draft-prs-e) | **Branch**: `feat/FAL-58-modernizar-linear-workflow-draft-prs` | **Date**: 2026-10-29

---

## 1. CLI Commands Contract (`linear_api.py`)

### 1.1 `sync-boards`
Audita e reconcilia a esteira de estados em todos os times da organização ou em um time específico.

```bash
python skills/linear-workflow/scripts/linear_api.py sync-boards [--team-id <UUID>] [--dry-run]
```

#### Input Arguments:
| Argumento | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `--team-id` | String (UUID) | Opcional | Se fornecido, sincroniza apenas o time especificado. Se omitido, sincroniza todos os times retornados pela query de times da organização. |
| `--dry-run` | Flag (Booleano) | Opcional | Se presente, não executa mutações no Linear; apenas exibe no stdout as ações planejadas (renomeações, criações e ajustes de posições). |

#### Output Contract (JSON stdout):
```json
{
  "success": true,
  "dry_run": false,
  "teams_analyzed": 1,
  "results": [
    {
      "team_id": "44d94453-4212-4336-83af-9f6b56997e5e",
      "team_name": "FallKey",
      "states_created": [],
      "states_updated": [
        {
          "id": "322f06e4-d79e-4e4c-b6b3-69c06a897ea8",
          "previous_name": "Technical Analysis",
          "new_name": "Planned",
          "type": "unstarted",
          "position": 1.0,
          "color": "#F2C94C"
        }
      ],
      "states_current": [
        {"name": "Backlog", "position": 0.0, "type": "backlog"},
        {"name": "Planned", "position": 1.0, "type": "unstarted"},
        {"name": "Todo", "position": 2.0, "type": "unstarted"},
        {"name": "In Progress", "position": 3.0, "type": "started"},
        {"name": "In Review", "position": 4.0, "type": "started"},
        {"name": "Done", "position": 5.0, "type": "completed"},
        {"name": "Canceled", "position": 6.0, "type": "canceled"}
      ]
    }
  ]
}
```

---

### 1.2 `setup-board`
Provisiona idempotentemente todos os 6 estados operacionais (+ Canceled) em um time novo ou existente.

```bash
python skills/linear-workflow/scripts/linear_api.py setup-board --team-id <UUID> [--force]
```

#### Input Arguments:
| Argumento | Tipo | Obrigatório | Descrição |
| :--- | :--- | :--- | :--- |
| `--team-id` | String (UUID) | Obrigatório | Identificador único do time no Linear. |
| `--force` | Flag (Booleano) | Opcional | Força a reordenação e redefinição de cores mesmo se os estados já existirem. |

#### Output Contract (JSON stdout):
```json
{
  "success": true,
  "team_id": "44d94453-4212-4336-83af-9f6b56997e5e",
  "provisioned_states": [
    {"name": "Backlog", "status": "existing"},
    {"name": "Planned", "status": "created", "id": "..."},
    {"name": "Todo", "status": "existing"},
    {"name": "In Progress", "status": "existing"},
    {"name": "In Review", "status": "existing"},
    {"name": "Done", "status": "existing"},
    {"name": "Canceled", "status": "existing"}
  ]
}
```

---

### 1.3 `update-issue`
Execução atômica de transição de estado, título, descrição e comentários estruturados.

```bash
python skills/linear-workflow/scripts/linear_api.py update-issue "<ISSUE_ID_OR_KEY>" \
  [--state "<STATE_NAME>"] \
  [--title "<TITLE>"] \
  [--description-file "<PATH>"] \
  [--comment-file "<PATH>"]
```

#### Regras do Contrato:
1. Se `--state "Done"` for solicitado, a CLI **DEVE retornar erro**:
   `{"success": false, "error": "Transição para 'Done' é restrita a humanos após merge manual de Pull Request."}`
2. Todos os arquivos informados via `--description-file` e `--comment-file` passam por sanitização determinística `sanitize_markdown_payload` antes do envio.

---

## 2. Spec Kit Lifecycle Commands Contract

### 2.1 Requisito Obrigatório de Argumento `<CARD-ID>`

Todos os comandos pós-especificação exigem `<CARD-ID>`.

| Comando | Sintaxe | Parâmetro Obrigatório | Comportamento se omitido |
| :--- | :--- | :--- | :--- |
| `/speckit-specify` | `/speckit-specify <descrição>` | Não (gera card novo) | Prompt interativo para descrição |
| `/speckit-clarify` | `/speckit-clarify <CARD-ID>` | **Sim** (`<CARD-ID>`) | Aborta com: `Uso obrigatório: /speckit-clarify <CARD-ID>` |
| `/speckit-plan` | `/speckit-plan <CARD-ID>` | **Sim** (`<CARD-ID>`) | Aborta com: `Uso obrigatório: /speckit-plan <CARD-ID>` |
| `/speckit-tasks` | `/speckit-tasks <CARD-ID>` | **Sim** (`<CARD-ID>`) | Aborta com: `Uso obrigatório: /speckit-tasks <CARD-ID>` |
| `/speckit-implement` | `/speckit-implement <CARD-ID>` | **Sim** (`<CARD-ID>`) | Aborta com: `Uso obrigatório: /speckit-implement <CARD-ID>` |
| `/speckit-converge` | `/speckit-converge <CARD-ID>` | **Sim** (`<CARD-ID>`) | Aborta com: `Uso obrigatório: /speckit-converge <CARD-ID>` |

---

### 2.2 Mensagens de Orientação de Próximos Passos (Next Step Prompting)

Ao concluir cada comando, o agente DEVE orientar o desenvolvedor com o comando subsequente explicitamente parametrizado com o identificador do card em foco:

- Ao finalizar `/speckit-specify`: `Próximo passo: /speckit-clarify FAL-58 ou /speckit-plan FAL-58`
- Ao finalizar `/speckit-clarify`: `Próximo passo: /speckit-plan FAL-58`
- Ao finalizar `/speckit-plan`: `Próximo passo: /speckit-tasks FAL-58`
- Ao finalizar `/speckit-tasks`: `Próximo passo: /speckit-implement FAL-58`
- Ao finalizar `/speckit-implement`: `Próximo passo: Revisar Pull Request no GitHub e acionar /speckit-converge FAL-58 para feedbacks`
