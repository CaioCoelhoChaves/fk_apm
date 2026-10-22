---
name: fk-issue
description: Alias rápido para fk-new-issue. Planejamento, decomposição e criação atômica de novos cards no Linear com Consent Gate em 3 etapas.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-issue: Planejamento & Criação de Tarefas no Linear (Alias)

Alias rápido para o comando `/fk-new-issue`. Executa exatamente o mesmo rito com **Consent Gate em 3 etapas**:

1. **Etapa 1 (Zero Mutação)**: Localizar projeto pai via MCP ou CLI, decompor tarefas no chat com label `Front` ou `Back`. Não criar nenhum card.
2. **Etapa 2 (Consent Gate Interativo)**: Invocar a tool nativa de perguntas (`ask_question`, `AskUserQuestion`, etc.) com opções `(Recommended) Sim, aprovar` e `Editar...`. Se o desenvolvedor escolher `Editar...`, coletar os ajustes em texto livre e retornar à Etapa 1 sem criar cards no Linear.
3. **Etapa 3 (Execução Atômica)**: Criar os cards após `Sim, aprovar` e notificar o usuário com links e identificadores.

Consulte a skill base para documentação completa: [linear-workflow](../linear-workflow/SKILL.md).
