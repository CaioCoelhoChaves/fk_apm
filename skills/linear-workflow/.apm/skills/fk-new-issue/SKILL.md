---
name: fk-new-issue
description: Planejamento, decomposição e criação atômica de novos cards no Linear com o protocolo de Consent Gate em 3 etapas. Use quando o usuário invocar /fk-new-issue ou solicitar criação/planejamento de tarefas no Linear.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-new-issue: Planejamento & Criação Atômica de Tarefas no Linear

Este comando orquestra o rito de planejamento e decomposição de tarefas no Linear, aplicando integralmente o protocolo de **Consent Gate em 3 etapas** e as diretrizes da skill `linear-workflow`.

---

## Protocolo Inviolável em 3 Etapas

### 1. Etapa 1: Leitura, Decomposição & Apresentação (Zero Mutação)
- **Localização do Projeto**: Localize o projeto pai no Linear usando o MCP `linear_list_projects` ou o helper CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py find-project "<nome-do-projeto>"
  ```
- **Classificação de Componente**: Identifique a stack do repositório para taguear os cards com o componente apropriado:
  - **`Front`**: Flutter, React, Vue, Web, Mobile.
  - **`Back`**: Spring Boot, Node, Java, Python API.
- **Decomposição em Chat**: Apresente no chat a proposta de tarefas estruturadas:
  - Título objetivo no padrão `<tipo>(<escopo>): <descrição>`.
  - Descrição técnica com critérios de aceitação.
  - Label de componente (`Front` ou `Back`).
  - Status inicial proposto (`Backlog` ou `Todo`).
- ⚠️ **Zero Mutação**: **NÃO crie nenhum card no Linear nesta etapa.**

### 2. Etapa 2: Consent Gate Interativo (Confirmação Explícita)
- Apresente a pergunta de consentimento invocando a **ferramenta nativa de perguntas** do harness:
  - **Google Antigravity**: chame `ask_question`:
    ```json
    {
      "questions": [
        {
          "question": "O escopo e a divisão dos cards estão alinhados? Posso criá-los no Linear sob o status [Backlog/Todo]?",
          "options": [
            "(Recommended) Sim, aprovar",
            "Editar..."
          ],
          "is_multi_select": false
        }
      ]
    }
    ```
  - **Claude Code**: chame `AskUserQuestion` com opções `["Sim, aprovar", "Editar..."]`.
  - **OpenCode v2**: chame a ferramenta nativa de pergunta com opções `["Sim, aprovar", "Editar..."]`.
  - **Fallback Textual (Cursor, Copilot, Gemini CLI ou sem tool nativa)**: apresente em bloco Markdown destacado com opções numeradas (`1. (Recomendado) Sim, aprovar` e `2. Editar...`).
- **Tratamento das Opções**:
  - `(Recommended) Sim, aprovar`: avança imediatamente para a **Etapa 3 (Execução Atômica)**.
  - `Editar...`: permite ao desenvolvedor indicar correções ou novos cards em texto livre. O agente **retorna à Etapa 1**, refina a divisão de tarefas no chat e apresenta novo Consent Gate. **Zero mutação é estritamente mantida**.

### 3. Etapa 3: Execução Atômica
- Após aprovação, crie cada card no Linear via MCP (`linear_create_issue`) ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py create-issue \
    --team-id "<team-id>" \
    --project-id "<project-id>" \
    --title "<título>" \
    --description "<descrição>" \
    --state "<Backlog ou Todo>" \
    --label "<Front ou Back>"
  ```
- Informe o desenvolvedor com links diretos e identificadores criados (ex: `FAL-10`).
