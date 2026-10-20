---
name: fk-issue
description: Alias rápido para fk-new-issue. Planejamento, decomposição e criação atômica de novos cards no Linear com Consent Gate em 3 etapas.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-issue: Planejamento & Criação de Tarefas no Linear (Alias)

Alias rápido para o comando `/fk-new-issue`. Executa exatamente o mesmo rito com **Consent Gate em 3 etapas**:

1. **Etapa 1 (Zero Mutação)**: Localizar projeto pai via MCP ou CLI, decompor tarefas no chat com label `Front` ou `Back`. Não criar nenhum card.
2. **Etapa 2 (Consent Gate)**: Perguntar: *"O escopo e a divisão dos cards estão alinhados? Posso criá-los no Linear sob o status [Backlog/Todo]?"*
3. **Etapa 3 (Execução Atômica)**: Criar os cards após confirmação explícita e notificar o usuário com links e identificadores.

Consulte a skill base para documentação completa: [linear-workflow](../linear-workflow/SKILL.md).
