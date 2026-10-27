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
   - **Renderização Prévia Obrigatória**: Emita integralmente no texto visível do chat o **Título Revisado** e a **Descrição Atualizada** do card, além da especificação técnica completa em 5 seções: 1. Diagnóstico e Contexto, 2. Arquitetura da Solução & Desenho Técnico, 3. Checklist de Arquivos Impactados, 4. Estratégia de Testes, e 5. Plano Gitflow antes de acionar a pergunta da Etapa 2. **Não comente e não altere o estado, título ou descrição do card no Linear nesta etapa.**
2. **Etapa 2 - Consent Gate Interativo (Confirmação Explícita)**:
   - **Proibido Consent Gate Cego**: Só invoque `ask_question` / `AskUserQuestion` após renderizar o Título Revisado, a Descrição Atualizada e todas as 5 seções no texto do chat, e inclua um resumo conciso (`Resumo da análise (<issue-key>): <resumo-solucao> | Arquivos: <N> | Branch: <branch>`) dentro do próprio campo `question` da ferramenta interativa ou fallback textual com opções `(Recommended) Sim, aprovar` e `Editar...`.
   - Se `Editar...`: receba apontamentos arquiteturais em texto livre, retorne à Etapa 1 para refinar a análise e reapresente o Consent Gate. Zero mutação no Linear até aprovação explícita.
   - Aguarde `Sim, aprovar` antes de qualquer transição.
3. **Etapa 3 - Execução Atômica & Persistência Integral da Especificação Técnica**:
   - Após aprovação, execute atomicamente a transição para `Todo` acompanhada da **atualização obrigatória do título (`--title`) e da descrição do card (`--description` ou `--description-file`)** e da persistência obrigatória da especificação técnica completa (5 seções) no comentário consolidado (`update-issue --state "Todo" --title "..." --description "..." --comment "..."`), substituindo rascunhos preliminares de `Backlog` e assegurando que sessões futuras de `/fk-develop` herdem o contexto integral sem perda de informação.
