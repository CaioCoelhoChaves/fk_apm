# Data Model: Criação de Cards Manuais no Linear (/fk-new-manual-issue)

**Feature**: `055-manual-linear-cards` | **Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)  
**Date**: 2026-10-31 | **Status**: Complete

---

## 1. Entidades Principais

### 1.1 `ManualTaskInput` (Entrada do Usuário)
Representa uma tarefa operacional manual extraída a partir das instruções ou prompts do usuário.

| Campo | Tipo | Obrigatório | Descrição | Validação |
| :--- | :--- | :---: | :--- | :--- |
| `title` | `string` | Sim | Título conciso da atividade operacional humana | Não vazio, máx. 255 caracteres |
| `context` | `string` | Não | Contexto, justificativa e detalhes operacionais | Texto Markdown válido |
| `actions` | `List[string]` | Não | Checklist de passos manuais a serem executados | Lista de strings |
| `acceptance_criteria` | `List[string]` | Não | Critérios para validação de conclusão humana | Lista de strings |
| `priority` | `int` | Não | Prioridade no Linear (0 = Sem prioridade, 1 = Urgente, 2 = Alta, 3 = Média, 4 = Baixa) | Entre 0 e 4 (default 0) |

### 1.2 `ManualIssueBatchPayload` (Estrutura de Lote para CLI)
Estrutura serializável em JSON utilizada pelo subcomando `linear_api.py create-manual-issues --batch-file <path>`.

```json
{
  "team_id": "44d94453-4212-4336-83af-9f6b56997e5e",
  "project_id": "50e60bf5-9d19-43d9-81bf-96987e50b982",
  "issues": [
    {
      "title": "Configurar credenciais de produção no Gateway de Pagamento",
      "description": "## Contexto da Tarefa Manual\n...\n\n## Ações Manuais a Executar\n- [ ] ...\n\n## Critérios de Conclusão\n- [ ] ...",
      "priority": 2
    }
  ]
}
```

### 1.3 `LinearManualIssue` (Entidade Persistida no Linear)
Entidade criada no Linear via mutação GraphQL `issueCreate`.

| Propriedade Linear | Valor / Origem | Regra de Governança |
| :--- | :--- | :--- |
| `id` | UUID gerado pelo Linear | Identificador único interno |
| `identifier` | Código legível (ex: `FAL-60`) | Sequencial gerado pelo Linear |
| `title` | Informado pelo usuário | Sanitizado |
| `description` | Markdown padronizado | Sanitizado via `sanitize_markdown_payload` |
| `stateId` | ID do estado `Backlog` | **Obrigatório**: Sempre `Backlog` |
| `labelIds` | ID da label `manual` (+ outras opcionais) | **Obrigatório**: Conter a tag `manual` |
| `projectId` | ID do projeto Linear ativo | Vinculado ao projeto detectado |
| `teamId` | ID do time Linear | Vinculado ao time |

---

## 2. Ciclo de Vida e Máquina de Estados

### 2.1 Papel do Agente vs. Operador Humano

```
[ Usuário ] 
     │
     ▼
[ /fk-new-manual-issue ] ──► Consent Gate (Pre-Render)
     │
     ▼ (Aprovação)
[ Linear GraphQL API ] ────► Criação no estado "Backlog" + Tag "manual"
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    │                                                               │
    ▼ (Ação do Agente de Código)                                    ▼ (Ação Humana no Linear)
[ FIM DO FLUXO DO AGENTE ]                              [ Operador assume o card ]
(Zero branches, Zero worktrees, Zero PRs)                           │
                                                                    ▼
                                                            Move para "Todo"
                                                                    │
                                                                    ▼
                                                        Move para "In Progress"
                                                                    │
                                                                    ▼
                                                            Move para "Done"
```

1. **Agente de IA**:
   - Conduz o usuário na definição do(s) card(s).
   - Executa a pré-visualização (Pre-Render Gate).
   - Após aprovação, cria os cards exclusivamente no estado `Backlog` com a etiqueta `manual`.
   - Finaliza o atendimento sem criar branches, sem commitar no Git e sem abrir PRs.
2. **Operadores Humanos**:
   - Assumem os cards manuais diretamente na interface web/desktop do Linear.
   - Realizam as tarefas operacionais fora do repositório.
   - Atualizam o status (`Todo` ➔ `In Progress` ➔ `Done`) manualmente no Linear.

---

## 3. Regras de Validação e Integridade

- **R1 - Isolamento de Branches**: Sob nenhuma hipótese o comando `/fk-new-manual-issue` deve invocar `git checkout -b` ou `create_ephemeral_worktree`.
- **R2 - Estado Imutável na Criação**: O estado inicial é fixado em `Backlog`. Qualquer tentativa de passar outro estado deve ser sobrescrita para `Backlog`.
- **R3 - Tag `manual` Mandatória**: A etiqueta `manual` deve ser garantida em todas as criações. Caso não exista no time do Linear, a API deve criá-la de forma idempotente via `resolve_or_create_label_id`.
- **R4 - Proteção contra Escapes**: Descrições com crases, aspas e quebras de linha devem trafegar estritamente por arquivos temporários UTF-8 ou payloads JSON sanitizados via `sanitize_markdown_payload`.
