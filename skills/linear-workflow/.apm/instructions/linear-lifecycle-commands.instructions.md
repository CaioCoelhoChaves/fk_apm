---
description: Interceptação universal e roteamento multi-harness para comandos de ciclo de vida do Linear (/fk-* e fk-*)
---

# Roteamento Universal de Comandos de Ciclo de Vida do Linear

Esta regra intercepta comandos de ciclo de vida do Linear em todos os harnesses (Google Antigravity, Claude Code, Cursor, GitHub Copilot e terminais de chat), garantindo tolerância sintática (com ou sem barra) e acionamento rigoroso da skill `linear-workflow`.

## 1. Gatilhos de Interceptação

Sempre que a mensagem do usuário contiver qualquer um dos seguintes gatilhos (com ou sem barra `/` inicial, maiúsculas ou minúsculas):

- **Planejamento / Criação**: `/fk-new-issue`, `fk-new-issue`, ou solicitações explícitas de planejar/decompor cards para o Linear.
- **Análise Técnica**: `/fk-technical-analysis`, `fk-technical-analysis`, ou solicitações de análise técnica/spike de um card do Linear.
- **Desenvolvimento**: `/fk-develop`, `fk-develop`, ou solicitações de desenvolver/implementar um card do Linear.
- **Correção de PR / Review Feedback**: `/fk-fix`, `fk-fix`, ou solicitações explícitas de aplicar feedback de code review em PR aberto.

## 2. Ações Mandatórias do Agente

1. **Ativação da Skill**:
   - Ative imediatamente as instruções e fluxos definidos em `skills/linear-workflow/SKILL.md`.

2. **Protocolo Inviolável de 3 Etapas (*Consent Gate*) & Comandos Autônomos**:
   - Para `fk-new-issue` e `fk-technical-analysis`:
     - **Etapa 1 (Leitura, Renderização Visível & Alinhamento)**: Apenas operações de leitura no Linear (`get-issue`, `search-issues`, `list-projects`). Zero mutação no Linear antes da aprovação do desenvolvedor. No planejamento (`fk-new-issue`), classifique labels respeitando a natureza do repositório (`Front` para UI/web/mobile, `Back` para APIs/serviços de servidor, e `Feature` ou sem tag para repositórios de tooling, pacotes de skills/prompts como `fk_apm`, CLIs e infraestrutura — nunca force `Back` apenas por scripts Python/Shell). Na análise técnica (`fk-technical-analysis`), a proposta deve apresentar obrigatoriamente o **Título Revisado** e a **Descrição Atualizada** do card junto às 5 seções estruturadas: Diagnóstico, Arquitetura, Checklist de Arquivos, Testes e Plano Gitflow. **É estritamente proibido invocar `ask_question` / `AskUserQuestion` sem antes emitir integralmente no texto visível do chat toda a tabela de tarefas ou o título/descrição revisados e as 5 seções da análise técnica.**
     - **Etapa 2 (Consent Gate Interativo com Resumo Embutido)**: Após renderizar a proposta completa no chat, acione a **ferramenta nativa de perguntas** do harness (`ask_question` no Antigravity, `AskUserQuestion` no Claude Code, tool nativa no OpenCode, ou fallback em texto formatado para outros harnesses) incluindo obrigatoriamente um **resumo conciso da proposta dentro do próprio campo `question`** (títulos/labels dos cards no `/fk-new-issue`, ou resumo da solução, total de arquivos e branch no `/fk-technical-analysis`), com as opções:
       - `(Recommended) Sim, aprovar`: avança para a Etapa 3.
       - `Editar...`: desenvolvedor informa ajustes em texto livre; o agente retorna à Etapa 1 sem qualquer mutação e reapresenta o Consent Gate após ajustar o plano.
     - **Etapa 3 (Execução Atômica)**: Somente após `Sim, aprovar`, realize a transição de estado no Linear. Na criação de cards (`fk-new-issue`), utilize `--description-file "<path>"`. Na análise técnica (`fk-technical-analysis`), é **mandatório atualizar atomicamente o título (`--title`) e a descrição do card (`--description-file`)** juntamente com `--state "Todo"` e **persistir a especificação técnica integral** sob o formato de 5 seções no comentário consolidado (`--comment-file`).
   - ⚠️ **Comandos de Execução Autônoma sem Consent Gate (`/fk-develop` e `/fk-fix`)**:
     - Os comandos `/fk-develop` e `/fk-fix` rodam **sem Consent Gate**.
     - **`/fk-develop`**: Leitura de requisitos/critérios (consumindo prioritariamente a especificação técnica completa persistida da análise técnica) ➔ transição imediata para `In Progress` com comentário (`--comment-file`) informando branch e premissas assumidas ➔ criação de branch Gitflow ➔ implementação e testes sem confirmações intermediárias (perguntas ao desenvolvedor apenas em ambiguidade real e bloqueante; padrão: decidir, registrar premissa e seguir) ➔ abertura de PR no GitHub (`gh pr create --body-file`) ➔ transição obrigatória para `In Review` no Linear (`--comment-file`).
     - **`/fk-fix`**: Leitura dos comentários/reviews do PR e texto extra ➔ transição imediata para `In Progress` no Linear (`--comment-file`) ➔ aplicação de correções e testes na branch ➔ push e comentário no PR (`gh pr comment --body-file`) ➔ transição final para `In Review` no Linear (`--comment-file`).
     - Não solicite confirmação em nenhuma etapa do `/fk-develop` ou `/fk-fix`. Se no `/fk-fix` não houver comentários/reviews nem texto extra, informe o usuário e finalize sem mutação.

3. **Mapeamento de Estados por Rito**:
   - `fk-new-issue` ➔ Criação sob **`Backlog`** (padrão, com Consent Gate); `Todo` apenas como exceção explícita (card trivial ou com escopo técnico 100% resolvido).
   - `fk-technical-analysis` ➔ `Technical Analysis` ➔ **`Todo`** (com Consent Gate, atualização obrigatória de título e descrição do card e especificação técnica completa persistida).
   - `fk-develop` ➔ `Todo` ➔ **`In Progress`** (autônomo, com branch criada) ➔ **`In Review`** (ao abrir PR no GitHub).
   - `fk-fix` ➔ `In Review` ➔ **`In Progress`** (ao iniciar correção) ➔ **`In Review`** (ao enviar push e comentar no PR).
   - **`Done`**: O agente **NUNCA** move cards para `Done`. A transição para `Done` é exclusiva do desenvolvedor após o merge do PR.

4. **Identidade do Agente, Idempotência & Proteção Anti-Corrupção de Crases no Shell**:
   - Todos os comentários no Linear devem ser prefixados com `🤖 **AI Agent Update**:`.
   - **Proibição de Markdown Inline no Shell**: Em Windows PowerShell e Bash, nunca passe Markdown contendo crases (`` ` ``), blocos de código ou aspas duplas via `--description "..."`, `--comment "..."` ou `gh pr create/comment --body "..."` (no PowerShell, `` `f ``, `` `t ``, `` `r ``, `` `b ``, `` `n `` corrompem `` `feat` `` ➔ `eat`, `` `fix` `` ➔ `ix`, `` `test` `` ➔ `est`, `` `refactor` `` ➔ `efactor`). Sempre grave o conteúdo em arquivo UTF-8 temporário e utilize `--description-file`, `--comment-file` e `--body-file`.
