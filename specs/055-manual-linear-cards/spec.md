# Feature Specification: Criação de Cards Manuais no Linear com comando fk-new-manual-issue

**Feature Branch**: `feat/FAL-59-fk-new-manual-issue`

**Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)

**Created**: 2026-10-31

**Status**: Draft

**Input**: User description: "Quero criar uma skill para o meu projeto que faça com que seja possível eu criar UM ou vários cards no linear com a tag "manual", ou seja, cards que necessitam de ações totalmente manuais e que não são relacionadas com o código do projeto em si. Eu devo conseguir invocar está skill pelo comando "fk-new-manual-issue", essas issues devem começar em backlog."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criação de Card Manual Individual via Comando (Priority: P1)

Como desenvolvedor, tech lead ou gestor de produto, desejo acionar o comando `/fk-new-manual-issue` fornecendo o título e o contexto de uma tarefa manual, para que seja criado um card no Linear na coluna `Backlog` com a etiqueta `manual`, garantindo que atividades operacionais fora do código sejam registradas e visíveis para a equipe.

**Why this priority**: É a funcionalidade central e o caso de uso primário do usuário (criar uma tarefa manual no Linear de forma rápida e padronizada).

**Independent Test**: Pode ser validado invocando o comando `/fk-new-manual-issue` com os dados de uma única tarefa (ex: "Criar conta de desenvolvedor no portal de pagamentos"), confirmando que o card é gerado no Linear em `Backlog` com a etiqueta `manual`.

**Acceptance Scenarios**:

1. **Given** o usuário executando o comando `/fk-new-manual-issue` informando uma única tarefa operacional, **When** o fluxo processa a solicitação e o usuário confirma a criação, **Then** exatamente um card é criado no Linear associado ao projeto correto, na coluna `Backlog` e com a etiqueta `manual`.
2. **Given** a tarefa criada no Linear, **When** qualquer membro da equipe inspeciona o card, **Then** a descrição detalha o contexto da ação manual, o passo a passo necessário e os critérios de conclusão sem referências a branches de código ou testes automatizados de software.

---

### User Story 2 - Criação em Lote de Múltiplos Cards Manuais (Priority: P1)

Como usuário gerenciando múltiplas dependências operacionais (ex: provisionar credenciais, registrar domínios e solicitar acessos a terceiros), desejo fornecer uma lista ou lote de tarefas manuais em uma única invocação do `/fk-new-manual-issue`, para que todos os cards sejam criados de uma só vez na coluna `Backlog` com a etiqueta `manual`.

**Why this priority**: O usuário solicitou explicitamente a capacidade de criar "UM ou vários cards", sendo crítico para o planejamento inicial de projetos e integrações com serviços externos.

**Independent Test**: Pode ser testado fornecendo uma lista estruturada de 3 ou mais tarefas manuais ao comando, verificando se todos os itens são processados, apresentados juntos para validação e criados atomicamente no Linear com a tag `manual`.

**Acceptance Scenarios**:

1. **Given** o usuário informando uma lista de múltiplas tarefas operacionais (ex: 3 tarefas distintas), **When** o comando `/fk-new-manual-issue` é acionado, **Then** o sistema analisa a lista, extrai título e descrição de cada item e prepara a criação em lote.
2. **Given** a confirmação do lote pelo usuário, **When** a criação é executada, **Then** todos os cards são cadastrados no Linear em `Backlog` com a etiqueta `manual` individualmente, retornando a lista de identificadores criados.

---

### User Story 3 - Consent Gate Interativo com Pré-Visualização Antes da Criação (Priority: P2)

Como usuário, desejo visualizar um resumo claro e estruturado de todos os cards manuais propostos (título, coluna inicial `Backlog`, etiqueta `manual` e resumo do escopo) antes de qualquer gravação no Linear, podendo aprovar ou solicitar ajustes interativamente.

**Why this priority**: Evita a criação acidental de cards duplicados ou com títulos/descrições inadequadas no Linear, garantindo integridade e conformidade com os princípios de governança do projeto.

**Independent Test**: Invocar o comando, verificar a renderização da tabela de pré-visualização no chat e assegurar que nenhuma mutação ocorra no Linear antes da aprovação explícita.

**Acceptance Scenarios**:

1. **Given** a solicitação de criação de um ou mais cards manuais, **When** o comando processa os dados de entrada, **Then** nenhuma chamada de escrita ao Linear é realizada antes da confirmação do usuário (Zero Mutation).
2. **Given** a pré-visualização exibida com sucesso, **When** o usuário escolhe aprovar, **Then** os cards são persistidos no Linear; caso opte por editar, o sistema permite ajustar os textos antes da criação.

---

### User Story 4 - Isolamento Operacional Sem Gatilho de Pipeline de Código (Priority: P2)

Como desenvolvedor, desejo que os cards manuais criados sejam estritamente demarcados como tarefas operacionais humanas, garantindo que o fluxo não crie branches Git, não gere worktrees locais, não crie Pull Requests em modo Draft e não exija especificações técnicas de código.

**Why this priority**: Tarefas manuais (como pagamentos, aprovações jurídicas, configurações de console de terceiros) não devem poluir a árvore Git do repositório nem exigir pipelines de desenvolvimento de software.

**Independent Test**: Confirmar que a criação de cards manuais via `/fk-new-manual-issue` conclui sem criar branches no Git, sem tocar na árvore de trabalho local e sem abrir PRs no GitHub.

**Acceptance Scenarios**:

1. **Given** a execução e conclusão bem-sucedida do comando `/fk-new-manual-issue`, **When** o repositório Git local e remoto é verificado, **Then** nenhuma branch Git adicional é criada e nenhum arquivo de código é alterado.
2. **Given** o card manual aberto no Linear, **When** o time conclui as ações operacionais no mundo real, **Then** o ciclo de vida do card é gerido diretamente no Linear pelos operadores humanos.

---

### Edge Cases

- **Etiqueta `manual` inexistente no Linear**: Se a equipe/organização no Linear ainda não possuir a etiqueta com o nome `manual`, o sistema deve criá-la dinamicamente de forma idempotente sem falhar.
- **Entrada vazia ou insuficiente**: Se o comando for acionado sem argumentos ou com instruções vagas, o sistema deve interagir amigavelmente solicitando o título e as instruções das tarefas manuais desejadas.
- **Identificação ambígua de múltiplos cards**: Se o usuário fornecer um texto contínuo descrevendo várias ações sem separação explícita, o sistema deve estruturar a divisão em itens distintos e solicitar confirmação na pré-visualização.
- **Falha de conectividade ou autenticação com a API do Linear**: O sistema deve apresentar mensagem de erro clara orientando a verificação de credenciais e integridade de rede, sem criar cards inconsistentes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer o comando invocável `/fk-new-manual-issue` em todos os ambientes e harnesses suportados pelo ecossistema de skills.
- **FR-002**: O sistema DEVE permitir a criação de um único card manual a partir da descrição fornecida pelo usuário.
- **FR-003**: O sistema DEVE permitir a criação em lote de múltiplos cards manuais a partir de uma lista ou instruções fornecidas pelo usuário.
- **FR-004**: O sistema DEVE atribuir obrigatoriamente a etiqueta `manual` a todos os cards gerados por este comando.
- **FR-005**: O sistema DEVE posicionar todos os novos cards criados obrigatoriamente na coluna de estado `Backlog`.
- **FR-006**: O sistema DEVE associar o(s) card(s) ao projeto Linear correspondente ao repositório ou contexto ativo.
- **FR-007**: O sistema DEVE formatar a descrição do card no Linear contendo seções padronizadas de Contexto, Ações Manuais a Executar (checklist) e Critérios de Conclusão.
- **FR-008**: O sistema DEVE executar um portão de consentimento (Consent Gate) pré-renderizando a lista de cards antes de persistir alterações no Linear.
- **FR-009**: O sistema NÃO DEVE criar branches Git, Pull Requests ou worktrees locais durante a execução deste comando.
- **FR-010**: O sistema DEVE garantir a integridade dos textos e caracteres especiais ao enviar as descrições para o Linear, evitando corrupção de formatação.

### Key Entities

- **Manual Task Item**: Representa uma tarefa operacional humana individual contendo título da atividade, detalhamento dos passos manuais necessários, justificativa e critérios de sucesso.
- **Linear Manual Issue**: Entidade persistida no Linear que materializa o card com identificador (ex: FAL-NNN), título estruturado, estado inicial `Backlog`, etiqueta `manual` e corpo descritivo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuário consegue registrar uma ou mais tarefas operacionais no Linear em menos de 30 segundos de interação.
- **SC-002**: 100% dos cards gerados pelo comando são criados no estado `Backlog` e contêm a etiqueta `manual`.
- **SC-003**: 0% de impacto na árvore Git (zero branches, zero commits e zero PRs gerados para tarefas estritamente manuais).
- **SC-004**: 100% de precisão na apresentação dos cards propostos na etapa de pré-visualização antes da confirmação.

## Assumptions

- O repositório ou ambiente possui acesso configurado à API do Linear via variável de ambiente ou configuração padrão.
- O time no Linear aceita criação de tarefas manuais com a etiqueta `manual`.
- Usuários que acionam o comando têm clareza sobre quais tarefas são estritamente operacionais (externas ao código) versus tarefas de desenvolvimento de software que exigem o fluxo completo do Spec Kit.
