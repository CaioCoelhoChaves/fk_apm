---
name: fk-technical-analysis
description: Investigação arquitetural, spikes técnicos, desenho de solução e avanço para Todo no Linear com o protocolo de Consent Gate em 3 etapas. Use quando o usuário invocar /fk-technical-analysis ou solicitar análise técnica de um card.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-technical-analysis: Análise Técnica & Spikes Arquiteturais no Linear

Este comando orquestra o rito de análise técnica de uma tarefa no Linear, aplicando integralmente o protocolo de **Consent Gate em 3 etapas** e as diretrizes da skill `linear-workflow`.

---

## Protocolo Inviolável em 3 Etapas

### 1. Etapa 1: Cognitive Scaffolding, Artefatos `.specs/<issue-key>/` & Executive Briefing (Zero Mutação no Linear)
- **Consulta da Issue**: Consulte os detalhes da issue indicada via MCP `linear_issue_search` ou CLI:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"
  ```
- **Cognitive Scaffolding & Investigação Arquitetural**:
  - Leia `.speckit/constitution.md` (se presente no repositório) para ancorar a análise nos princípios inegociáveis do projeto.
  - Inspecione a arquitetura do workspace, dependências, arquivos impactados e contratos, avaliando trade-offs, riscos e necessidades de refatoração.
- **Persistência Local Spec-Driven (`.specs/<issue-key>/`)**:
  - Crie ou atualize `.specs/<issue-key>/plan.md` contendo o desenho técnico completo sob as 5 seções obrigatórias (`1. Diagnóstico e Contexto`, `2. Arquitetura da Solução & Desenho Técnico`, `3. Checklist de Arquivos Impactados`, `4. Estratégia de Testes`, `5. Plano Gitflow`).
  - Crie ou atualize `.specs/<issue-key>/tasks.md` contendo o checklist atômico e sequencial (`- [ ]`) para execução futura no `/fk-develop`.
  - Opcionalmente, crie ou refine `.specs/<issue-key>/spec.md` com os requisitos funcionais e critérios de aceitação.
- **Validação Determinística de Integridade (`validate-plan`)**:
  - Antes de apresentar o Consent Gate, execute obrigatoriamente o validador estático local:
    ```bash
    python .agents/skills/linear-workflow/scripts/linear_api.py validate-plan "<issue-key>"
    ```
  - Corrija quaisquer seções faltantes ou caminhos de arquivos inválidos apontados por `validate-plan`.
- **Apresentação em Chat (Padrão Executive Briefing)**: Apresente obrigatoriamente no chat um **Executive Briefing** conciso (10 a 15 linhas com métricas-chave e referência para `.specs/<issue-key>/`), contendo a proposta de **Título Revisado** e **Descrição Atualizada** do card (refletindo as descobertas arquiteturais e substituindo rascunhos preliminares de `Backlog`), seguida da síntese executiva estruturada sob as 5 seções obrigatórias:
  - **Título Revisado do Card**: `<type>(<scope>): <resumo-tecnico-refinado>`
  - **Descrição Atualizada do Card**: Corpo principal atualizado com contexto, problema, escopo técnico refinado e critérios de aceitação.
  - **Artefatos Spec-Kit Validados**: `.specs/<issue-key>/plan.md` e `.specs/<issue-key>/tasks.md` (`validate-plan`: OK).
  1. **Diagnóstico e Contexto**: Causa-raiz (se bug) ou motivação e requisitos técnicos (se feature).
  2. **Arquitetura da Solução & Desenho Técnico**: Decisões de design, novos contratos, trade-offs e dependências.
  3. **Checklist de Arquivos Impactados**: Lista explícita de caminhos de arquivos a criar, modificar ou remover.
  4. **Estratégia de Testes**: Testes unitários, de integração, comandos de validação e critérios técnicos de aceitação.
  5. **Plano Gitflow**: Nome da branch (`<type>/<issue-key>-<slug>`), padrão de commit (Conventional Commits 1.0.0) e estado alvo `Todo`.
- ⚠️ **Zero Mutação no Linear**: **NÃO altere o status, título ou descrição do card e NÃO comente no Linear nesta etapa.**

> [!IMPORTANT]
> **Proibição de Consent Gate Cego (Renderização Prévia Obrigatória)**:
> É **estritamente proibido** invocar `ask_question` / `AskUserQuestion` sem antes emitir integralmente no texto visível do chat o **Título Revisado**, a **Descrição Atualizada** e a especificação técnica completa com todas as 5 seções obrigatórias. O desenvolvedor jamais deve receber a pergunta de aprovação sem que toda a análise técnica esteja renderizada de forma visível no chat.

### 2. Etapa 2: Consent Gate Interativo (Confirmação Explícita)
- Certifique-se de que o Título Revisado, a Descrição Atualizada e as 5 seções da especificação técnica já foram emitidos no corpo textual da resposta e apresente a pergunta de consentimento invocando a **ferramenta nativa de perguntas** do harness, incluindo obrigatoriamente um **resumo conciso da análise** no próprio texto de `question` como salvaguarda:
  - **Google Antigravity**: chame `ask_question`:
    ```json
    {
      "questions": [
        {
          "question": "Resumo da análise (<issue-key>): <resumo-solucao> | Arquivos: <N> | Branch: <branch>. A análise técnica (incluindo título e descrição revisados) está aprovada? Posso atualizar o card, registrar a especificação técnica no Linear e movê-lo para Todo (pronto para desenvolvimento)?",
          "options": [
            "(Recommended) Sim, aprovar",
            "Editar..."
          ],
          "is_multi_select": false
        }
      ]
    }
    ```
  - **Claude Code**: chame `AskUserQuestion` com o resumo conciso na pergunta e opções `["Sim, aprovar", "Editar..."]`.
  - **OpenCode v2**: chame a ferramenta nativa de pergunta com o resumo conciso na pergunta e opções `["Sim, aprovar", "Editar..."]`.
  - **Fallback Textual (Cursor, Copilot, Gemini CLI ou sem tool nativa)**: apresente em bloco Markdown destacado com o resumo conciso e opções numeradas (`1. (Recomendado) Sim, aprovar` e `2. Editar...`).
- **Tratamento das Opções**:
  - `(Recommended) Sim, aprovar`: avança imediatamente para a **Etapa 3 (Execução Atômica)**.
  - `Editar...`: permite ao desenvolvedor indicar alterações arquiteturais, trade-offs, título/descrição ou arquivos em texto livre. O agente **retorna à Etapa 1**, refina a análise no chat e apresenta novo Consent Gate. **Zero mutação é estritamente mantida**.

### 3. Etapa 3: Execução Atômica & Persistência do Executive Briefing no Linear
- **Persistência Obrigatória no Linear via Arquivos UTF-8 (Estado + Título + Descrição + Executive Briefing de 5 Seções)**: Após aprovação, grave a descrição atualizada e o comentário consolidado (Executive Briefing de 10-15 linhas com síntese das 5 seções e referência a `.specs/<issue-key>/`) em arquivos UTF-8 temporários e execute atomicamente a transição de estado para `Todo` acompanhada da **atualização obrigatória de `--title`, `--description-file` e `--comment-file`** (sanitizados automaticamente por `sanitize_markdown_payload`; nunca passe Markdown contendo crases `` ` `` ou aspas duplas via `--description "..."` ou `--comment "..."` inline, evitando corrupção no PowerShell/Bash):
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "Todo" \
    --title "<titulo-revisado>" \
    --description-file "<descricao-atualizada-utf8.md>" \
    --comment-file "<executive-briefing-5-secoes-utf8.md>"
  ```
  Conteúdo estruturado obrigatório para `<executive-briefing-5-secoes-utf8.md>` (Executive Briefing):
  ```markdown
  🤖 **AI Agent Update**: Análise Técnica Concluída (Executive Briefing)

  - **Artefatos Spec-Kit**: `.specs/<issue-key>/plan.md` & `.specs/<issue-key>/tasks.md` (`validate-plan`: OK)
  - **Métricas**: <N> arquivos impactados | <M> tasks planejadas | Branch: `<type>/<issue-key>-<slug>`

  ### 1. Diagnóstico e Contexto
  <resumo-objetivo-diagnostico>

  ### 2. Arquitetura da Solução & Desenho Técnico
  <resumo-decisoes-e-trade-offs>

  ### 3. Checklist de Arquivos Impactados
  - `<arquivo-1>`
  - `<arquivo-2>`

  ### 4. Estratégia de Testes
  <comandos-e-validacoes-chave>

  ### 5. Plano Gitflow
  - Branch: `<type>/<issue-key>-<slug>` | Commits: Conventional Commits 1.0.0 | Status: `Todo`
  ```
- **Proteção Anti-Corrupção de Shell & Sanitização**: Use sempre `--description-file "<path>"` e `--comment-file "<path>"` para preservar integralmente crases (como `` `feat` ``, `` `fix` ``, `` `test` ``, `` `refactor` ``, `` `chore` ``), blocos de código e aspas duplas em qualquer terminal, contando com `sanitize_markdown_payload` no CLI.
- Notifique o desenvolvedor com a chave do card (ex: `FAL-25`), o título e descrição atualizados, os artefatos em `.specs/<issue-key>/` e o novo status `Todo`.
