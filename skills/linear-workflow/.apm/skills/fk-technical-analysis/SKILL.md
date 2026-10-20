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

### 2. Etapa 2: Consent Gate (Confirmação Explícita)
- Apresente a pergunta de consentimento ao desenvolvedor:
  > *"A análise técnica está aprovada? Posso registrar as decisões no Linear e mover o card para **Todo** (pronto para desenvolvimento)?"*
- **Aguarde aprovação explícita** do desenvolvedor antes de avançar.

### 3. Etapa 3: Execução Atômica
- Após aprovação, execute atomicamente a transição de estado para `Todo` acompanhada do comentário consolidado prefixado com `🤖 **AI Agent Update**:`, via MCP ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "Todo" \
    --comment "🤖 **AI Agent Update**: Análise Técnica Concluída...\n\n<sumário>"
  ```
- Notifique o desenvolvedor com a chave do card (ex: `FAL-25`) e o novo status `Todo`.
