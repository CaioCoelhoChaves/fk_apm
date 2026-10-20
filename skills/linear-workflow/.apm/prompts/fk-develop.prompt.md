---
description: Início do desenvolvimento, criação de branch Gitflow e implementação de tarefa Linear com consent gate em 3 etapas
argument-hint: "<issue-key>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-develop: Ciclo de Desenvolvimento & Implementação no Linear

Execute o rito de desenvolvimento para a tarefa Linear indicada seguindo rigorosamente a skill `linear-workflow` e o protocolo de **Consent Gate em 3 etapas**:

Alvo / Issue: $ARGUMENTS

## Diretrizes de Execução
1. **Etapa 1 - Leitura & Apresentação (Zero Mutação)**:
   - Consulte o card via `get-issue $ARGUMENTS` ou MCP `linear_issue_search`, lendo requisitos, histórico e critérios de aceitação.
   - Apresente no chat o plano de implementação, arquivos afetados e a branch de trabalho proposta (`<type>/<key>-<slug>`). **Não altere o Linear nesta etapa.**
2. **Etapa 2 - Consent Gate (Confirmação Explícita)**:
   - Pergunte ao desenvolvedor: *"O plano de desenvolvimento está aprovado? Posso mover o card para **In Progress** e criar a branch de trabalho?"*
   - Aguarde aprovação inequívoca antes de qualquer mutação.
3. **Etapa 3 - Execução Atômica & Codificação**:
   - Transicione o card para `In Progress` com comentário inicial (`🤖 **AI Agent Update**: Início do desenvolvimento na branch <branch-name>...`).
   - Crie a branch Git e execute a codificação e testes.
4. **Etapa 4 - Finalização & In Review**:
   - Ao concluir a implementação e testes, abra o Pull Request no GitHub (`gh pr create`).
   - Mova obrigatoriamente o card para `In Review` com comentário linkando o PR.
