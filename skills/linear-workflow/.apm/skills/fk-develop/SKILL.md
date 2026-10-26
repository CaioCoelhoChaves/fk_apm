---
name: fk-develop
description: Início autônomo do desenvolvimento, criação de branch Gitflow, implementação de código e testes sem Consent Gate, e avanço para In Review ao abrir PR. Use quando o usuário invocar /fk-develop ou solicitar implementação de um card.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-develop: Ciclo Autônomo de Desenvolvimento & Implementação no Linear

Este comando orquestra o ciclo completo de desenvolvimento de uma tarefa no Linear de forma **autônoma (sem Consent Gate)**, aplicando Gitflow e as diretrizes da skill `linear-workflow`.

> [!IMPORTANT]
> **Execução Autônoma (SEM Consent Gate)**:
> Ao contrário de `/fk-new-issue` e `/fk-technical-analysis`, o comando `/fk-develop` roda **sem Consent Gate**. O desenvolvedor apenas invoca o comando e o agente assume a execução imediatamente: move o card para **`In Progress`**, cria a branch Gitflow, implementa código e testes, abre o Pull Request e transiciona o card para **`In Review`**.
>
> **Diretriz de Decisão em Caso de Dúvidas**:
> - O agente **só deve fazer perguntas ao desenvolvedor em casos excepcionais de ambiguidade real e bloqueante** (ex.: ausência total de critérios, conflito insolúvel de requisitos ou credenciais ausentes).
> - **Comportamento Padrão**: Se houver mais de uma alternativa técnica ou detalhe menor de especificação, **decida tecnicamente**, registre explicitamente a **premissa assumida** no comentário inicial do card e no PR, e siga em frente sem interromper o fluxo.

---

## Ciclo de Desenvolvimento Autônomo

### 1. Leitura & Identificação da Issue
- **Consulta da Issue**: Consulte os detalhes da issue indicada via MCP `linear_issue_search` ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"
  ```
- **Consumo Prioritário da Especificação Técnica**:
  - Analise prioritariamente a especificação técnica completa registrada no histórico de comentários (comentário consolidado `🤖 **AI Agent Update**: Análise Técnica Concluída`) ou na descrição do card.
  - Extraia diretamente da especificação persistida:
    1. **Diagnóstico & Contexto**: causa-raiz ou motivação técnica.
    2. **Arquitetura da Solução**: decisões de desenho técnico, trade-offs e dependências.
    3. **Checklist de Arquivos Impactados**: arquivos a criar, modificar ou remover.
    4. **Estratégia de Testes**: testes unitários, validações automáticas e comandos de execução.
    5. **Plano Gitflow**: nome da branch planejado no padrão `<type>/<issue-key>-<slug>`.
  - Se o card não contiver análise prévia consolidada, utilize os requisitos da descrição e critérios de aceitação.
- **Planejamento da Branch**: Adote o nome da branch indicado na especificação técnica ou formate no padrão Linear `<type>/<issue-key>-<slug>` (ex: `feat/FAL-34-persistir-especificacao-tecnica-linear`).

### 2. Transição Imediata para In Progress (Sem Confirmação)
- Transicione o card no Linear para **`In Progress`** com comentário inicial informando a branch e premissas assumidas (se houver):
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "In Progress" \
    --comment "🤖 **AI Agent Update**: Início autônomo do desenvolvimento na branch <branch-name>."
  ```
  *(A idempotência de 10 minutos é garantida pelo CLI).*

### 3. Criação da Branch Gitflow
- Garanta que a branch base (ex: `main`) esteja atualizada e crie/mude para a branch de trabalho:
  ```bash
  git checkout -b <branch-name>
  ```

### 4. Implementação de Código & Testes
- Execute o desenvolvimento diretamente no workspace, mantendo testes unitários e qualidade de código.
- Implemente sem pedir confirmações intermediárias nem pausar a esteira.

### 5. Conclusão do Desenvolvimento & Avanço para In Review
- Ao concluir a codificação e aprovação dos testes locais:
  - Realize commit semântico seguindo a skill `git-workflow` (Conventional Commits 1.0.0).
  - Envie a branch para o repositório remoto (`git push -u origin <branch-name>`).
  - Abra o Pull Request no GitHub:
    ```bash
    gh pr create --title "..." --body "..."
    ```
  - **Transicione obrigatoriamente o card para `In Review`** com o link do PR e sumário técnico:
    ```bash
    python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
      --state "In Review" \
      --comment "🤖 **AI Agent Update**: Desenvolvimento concluído. PR aberto: <pr-url>"
    ```

---

## Regra Rito Exclusivamente Manual a partir de In Review

- ⚠️ **`Done` é Exclusivo do Desenvolvedor**: O agente **NUNCA** move o card para `Done`. Apenas o desenvolvedor move para `Done` após revisar o PR no GitHub, validar testes e realizar o merge.
- **Retorno de Correção**: Se houver apontamentos no code review, o desenvolvedor ou o comando `/fk-fix` retorna o card para `In Progress` para novas correções.
