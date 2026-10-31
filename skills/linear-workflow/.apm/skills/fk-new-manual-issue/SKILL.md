---
name: "fk-new-manual-issue"
description: "Criar um ou múltiplos cards estritamente manuais e operacionais no Linear na coluna Backlog com tag 'manual' via 3-Stage Consent Gate. Zero branches Git, zero commits, zero Pull Requests."
compatibility: "Compatível com Google Antigravity, Claude Code, Cursor, Copilot e OpenCode. Requer Python 3.8+ e credenciais do Linear."
metadata:
  author: "fk_apm"
  source: "skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md"
---

## User Input

```text
$ARGUMENTS
```

Você **DEVE** considerar a entrada do usuário acima antes de prosseguir.

---

## Objetivo & Filosofia de Isolamento Total de Código

O comando `/fk-new-manual-issue` é destinado **exclusivamente a tarefas operacionais e humanas** que não alteram o código-fonte da aplicação (ex: registro de contas de terceiros, pagamentos, configurações em dashboards externos, chamadas e alinhamentos operacionais).

### ⛔ Salvaguardas Mandatórias de Isolamento Git:
- **ZERO Branches Git**: NUNCA crie branch `feat/*`, `fix/*` ou qualquer outra para cards gerados por este comando.
- **ZERO Worktrees**: NUNCA crie `.worktrees/<CARD-ID>`.
- **ZERO Draft PRs**: NUNCA abra Pull Requests no GitHub para tarefas manuais.
- **ZERO Alterações de Código**: NUNCA modifique ou comite arquivos da aplicação para tarefas manuais.
- **Estado Inicial Imutável**: Todos os cards manuais são criados obrigatoriamente na coluna `Backlog`.
- **Tag Obrigatória**: Todos os cards recebem invariavelmente a etiqueta `manual`.

---

## Protocolo de Execução: 3-Stage Consent Gate

### Estágio 1: Pre-Render Gate (Zero Mutação Remota)

1. Se `$ARGUMENTS` estiver vazio, pergunte ao usuário o título e as ações da(s) tarefa(s) manual(is).
2. Se `$ARGUMENTS` contiver uma descrição ou lista de tarefas, processe e normalize cada tarefa com a estrutura padrão:
   - **Título**: Resumo claro e objetivo da atividade operacional.
   - **Descrição**:
     ```markdown
     ## Contexto da Tarefa Manual
     <Contexto operacional e justificativa da atividade>

     ## Ações Manuais a Executar
     - [ ] <Ação 1>
     - [ ] <Ação 2>

     ## Critérios de Conclusão
     - [ ] <Evidência ou resultado comprovado da conclusão>
     ```
3. **Renderize a tabela de pré-visualização no chat** antes de qualquer chamada remota ao Linear:

```markdown
### 📋 Proposta de Cards Manuais no Linear

| # | Título | Estado Inicial | Etiqueta | Escopo da Ação Manual |
|---|--------|----------------|----------|------------------------|
| 1 | <Título 1> | Backlog | manual | <Resumo da ação manual 1> |
| 2 | <Título 2> | Backlog | manual | <Resumo da ação manual 2> |
```

---

### Estágio 2: Confirmação Interativa

Acione a ferramenta interativa de perguntas (`ask_question` / `AskUserQuestion`):
- **Pergunta**: `Deseja aprovar a criação de X card(s) manual(is) no Linear na coluna Backlog com a tag 'manual'?`
- **Opções**:
  - `(Recommended) Sim, aprovar criação no Linear`
  - `Editar lista antes de criar...`

Se o usuário escolher `Editar lista antes de criar...` ou recusar, pause e solicite os ajustes necessários sem criar nenhum card no Linear.

---

### Estágio 3: Criação Atômica via Arquivo UTF-8

Após aprovação explícita pelo usuário:

1. Grave a lista de issues em um arquivo JSON temporário `.tmp-manual-issues.json` codificado em UTF-8:
   ```json
   {
     "issues": [
       {
         "title": "<Título 1>",
         "description": "<Descrição 1 Markdown>",
         "priority": 0
       }
     ]
   }
   ```
2. Execute o subcomando CLI:
   ```bash
   python skills/linear-workflow/scripts/linear_api.py create-manual-issues --batch-file ".tmp-manual-issues.json"
   ```
3. Remova imediatamente o arquivo temporário `.tmp-manual-issues.json`.
4. Exiba no chat a lista com os cards criados, seus identificadores gerados (ex: `FAL-XX`) e links diretos para o Linear.
5. Finalize a execução sem criar branches ou commits.
