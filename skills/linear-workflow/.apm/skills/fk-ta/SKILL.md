---
name: fk-ta
description: Alias rápido para fk-technical-analysis. Investigação arquitetural, spikes técnicos, desenho de solução e avanço para Todo no Linear com Consent Gate em 3 etapas.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-ta: Análise Técnica & Spikes no Linear (Alias)

Alias rápido para o comando `/fk-technical-analysis`. Executa exatamente o mesmo rito com **Consent Gate em 3 etapas**:

1. **Etapa 1 (Zero Mutação)**: Consultar card via MCP ou CLI, investigar arquitetura e propor solução detalhada no chat. Não alterar nada no Linear.
2. **Etapa 2 (Consent Gate Interativo)**: Invocar a tool nativa de perguntas (`ask_question`, `AskUserQuestion`, etc.) com opções `(Recommended) Sim, aprovar` e `Editar...`. Se o desenvolvedor escolher `Editar...`, coletar os apontamentos em texto livre e retornar à Etapa 1 sem alterar o Linear.
3. **Etapa 3 (Execução Atômica)**: Após `Sim, aprovar`, transicionar card para `Todo` com comentário consolidado `🤖 **AI Agent Update**:`.

Consulte a skill base para documentação completa: [linear-workflow](../linear-workflow/SKILL.md).
