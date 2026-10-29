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
1. **Etapa 1 - Cognitive Scaffolding, Artefatos `.specs/<issue-key>/` & Executive Briefing (Zero Mutação no Linear)**:
   - Consulte os detalhes do card via `get-issue $ARGUMENTS` ou MCP `linear_issue_search` e leia `.speckit/constitution.md` (se presente).
   - Inspecione a arquitetura do workspace, dependências, arquivos impactados e trade-offs de implementação.
   - Gere/atualize localmente `.specs/<issue-key>/plan.md` (5 seções obrigatórias) e `.specs/<issue-key>/tasks.md` (checklist atômico `- [ ]`) e valide via `validate-plan <issue-key>`.
   - **Renderização Prévia Obrigatória (Executive Briefing)**: Emita no texto visível do chat um **Executive Briefing** conciso (10-15 linhas com métricas e referência a `.specs/<issue-key>/`), apresentando o **Título Revisado** e a **Descrição Atualizada** do card, além da síntese da especificação técnica em 5 seções: 1. Diagnóstico e Contexto, 2. Arquitetura da Solução & Desenho Técnico, 3. Checklist de Arquivos Impactados, 4. Estratégia de Testes, e 5. Plano Gitflow antes de acionar a pergunta da Etapa 2. **Não comente e não altere o estado, título ou descrição do card no Linear nesta etapa.**
2. **Etapa 2 - Consent Gate Interativo (Confirmação Explícita)**:
   - **Proibido Consent Gate Cego**: Só invoque `ask_question` / `AskUserQuestion` após renderizar o Título Revisado, a Descrição Atualizada e todas as 5 seções no texto do chat, e inclua um resumo conciso (`Resumo da análise (<issue-key>): <resumo-solucao> | Arquivos: <N> | Tasks: <M> | Branch: <branch>`) dentro do próprio campo `question` da ferramenta interativa ou fallback textual com opções `(Recommended) Sim, aprovar` e `Editar...`.
   - Se `Editar...`: receba apontamentos arquiteturais em texto livre, retorne à Etapa 1 para refinar `.specs/<issue-key>/plan.md` e `tasks.md`, reexecute `validate-plan` e reapresente o Consent Gate. Zero mutação no Linear até aprovação explícita.
   - Aguarde `Sim, aprovar` antes de qualquer transição.
3. **Etapa 3 - Execução Atômica & Persistência do Executive Briefing no Linear**:
   - Após aprovação, execute atomicamente a transição para `Todo` acompanhada da **atualização obrigatória do título (`--title`) e da descrição do card (`--description-file`)** e da persistência obrigatória do Executive Briefing (5 seções + link para `.specs/<issue-key>/`) no comentário consolidado via arquivos UTF-8 (`update-issue --state "Todo" --title "..." --description-file "<desc-utf8.md>" --comment-file "<spec-utf8.md>"`), sanitizados automaticamente por `sanitize_markdown_payload`, evitando corrupção de crases e aspas no shell, substituindo rascunhos preliminares de `Backlog` e assegurando que sessões futuras de `/fk-develop` consumam `.specs/<issue-key>/tasks.md` sem perda de informação.
