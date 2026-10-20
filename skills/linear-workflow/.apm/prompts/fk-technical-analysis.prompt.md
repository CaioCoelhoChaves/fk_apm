---
description: Investigação arquitetural, spikes técnicos e desenho de solução para tarefa Linear com consent gate em 3 etapas
argument-hint: "<issue-key>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-technical-analysis: Análise Técnica & Spikes Arquiteturais no Linear

Execute o rito de análise técnica para a tarefa Linear indicada seguindo rigorosamente a skill `linear-workflow` e o protocolo de **Consent Gate em 3 etapas**:

Alvo / Issue: $ARGUMENTS

## Diretrizes de Execução
1. **Etapa 1 - Leitura & Investigação (Zero Mutação)**:
   - Consulte os detalhes do card via `get-issue $ARGUMENTS` ou MCP `linear_issue_search`.
   - Inspecione a arquitetura do workspace, dependências, arquivos impactados e trade-offs de implementação.
   - Elabore a análise técnica detalhada no chat. **Não comente e não altere o estado do card no Linear nesta etapa.**
2. **Etapa 2 - Consent Gate (Confirmação Explícita)**:
   - Pergunte ao desenvolvedor: *"A análise técnica está aprovada? Posso registrar as decisões no Linear e mover o card para **Todo** (pronto para desenvolvimento)?"*
   - Aguarde aprovação inequívoca antes de qualquer transição.
3. **Etapa 3 - Execução Atômica**:
   - Após aprovação, execute atomicamente a transição para `Todo` acompanhada do comentário consolidado prefixado com `🤖 **AI Agent Update**:`.
