# Contract: Spec Kit Continuous Autonomous Execution

Este contrato especifica as interfaces, pré-requisitos, pós-condições e garantias operacionais de cada comando do Spec Kit no modelo contínuo e autônomo com revisão no GitHub.

---

## 1. Princípios de Execução

1. **Zero Consent Gates**: O agente NUNCA deve chamar ferramentas síncronas de perguntas interativas (`ask_question`, `AskUserQuestion`) entre os comandos de ciclo de vida.
2. **Commit & Push Automatizado**: Todo artefato gerado ou modificado deve ser imediatamente comitado seguindo Conventional Commits 1.0.0 e enviado (`git push origin <branch>`) para o Draft PR remoto.
3. **Avanço Atômico de Estado**: O avanço no Linear (`Backlog` ➔ `Planned` ➔ `Todo`) ocorre via `linear_api.py update-issue` utilizando arquivos temporários UTF-8 para prevenir problemas de escape de shell.
4. **Isolamento em Worktree Efêmero**: Comandos que operam sobre um `<CARD-ID>` específico devem executar no worktree `.worktrees/<CARD-ID>` caso a sessão principal não esteja na branch correspondente.

---

## 2. Especificação por Comando

### `/speckit-specify <descrição>`
- **Input**: Descrição em linguagem natural da funcionalidade.
- **Execução**:
  1. Cria branch Gitflow `feat/<CARD-ID>-<slug>` a partir de `develop` (ou `main`).
  2. Inicializa diretório `specs/<feature>/` com `spec.md` e `checklists/requirements.md`.
  3. Comita os artefatos: `docs(spec): specify <CARD-ID> - <slug>`.
  4. Abre Draft PR no GitHub: `gh pr create --draft --title "feat(...) ..." --body-file ...`.
  5. Cria ou associa card no Linear no estado `Backlog`, inserindo link do Draft PR.
  6. Emite Executive Report com links no chat.

### `/speckit-clarify <CARD-ID>`
- **Input**: `<CARD-ID>` obrigatório.
- **Execução**:
  1. Entra no worktree `.worktrees/<CARD-ID>`.
  2. Sincroniza alterações remotas do desenvolvedor: `git pull --rebase origin <branch>`.
  3. Lê `spec.md`, processa marcações de clarificação ou feedbacks.
  4. Comita: `docs(clarify): resolve ambiguities and sync GitHub review for <CARD-ID>`.
  5. Envia ao remote: `git push origin <branch>`.
  6. Emite Executive Report informando prontidão para `/speckit-plan <CARD-ID>`.

### `/speckit-plan <CARD-ID>`
- **Input**: `<CARD-ID>` obrigatório.
- **Execução**:
  1. Entra no worktree `.worktrees/<CARD-ID>`.
  2. Gera artefatos técnicos: `plan.md` (com as 5 seções obrigatórias), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.
  3. Comita: `docs(plan): technical plan and architecture for <CARD-ID>`.
  4. Envia ao remote: `git push origin <branch>`.
  5. Transiciona card no Linear para `Planned` com comentário técnico anexado.
  6. Emite Executive Report no chat sugerindo `/speckit-tasks <CARD-ID>`.

### `/speckit-tasks <CARD-ID>`
- **Input**: `<CARD-ID>` obrigatório.
- **Execução**:
  1. Entra no worktree `.worktrees/<CARD-ID>`.
  2. Gera `tasks.md` ordenado por dependências com checkboxes `- [ ]`.
  3. Executa validação estática: `python skills/linear-workflow/scripts/linear_api.py validate-plan <CARD-ID>`.
  4. Comita: `docs(tasks): implementation tasks decomposition for <CARD-ID>`.
  5. Envia ao remote: `git push origin <branch>`.
  6. Transiciona card no Linear para `Todo`.
  7. Emite Executive Report no chat sugerindo `/speckit-implement <CARD-ID>`.

### `/speckit-implement <CARD-ID>`
- **Input**: `<CARD-ID>` obrigatório.
- **Execução**:
  1. Transiciona card no Linear de `Todo` ➔ `In Progress`.
  2. Executa código e testes conforme `tasks.md`, marcando `- [x]`.
  3. Roda suite de testes e validação com sucesso.
  4. Promove o Pull Request de Draft para Ready: `gh pr ready <pr-number>`.
  5. Transiciona card no Linear para `In Review`.
  6. Emite Executive Report no chat.

### `/speckit-converge <CARD-ID>`
- **Input**: `<CARD-ID>` obrigatório.
- **Execução**:
  1. Transiciona card no Linear de `In Review` ➔ `In Progress`.
  2. Aplica correções solicitadas nas revisões do GitHub.
  3. Comita, roda testes e envia ao PR.
  4. Registra comentário de resolução no PR no GitHub.
  5. Retorna card no Linear para `In Review`.
  6. Emite Executive Report no chat.
