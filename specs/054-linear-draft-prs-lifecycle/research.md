# Research: Modernização do linear-workflow com Ciclo de Draft PRs e Sync de Boards

**Issue**: [FAL-58](https://linear.app/fallkey/issue/FAL-58/featworkflow-modernizar-linear-workflow-com-ciclo-draft-prs-e) | **Branch**: `feat/FAL-58-modernizar-linear-workflow-draft-prs` | **Date**: 2026-10-29

---

## 1. GraphQL API do Linear: Gerenciamento e Sincronização de Estados (Workflow States)

### Decision
Utilizar a API GraphQL nativa do Linear (`https://api.linear.app/graphql`) via chamadas HTTP com `urllib.request` no script padrão zero-dependências `skills/linear-workflow/scripts/linear_api.py`. Implementar dois novos subcomandos na CLI:
1. `sync-boards`: Inspeciona todos os times (ou um time específico via `--team-id`) da organização, audita os estados existentes e aplica a esteira padronizada de 6 estados (+ Canceled), migrando estados legados (`Technical Analysis` -> `Planned`), ordenando posições e padronizando cores. Suporta `--dry-run`.
2. `setup-board`: Provisiona idempotentemente a esteira completa de 6 estados em um time recém-criado ou existente.

### Rationale
- O Linear possui suporte completo de primeira classe a mutações de estados via GraphQL: `workflowStateCreate` e `workflowStateUpdate`.
- A biblioteca padrão do Python (`urllib.request` e `json`) já é o padrão arquitetural do projeto (Constituição Princípio I), garantindo portabilidade entre Windows PowerShell e POSIX sem dependências externas (`requests`, `gql`, etc.).
- A migração de `Technical Analysis` para `Planned` deve ser não-destrutiva: se o estado `Technical Analysis` contiver issues ativas, a mutação de renomeação (`workflowStateUpdate(id: $id, input: { name: "Planned", position: 1.0, color: "#F2C94C" })`) preserva o histórico e associações de todos os cards existentes sem necessidade de realocação manual de issues.

### Alternatives Considered
- *CLI oficial do Linear (`@linear/cli` via npm)*: Rejeitado porque introduziria dependência do ecossistema Node/npm em repositórios onde o desenvolvedor ou agente utiliza apenas Python, violando o princípio de zero dependências externas.
- *Manter `Technical Analysis` no board*: Rejeitado porque o nome `Technical Analysis` é resquício da pipeline legada `/fk-*` e não reflete a terminologia padrão do Spec Kit (`spec.md` -> `plan.md` -> `tasks.md`), onde a etapa de planejamento culmina no estado `Planned`.

### Linear GraphQL Schema Contracts
```graphql
# Query de times e estados
query WorkspaceTeamsAndStates {
  teams {
    nodes {
      id
      name
      key
      states {
        nodes {
          id
          name
          type
          position
          color
        }
      }
    }
  }
}

# Criação de Workflow State
mutation WorkflowStateCreate($input: WorkflowStateCreateInput!) {
  workflowStateCreate(input: $input) {
    success
    workflowState {
      id
      name
      type
      position
      color
    }
  }
}

# Atualização de Workflow State
mutation WorkflowStateUpdate($id: String!, $input: WorkflowStateUpdateInput!) {
  workflowStateUpdate(id: $id, input: $input) {
    success
    workflowState {
      id
      name
      type
      position
      color
    }
  }
}
```

---

## 2. Padrão de 6 Estados do Board & Mapeamento de Transições

### Decision
Adotar o padrão rigoroso de 6 estados operacionais (+ Canceled) alinhado aos tipos nativos do Linear e às etapas do Spec Kit:

| Ordem | Nome do Estado | Tipo Linear (`type`) | Cor Hex | Gatilho / Comando | Modo de Execução |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **0** | `Backlog` | `backlog` | `#BEC2C8` | `/speckit-specify` | 3-Stage Consent Gate |
| **1** | `Planned` | `unstarted` | `#F2C94C` | `/speckit-plan` | 3-Stage Consent Gate |
| **2** | `Todo` | `unstarted` | `#4EA7FC` | `/speckit-tasks` | 3-Stage Consent Gate |
| **3** | `In Progress` | `started` | `#F2994A` | `/speckit-implement`, `/speckit-converge` | Autônomo (Sem Consent Gate) |
| **4** | `In Review` | `started` | `#BB87FC` | Ao abrir PR ou concluir `/speckit-converge` | Autônomo (Sem Consent Gate) |
| **5** | `Done` | `completed` | `#56D364` | Merge manual do PR no GitHub | **Exclusivamente Manual (Humano)** |
| **6** | `Canceled` | `canceled` | `#828282` | Cancelamento de demanda | Manual ou via comando de abort |

### Rationale
- Separa com clareza issues em fase de arquitetura/plano (`Planned`) daquelas prontas para desenvolvimento com backlog granular e tarefas validadas (`Todo`).
- O estado `Done` é protegido por regra arquitetural: nenhuma ferramenta ou agente pode transicionar um card para `Done`. Apenas humanos após validação e merge do PR.

### Alternatives Considered
- *Avançar direto de `Backlog` para `Todo` no `/speckit-plan`*: Rejeitado porque `plan.md` define a arquitetura, enquanto `tasks.md` define o checklist granular executável. Colocar em `Todo` antes do checklist gera falsos positivos de prontidão para sprint.
- *Permitir que `/speckit-implement` marque `Done` após o PR*: Rejeitado pela Constituição (Princípio II, item 26). O merge é rito exclusivo do desenvolvedor/maintainer.

---

## 3. Isolamento Operacional via Git Worktree Efêmero

### Decision
Implementar um mecanismo de worktree efêmero para execução de comandos do Spec Kit apontados para um card específico (`/speckit-<cmd> <CARD-ID>`):
1. **Validação Estrita de Argumento**: Todos os comandos pós-especificação (`/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`) exigem o argumento obrigatório `<CARD-ID>` (ex: `FAL-58`). Se ausente, o comando aborta na pré-validação com mensagem de erro orientativa.
2. **Detecção de Árvore Ativa**: Se o repositório corrente já estiver na branch de trabalho do card (`git branch --show-current == feat/<CARD-ID>-...`), executa diretamente no workspace atual para evitar conflitos de lock do git (`fatal: '<branch>' is already checked out`).
3. **Instanciação Efêmera**: Se o desenvolvedor estiver em outra branch (ex: `develop`, `main` ou outra feature), o sistema:
   - Cria o diretório efêmero `.worktrees/<CARD-ID>` via `git worktree add .worktrees/<CARD-ID> feat/<CARD-ID>-...`.
   - Executa a etapa do ciclo dentro do worktree isolado.
   - Realiza commit convencional e `git push` para o remote do PR Draft.
   - Retorna ao diretório raiz original e executa `git worktree remove --force .worktrees/<CARD-ID>` seguido de `git worktree prune`.
4. **Resiliência a Travas do SO**: No Windows, se processos em background mantiverem locks em arquivos do worktree, aplicar remoção com `--force` e registrar no `.gitignore` a pasta `.worktrees/`.

### Rationale
- Permite que desenvolvedores trabalhem em múltiplos cards sem sofrer trocas inesperadas de branch no editor nem perder alterações não commitadas na raiz.
- Garante total rastreabilidade remota, mantendo o PR Draft sempre sincronizado com o Linear.

### Alternatives Considered
- *Stash temporário e `git checkout`*: Rejeitado porque `git stash` pode gerar conflitos ao desempilhar e afeta o workspace ativo do desenvolvedor durante a execução de agentes autônomos.
- *Worktrees permanentes mantidos em disco*: Rejeitado porque acumula espaço em disco e causa inconsistências ao longo do tempo. O modelo efêmero (cria -> executa -> remove) é limpo e determinístico.

---

## 4. Ciclo de Draft PRs & Living Specs no GitHub

### Decision
Integrar o ciclo de vida do Spec Kit com Pull Requests em modo Draft no GitHub:
1. `/speckit-specify`: Criação de branch Gitflow (`feat/<issue-id>-<slug>`), commit inicial de `spec.md`, `git push -u origin <branch>` e abertura de PR via `gh pr create --draft`. A URL gerada é incluída no corpo do card no Linear.
2. `/speckit-clarify`: Commits incrementais de clarificação em `spec.md` enviados ao remote do PR Draft.
3. `/speckit-plan`: Adição de `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, commit convencional `docs(plan): ...` enviado ao PR Draft.
4. `/speckit-tasks`: Adição de `tasks.md`, commit convencional `docs(tasks): ...` enviado ao PR Draft.
5. `/speckit-implement`: Execução das tasks, código e testes unitários. Ao concluir todas as tarefas e validações, promove o PR de Draft para pronto via `gh pr ready <pr-number>` e atualiza o card para `In Review`.
6. `/speckit-converge`: Autonomamente aplica fixes decorrentes de code review na branch do PR, envia novos commits e comenta no PR.

### Rationale
- Transforma especificações em *Living Specs*: a documentação técnica é compartilhada e revisada pela equipe desde o dia zero, eliminando o isolamento de branches locais.
- Permite feedback contínuo antes mesmo de uma única linha de código de produção ser escrita.

---

## 5. Estratégia de Limpeza de Legado e Paridade Multi-Harness

### Decision
Expurgar completamente todas as referências a `/fk-*` (`/fk-develop`, `/fk-fix`, `/fk-new-issue`, `/fk-technical-analysis`) e à antiga coluna `Technical Analysis` nos seguintes arquivos:
- `skills/linear-workflow/SKILL.md`
- `skills/linear-workflow/.apm/prompts/*.prompt.md`
- `skills/linear-workflow/.apm/instructions/*.instructions.md`
- `skills/linear-workflow/references/*.md`
- `skills/linear-workflow/assets/.specify/`
- `.specify/memory/constitution.md` e templates em `.specify/templates/`
- Suíte de testes `skills/linear-workflow/tests/test_linear_api.py`

### Rationale
- Mantém o repositório `fk_apm` aderente aos mais altos padrões de higiene de código e alinhado com a distribuição APM para Google Antigravity, Claude Code, Cursor, Copilot e OpenCode.
