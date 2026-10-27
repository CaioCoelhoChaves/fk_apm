---
name: fk-fix
description: Aplicação autônoma de feedback de code review em PR aberto sem Consent Gate. Lê comentários e reviews do PR, move o card Linear para In Progress, aplica correções na branch existente, comenta no PR e retorna o card para In Review. Use quando o usuário invocar /fk-fix ou fk-fix.
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-fix: Aplicação de Feedback de Code Review no PR & Linear

Este comando automatiza o ciclo completo de resolução de apontamentos de code review em um Pull Request já aberto, sincronizando o card correspondente no Linear.

> [!IMPORTANT]
> **Execução Autônoma (SEM Consent Gate)**:
> Ao contrário de `/fk-new-issue` e `/fk-technical-analysis`, os comandos de execução (`/fk-develop` e `/fk-fix`) rodam **sem Consent Gate**. O desenvolvedor apenas invoca o comando e o agente executa atomicamente todo o fluxo até o retorno para **`In Review`**.

---

## Fluxo de Execução

### 1. Identificação do Card e do PR
- **Identificação da Issue**:
  - Extraia a chave da issue informada como argumento (ex.: `/fk-fix FAL-24` ou `/fk-fix FAL-24 ajustar testes unitários`);
  - Se omitida no argumento, deduza a issue pela branch Git atual, seguindo a convenção Linear `<type>/<issue-key>-<slug>` (ex.: `feat/FAL-24-auth` ➔ `FAL-24`).
  - Se não for possível identificar a issue, alerte o desenvolvedor no chat e continue a investigação apenas com base no PR do repositório.
- **Localização do PR**:
  - Localize o PR aberto no GitHub correspondente à branch de trabalho atual:
    ```bash
    gh pr view --json number,title,url,headRefName,state
    ```
  - Se nenhum PR aberto for encontrado, informe ao desenvolvedor e finalize sem realizar alterações.

### 2. Leitura & Consolidação do Feedback
- **Coleta de Apontamentos**:
  - **Comentários gerais do PR**:
    ```bash
    gh pr view --comments
    ```
  - **Reviews e pareceres de revisores**:
    ```bash
    gh api repos/{owner}/{repo}/pulls/{number}/reviews
    ```
  - **Comentários inline no código (review comments)**:
    ```bash
    gh api repos/{owner}/{repo}/pulls/{number}/comments
    ```
  - **Instruções adicionais**: Inclua o texto complementar fornecido pelo desenvolvedor na invocação do comando.
- **Filtros Mandatórios**:
  - **Ignorar comentários anteriores do agente**: Ignore comentários com prefixo `🤖 **AI Agent Update**:` ou de autoria de bots de automação.
  - **Ignorar threads resolvidas / out-of-date**: Desconsidere apontamentos já resolvidos ou cujos trechos de código foram modificados em commits posteriores.
- **Validação de Feedback Vazio**:
  - Se não houver comentários, reviews pendentes nem texto adicional do usuário, avise o desenvolvedor:
    > *"Nenhum feedback pendente ou comentário de review foi encontrado para o PR #<number>. Nenhuma alteração foi realizada."*
  - **Interrompa a execução imediatamente** sem alterar branches ou cards no Linear.

### 3. Movimentação do Card para In Progress (Sem Confirmação)
- Consulte a issue no Linear via CLI ou MCP:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py get-issue "<issue-key>"
  ```
- Se o projeto ou card não existir no Linear, alerte o usuário com transparência e prossiga com o fix técnico no repositório.
- Se o card existir, transicione imediatamente para **`In Progress`** com comentário estruturado via `--comment-file` (arquivo UTF-8 temporário para evitar corrupção de crases e aspas no shell):
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "In Progress" \
    --comment-file "<comentario-fix-inicio-utf8.md>"
  ```
  *(A idempotência de 10 minutos é garantida pelo CLI).*

### 4. Implementação & Testes na Branch Existente
- Certifique-se de estar na branch correspondente ao PR existente (`git status`).
- Implemente as correções solicitadas diretamente nos arquivos do projeto.
- Execute a suíte de testes locais para assegurar que não haja regressão.
- Crie commit(s) semânticos seguindo Conventional Commits 1.0.0 (ex.: `fix(...)`, `test(...)`).
- Envie as alterações para o repositório remoto via `git push origin <branch-name>`:
  - ⚠️ **NÃO crie um novo PR**. O push atualiza automaticamente o PR já existente.

### 5. Registro de Feedback no PR do GitHub
- Grave o comentário em um arquivo UTF-8 temporário e publique no PR via GitHub CLI com `--body-file` (nunca use `--body "..."` inline com crases ou blocos de código):
  ```bash
  gh pr comment <pr-number> --body-file "<pr-comment-utf8.md>"
  ```
  Estrutura recomendada para `<pr-comment-utf8.md>`:
  ```markdown
  🤖 **AI Agent Update**: Correções de code review aplicadas nos commits recentes:

  ### ✅ Itens Corrigidos
  - **<Arquivo/Contexto>**: <Descrição da correção realizada>.

  ### ℹ️ Itens Não Alterados (se houver)
  - **<Contexto>**: <Motivo técnico justificado>.
  ```

### 6. Transição Final do Card para In Review no Linear
- Atualize atomicamente o card no Linear para **`In Review`** usando `--comment-file`:
  ```bash
  python .agents/skills/linear-workflow/scripts/linear_api.py update-issue "<issue-id>" \
    --state "In Review" \
    --comment-file "<comentario-fix-concluido-utf8.md>"
  ```
- Notifique o usuário no chat com o resumo das alterações e link do PR atualizado.

---

## Regra de Ouro: Rito Manual para Done

- O agente **NUNCA** move o card para **`Done`**.
- O status `Done` permanece sob controle manual e exclusivo do desenvolvedor, que só deve ser marcado após merge do PR e homologação final da entrega.
