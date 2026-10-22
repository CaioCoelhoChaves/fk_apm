---
name: linear-workflow
description: Synchronize development and planning tasks with Linear issue tracking across any project and harness (Google Antigravity, Claude Code, Cursor, Copilot). Enforces lifecycle commands (/fk-new-issue, fk-new-issue, /fk-technical-analysis, fk-technical-analysis, /fk-develop, fk-develop, /fk-fix, fk-fix), the mandatory 3-stage Consent Gate protocol (zero mutation until user approval), autonomous code review fixes (/fk-fix), atomic state advancement (advancing to In Review upon PR opening), comment idempotency (10-minute deduplication window), manual-only developer transitions for 'Done', and review feedback loops returning to 'In Progress'. Checks Linear via MCP tools or bundled CLI (scripts/linear_api.py), tags monorepo subprojects with Front/Back labels, and notifies the user of all board actions.
allowed-tools: Read,Glob,Grep,Bash
---

# Linear Workflow: Seamless Task Tracking, Lifecycle Commands & Consent Gate

A standardized workflow for AI coding agents to integrate Linear issue management directly into development and planning lifecycles. Supports native Linear MCP servers and provides a standalone zero-dependency Python CLI helper (`scripts/linear_api.py`) for GraphQL API execution with built-in comment idempotency, atomic updates, and automated state resolution.

---

## Core Non-Negotiable Standards

1. **Zero Hardcoded Secrets & Dynamic Credential Resolution**:
   - Never hardcode tokens or API keys into prompts, code, or configuration files.
   - Dynamically discover credentials in priority order:
     1. Linear MCP server tools (`linear_issue_search`, `linear_create_issue`, etc.), if present.
     2. Environment variable: `LINEAR_API_KEY` or `LINEAR_TOKEN`.
     3. Project-level `.linear.json`, `.linearrc`, or `.env`.
   - If no credentials exist, warn the user once and continue the development task without blocking.

2. **Non-Blocking Project Fallback**:
   - If the project does not exist in Linear, **never halt or abort** the user's task.
   - Proceed with development or implementation normally.
   - Inform the user clearly at the start or completion that the project is not tracked in Linear.

3. **Lifecycle State Machine & Responsabilidades de Transição**:
   - Enforce the official state progression:
     `Backlog` ➔ `Technical Analysis` ➔ `Todo` ➔ `In Progress` ➔ `In Review` ➔ `Done` (plus `Canceled` or `Duplicate`).
   - **Transições do Agente (Anti-Estagnação)**:
     - Conclusão de Análise Técnica: Agente move de `Technical Analysis` ➔ **`Todo`** com comentário estruturado.
     - Início de Desenvolvimento: Agente move de `Todo` ➔ **`In Progress`** com branch Git criada.
     - Conclusão de Desenvolvimento (PR Aberto): Agente move obrigatoriamente de `In Progress` ➔ **`In Review`** com link do PR e sumário técnico.
     - Correções de Code Review (`/fk-fix`): Agente move de `In Review` ➔ **`In Progress`** (início do fix) ➔ **`In Review`** (após commits e push).
   - **Rito Exclusivamente Manual a partir de `In Review`**:
     - A partir de **`In Review`**, o controle é **exclusivamente manual pelo desenvolvedor**.
     - **`Done`**: O desenvolvedor move manualmente para **`Done`** após revisar o PR no GitHub, validar os testes e realizar o merge. O agente **NUNCA** move o card para `Done`.
     - **Retorno para Correções**: Se o desenvolvedor encontrar falhas ou pedir ajustes durante o review, o card pode ser retornado para **`In Progress`** (manualmente ou via comando `/fk-fix`) para que o agente execute o ciclo corretivo.

4. **Mandatory 3-Stage Protocol (*Consent Gate*) & Autonomous Fix Exception**:
   - For standard lifecycle commands (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`) and natural language triggers, the agent must strictly follow this protocol across all harnesses (Google Antigravity, Claude Code, OpenCode, Cursor, GitHub Copilot):
     - **Stage 1 (Initial Presentation & Questions)**: The agent prepares the plan/analysis in chat/workspace, raising options and doubts with the developer. **Zero mutation**: No API calls altering Linear (`update-issue`, `create-issue`, `create-comment`) are permitted in this stage. Only read queries (`get-issue`, `search-issues`, `list-states`, `list-projects`) are allowed.
     - **Stage 2 (Consent Gate - Interactive Prompt & Options)**: After resolving questions, the agent presents the consent confirmation using the **native question tool** of the active harness:
       - **Google Antigravity**: tool nativa `ask_question`.
       - **Claude Code**: tool nativa `AskUserQuestion`.
       - **OpenCode v2**: tool nativa de perguntas (`ask`/`question`).
       - **Fallback Textual (Cursor, Copilot, Gemini CLI ou sem tool nativa)**: Bloco formatado em Markdown no chat com opções estruturadas.
       - **Opções Estruturadas**:
         1. `(Recommended) Sim, aprovar`: Avança atomicamente para a Stage 3.
         2. `Editar...`: Permite texto livre para o desenvolvedor informar o que deseja ajustar. O agente recebe o feedback, **retorna à Stage 1**, ajusta o plano/análise e apresenta novamente antes de acionar um novo Consent Gate.
     - **Stage 3 (Atomic Execution - Move Card + Register Comment)**: Only after affirmative developer response (`Sim, aprovar`), execute the closing actions atomically on Linear (advancing the status, registering the consolidated comment, or creating cards/branches).
   - ⚠️ **Exceção de Consent Gate para `/fk-fix`**:
     - O comando `/fk-fix` roda **sem Consent Gate**. Por se tratar de um ciclo corretivo solicitado por revisores humanos em um PR existente, o agente executa diretamente a leitura do feedback, movimentação para `In Progress`, implementação na branch, comentário no PR e retorno para `In Review` sem requerer aprovação prévia.

5. **Comment Idempotency & AIG Compliance**:
   - In accordance with Linear's official [Agent Interaction Guidelines (AIG)](https://linear.app/developers/agents):
     - Clearly signal agent identity: prefix all comments with `🤖 **AI Agent Update**:`.
     - Align with Linear Git automation: use the standard branch format `<type>/<identifier>-<slug>` (e.g. `feat/RENT-104-user-auth`).
     - **Idempotency Protection**: `scripts/linear_api.py` inspects recent card comments to prevent duplicate comments with identical body/payload within a 10-minute window.

6. **Parent Project & Subproject Component Labeling**:
   - Detect when a repository represents a subproject of a unified Linear project (e.g., local project `Rent Easy Frontend` or `Rent Easy Backend` mapping to parent Linear project `Rent Easy`).
   - Automatically tag cards with **`Front`** (Flutter, React, Vue, Web, Mobile) or **`Back`** (Spring Boot, Node, Java, Python API) component labels.

7. **100% Transparency & User Notification**:
   - Every Linear operation (issue queried, card created, state transitioned, or comment added) must be explicitly communicated in the response with issue keys (e.g. `LIN-42`) and status.

8. **Multi-Harness Architecture Support**:
   - Standardized APM primitives under `.apm/skills/` (`SKILL.md`), `.apm/prompts/` (`.prompt.md`) and `.apm/instructions/` (`.instructions.md`) provide cross-platform command routing:
     - **Google Antigravity**: Native slash commands via promoted sub-skills in `.agents/skills/` (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`, `/fk-fix`), backed by unconditional rules in `.agents/rules/` and compiled `AGENTS.md`.
     - **Claude Code**: Native custom slash commands in `.claude/commands/` and rules in `.claude/rules/`.
     - **Cursor**: Custom slash commands in `.cursor/commands/` and rules in `.cursor/rules/`.
     - **GitHub Copilot**: Prompt templates in `.github/prompts/` and instructions in `.github/instructions/`.

---

## Lifecycle Commands Reference

| Canonical Trigger | Slash-Free Variant | Target State Transition | Executado Por | Scope & Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`/fk-new-issue`** | `fk-new-issue` | `Backlog` ou `Todo` | **Agente** (com Consent Gate) | Planejamento, decomposição e criação atômica de novos cards no Linear. |
| **`/fk-technical-analysis`** | `fk-technical-analysis` | `Technical Analysis` ➔ `Todo` | **Agente** (com Consent Gate) | Investigação arquitetural, spikes técnicos, desenho de solução e avanço para `Todo` ao concluir. |
| **`/fk-develop`** | `fk-develop` | `Todo` ➔ `In Progress` ➔ `In Review` | **Agente** (com Consent Gate) | Início do desenvolvimento (`In Progress`), implementação, testes e avanço para `In Review` ao abrir o PR. |
| **`/fk-fix`** | `fk-fix` | `In Review` ➔ `In Progress` ➔ `In Review` | **Agente** (sem Consent Gate) | Aplica correções do review de um PR aberto (lê reviews, inline comments e texto extra), comita na branch, comenta no PR e devolve o card para `In Review`. |
| *(Transição Manual)* | — | `In Review` ➔ `Done` | **Desenvolvedor** | **Exclusivamente manual pelo desenvolvedor** após merge e homologação da entrega. |

---

## Tool Execution Matrix (MCP vs Bundled CLI)

The agent dynamically uses whatever tool is available in the current environment:

| Operation | Official Linear MCP (`https://mcp.linear.app/mcp`) | Bundled CLI (`python skills/linear-workflow/scripts/linear_api.py`) |
| :--- | :--- | :--- |
| **Verify Auth** | OAuth 2.1 via Linear MCP | `python <skill-dir>/scripts/linear_api.py auth-check` |
| **Find Project** | `linear_list_projects` | `python <skill-dir>/scripts/linear_api.py find-project "<name>"` |
| **Get Issue** | `linear_issue_search` | `python <skill-dir>/scripts/linear_api.py get-issue "<key-or-id>"` |
| **Search Issue** | `linear_issue_search` | `python <skill-dir>/scripts/linear_api.py search-issues "<term>" [--project-id "<id>"]` |
| **Create Card** | `linear_create_issue` | `python <skill-dir>/scripts/linear_api.py create-issue --team-id "<tid>" --project-id "<pid>" --title "<title>" --description "<desc>" --state "<state>" --label "Front"` |
| **Atomic Update** | `linear_update_issue` + `linear_create_comment` | `python <skill-dir>/scripts/linear_api.py update-issue "<id>" [--team-id "<tid>"] [--state "<state>"] [--comment "<summary>"]` |
| **Add Comment** | `linear_create_comment` | `python <skill-dir>/scripts/linear_api.py update-issue "<id>" --comment "<summary>"` *(idempotente)* |

---

## Workflow 1: Protocolo Universal Consent Gate em 3 Etapas

Para comandos de planejamento e início de desenvolvimento (`/fk-new-issue`, `/fk-technical-analysis`, `/fk-develop`), segue-se rigorosamente este fluxo:

```mermaid
flowchart TD
    A["1. Comando de Rito (/fk-*) ou Linguagem Natural"] --> B["Etapa 1: Leitura, Apresentação & Alinhamento"]
    B --> C["Zero Mutação: Apenas Leitura no Linear"]
    C --> D{"Dúvidas resolvidas e plano estruturado?"}
    D -- "Não" --> B
    D -- "Sim" --> E["Etapa 2: Consent Gate Interativo (Tool Nativa)"]
    E --> F{"Opção Selecionada"}
    F -- "Editar... (Texto Livre)" --> B
    F -- "(Recommended) Sim, aprovar" --> G["Etapa 3: Execução Atômica"]
    H["Mover Card / Criar Cards + Comentário Consolidado"]
    G --> H
    H --> I["Prosseguir com implementação ou branch Git"]
```

### Mecanismo de Pergunta Interativa por Harness:
- **Google Antigravity**: Dispara a tool nativa `ask_question` com opções `["(Recommended) Sim, aprovar", "Editar..."]`.
- **Claude Code**: Dispara a tool nativa `AskUserQuestion` com opções `["Sim, aprovar", "Editar..."]`.
- **OpenCode v2**: Dispara a tool nativa de perguntas (`ask`/`question`) com opções `["Sim, aprovar", "Editar..."]`.
- **Fallback Textual (Cursor, Copilot, Gemini CLI ou sem suporte a tool)**: Exibe a pergunta no chat em bloco Markdown destacado:
  ```markdown
  > [!IMPORTANT]
  > **Consent Gate (Confirmação Explícita)**:
  > <pergunta de consentimento>
  > - **1. (Recomendado) Sim, aprovar**: Prosseguir com a execução atômica no Linear.
  > - **2. Editar...**: Digite os ajustes desejados para revisarmos o plano na Etapa 1.
  ```
- **Semântica das Opções**:
  - `(Recommended) Sim, aprovar`: Autoriza imediatamente a transição para a **Etapa 3: Execução Atômica**.
  - `Editar...`: Permite texto livre para o desenvolvedor apontar ajustes no plano. O agente **retorna à Etapa 1**, reapresenta a proposta corrigida e aciona novo Consent Gate. **Zero mutação é mantida até aprovação explícita**.

---

## Workflow 2: Planejamento & Criação de Tarefas (`/fk-new-issue`)

Gatilhos: `/fk-new-issue`, `fk-new-issue`, *"vamos planejar tarefas"*, *"crie os cards para..."*.

1. **Etapa 1 - Apresentação & Dúvidas (Leitura)**:
   - Localiza o projeto pai no Linear (`find-project`).
   - Decompõe os requisitos em tarefas atômicas no chat (título, descrição, critérios de aceitação e label `Front`/`Back`).
   - Apresenta a tabela proposta sem chamar `create-issue`.
2. **Etapa 2 - Consent Gate Interativo**:
   - Aciona a ferramenta interativa de perguntas do harness (ex: `ask_question` / `AskUserQuestion`) ou fallback textual com as opções `(Recommended) Sim, aprovar` e `Editar...`:
     - Pergunta: *"O escopo e a divisão dos cards estão alinhados? Posso criá-los no Linear sob o status [Backlog/Todo]?"*
   - Se o usuário escolher `Editar...`: coleta as correções em texto livre, retorna à Etapa 1 para atualizar a decomposição e reapresenta o Consent Gate.
3. **Etapa 3 - Execução Atômica**:
   - Somente após `Sim, aprovar`, cria os cards no Linear via CLI/MCP.
   - Apresenta o sumário final com links diretos e IDs.

---

## Workflow 3: Análise Técnica & Spikes Arquiteturais (`/fk-technical-analysis`)

Gatilhos: `/fk-technical-analysis`, `fk-technical-analysis`, *"vamos analisar tecnicamente o card X"*, *"faça um spike técnico sobre Y"*.

1. **Etapa 1 - Apresentação & Dúvidas (Leitura)**:
   - Consulta o card via `get-issue` ou `search-issues`.
   - Se o card estava em `Backlog`, o início da análise é apresentado no chat.
   - Realiza a análise arquitetural, opções de implementação, trade-offs e impactos no workspace.
   - **Zero mutação prematura no card**: Nenhum comentário preliminar ou mudança de estado é postada enquanto houver dúvidas em aberto.
2. **Etapa 2 - Consent Gate Interativo**:
   - Aciona a ferramenta interativa de perguntas do harness (ex: `ask_question` / `AskUserQuestion`) ou fallback textual com as opções `(Recommended) Sim, aprovar` e `Editar...`:
     - Pergunta: *"A análise técnica está aprovada? Posso registrar as decisões no Linear e mover o card para **Todo** (pronto para desenvolvimento)?"*
   - Se o usuário escolher `Editar...`: recebe os direcionamentos técnicos adicionais, volta à Etapa 1 para refinar a análise e reapresenta o Consent Gate.
3. **Etapa 3 - Execução Atômica**:
   - Somente após `Sim, aprovar`, executa atomicamente:
     ```bash
     python skills/linear-workflow/scripts/linear_api.py update-issue "<id>" --state "Todo" --comment "🤖 **AI Agent Update**: Análise Técnica Consolidada..."
     ```
   - O card avança formalmente para **`Todo`** e não permanece em `Technical Analysis`.

---

## Workflow 4: Ciclo de Desenvolvimento & Implementação (`/fk-develop`)

Gatilhos: `/fk-develop`, `fk-develop`, *"vamos desenvolver a tarefa X"*, *"quero implementar o card Y"*.

1. **Etapa 1 - Apresentação & Dúvidas (Leitura)**:
   - Lê o card (`get-issue <id>`), requisitos, histórico de comentários e critérios de aceitação.
   - Apresenta o plano de implementação, arquivos afetados e a branch de trabalho proposta (`<type>/<key>-<slug>`).
2. **Etapa 2 - Consent Gate Interativo**:
   - Aciona a ferramenta interativa de perguntas do harness (ex: `ask_question` / `AskUserQuestion`) ou fallback textual com as opções `(Recommended) Sim, aprovar` e `Editar...`:
     - Pergunta: *"O plano de desenvolvimento está aprovado? Posso mover o card para **In Progress** e criar a branch de trabalho?"*
   - Se o usuário escolher `Editar...`: recebe observações sobre a estratégia de arquivos ou branch, volta à Etapa 1 para retificar o plano e reapresenta o Consent Gate.
3. **Etapa 3 - Execução Atômica & Início de Codificação**:
   - Somente após `Sim, aprovar`, transiciona o card para **`In Progress`** com comentário inicial:
     ```bash
     python skills/linear-workflow/scripts/linear_api.py update-issue "<id>" --state "In Progress" --comment "🤖 **AI Agent Update**: Início do desenvolvimento na branch <branch-name>..."
     ```
   - Cria a branch Git alinhada ao Gitflow e inicia a codificação e testes.
4. **Etapa 4 - Finalização do Desenvolvimento & Movimentação para `In Review`**:
   - Após implementar, rodar a suíte de testes e abrir o Pull Request no GitHub (`gh pr create`):
   - **O agente move obrigatoriamente o card para `In Review`**:
     ```bash
     python skills/linear-workflow/scripts/linear_api.py update-issue "<id>" --state "In Review" --comment "🤖 **AI Agent Update**: Desenvolvimento concluído e PR aberto no GitHub: <pr-url>..."
     ```
   - Notifica o desenvolvedor de que a tarefa está pronta para sua revisão manual.

---

## Workflow 5: Rito de Revisão Manual & Conclusão (`In Review` ➔ `Done`)

A partir da coluna **`In Review`**, o controle é exclusivamente manual pelo desenvolvedor:

1. **Revisão Humana do Pull Request**:
   - O desenvolvedor analisa o código no GitHub, valida os testes automatizados e a conformidade funcional.
2. **Cenário A: Necessidade de Correções / Ajustes (`/fk-fix`)**:
   - Quando houver comentários de revisão no PR ou solicitações de ajustes, o comando `/fk-fix` pode ser invocado (ex: `/fk-fix FAL-24` ou simplesmente `/fk-fix` na branch atual).
   - O agente assume as correções de forma autônoma sem Consent Gate (Workflow 6), atualiza a branch, comenta no PR e retorna o card para **`In Review`**.
3. **Cenário B: Aprovação & Merge**:
   - O desenvolvedor realiza o merge do PR no GitHub.
   - O **desenvolvedor move manualmente o card para `Done`**.
   - O agente nunca força a transição para `Done` sem intervenção humana no repositório remoto.

---

## Workflow 6: Aplicação Autônoma de Feedback de Code Review (`/fk-fix`)

Gatilhos: `/fk-fix`, `fk-fix`, *"aplicar correções do review"*, *"resolver feedback de code review no PR"*.

> [!IMPORTANT]
> **Execução Autônoma (SEM Consent Gate)**:
> O comando `/fk-fix` não solicita confirmação prévia antes de iniciar o fix ou mover o card para `In Progress`. O feedback deixado pelos revisores humanos no PR já expressa a intenção do desenvolvedor.

1. **Etapa 1 - Identificação do Card e do PR**:
   - Identifica a chave da issue informada no argumento (ex.: `/fk-fix FAL-24`) ou deduz a issue pela branch atual (`<type>/<key>-<slug>`).
   - Localiza o PR correspondente no GitHub via `gh pr view --json number,title,url,headRefName,state`.
   - Se nenhum PR aberto for encontrado, alerta o desenvolvedor e finaliza sem modificações.
2. **Etapa 2 - Leitura & Triagem do Feedback**:
   - Coleta comentários gerais do PR (`gh pr view --comments`), reviews (`gh api repos/{owner}/{repo}/pulls/{n}/reviews`) e comentários inline no código (`gh api repos/{owner}/{repo}/pulls/{n}/comments`), além de eventuais instruções extras fornecidas pelo usuário.
   - **Filtros Mandatórios**: Ignora comentários anteriores do próprio agente (`🤖 **AI Agent Update**:`) e threads/comentários já resolvidos ou out-of-date.
   - **Validação de Feedback Vazio**: Se não houver comentários, reviews pendentes nem texto extra do usuário, o agente avisa o usuário no chat e encerra **sem realizar qualquer modificação** na branch ou no Linear.
3. **Etapa 3 - Transição para `In Progress` no Linear (Sem Confirmação)**:
   - Move o card no Linear para **`In Progress`** com comentário estruturado contendo o resumo dos apontamentos a tratar:
     ```bash
     python skills/linear-workflow/scripts/linear_api.py update-issue "<id>" --state "In Progress" --comment "🤖 **AI Agent Update**: Início da aplicação de feedback do PR #<pr-number>. Apontamentos em tratamento:
- <resumo de cada apontamento identificado>"
     ```
   - Se o projeto/card não existir no Linear, avisa o usuário com transparência e prossegue com o fix no repositório.
4. **Etapa 4 - Implementação & Testes na Branch Existente**:
   - Implementa as correções solicitadas diretamente nos arquivos da branch atual.
   - Executa a suíte de testes locais para assegurar que não haja regressão.
   - Realiza commits semânticos (Conventional Commits 1.0.0) e push na branch atual (atualizando o PR existente, sem abrir novo PR).
5. **Etapa 5 - Comentário Estruturado no PR do GitHub**:
   - Registra um comentário no PR via `gh pr comment` com prefixo `🤖 **AI Agent Update**:`, discriminando com clareza:
     - O que foi corrigido por cada apontamento/comentário;
     - O que eventualmente não foi alterado, acompanhado de justificativa técnica.
6. **Etapa 6 - Retorno do Card para `In Review` no Linear**:
   - Transiciona atomicamente o card no Linear para **`In Review`** com comentário registrando a conclusão das correções e o link do PR atualizado.
7. **Regra de Ouro**: O card **NUNCA** é movido para `Done` pelo agente (permanece manual pelo desenvolvedor após merge).

---

## Concrete Interaction Examples

### Example 1: Consent Gate em Análise Técnica (Tool Interativa)
**Usuário**: `"/fk-technical-analysis FAL-24"`  
**Agente (Etapa 1)**: Consulta `get-issue FAL-24`, estuda a arquitetura e responde no chat com a análise detalhada e trade-offs.  
**Agente (Etapa 2 - Consent Gate Interativo)**: Invoca tool nativa de perguntas (`ask_question` / `AskUserQuestion`):
- Pergunta: *"A análise técnica está aprovada? Posso registrar as decisões no Linear e mover o card para **Todo**?"*
- Opções: `["(Recommended) Sim, aprovar", "Editar..."]`
**Usuário (Seleção)**: `"(Recommended) Sim, aprovar"`  
**Agente (Etapa 3)**: Executa `update-issue FAL-24 --state "Todo" --comment "..."`. Comunica ao usuário a transição concluída.

### Example 2: Consent Gate com Loopback ("Editar...") e Desenvolvimento
**Usuário**: `"/fk-develop FAL-24"`  
**Agente (Etapa 1)**: Lê os critérios do card, apresenta o plano de branch e arquivos a alterar.  
**Agente (Etapa 2 - Consent Gate Interativo)**: Invoca `ask_question`:
- Pergunta: *"O plano de desenvolvimento está aprovado? Posso mover o card para **In Progress** e iniciar a branch?"*
- Opções: `["(Recommended) Sim, aprovar", "Editar..."]`  
**Usuário (Seleção/Texto)**: `"Editar... adicionar testes de widget para tela de login"`  
**Agente (Retorno à Etapa 1)**: Não altera o Linear (Zero Mutação). Ajusta o plano técnico incluindo a suíte de testes de widget e reapresenta o plano revisado.  
**Agente (Etapa 2 - Novo Consent Gate)**: Invoca novamente a tool de pergunta interativa.  
**Usuário**: `"(Recommended) Sim, aprovar"`  
**Agente (Etapa 3 & 4)**: Executa `update-issue FAL-24 --state "In Progress" --comment "..."`, cria a branch, implementa código e testes, abre o PR #5 no GitHub e transiciona para `In Review`:
```bash
python skills/linear-workflow/scripts/linear_api.py update-issue FAL-24 --state "In Review" --comment "🤖 **AI Agent Update**: PR #5 aberto no GitHub..."
```

### Example 3: Correções de Review com `/fk-fix` (Sem Consent Gate)
**Usuário**: `"/fk-fix FAL-24 ajustar validação de email nulo"`  
**Agente**:
1. Localiza o PR #8 da branch `feat/FAL-24-auth` e lê comentários gerais, reviews e comentários inline;
2. Atualiza o card FAL-24 no Linear para **`In Progress`** com o resumo dos itens a corrigir;
3. Aplica a correção no código, executa os testes unitários, realiza commit semântico e faz `git push origin feat/FAL-24-auth`;
4. Comenta no PR #8 listando as alterações realizadas;
5. Atualiza o card FAL-24 no Linear para **`In Review`** e notifica o desenvolvedor no chat com o sumário da entrega.

---

## References

- [references/multi-harness-commands.md](references/multi-harness-commands.md) for cross-harness architecture (Antigravity, Claude, Cursor, Copilot) and APM primitives.
- [references/states-and-labels.md](references/states-and-labels.md) for full state definitions, subproject rules, and AIG compliance.
- [references/configuration.md](references/configuration.md) for API key setup and MCP integration.
- [Linear Developers: Agent Interaction Guidelines (AIG)](https://linear.app/developers/agents)
- [Linear Docs: Model Context Protocol (MCP)](https://linear.app/docs/mcp)
