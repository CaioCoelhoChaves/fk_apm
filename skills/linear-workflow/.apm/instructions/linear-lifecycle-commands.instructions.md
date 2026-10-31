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
   - Ao especificar um card novo com execução autônoma, cria a branch Gitflow `<type>/<CARD-ID>-<slug>`, realiza commit inicial de `spec.md`, abre Pull Request em modo Draft via `gh pr create --draft` e registra o link no card em `Backlog`.

3. **Esteira Contínua e Autônoma de Ciclo de Vida (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`)**:
   - **Zero Consent Gates no Chat**: Todos os comandos de ciclo de vida executam com 100% de autonomia, sem invocar `ask_question` ou `AskUserQuestion`. A governança, diffs e revisão técnica ocorrem diretamente no GitHub através do Living Spec Draft PR.
   - **Execução Sequencial Autônoma**:
     - `/speckit-specify`: Gera `spec.md` e `checklists/requirements.md`, cria branch Gitflow, abre Draft PR no GitHub via `gh pr create --draft`, cria card no Linear em **`Backlog`** e emite Executive Report com links no chat.
     - `/speckit-plan`: Gera `plan.md` (com as 5 seções obrigatórias), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, comita na branch remota do Draft PR e avança card para **`Planned`** com **Título Revisado** e **Descrição Atualizada** (`update-issue "<id>" --state "Planned" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"`).
     - `/speckit-tasks`: Gera `tasks.md` ordenado por dependências, valida com `linear_api.py validate-plan`, comita na branch remota do Draft PR e avança card para **`Todo`** com **Título Revisado** e **Descrição Atualizada** (`update-issue "<id>" --state "Todo" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"`).
     - `/speckit-taskstoissues`: Converte tasks em sub-cards atômicos em **`Backlog`** de forma autônoma utilizando arquivos temporários UTF-8.

4. **Execução Autônoma de Implementação e Convergência (`/speckit-implement` e `/speckit-converge`)**:
   - **`/speckit-implement`**: Verifica pré-requisitos (`check_prerequisites.py` e `validate-plan`) ➔ move o card imediatamente para **`In Progress`** (`--comment-file`) ➔ executa na branch Gitflow do PR ou em worktree efêmero ➔ completa todas as tasks de `tasks.md` marcando `- [X]` ➔ roda testes ➔ promove PR para pronto (`gh pr ready`) ➔ move obrigatoriamente o card para **`In Review`** (`--comment-file`).
   - **`/speckit-converge`**: Lê comentários/reviews do PR aberto ➔ move o card para **`In Progress`** (`--comment-file`) ➔ aplica correções na branch do PR ➔ faz push e comenta no PR (`gh pr comment --body-file`) ➔ retorna o card para **`In Review`** (`--comment-file`).
   - **Salvaguarda Inviolável para `Done`**: O agente **NUNCA** move cards para `Done` (transição exclusivamente manual pelo desenvolvedor após o merge do PR).

5. **Proibição de Markdown Inline no Shell & Sanitização (`sanitize_markdown_payload`)**:
   - Nunca passe Markdown contendo crases (`` ` ``), blocos de código ou aspas duplas via `--description "..."`, `--comment "..."` ou `--body "..."`. Sempre utilize arquivos UTF-8 temporários com `--description-file`, `--comment-file` e `--body-file`.
