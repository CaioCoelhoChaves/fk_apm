---
description: Interceptação universal e roteamento multi-harness para comandos de ciclo de vida do Linear (/fk-* e fk-*)
---

# Roteamento Universal de Comandos de Ciclo de Vida do Linear

Esta regra intercepta comandos de ciclo de vida do Linear em todos os harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot e terminais de chat), garantindo tolerância sintática (com ou sem barra) e acionamento rigoroso da skill `linear-workflow`.

## 1. Gatilhos de Interceptação

Sempre que a mensagem do usuário contiver qualquer um dos seguintes gatilhos (com ou sem barra `/` inicial, maiúsculas ou minúsculas):

- **Planejamento / Criação**: `/fk-new-issue`, `fk-new-issue`, `/fk-issue`, `fk-issue`, ou solicitações explícitas de planejar/decompor cards para o Linear.
- **Análise Técnica**: `/fk-technical-analysis`, `fk-technical-analysis`, `/fk-ta`, `fk-ta`, ou solicitações de análise técnica/spike de um card do Linear.
- **Desenvolvimento**: `/fk-develop`, `fk-develop`, `/fk-dev`, `fk-dev`, ou solicitações de desenvolver/implementar um card do Linear.
- **Correção de PR / Review Feedback**: `/fk-fix`, `fk-fix`, ou solicitações explícitas de aplicar feedback de code review em PR aberto.

## 2. Ações Mandatórias do Agente

1. **Ativação da Skill**:
   - Ative imediatamente as instruções e fluxos definidos em `skills/linear-workflow/SKILL.md`.

2. **Protocolo Inviolável de 3 Etapas (*Consent Gate*) & Exceção Autônoma**:
   - Para `fk-new-issue`, `fk-technical-analysis` e `fk-develop` (e seus aliases):
     - **Etapa 1 (Leitura & Alinhamento)**: Apenas operações de leitura no Linear (`get-issue`, `search-issues`, `list-projects`). Zero mutação no Linear antes da aprovação do desenvolvedor.
     - **Etapa 2 (Consent Gate)**: Apresente o plano ou análise e faça a pergunta explícita de consentimento ao desenvolvedor.
     - **Etapa 3 (Execução Atômica)**: Somente após resposta afirmativa ("sim", "aprovado", "pode prosseguir"), realize a transição de estado no Linear acompanhada do comentário consolidado.
   - ⚠️ **Exceção ao Consent Gate (`/fk-fix` / `fk-fix`)**:
     - O comando `/fk-fix` roda **sem Consent Gate**.
     - Ao ser invocado, o agente executa diretamente: leitura dos comentários/reviews do PR e texto extra ➔ transição para `In Progress` no Linear ➔ aplicação de correções e testes na branch ➔ push e comentário no PR ➔ transição final para `In Review` no Linear.
     - Não solicite confirmação em nenhuma etapa do `/fk-fix`. Se não houver comentários/reviews nem texto extra, informe o usuário e finalize sem mutação.

3. **Mapeamento de Estados por Rito**:
   - `fk-new-issue` ➔ Criação sob `Backlog` ou `Todo`.
   - `fk-technical-analysis` / `fk-ta` ➔ `Technical Analysis` ➔ **`Todo`** (com análise técnica registrada).
   - `fk-develop` / `fk-dev` ➔ `Todo` ➔ **`In Progress`** (com branch criada) ➔ **`In Review`** (ao abrir PR no GitHub).
   - `fk-fix` ➔ `In Review` ➔ **`In Progress`** (ao iniciar correção) ➔ **`In Review`** (ao enviar push e comentar no PR).
   - **`Done`**: O agente **NUNCA** move cards para `Done`. A transição para `Done` é exclusiva do desenvolvedor após o merge do PR.

4. **Identidade do Agente & Idempotência**:
   - Todos os comentários no Linear devem ser prefixados com `🤖 **AI Agent Update**:`.
