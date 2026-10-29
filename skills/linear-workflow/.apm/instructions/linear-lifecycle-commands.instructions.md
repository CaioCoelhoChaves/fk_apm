---
description: Interceptação universal e roteamento multi-harness para comandos Spec Kit acoplados ao Linear (/speckit-* e compatibilidade /fk-*)
---

# Roteamento Universal de Comandos `/speckit-*` Acoplados ao Linear

Esta regra intercepta os comandos oficiais do pacote `github/spec-kit` (`/speckit-*`) acoplados ao ciclo de vida do Linear em todos os harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot, OpenCode), garantindo tolerância sintática e acionamento rigoroso da skill `linear-workflow`.

## 1. Gatilhos de Interceptação (`/speckit-*` Oficial + Compatibilidade Legada)

Sempre que a mensagem do usuário contiver qualquer um dos seguintes gatilhos (com ou sem barra `/` inicial):

- **Governança / Constituição**: `/speckit-constitution`, `speckit-constitution`.
- **Especificação & Criação de Cards (`Backlog`)**: `/speckit-specify`, `speckit-specify`, `/speckit-taskstoissues`, `speckit-taskstoissues` (ou legado `/fk-new-issue`).
- **Clarificação de Requisitos**: `/speckit-clarify`, `speckit-clarify`.
- **Plano Técnico & Tasks (`Technical Analysis` ➔ `Todo`)**: `/speckit-plan`, `speckit-plan`, `/speckit-tasks`, `speckit-tasks` (ou legado `/fk-technical-analysis`).
- **Auditoria & Checklists**: `/speckit-analyze`, `speckit-analyze`, `/speckit-checklist`, `speckit-checklist`.
- **Implementação Autônoma (`Todo` ➔ `In Progress` ➔ `In Review`)**: `/speckit-implement`, `speckit-implement` (ou legado `/fk-develop`).
- **Convergência & Correção Autônoma de Review (`In Review` ➔ `In Progress` ➔ `In Review`)**: `/speckit-converge`, `speckit-converge` (ou legado `/fk-fix`).

## 2. Ações Mandatórias do Agente

1. **Ativação da Skill & Bootstrap `.specify/`**:
   - Ative imediatamente as instruções da sub-skill `/speckit-*` correspondente e os padrões de `skills/linear-workflow/SKILL.md`.
   - Caso o diretório `.specify/` ainda não exista na raiz do repositório consumidor, execute `python skills/linear-workflow/scripts/linear_api.py bootstrap-specify`.

2. **Protocolo Inviolável de 3 Etapas (*Consent Gate*) para Especificação e Planejamento (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`)**:
   - **Etapa 1 (Pre-Render Gate — Zero Mutação no Linear)**: Gere/atualize os artefatos oficiais do Spec Kit em `specs/<feature>/` (`spec.md`, `plan.md` com as 5 seções obrigatórias, `tasks.md` com `- [ ] T001 ...`), valide com `python skills/linear-workflow/scripts/linear_api.py validate-plan` e **renderize obrigatoriamente no texto visível do chat** a tabela de cards propostos (em `/speckit-specify` / `/speckit-taskstoissues`) ou o **Executive Briefing** contendo o **Título Revisado**, a **Descrição Atualizada** e as **5 seções obrigatórias** (`1. Diagnóstico e Contexto`, `2. Arquitetura da Solução & Desenho Técnico`, `3. Checklist de Arquivos Impactados`, `4. Estratégia de Testes`, `5. Plano Gitflow`) **antes** de invocar qualquer ferramenta de pergunta.
   - **Etapa 2 (Consent Gate Interativo com Resumo Embutido)**: Acione `ask_question` (Antigravity) ou `AskUserQuestion` (Claude Code / Cursor / Copilot) embutindo um resumo conciso no campo `question`, com as opções `["(Recommended) Sim, aprovar", "Editar..."]`.
   - **Etapa 3 (Execução Atômica no Linear via Arquivos UTF-8)**: Somente após aprovação explícita, crie os cards em **`Backlog`** (`create-issue --state "Backlog" --description-file "<utf8.md>"`) ou mova o card para **`Todo`** (`update-issue "<id>" --state "Todo" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"`).

3. **Execução Autônoma sem Consent Gate (`/speckit-implement` e `/speckit-converge`)**:
   - **`/speckit-implement`**: Verifica pré-requisitos (`check_prerequisites.py --json --require-tasks --include-tasks` e `validate-plan`) ➔ move o card imediatamente para **`In Progress`** (`--comment-file`) ➔ cria branch Gitflow `<type>/<issue-key>-<slug>` ➔ executa todas as tasks de `tasks.md` marcando `- [X]` ➔ roda testes ➔ abre PR (`gh pr create --body-file`) ➔ move obrigatoriamente o card para **`In Review`** (`--comment-file`).
   - **`/speckit-converge`**: Lê comentários/reviews do PR aberto e gaps da spec ➔ move o card para **`In Progress`** (`--comment-file`) ➔ registra e executa as tasks corretivas em `## Phase N: Convergence` no `tasks.md` ➔ faz push e comenta no PR (`gh pr comment --body-file`) ➔ retorna o card para **`In Review`** (`--comment-file`).
   - **`Done`**: O agente **NUNCA** move cards para `Done` (transição exclusivamente manual pelo desenvolvedor após o merge do PR).

4. **Proibição de Markdown Inline no Shell & Sanitização (`sanitize_markdown_payload`)**:
   - Nunca passe Markdown contendo crases (`` ` ``), blocos de código ou aspas duplas via `--description "..."`, `--comment "..."` ou `--body "..."`. Sempre utilize arquivos UTF-8 temporários com `--description-file`, `--comment-file` e `--body-file`.
