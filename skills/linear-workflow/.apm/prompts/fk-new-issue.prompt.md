---
description: Planejamento, decomposição e criação atômica de novos cards no Linear com consent gate em 3 etapas
argument-hint: "[contexto ou requisitos]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-new-issue: Planejamento & Criação Atômica de Tarefas no Linear

Execute o rito de planejamento e decomposição de tarefas seguindo rigorosamente a skill `linear-workflow` e o protocolo de **Consent Gate em 3 etapas**:

Contexto fornecido: $ARGUMENTS

## Diretrizes de Execução
1. **Etapa 1 - Leitura & Apresentação (Zero Mutação)**:
   - Localize o projeto pai no Linear usando `find-project` ou MCP `linear_list_projects`.
   - Analise os requisitos e decomponha-os em tarefas atômicas no chat (título, descrição estruturada, critérios de aceitação e label `Front` ou `Back`).
   - Apresente a tabela proposta no chat. **Não crie nenhum card no Linear nesta etapa.**
2. **Etapa 2 - Consent Gate (Confirmação Explícita)**:
   - Pergunte ao desenvolvedor: *"O escopo e a divisão dos cards estão alinhados? Posso criá-los no Linear sob o status [Backlog/Todo]?"*
   - Aguarde aprovação inequívoca antes de qualquer chamada de mutação.
3. **Etapa 3 - Execução Atômica**:
   - Após aprovação, crie os cards no Linear via CLI (`create-issue`) ou MCP (`linear_create_issue`).
   - Apresente o sumário final com links diretos e identificadores (ex: `FAL-10`).
