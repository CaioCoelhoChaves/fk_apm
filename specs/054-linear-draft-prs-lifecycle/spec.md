# Feature Specification: Living Specs & Draft PR Lifecycle com Linear Workflow e Sync de Boards

**Feature Branch**: `feat/FAL-58-modernizar-linear-workflow-draft-prs`

**Linear Issue**: [FAL-58](https://linear.app/fallkey/issue/FAL-58/featworkflow-modernizar-linear-workflow-com-ciclo-draft-prs-e)

**Created**: 2026-10-29

**Status**: Draft

**Input**: User description: "Refatorar e modernizar integralmente a integração do github/spec-kit com o Linear e o Gitflow na skill linear-workflow, implementando o ciclo de vida com Draft PRs desde a concepção da spec, novo mapeamento de estados do Linear (Backlog -> Planned -> Todo -> In Progress -> In Review -> Done), ferramenta de provisionamento e sincronização de boards do Linear, e limpeza de todo o código legado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Concepção da Spec com Draft PR Imediato e Card em Backlog (Priority: P1)

Como desenvolvedor ou arquiteto de software utilizando `/speckit-specify`, desejo que a branch Gitflow seja criada e enviada ao GitHub com um Pull Request em modo Draft logo no início da especificação, vinculando o card criado no Linear (na coluna `Backlog`) à URL do PR Draft para garantir visibilidade contínua e colaboração antecipada (*Living Specs*).

**Why this priority**: Estabelece a fundação de visibilidade e versionamento imediato de specs no GitHub e Linear, substituindo a prática de branches e artefatos locais não rastreados até a fase de implementação.

**Independent Test**: Pode ser validado executando `/speckit-specify` com descrição de feature, verificando a criação da branch local/remota, publicação do Draft PR no GitHub via `gh pr create --draft`, e criação do card no Linear em `Backlog` contendo o link do PR no corpo da issue.

**Acceptance Scenarios**:

1. **Given** um repositório limpo configurado com GitHub CLI e credenciais do Linear, **When** o usuário executa `/speckit-specify` e aprova a proposta no Consent Gate (Estágio 2), **Then** o sistema cria a branch `feat/<issue-id>-<slug>`, versiona `specs/<feature>/spec.md` com Conventional Commit `docs(spec): add specification for <issue-id>`, realiza `git push -u origin <branch>`, abre o PR Draft via `gh pr create --draft` e cria o card no Linear em `Backlog` vinculado ao PR.
2. **Given** um card já criado em `Backlog`, **When** o usuário aciona `/speckit-clarify` para dirimir dúvidas, **Then** as alterações em `spec.md` são commitadas e enviadas ao PR Draft existente, mantendo o card no Linear em `Backlog` sem duplicar issues.

---

### User Story 2 - Máquina de Estados Linear de 6 Estágios e Transições Controladas (Priority: P1)

Como tech lead e desenvolvedor, desejo que cada etapa do ciclo Spec Kit avance o card no Linear estritamente para a coluna correspondente (`Backlog` -> `Planned` -> `Todo` -> `In Progress` -> `In Review` -> `Done`), garantindo que o status do board represente com precisão a maturidade do artefato e o estágio de engenharia.

**Why this priority**: Padroniza os boards e elimina discrepâncias entre o progresso da especificação e o status do time no Linear.

**Independent Test**: Pode ser testado sequencialmente acionando os comandos do Spec Kit e inspecionando o estado da issue via `linear_api.py get-issue`.

**Acceptance Scenarios**:

1. **Given** um card em `Backlog`, **When** `/speckit-plan` conclui a arquitetura com aprovação no Consent Gate, **Then** o card é transicionado para `Planned`, com commit no PR Draft (`docs(plan): ...`) e comentário estruturado via `--comment-file`.
2. **Given** um card em `Planned`, **When** `/speckit-tasks` valida o checklist de execução com aprovação no Consent Gate, **Then** o card avança para `Todo`, com commit no PR Draft (`docs(tasks): ...`) e comentário estruturado via `--comment-file`.
3. **Given** um card em `Todo`, **When** `/speckit-implement` inicia a codificação autônoma, **Then** o card é movido para `In Progress`, os testes e códigos são implementados, o PR Draft é promovido para pronto via `gh pr ready`, e o card é avançado para `In Review`.
4. **Given** um card em `In Review`, **When** qualquer agente tenta realizar transição automatizada para `Done`, **Then** a operação é estritamente proibida e rejeitada, pois `Done` é rito exclusivo manual do desenvolvedor pós-merge.

---

### User Story 3 - Provisionamento e Sincronização Inteligente de Boards do Linear (Priority: P2)

Como mantenedor de projetos e Scrum Master, desejo comandos de automação (`sync-boards` e `setup-board`) na CLI `linear_api.py` para inspecionar todos os boards da organização, alinhar cores/ordenações de colunas e migrar estados legados (ex: `Technical Analysis`) para a nova esteira sem perda de dados.

**Why this priority**: Permite que times novos e existentes adotem o novo fluxo sem fricção manual de configuração de workflow no Linear.

**Independent Test**: Pode ser testado executando `linear_api.py sync-boards --dry-run` e `linear_api.py setup-board --team-id <TID>`, validando a detecção e reconciliação de estados.

**Acceptance Scenarios**:

1. **Given** um time no Linear sem a coluna `Planned` ou com `Technical Analysis` legada, **When** o usuário executa `linear_api.py sync-boards`, **Then** o script cria ou renomeia o estado `Planned` com tipo `unstarted`, ajusta posições das colunas (`Backlog`=0, `Planned`=1, `Todo`=2, `In Progress`=3, `In Review`=4, `Done`=5, `Canceled`=6) e mapeia cards ativos de forma segura.
2. **Given** um novo time recém-criado no Linear, **When** o administrador executa `linear_api.py setup-board --team-id <TID>`, **Then** o script provisiona idempotentemente todos os 6 estados com seus tipos nativos e cores padronizadas.

---

### User Story 4 - Convergência Autônoma e Resolução de Code Review com Draft PR (Priority: P2)

Como desenvolvedor, desejo que `/speckit-converge` leia comentários e revisões do Pull Request, mova o card temporariamente para `In Progress`, aplique correções de código e testes diretamente na branch, comente no PR o que foi resolvido e retorne o card para `In Review` de forma autônoma.

**Why this priority**: Fecha o ciclo de vida de feedback de código sem necessidade de intervenção repetitiva do desenvolvedor na esteira do Linear.

**Independent Test**: Pode ser validado simulando um PR com comentários de review, invocando `/speckit-converge`, e conferindo o ciclo `In Review` -> `In Progress` -> Fixes + Commits -> `In Review` com comentário no PR.

**Acceptance Scenarios**:

1. **Given** um PR em revisão vinculado a um card `In Review`, **When** `/speckit-converge` é acionado, **Then** o card é movido para `In Progress`, as correções solicitadas são implementadas e testadas, um novo commit é enviado à branch remota, um comentário de fechamento é publicado no PR e o card retorna para `In Review`.

---

### User Story 5 - Limpeza e Depreciação de Código Legado (Priority: P3)

Como mantenedor da base de código do `fk_apm`, desejo que todos os resquícios do fluxo legado (como referências a `/fk-*`, estados obsoletos, templates não padronizados e scripts duplicados) sejam completamente removidos ou atualizados, garantindo um repositório limpo e coeso.

**Why this priority**: Previne desvios conceituais, confusão entre desenvolvedores e dívida técnica nos bundles do APM.

**Independent Test**: Verificação por varredura estática de texto (`grep`/`ripgrep`) garantindo ausência de menções aos fluxos legados e conferindo se todos os testes unitários cobrem apenas a nova esteira.

**Acceptance Scenarios**:

1. **Given** o repositório `fk_apm`, **When** a limpeza for executada, **Then** a pasta `skills/linear-workflow` e os templates em `.specify/` não possuem nenhuma menção a comandos legados depreciados e a cobertura de testes reflete 100% da nova especificação.

---

### Edge Cases

- O que acontece se a chamada para `gh pr create --draft` falhar por falta de autenticação no GitHub CLI?
  O sistema interrompe a transição, salva os artefatos locais com segurança, e orienta o usuário a executar `gh auth login` antes de retomar.
- O que acontece se o time no Linear já possui um estado com nome ligeiramente diferente (ex: "Em Planejamento" ou "Planejado")?
  O subcomando `sync-boards` opera com tolerância e mapeamento de sinônimos conhecidos, solicitando confirmação do usuário antes de renomear ou migrar.
- Como o sistema trata comandos executados em repositório sem remote configurado?
  A criação do PR Draft é suspensa com mensagem clara instruindo a configuração de `git remote add origin ...`, operando em modo offline/local até que o remote esteja acessível.
- E se o usuário fechar ou cancelar o PR no GitHub manualmente?
  Ao detectar o PR fechado sem merge durante `/speckit-converge` ou consulta de status, o agente orienta a transição do card para `Canceled` ou reabertura do PR.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE criar a branch Gitflow (`feat/<issue-id>-<slug>`) e o Pull Request em modo Draft (`gh pr create --draft`) logo na etapa de `/speckit-specify` assim que o Consent Gate for aprovado.
- **FR-002**: O sistema DEVE criar o card no Linear na coluna `Backlog` (tipo nativo `backlog`), vinculando explicitamente a URL do Draft PR no corpo da issue.
- **FR-003**: O comando `/speckit-clarify` DEVE commitar atualizações de `spec.md` na branch do PR Draft e manter o card no Linear em `Backlog`.
- **FR-004**: O comando `/speckit-plan` DEVE gerar `plan.md` com arquitetura e impacto, commitar no PR Draft (`docs(plan): ...`), e avançar o card no Linear para `Planned` (tipo nativo `unstarted`) após aprovação no Consent Gate.
- **FR-005**: O comando `/speckit-tasks` DEVE quebrar a implementação em checklist ordenado em `tasks.md`, commitar no PR Draft (`docs(tasks): ...`), validar com `validate-plan`, e avançar o card no Linear para `Todo` (tipo nativo `unstarted`) após aprovação no Consent Gate.
- **FR-006**: O comando `/speckit-implement` DEVE operar de forma autônoma (sem Consent Gate), movendo o card para `In Progress` (tipo nativo `started`), executando a codificação e testes, convertendo o PR para pronto (`gh pr ready`) e movendo o card para `In Review` (tipo nativo `started`).
- **FR-007**: O comando `/speckit-converge` DEVE operar de forma autônoma (sem Consent Gate), transicionando temporariamente o card para `In Progress` durante correções de code review e retornando para `In Review` ao finalizar e enviar os commits ao PR.
- **FR-008**: O sistema NUNCA DEVE mover cards automaticamente para `Done` (tipo nativo `completed`), assegurando que esta ação seja prerrogativa estritamente humana após o merge do PR.
- **FR-009**: A CLI `linear_api.py` DEVE disponibilizar os subcomandos `sync-boards` e `setup-board`, permitindo auditoria, provisionamento e padronização idempotente dos estados (`Backlog`, `Planned`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`) com cores e posições estritas em todos os times do workspace.
- **FR-010**: A CLI `linear_api.py` DEVE suportar migração transparente de cards em estados legados (como `Technical Analysis`) para `Planned` sem corromper histórico ou atribuições.
- **FR-011**: O sistema DEVE aplicar sanitização determinística (`sanitize_markdown_payload`) em todas as comunicações com o Linear e GitHub, proibindo payloads markdown inline em argumentos de linha de comando.
- **FR-012**: O Consent Gate em 3 etapas (Pre-Render Gate visual, confirmação via `ask_question`/`AskUserQuestion`, execução atômica) DEVE ser mantido como barreira inviolável nas etapas de especificação e planejamento (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`).
- **FR-013**: Todo código legado, menções a scripts de pipeline legados (`/fk-*`) e regras defasadas DEVEM ser expurgados da skill `linear-workflow` e seus assets.

### Key Entities *(include if feature involves data)*

- **Linear Workflow State**: Representa uma coluna na esteira Kanban do Linear. Atributos: `id`, `name` (`Backlog`, `Planned`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`), `type` (`backlog`, `unstarted`, `started`, `completed`, `canceled`), `position` (ordenação sequencial), `color` (código hexadecimal).
- **Living Spec Draft PR**: Pull Request no GitHub aberto em modo Draft na concepção da spec. Atributos: `pr_number`, `branch_name`, `is_draft` (booleano), `title` (`feat(<issue-id>): <slug>`), `spec_files` (`spec.md`, `plan.md`, `tasks.md`).
- **Linear Issue Context**: Card de trabalho vinculado ao ciclo Spec Kit. Atributos: `issue_id`, `identifier` (ex: `FAL-54`), `title`, `state`, `pr_url`, `project_id`, `team_id`, `labels`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% dos novos cards gerados por `/speckit-specify` nascem com Pull Request Draft ativo no GitHub vinculado ao corpo do card no Linear.
- **SC-002**: Redução a zero (0) de falhas de renderização de markdown (crases órfãs, pipes desalinhados, caracteres de escape) em cards e comentários do Linear.
- **SC-003**: 100% de conformidade dos times inspecionados por `sync-boards` com a esteira padronizada de 6 estágios (`Backlog` -> `Planned` -> `Todo` -> `In Progress` -> `In Review` -> `Done`).
- **SC-004**: Zero ocorrências de transições automatizadas indevidas para o estado `Done`, preservando a auditoria manual de merge.
- **SC-005**: 100% dos testes unitários da suíte `test_linear_api.py` passando com validação completa dos novos subcomandos e estados.

## Assumptions

- O desenvolvedor possui o GitHub CLI (`gh`) instalado e autenticado com permissões para criar branches, pushes e Pull Requests no repositório remoto.
- A API Key do Linear ou integração Linear MCP Server possui permissões administrativas para gerenciar workflow states caso `sync-boards` ou `setup-board` sejam invocados.
- A branch base padrão do repositório é `main` ou `develop`.
- O repositório segue a convenção de monorepo ou pacote APM onde artefatos de spec residem em `specs/<feature-dir>/`.
