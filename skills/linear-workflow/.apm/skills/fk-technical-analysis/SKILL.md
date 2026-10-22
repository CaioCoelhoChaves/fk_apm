---
name: fk-technical-analysis
description: Investigação arquitetural, spikes técnicos, desenho de solução e avanço para Todo no Linear com o protocolo de Consent Gate em 3 etapas. Use quando o usuário invocar /fk-technical-analysis ou solicitar análise técnica de um card.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-technical-analysis: Análise Técnica & Spikes Arquiteturais no Linear

Este comando orquestra o rito de análise técnica de uma tarefa no Linear, aplicando integralmente o protocolo de **Consent Gate em 3 etapas** e as diretrizes da skill `linear-workflow`.

---

## Protocolo Inviolável em 3 Etapas

### 1. Etapa 1: Leitura & Investigação Técnica (Zero Mutação)
- **Consulta da Issue**: Consulte os detalhes da issue indicada via MCP `linear_issue_search` ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"
  ```
- **Investigação Arquitetural**:
  - Inspecione a arquitetura do workspace, dependências, arquivos impactados e contratos.
  - Avalie trade-offs, riscos e necessidades de refatoração ou migração.
- **Apresentação em Chat**: Apresente no chat a análise técnica completa:
  - Diagnóstico e causa-raiz (se bug) ou requisitos técnicos (se feature).
  - Arquitetura da solução e arquivos a modificar/criar.
  - Estratégia de testes e validação.
- ⚠️ **Zero Mutação**: **NÃO altere o status do card e NÃO comente no Linear nesta etapa.**

### 2. Etapa 2: Consent Gate Interativo (Confirmação Explícita)
- Apresente a pergunta de consentimento invocando a **ferramenta nativa de perguntas** do harness:
  - **Google Antigravity**: chame `ask_question`:
    ```json
    {
      "questions": [
        {
          "question": "A análise técnica está aprovada? Posso registrar as decisões no Linear e mover o card para Todo (pronto para desenvolvimento)?",
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
  - `Editar...`: permite ao desenvolvedor indicar alterações arquiteturais, trade-offs ou arquivos em texto livre. O agente **retorna à Etapa 1**, refina a análise no chat e apresenta novo Consent Gate. **Zero mutação é estritamente mantida**.

### 3. Etapa 3: Execução Atômica
- Após aprovação, execute atomicamente a transição de estado para `Todo` acompanhada do comentário consolidado prefixado com `🤖 **AI Agent Update**:`, via MCP ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "Todo" \
    --comment "🤖 **AI Agent Update**: Análise Técnica Concluída...\n\n<sumário>"
  ```
- Notifique o desenvolvedor com a chave do card (ex: `FAL-25`) e o novo status `Todo`.
