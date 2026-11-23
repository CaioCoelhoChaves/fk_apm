# Feature Specification: Remover Rito de Aprovação Final (Consent Gate) no Linear Workflow

**Feature Branch**: `055-remove-consent-gate-rite`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: "Quero fazer com que a minha skill o meu linear workflow não precise mais da minha aprovação final nas etapas "speckit-specify", "speckit-plan", "speckit-tasks" e "speckit-implement". Apenas os diálogos entre eu e a LLM serão necessários, a aprovação final como um "rito" pode sair do fluxo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fluxo Orientado a Diálogo sem Rito de Aprovação Final (Priority: P1)

Como desenvolvedor utilizando o `linear-workflow` e os comandos `/speckit-*`, quero que as etapas `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` e `/speckit-implement` avancem diretamente após a geração dos artefatos e apresentação do resumo no chat, sem exigir um rito formal de aprovação final (`ask_question` / `AskUserQuestion` com opções "Sim, aprovar" / "Editar..."), mantendo apenas os diálogos naturais entre mim e a LLM quando houver necessidade de refinamento ou dúvidas.

**Why this priority**: Elimina fricção repetitiva no ciclo Spec-Driven Development, permitindo que a conversa natural com a LLM conduza o refinamento dos artefatos sem interromper cada etapa com um gate burocrático de confirmação.

**Independent Test**: Pode ser testado executando cada um dos quatro comandos (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) e verificando nas instruções e prompts da skill que nenhum deles exige chamada obrigatória a `ask_question` / `AskUserQuestion` para aprovação final antes de persistir artefatos ou transicionar o card no Linear.

**Acceptance Scenarios**:

1. **Given** uma descrição de funcionalidade enviada via `/speckit-specify`, **When** a especificação (`spec.md`) e o checklist de qualidade são gerados e o resumo é apresentado no chat, **Then** o fluxo cria diretamente a branch, o Draft PR e o card em `Backlog` no Linear sem acionar um rito formal de aprovação final.
2. **Given** um card em `Backlog` processado via `/speckit-plan <CARD-ID>`, **When** os artefatos de arquitetura (`plan.md`, `research.md`, `data-model.md`) são gerados e o Executive Briefing é exibido no chat, **Then** o fluxo comita os artefatos no Draft PR e avança diretamente o card para `Planned` sem acionar um Consent Gate final.
3. **Given** um card em `Planned` processado via `/speckit-tasks <CARD-ID>`, **When** `tasks.md` é gerado, validado e o Executive Briefing é exibido no chat, **Then** o fluxo comita os artefatos no Draft PR e avança diretamente o card para `Todo` sem acionar um Consent Gate final.
4. **Given** um card em `Todo` processado via `/speckit-implement <CARD-ID>`, **When** a implementação é iniciada e concluída, **Then** o fluxo permanece 100% autônomo (sem Consent Gate final), movendo o card para `In Progress` durante a execução e para `In Review` após promover o PR.

---

### User Story 2 - Preservação do Pre-Render, Diálogo Natural e Exceções Explícitas (Priority: P2)

Como desenvolvedor, quero que a remoção do rito de aprovação final preserve a visibilidade dos artefatos no chat (tabela de card(s) e Executive Briefing com Título Revisado, Descrição Atualizada e 5 seções obrigatórias), a possibilidade de diálogo natural para ajustes ou esclarecimentos, e mantenha o Consent Gate apenas onde ainda for desejado (como `/speckit-taskstoissues`, que cria múltiplos sub-cards em lote).

**Why this priority**: Garante transparência total no chat sobre o que foi gerado e enviado ao Linear, evitando mutações silenciosas mesmo sem o gate bloqueante.

**Independent Test**: Inspecionar os arquivos de definição, referências e suíte de testes automatizados da skill `linear-workflow` confirmando que o Pre-Render no chat e a segurança de payload UTF-8 continuam obrigatórios e validados.

**Acceptance Scenarios**:

1. **Given** a execução de `/speckit-specify`, `/speckit-plan` ou `/speckit-tasks`, **When** o agente conclui a geração dos artefatos, **Then** o resumo ou Executive Briefing é renderizado integralmente no texto visível do chat junto com a execução atômica no Linear.
2. **Given** uma dúvida genuína ou solicitação de ajuste feita pelo usuário em conversa, **When** ocorre diálogo entre usuário e LLM, **Then** o agente refina os artefatos e atualiza o Linear/PR naturalmente sem depender de um fluxo rígido de "Editar..." via gate.

---

### Edge Cases

- E se houver ambiguidade crítica na descrição inicial de `/speckit-specify` ou `/speckit-implement`? O agente pode esclarecer via diálogo natural (ou `/speckit-clarify`), mas não deve usar a ferramenta de pergunta como rito obrigatório de aprovação ao final de cada etapa.
- E quanto a `/speckit-taskstoissues`? Como não foi listado para remoção, mantém o 3-Stage Consent Gate por lidar com criação em lote de múltiplos sub-cards.
- E quanto à transição para `Done`? Continua sendo exclusivamente manual pelo desenvolvedor após revisão e merge do PR.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A skill `linear-workflow` e suas sub-skills/prompts (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`) DEVEM operar sem exigir rito de aprovação final (`ask_question` / `AskUserQuestion` com opções de aprovar/editar) antes de criar ou transicionar cards no Linear.
- **FR-002**: As etapas `/speckit-specify`, `/speckit-plan` e `/speckit-tasks` DEVEM continuar renderizando no chat o resumo da especificação/tabela de cards ou o Executive Briefing (Título Revisado, Descrição Atualizada e as 5 seções obrigatórias) antes ou junto da execução atômica no Linear.
- **FR-003**: A etapa `/speckit-implement` DEVE manter execução 100% autônoma sem Consent Gate final, transicionando `Todo` ➔ `In Progress` ➔ `In Review`.
- **FR-004**: As instruções multi-harness, documentos de referência (`multi-harness-commands.md`, `states-and-labels.md`), avaliações (`evals.json`) e testes unitários da skill DEVEM refletir o novo fluxo orientado a diálogo (sem Consent Gate final nessas 4 etapas).
- **FR-005**: Os artefatos implantados em `.agents/skills/` DEVEM permanecer sincronizados com as definições de `skills/linear-workflow/` após a atualização.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das 4 etapas citadas (`speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`) executam sem interrupção por rito de aprovação final.
- **SC-002**: 100% da suíte de testes unitários de `linear-workflow` passa após a atualização dos contratos da skill.
- **SC-003**: Zero divergência entre os arquivos fonte em `skills/linear-workflow/` e os arquivos implantados em `.agents/skills/`.

## Assumptions

- O usuário prefere revisar e ajustar especificações, planos e tarefas por meio de diálogo aberto com a LLM, mantendo o controle humano final apenas na revisão e merge do Pull Request (`In Review` ➔ `Done`).
- O comando `/speckit-taskstoissues` não foi incluído na lista de remoção e pode manter seu Consent Gate em 3 etapas.
