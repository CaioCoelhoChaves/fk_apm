# Feature Specification: Fluxo Contínuo e Autônomo do Spec Kit com Revisão Centralizada no GitHub

**Feature Branch**: `feat/FAL-60-autonomous-speckit-github-review`

**Linear Issue**: [FAL-60](https://linear.app/fallkey/issue/FAL-60/featworkflow-eliminar-consent-gates-entre-fases-do-speckit-e-habilitar)

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Eu quero fazer mudanças no meu fluxo com speckit, atualmente é me pedido aprovação a cada etapa, porém não está sendo útil, pois no final das contas eu vejo o andamento no github, e eu gostaria de fazer a revisão por lá, e caso tenha algo a ser mudado na fase de specify eu rodo o clarify e ele pega as mudanças no github sozinho, e por assim vai. Sem nenhum gate de aprovação por entre as fases"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execução Autônoma Entre Fases Sem Consent Gates Interativos (Priority: P1)

Como desenvolvedor ou arquiteto de software utilizando os comandos de ciclo de vida do Spec Kit (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`), desejo que a execução de cada etapa ocorra de ponta a ponta sem interrupções de confirmação interativa no chat (eliminação do Consent Gate de 3 etapas com `ask_question`), realizando automaticamente as mutações locais, versionamento Git, sincronização com o Draft PR no GitHub e transição do estado correspondente no Linear (`Backlog` ➔ `Planned` ➔ `Todo`).

**Why this priority**: Elimina a principal fonte de atrito e bloqueios no fluxo de trabalho do desenvolvedor, permitindo que a IA execute as etapas técnicas sem exigir aprovações redundantes no chat.

**Independent Test**: Pode ser validado disparando sequencialmente `/speckit-specify`, `/speckit-plan <CARD-ID>` e `/speckit-tasks <CARD-ID>` e verificando que cada comando conclui com sucesso, sincroniza com o GitHub, transiciona o Linear sem exibir nenhuma caixa ou pergunta de aprovação síncrona (`ask_question`).

**Acceptance Scenarios**:

1. **Given** um repositório configurado com as credenciais do GitHub e Linear, **When** o usuário aciona `/speckit-specify <descrição>`, **Then** o sistema gera os artefatos `spec.md` e checklist, cria o card no Linear em `Backlog`, inicializa a branch Gitflow, versiona os artefatos, abre o Draft PR no GitHub via `gh pr create --draft`, vincula o PR ao card e reporta a conclusão sem solicitar confirmação interativa no chat.
2. **Given** um card em `Backlog`, **When** o usuário aciona `/speckit-plan <CARD-ID>`, **Then** o sistema gera o plano técnico (`plan.md`, `research.md`, `data-model.md`, `quickstart.md`), comita e envia as alterações ao PR Draft no GitHub, transiciona o card no Linear para `Planned`, registra o comentário estruturado e finaliza sem nenhum gate de confirmação interativa.
3. **Given** um card em `Planned`, **When** o usuário aciona `/speckit-tasks <CARD-ID>`, **Then** o sistema gera `tasks.md`, executa a validação do plano, comita no PR Draft, transiciona o card no Linear para `Todo` e finaliza sem solicitar aprovação no chat.

---

### User Story 2 - Revisão e Acompanhamento Centralizado no GitHub com Living Specs (Priority: P1)

Como desenvolvedor, desejo que toda a validação e inspeção do trabalho produzido pela IA ocorra diretamente na interface do GitHub (através do Pull Request em modo Draft, diff de commits, visualização de arquivos markdown renderizados e comentários de PR), mantendo o chat apenas com resumos executivos objetivos e links diretos para os artefatos.

**Why this priority**: Alinha a experiência do desenvolvedor com o fluxo natural de engenharia de software moderno (revisão de código assíncrona no repositório remoto) em vez de validações manuais desconfortáveis na janela de chat da LLM.

**Independent Test**: Pode ser validado inspecionando os Draft PRs criados e garantindo que todas as especificações e planos estão legíveis, linkados no Linear e acessíveis no GitHub para revisão humana.

**Acceptance Scenarios**:

1. **Given** qualquer fase do Spec Kit concluída (`specify`, `plan`, `tasks`), **When** o agente emite o relatório de conclusão no chat, **Then** o relatório exibe o identificador do card, o status do Linear, links clicáveis para o Draft PR no GitHub e os caminhos locais dos artefatos, sem prender o usuário em decisões no chat.
2. **Given** o desenvolvedor inspecionando o PR no GitHub, **When** ele identifica a necessidade de ajustes na especificação ou no plano, **Then** ele pode optar por editar os arquivos diretamente na branch remota ou adicionar comentários no Pull Request.

---

### User Story 3 - Sincronização Autônoma do `/speckit-clarify` com Modificações do GitHub (Priority: P2)

Como desenvolvedor, quando eu realizar alterações ou revisões na especificação diretamente no GitHub durante a fase de especificação, desejo que ao acionar `/speckit-clarify <CARD-ID>` o sistema baixe e incorpore automaticamente as alterações mais recentes da branch remota e/ou feedbacks do Pull Request, dirima ambiguidades pendentes no `spec.md`, comite e sincronize com o Draft PR de forma 100% autônoma.

**Why this priority**: Fecha o ciclo de feedback da especificação: o usuário revisa no GitHub, faz ajustes ou aponta pontos, e o comando clarify absorve isso diretamente do repositório remoto sem requerer cópia/cola ou intervenção manual no chat.

**Independent Test**: Pode ser testado editando o `spec.md` ou comentando no Draft PR no GitHub, executando `/speckit-clarify <CARD-ID>` localmente e verificando que a branch local é atualizada com `git pull`, as alterações são preservadas, pendências são resolvidas e enviadas de volta ao remote.

**Acceptance Scenarios**:

1. **Given** uma branch de especificação com edições remotas no GitHub, **When** o usuário aciona `/speckit-clarify <CARD-ID>`, **Then** o sistema executa a sincronização do branch remoto (`git pull origin <branch>`), lê o `spec.md` atualizado, processa eventuais marcadores de clarificação ou comentários, atualiza o checklist e comita as melhorias diretamente no PR.
2. **Given** uma execução de `/speckit-clarify`, **When** todas as ambiguidades forem sanadas, **Then** o comando comita as alterações (`docs(clarify): ...`), faz push e reporta prontidão para `/speckit-plan <CARD-ID>` sem abrir gates de confirmação.

---

### User Story 4 - Atualização Constitucional e Harmonização dos Manifestos de Skills (Priority: P2)

Como arquiteto do projeto `fk_apm`, desejo que a Constituição do repositório (`.specify/memory/constitution.md`), as skills em `skills/linear-workflow`, `.agents/skills/linear-workflow` e as regras de ciclo de vida sejam atualizadas para ratificar a remoção de Consent Gates interativos e formalizar a revisão assíncrona via GitHub.

**Why this priority**: Garante governança, conformidade das instruções entre diferentes harnesses e consistência arquitetural para todos os times e agentes que consom o `fk_apm`.

**Independent Test**: Pode ser validado por inspeção estática dos arquivos de skill e constituição, confirmando a eliminação de regras obrigatórias de `ask_question` para avanço de fases.

**Acceptance Scenarios**:

1. **Given** a Constituição `.specify/memory/constitution.md`, **When** for atualizada, **Then** ela ratifica a esteira contínua e autônoma sem Consent Gates interativos entre fases, mantendo apenas a proteção inviolável de que a transição para `Done` é estritamente manual pelo desenvolvedor.
2. **Given** os arquivos de skill de ciclo de vida (`linear-workflow/SKILL.md` e `speckit-*`), **When** forem atualizados, **Then** as instruções direcionam os agentes a executar a fase completa e notificar com links para revisão no GitHub, sem chamadas bloqueantes a question tools.

---

### Edge Cases

- O que acontece se a branch remota no GitHub divergir por commits realizados pelo desenvolvedor enquanto um comando local é executado? O sistema deve tentar `git pull --rebase origin <branch>` antes de aplicar commits locais; havendo conflitos, reportar claramente para resolução humana.
- O que acontece se a issue no Linear já estiver em um estado mais avançado (ex: `Todo`) e o usuário rodar `/speckit-plan <CARD-ID>`? O comando deve preservar ou não regredir indevidamente o estado, informando o desenvolvedor.
- O que acontece se o desenvolvedor rodar `/speckit-implement <CARD-ID>` enquanto o card ainda está em `Backlog`? O sistema deve alertar que a arquitetura e decomposição de tarefas não foram concluídas, recomendando a execução sequencial do fluxo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O comando `/speckit-specify` DEVE criar a branch Gitflow, versionar `spec.md`, abrir o Draft PR no GitHub via `gh pr create --draft`, criar o card no Linear em `Backlog` vinculado ao PR e concluir de forma 100% autônoma, SEM invocar nenhuma ferramenta de questionamento interativo (`ask_question`).
- **FR-002**: O comando `/speckit-plan` DEVE gerar o plano de implementação (`plan.md`, `research.md`, `data-model.md`), sincronizar os commits com o Draft PR no GitHub, avançar o card do Linear de `Backlog` para `Planned`, e concluir SEM interrupções de confirmação interativa no chat.
- **FR-003**: O comando `/speckit-tasks` DEVE gerar a decomposição de tarefas em `tasks.md`, validar a integridade do plano, sincronizar commits com o Draft PR, avançar o card do Linear de `Planned` para `Todo`, e concluir SEM interrupções de confirmação interativa no chat.
- **FR-004**: O comando `/speckit-clarify` DEVE sincronizar a branch local com as alterações mais recentes do GitHub antes de processar clarificações, resolver pendências no `spec.md`, comitar e sincronizar com o Draft PR sem requerer gates síncronos.
- **FR-005**: Todos os comandos DEVE emitir no chat um relatório executivo conciso contendo links clicáveis para o Pull Request no GitHub, URL do card no Linear e caminhos locais dos artefatos.
- **FR-006**: A Constituição do repositório (`.specify/memory/constitution.md`) DEVE ser ratificada com nova versão SemVer registrando a esteira contínua e autônoma com revisão centralizada no GitHub e abolição de Consent Gates entre fases.
- **FR-007**: As descrições e instruções das skills em `skills/` e `.agents/skills/` DEVEM ser uniformizadas para garantir que nenhum harness (Antigravity, Claude Code, Cursor, Copilot, OpenCode) exija aprovações manuais no chat entre as etapas.
- **FR-008**: A regra de salvaguarda inegociável de que a transição de cards para `Done` é EXCLUSIVAMENTE manual pelo desenvolvedor após o merge do PR DEVE ser mantida intacta em todos os scripts e documentos.

### Key Entities

- **Living Spec Pull Request**: PR no GitHub em modo Draft criado na fase de especificação e progressivamente enriquecido com commits de cada etapa (`spec`, `plan`, `tasks`, `code`), servindo como centro único de revisão para o desenvolvedor.
- **Linear Issue Lifecycle**: Card no Linear que reflete o estado exato de maturação (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done`), atualizado autonomamente pelos agentes a cada comando.
- **Continuous Execution Pipeline**: Fluxo ininterrupto onde cada comando do Spec Kit realiza suas tarefas sem bloqueios síncronos, transferindo a governança de revisão para o GitHub.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Redução a zero (0) de prompts interativos de confirmação (`ask_question`) disparados pelos comandos de ciclo de vida (`specify`, `plan`, `tasks`, `clarify`, `implement`, `converge`).
- **SC-002**: 100% dos artefatos gerados continuam sendo versionados e sincronizados com a branch do GitHub Draft PR ao término de cada comando.
- **SC-003**: 100% das transições de estado do Linear (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`) continuam sendo realizadas deterministicamente e vinculadas ao PR.
- **SC-004**: Redução no tempo de ciclo de ponta a ponta da concepção à implementação, eliminando esperas ociosas por cliques de aprovação humana no chat.

## Assumptions

- O desenvolvedor possui o GitHub CLI (`gh`) e as credenciais do Linear devidamente autenticadas em seu ambiente.
- O desenvolvedor prefere realizar comentários de código e sugestões diretamente no PR do GitHub ou na branch remota em vez de responder enquetes no chat da IDE.
- A salvaguarda de transição para `Done` continua estritamente humana e manual após o merge, prevenindo fechamento indevido de issues por agentes.
