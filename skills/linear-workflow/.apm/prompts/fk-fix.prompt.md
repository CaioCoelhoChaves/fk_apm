---
description: Aplicação de feedback de code review em PR aberto sem Consent Gate, com commits na branch, comentário no PR e retorno a In Review no Linear
argument-hint: "[<issue-key>] [instruções adicionais]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# /fk-fix: Aplicação de Feedback de Code Review no PR & Linear

Aplique as correções pedidas na revisão de um PR já aberto para a issue indicada, rodando **sem Consent Gate**:

Entrada / Argumentos: $ARGUMENTS

## Fluxo de Execução
1. **Identificação**: Identifique o card Linear (via argumento ou deduzido da branch atual `<type>/<issue-key>-<slug>`) e o PR aberto no GitHub via `gh pr view`.
2. **Coleta de Feedback**:
   - Leia os comentários do PR (`gh pr view --comments`), reviews (`gh api repos/{owner}/{repo}/pulls/{n}/reviews`) e comentários inline (`gh api repos/{owner}/{repo}/pulls/{n}/comments`), além das instruções passadas em `$ARGUMENTS`.
   - Ignore comentários anteriores do agente (`🤖 **AI Agent Update**:`) e threads resolvidas.
   - Se não houver comentários nem instruções extras, alerte o desenvolvedor e interrompa a execução sem fazer alterações.
3. **Mover para In Progress (Sem Confirmação)**:
   - Avance o card para `In Progress` no Linear com comentário resumindo o início do fix.
   - Se o projeto/card não existir no Linear, avise o usuário e continue a correção na branch existente.
4. **Implementação na Branch Existente**:
   - Aplique as correções nos arquivos do projeto e valide com testes automatizados locais.
   - Crie commits semânticos (Conventional Commits 1.0.0) e faça push na branch existente para atualizar o PR (sem criar novo PR).
5. **Comentar no PR**:
   - Publique comentário no PR (`gh pr comment`) com prefixo `🤖 **AI Agent Update**:`, detalhando itens corrigidos e eventuais itens não alterados com justificativa.
6. **Mover para In Review**:
   - Mova o card no Linear para `In Review` com comentário contendo o link do PR e resumo técnico.
7. **Regra de Ouro**: O card nunca é movido para `Done` pelo agente (permanece manual pelo desenvolvedor).
