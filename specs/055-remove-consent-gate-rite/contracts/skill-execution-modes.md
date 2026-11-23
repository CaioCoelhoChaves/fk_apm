# Contracts: Modos de Execução das Skills `/speckit-*` no Linear Workflow

**Issue**: [FAL-74](https://linear.app/fallkey/issue/FAL-74/featlinear-workflow-remover-rito-de-aprovacao-final-nas-etapas-speckit) | **Branch**: `feat/FAL-74-remove-consent-gate-rite` | **Date**: 2026-11-23

Este contrato especifica o comportamento normativo esperado para os comandos do `linear-workflow`, suas instruções multi-harness (`.apm/skills/`, `.apm/prompts/`, `.apm/instructions/`) e as invariantes verificadas pela suíte de testes unitários.

---

## 1. Contratos de Execução Direta Orientada a Diálogo (Sem Rito de Aprovação Final)

### 1.1 `/speckit-specify <descrição>`
- **Pré-condições**: Diretório `.specify/` presente (ou inicializado via `linear_api.py bootstrap-specify`).
- **Execução**:
  1. Gera `specs/<feature>/spec.md` e `specs/<feature>/checklists/requirements.md`.
  2. Identifica projeto/labels e deduplica issues no Linear (`find-project`, `search-issues`).
  3. **Pre-Render Obrigatório no Chat**: Renderiza a tabela Markdown completa do card proposto (`# | Título Proposto | Coluna Inicial (Backlog) | Label | Projeto Linear | Resumo & Critérios de Aceite`) diretamente no texto visível do chat.
  4. **Execução Direta (Zero Rito de Aprovação Final)**: Não invoca `ask_question` / `AskUserQuestion` com opções `"Sim, aprovar"` / `"Editar..."`. Cria diretamente a branch Gitflow `<type>/<CARD-ID>-<slug>`, comita `spec.md` e `checklists/requirements.md`, faz push, abre o Draft PR via `gh pr create --draft --body-file` e cria o card no Linear em `Backlog` via `linear_api.py create-issue --state "Backlog" --description-file`.
  5. Se houver ambiguidade crítica real, resolve por diálogo natural com o usuário antes de fechar a especificação ou orienta `/speckit-clarify <CARD-ID>`.

### 1.2 `/speckit-plan <CARD-ID>`
- **Pré-condições**: `<CARD-ID>` válido (`^[A-Z]{2,10}-\d+$`); workspace na branch do card ou em `.worktrees/<CARD-ID>`.
- **Execução**:
  1. Executa `setup_plan.py --json` e gera `plan.md` (contendo as 5 seções obrigatórias), `research.md`, `data-model.md`, `contracts/` e `quickstart.md`.
  2. Valida localmente com `linear_api.py validate-plan <CARD-ID>` (garantindo as 5 seções e caminhos reais válidos em `plan.md`).
  3. Comita e envia os artefatos de planejamento para a branch do Draft PR.
  4. **Pre-Render Obrigatório no Chat**: Renderiza no chat o **Executive Briefing** completo contendo **Título Revisado**, **Descrição Atualizada** e o resumo das **5 seções obrigatórias**.
  5. **Execução Direta (Zero Rito de Aprovação Final)**: Não invoca `ask_question` / `AskUserQuestion` para confirmação final. Executa imediatamente `linear_api.py update-issue "<issue-id>" --state "Planned" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"` e orienta `Próximo passo: /speckit-tasks <CARD-ID>`.

### 1.3 `/speckit-tasks <CARD-ID>`
- **Pré-condições**: `<CARD-ID>` válido; `plan.md` presente; workspace na branch do card ou em `.worktrees/<CARD-ID>`.
- **Execução**:
  1. Executa `setup_tasks.py --json` e gera `specs/<feature>/tasks.md` com checklist acionável `- [ ] T001 ...`.
  2. Executa `linear_api.py validate-plan <CARD-ID>` e verifica `"valid": true`.
  3. Comita e envia `tasks.md` para a branch do Draft PR.
  4. **Pre-Render Obrigatório no Chat**: Renderiza no chat o **Executive Briefing** contendo **Título Revisado**, **Descrição Atualizada**, resumo das **5 seções obrigatórias** e contagem de tasks por User Story.
  5. **Execução Direta (Zero Rito de Aprovação Final)**: Não invoca `ask_question` / `AskUserQuestion` para confirmação final. Executa imediatamente `linear_api.py update-issue "<issue-id>" --state "Todo" --title "<titulo-revisado>" --description-file "<desc-utf8.md>" --comment-file "<briefing-utf8.md>"` e orienta `Próximo passo: /speckit-implement <CARD-ID>`.

### 1.4 `/speckit-implement <CARD-ID>`
- **Execução 100% Autônoma**:
  1. Verifica pré-requisitos (`check_prerequisites.py --json --require-tasks --include-tasks` e `validate-plan <CARD-ID>`).
  2. Move imediatamente o card para `In Progress` (`--comment-file`), implementa todas as tasks marcando `- [X]`, executa a suíte de testes e atualiza `CHANGELOG.md`.
  3. Comita, faz push, promove o PR para pronto (`gh pr ready`) com `--body-file` e move o card para `In Review` (`--comment-file`).
  4. **Zero Rito de Aprovação Final**: Nunca pergunta antes de iniciar, implementar, promover PR ou mover para `In Review`. Em caso de ambiguidade genuinamente bloqueante em `spec.md`/`plan.md`, utiliza diálogo natural ou decide tecnicamente documentando a premissa.
  5. Nunca transiciona para `Done` (rito exclusivo humano após merge).

---

## 2. Exceção Explicitamente Preservada: `/speckit-taskstoissues [<CARD-ID>]`

- Mantém integralmente o **3-Stage Consent Gate**:
  1. **Stage 1 (Pre-Render Gate)**: Renderiza a tabela completa de sub-cards propostos no chat sem mutar o Linear.
  2. **Stage 2 (Interactive Confirmation)**: Invoca `ask_question` / `AskUserQuestion` com resumo embutido e opções `["(Recommended) Sim, aprovar", "Editar..."]`.
  3. **Stage 3 (Atomic Creation)**: Somente após aprovação explícita cria os sub-cards em `Backlog` via `--description-file`.

---

## 3. Contratos Verificados pela Suíte `test_linear_api.py`

1. **Pre-Render & Payloads UTF-8**: `SKILL.md`, `speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`, `speckit-converge`, `linear-lifecycle-commands.instructions.md`, `multi-harness-commands.md` e `states-and-labels.md` DEVEM manter obrigatoriamente `Pre-Render`, `Executive Briefing`, `Título Revisado`, `Descrição Atualizada`, `--title`, `--description-file`, `--comment-file` e `--body-file`.
2. **Ausência de Rito Final nas 4 Etapas**: Os arquivos `.apm/skills/<cmd>/SKILL.md` e `.apm/prompts/<cmd>.prompt.md` de `speckit-specify`, `speckit-plan`, `speckit-tasks` e `speckit-implement` NÃO DEVEM exigir invocação de `"Sim, aprovar"` / `"Editar..."` nem conter instruções obrigando Consent Gate final antes de criar/transicionar cards.
3. **Preservação do Consent Gate em `speckit-taskstoissues`**: `speckit-taskstoissues/SKILL.md` e `speckit-taskstoissues.prompt.md` DEVEM manter o protocolo de 3 etapas com `"Sim, aprovar"` e `"Editar..."`.
4. **Paridade Multi-Harness & Deploy `.agents/`**: Cada par `.apm/skills/<cmd>/SKILL.md` e `.apm/prompts/<cmd>.prompt.md` deve permanecer sincronizado com seu equivalente implantado em `.agents/skills/<cmd>/SKILL.md` após `apm install`.
