---
name: fk-dev
description: Alias rápido para fk-develop. Início do desenvolvimento, criação de branch Gitflow, implementação e avanço para In Review com Consent Gate.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-dev: Ciclo de Desenvolvimento no Linear (Alias)

Alias rápido para o comando `/fk-develop`. Executa exatamente o mesmo rito com **Consent Gate em 3 etapas**:

1. **Etapa 1 (Zero Mutação)**: Consultar card, apresentar plano de desenvolvimento e branch proposta (`<type>/<key>-<slug>`). Não alterar o Linear.
2. **Etapa 2 (Consent Gate)**: Perguntar: *"O plano de desenvolvimento está aprovado? Posso mover o card para **In Progress** e iniciar a branch?"*
3. **Etapa 3 (Execução Atômica)**: Mover para `In Progress`, criar branch, implementar código e testes.
4. **Etapa 4 (In Review)**: Ao abrir o PR via GitHub CLI (`gh pr create`), transicionar card para `In Review`. A transição para `Done` é exclusivamente manual pelo desenvolvedor.

Consulte a skill base para documentação completa: [linear-workflow](../linear-workflow/SKILL.md).
