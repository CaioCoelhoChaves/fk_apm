---
description: Interceptação universal e roteamento multi-harness para comandos Spec Kit acoplados ao Linear (/speckit-*)
---

# Roteamento Universal de Comandos `/speckit-*` Acoplados ao Linear

Esta regra intercepta os comandos oficiais do pacote `github/spec-kit` (`/speckit-*`) acoplados ao ciclo de vida de 6 estados do Linear (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`) em todos os harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, OpenCode), garantindo tolerância sintática, Living Specs com Draft PRs imediatos e isolamento via Git Worktrees efêmeros acionados por `<CARD-ID>`.

## 1. Gatilhos de Interceptação (`/speckit-*` Oficial)

Sempre que a mensagem do usuário contiver qualquer um dos seguintes gatilhos (com ou sem barra `/` inicial):

- **Governança / Constituição**: `/speckit-constitution`, `speckit-constitution`.
- **Especificação & Criação de Cards (`Backlog`)**: `/speckit-specify`, `speckit-specify`, `/speckit-taskstoissues`, `speckit-taskstoissues`.
- **Clarificação de Requisitos**: `/speckit-clarify`, `speckit-clarify`.
- **Plano Técnico (`Backlog` ➔ `Planned`)**: `/speckit-plan`, `speckit-plan`.
- **Checklist de Tasks (`Planned` ➔ `Todo`)**: `/speckit-tasks`, `speckit-tasks`.
- **Auditoria & Checklists**: `/speckit-analyze`, `speckit-analyze`, `/speckit-checklist`, `speckit-checklist`.
- **Implementação Autônoma (`Todo` ➔ `In Progress` ➔ `In Review`)**: `/speckit-implement`, `speckit-implement`.
- **Convergência & Correção Autônoma de Review (`In Review` ➔ `In Progress` ➔ `In Review`)**: `/speckit-converge`, `speckit-converge`.

## 2. Ações Mandatórias do Agente

1. **Ativação da Skill & Bootstrap `.specify/`**:
   - Ative imediatamente as instruções da sub-skill `/speckit-*` correspondente e os padrões de `skills/linear-workflow/SKILL.md`.
   - Caso o diretório `.specify/` ainda não exista na raiz do repositório consumidor, execute `python skills/linear-workflow/scripts/linear_api.py bootstrap-specify`.

2. **Living Specs com Draft PR Imediato (`/speckit-specify`)**:
   - Ao especificar um card novo, renderiza a tabela Pre-Render no chat e cria diretamente a branch Gitflow `<type>/<CARD-ID>-<slug>`, realiza commit inicial de `spec.md`, abre Pull Request em modo Draft via `gh pr create --draft --body-file` e cria o card em `Backlog` via `--description-file`.

3. **Pre-Render Obrigatório + Execução Direta Orientada a Diálogo (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`) & Exceção em Lote (`/speckit-taskstoissues`)**:
   - **Pre-Render Obrigatório no Chat**: Gere/atualize os artefatos oficiais do Spec Kit em `specs/<feature>/` (`spec.md`, `plan.md` com as 5 seções obrigatórias, `tasks.md` com `- [ ] T001 ...`), valide com `python skills/linear-workflow/scripts/linear_api.py validate-plan <CARD-ID>` e **renderize obrigatoriamente no texto visível do chat** a tabela de card proposto (em `/speckit-specify`) ou o **Executive Briefing** contendo o **Título Revisado**, a **Descrição Atualizada** e as **5 seções obrigatórias** (`1. Diagnóstico e Contexto`, `2. Arquitetura da Solução & Desenho Técnico`, `3. Checklist de Arquivos Impactados`, `4. Estratégia de Testes`, `5. Plano Gitflow`).
   - **Execução Direta sem Rito Final (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`)**: Sem invocar ferramenta de pergunta de confirmação final, execute imediatamente via arquivos UTF-8: crie o card em **`Backlog`**, mova o card para **`Planned`** (`update-issue "<id>" --state "Planned" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"`) ou mova para **`Todo`** (`update-issue "<id>" --state "Todo" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"`). Eventuais ambiguidades críticas são resolvidas por diálogo natural com o usuário.
   - **Exceção Preservada (`/speckit-taskstoissues`)**: Mantém o **3-Stage Consent Gate** completo (`Pre-Render Gate` ➔ `ask_question` / `AskUserQuestion` com `["(Recommended) Sim, aprovar", "Editar..."]` ➔ criação atômica em lote em **`Backlog`**).

4. **Execução Autônoma sem Consent Gate (`/speckit-implement` e `/speckit-converge`)**:
   - **`/speckit-implement`**: Verifica pré-requisitos (`check_prerequisites.py` e `validate-plan`) ➔ move o card imediatamente para **`In Progress`** (`--comment-file`) ➔ executa na branch Gitflow do PR ou em worktree efêmero (diálogo natural apenas em ambiguidade genuinamente bloqueante) ➔ completa todas as tasks de `tasks.md` marcando `- [X]` ➔ roda testes ➔ promove PR para pronto (`gh pr ready --body-file`) ➔ move obrigatoriamente o card para **`In Review`** (`--comment-file`).
   - **`/speckit-converge`**: Lê comentários/reviews do PR aberto ➔ move o card para **`In Progress`** (`--comment-file`) ➔ aplica correções na branch do PR ➔ faz push e comenta no PR (`gh pr comment --body-file`) ➔ retorna o card para **`In Review`** (`--comment-file`).
   - **`Done`**: O agente **NUNCA** move cards para `Done` (transição exclusivamente manual pelo desenvolvedor após o merge do PR).

5. **Proibição de Markdown Inline no Shell & Sanitização (`sanitize_markdown_payload`)**:
   - Nunca passe Markdown contendo crases (`` ` ``), blocos de código ou aspas duplas via `--description "..."`, `--comment "..."` ou `--body "..."`. Sempre utilize arquivos UTF-8 temporários com `--description-file`, `--comment-file` e `--body-file`.
