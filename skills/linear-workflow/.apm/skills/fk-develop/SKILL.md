---
name: fk-develop
description: Início do desenvolvimento, criação de branch Gitflow, implementação de código e testes, e avanço para In Review ao abrir PR, com Consent Gate. Use quando o usuário invocar /fk-develop ou solicitar implementação de um card.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-develop: Ciclo de Desenvolvimento & Implementação no Linear

Este comando orquestra o ciclo de desenvolvimento de uma tarefa no Linear, aplicando integralmente o protocolo de **Consent Gate em 3 etapas**, Gitflow e as diretrizes da skill `linear-workflow`.

---

## Ciclo de Desenvolvimento & Consent Gate

### 1. Etapa 1: Leitura & Planejamento da Branch (Zero Mutação)
- **Consulta da Issue**: Consulte os detalhes da issue indicada via MCP `linear_issue_search` ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"
  ```
- **Planejamento da Branch**: Formate o nome da branch Gitflow no padrão Linear `<type>/<issue-key>-<slug>` (ex: `feat/FAL-25-antigravity-slash-commands`).
- **Apresentação em Chat**: Apresente no chat o plano de implementação, arquivos a modificar e a branch proposta.
- ⚠️ **Zero Mutação**: **NÃO altere o Linear nesta etapa.**

### 2. Etapa 2: Consent Gate Interativo (Confirmação Explícita)
- Apresente a pergunta de consentimento invocando a **ferramenta nativa de perguntas** do harness:
  - **Google Antigravity**: chame `ask_question`:
    ```json
    {
      "questions": [
        {
          "question": "O plano de desenvolvimento está aprovado? Posso mover o card para In Progress e iniciar a branch de trabalho?",
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
  - `Editar...`: permite ao desenvolvedor digitar observações ou ajustes no plano em texto livre. O agente **retorna à Etapa 1**, refina o plano de desenvolvimento/arquivos/branch e apresenta novo Consent Gate. **Zero mutação é estritamente mantida**.

### 3. Etapa 3: Execução Atômica & Codificação
- Transicione o card no Linear para **`In Progress`** com comentário inicial:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "In Progress" \
    --comment "🤖 **AI Agent Update**: Início do desenvolvimento na branch <branch-name>."
  ```
- Crie e mude para a branch de trabalho:
  ```bash
  git checkout -b <branch-name>
  ```
- Execute o desenvolvimento, mantendo testes unitários e qualidade de código.

### 4. Etapa 4: Conclusão do Desenvolvimento & Avanço para In Review
- Ao concluir a codificação e aprovação dos testes locais:
  - Realize commit semântico seguindo a skill `git-workflow`.
  - Abra o Pull Request no GitHub:
    ```bash
    gh pr create --title "..." --body "..."
    ```
  - **Transicione obrigatoriamente o card para `In Review`** com o link do PR e sumário técnico:
    ```bash
    python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
      --state "In Review" \
      --comment "🤖 **AI Agent Update**: Desenvolvimento concluído. PR aberto: <pr-url>"
    ```
- ⚠️ **Regra Rito Exclusivamente Manual a partir de In Review**:
  - O agente **NUNCA** move o card para `Done`. Apenas o desenvolvedor move para `Done` após revisar o PR no GitHub, validar testes e realizar o merge.
  - **Retorno de Correção**: Se houver apontamentos no code review, o desenvolvedor ou o agente pode retornar o card para `In Progress` para novas correções.
