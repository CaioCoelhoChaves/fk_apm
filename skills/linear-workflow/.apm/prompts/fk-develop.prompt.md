---
description: Início autônomo do desenvolvimento, criação de branch Gitflow e implementação de tarefa Linear sem Consent Gate
argument-hint: "<issue-key>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-develop: Ciclo Autônomo de Desenvolvimento & Implementação no Linear

Execute o rito de desenvolvimento para a tarefa Linear indicada de forma **autônoma (sem Consent Gate)**, seguindo a skill `linear-workflow` e Gitflow:

Alvo / Issue: $ARGUMENTS

## Diretrizes de Execução
1. **Leitura & Identificação da Issue**:
   - Consulte o card via `get-issue $ARGUMENTS` ou MCP `linear_issue_search`.
   - **Consuma prioritariamente a especificação técnica completa** persistida no histórico de comentários (`🤖 **AI Agent Update**: Análise Técnica Concluída`) ou descrição do card, extraindo o diagnóstico, arquitetura, checklist de arquivos impactados, estratégia de testes e nome da branch planejado.
   - Adote a branch planejada ou formate no padrão `<type>/<key>-<slug>`.
2. **Transição Imediata para In Progress (Sem Confirmação)**:
   - Transicione imediatamente o card para `In Progress` com comentário inicial via `--comment-file "<path>"` (`🤖 **AI Agent Update**: Início autônomo do desenvolvimento na branch <branch-name>...`).
3. **Criação da Branch & Codificação Autônoma**:
   - Crie a branch Git e execute a codificação e testes sem pedir confirmação prévia.
   - **Diretriz de Decisão**: Só faça perguntas ao desenvolvedor se houver dúvida realmente bloqueante. Em caso de detalhes ou trade-offs menores, decida tecnicamente, documente a premissa assumida no comentário/PR e continue.
4. **Finalização & In Review**:
   - Ao concluir a implementação e testes locais, abra o Pull Request no GitHub (`gh pr create --body-file "<pr-body-utf8.md>"`, proibindo `--body "..."` inline com crases).
   - Mova obrigatoriamente o card para `In Review` com comentário linkando o PR via `--comment-file "<comentario-pr-utf8.md>"`.
5. **Done Proibido para o Agente**:
   - A transição para `Done` é exclusivamente manual pelo desenvolvedor após o merge do PR. O agente nunca move para `Done`.
