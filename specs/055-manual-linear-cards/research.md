# Research: Criação de Cards Manuais no Linear com comando /fk-new-manual-issue

**Feature**: `055-manual-linear-cards` | **Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)  
**Date**: 2026-10-31 | **Status**: Completed

---

## 1. Contexto e Objetivos da Pesquisa

A funcionalidade visa disponibilizar o comando `/fk-new-manual-issue` para criação rápida de um ou múltiplos cards estritamente operacionais no Linear. Esses cards representam tarefas humanas que não envolvem alterações no código-fonte nem seguem o ciclo de vida de desenvolvimento de software do Spec Kit (`specs/`, branches de código, Draft PRs, testes automatizados de software).

Esta fase de pesquisa avaliou e consolidou as decisões técnicas para estruturação do comando, parsing de argumentos em lote, integração com a CLI `linear_api.py`, portão de consentimento e isolamento de código.

---

## 2. Decisões Arquiteturais e Justificativas

### Decisão 1: Ponto de Integração da Skill no Ecossistema `fk_apm`
- **Decisão**: Integrar a skill e o comando `/fk-new-manual-issue` sob o ecossistema `linear-workflow`, fornecendo:
  1. O prompt principal em `skills/linear-workflow/.apm/prompts/fk-new-manual-issue.prompt.md`.
  2. A declaração da skill em `skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md`.
  3. A instalação e espelhamento em `.agents/skills/fk-new-manual-issue/SKILL.md`.
  4. Suporte na CLI existente `skills/linear-workflow/scripts/linear_api.py` via subcomando dedicado `create-manual-issues`.
  5. Registro da documentação em `skills/linear-workflow/SKILL.md` e nos catálogos de comandos multi-harness.
- **Justificativa**: `linear-workflow` já centraliza a autenticação dinâmica do Linear (MCP, env vars, `.env`), sanitização de payloads Markdown, queries GraphQL de times/projetos/labels e o conjunto de comandos de governança. Evita duplicação de bibliotecas GraphQL e garante que qualquer repositório que consuma `linear-workflow` ou o bundle `default` tenha acesso imediato a `/fk-new-manual-issue`.
- **Alternativas consideradas**:
  - *Criar um pacote de skill totalmente isolado em `skills/fk-new-manual-issue`*: Rejeitado porque duplicaria `linear_api.py`, a lógica de autenticação GraphQL e os testes de conectividade.

### Decisão 2: Formato de Entrada e Criação em Lote (Single vs. Batch)
- **Decisão**: Suportar tanto entrada interativa/textual quanto arquivo JSON/Markdown estruturado via CLI:
  1. No CLI `linear_api.py`, criar o subcomando `create-manual-issues`:
     - Modo individual: aceita `--title`, `--description-file` (ou `--description`), `--team-id`, `--project-id`.
     - Modo em lote: aceita `--batch-file <path_to_json>` onde o JSON contém uma lista de objetos `{"title": "...", "description": "...", "priority": ...}`.
  2. O script garante de forma determinística que:
     - O estado inicial é fixado em `Backlog` (resolvendo o `stateId` de `Backlog` no time).
     - A etiqueta `manual` é adicionada automaticamente (resolvendo ou criando via `resolve_or_create_label_id`).
     - A resposta JSON retorna uma lista estruturada contendo todos os cards criados: `{"success": true, "created": [{"id": "...", "identifier": "FAL-60", "title": "...", "url": "..."}]}`.
- **Justificativa**: Oferece idempotência, facilidade de scripting automatizado e proteção contra inconsistências no estado e labels.
- **Alternativas consideradas**:
  - *Disparar múltiplos subprocessos chamando `create-issue` sequencialmente no prompt*: Rejeitado por ser mais lento, propenso a falhas parciais sem rollback/log unificado e sem garantia rígida de aplicação de regras de negócio específicas para tarefas manuais.

### Decisão 3: Protocolo do Consent Gate (3-Stage Consent Gate com Pre-Render)
- **Decisão**: Implementar o fluxo de 3 estágios estrito da constituição `fk_apm`:
  - **Stage 1 (Pre-Render Gate - Zero Mutação)**: O agente analisa a solicitação do usuário, extrai ou divide os cards manuais e renderiza na conversa do chat uma tabela de pré-visualização completa antes de chamar qualquer ferramenta de confirmação:
    | # | Título Proposto | Estado Inicial | Etiqueta | Escopo / Ações Manuais |
    |---|-----------------|----------------|----------|------------------------|
  - **Stage 2 (Confirmação Interativa)**: Invocação de `ask_question` com resumo conciso e opções:
    - `(Recommended) Sim, aprovar criação no Linear`
    - `Editar cards antes de criar...`
  - **Stage 3 (Execução Atômica)**: Após a confirmação, o agente grava o lote em arquivo temporário UTF-8 e invoca `python skills/linear-workflow/scripts/linear_api.py create-manual-issues --batch-file .tmp-manual-issues.json`.
- **Justificativa**: Cumpre o Princípio III (Zero Shell-Escaping Corruption) e a governança de Consent Gate, garantindo que o usuário veja exatamente o que será criado antes de qualquer mutação remota.
- **Alternativas consideradas**:
  - *Criar direto sem perguntar*: Viola a constituição e os requisitos de integridade do Linear.

### Decisão 4: Estrutura Padronizada da Descrição do Card Manual
- **Decisão**: Toda issue criada receberá uma descrição padronizada com três seções obrigatórias:
  ```markdown
  ## Contexto da Tarefa Manual
  [Motivação e objetivo da atividade operacional]

  ## Ações Manuais a Executar
  - [ ] Passo 1
  - [ ] Passo 2

  ## Critérios de Conclusão
  - [ ] Evidência ou resultado esperado para finalização humana
  ```
- **Justificativa**: Evita cards vagos ("Criar conta"), fornecendo clareza operacional imediata para a pessoa que for executar a tarefa no Linear.
- **Alternativas consideradas**:
  - *Aceitar texto livre sem formatação*: Resulta em cards despadronizados e sem critérios de aceite claros.

### Decisão 5: Isolamento Completo de Código (Zero Git Mutations)
- **Decisão**: O comando `/fk-new-manual-issue` NÃO executa:
  - Criação de branches Git (`git checkout -b`).
  - Criação de worktrees locais (`.worktrees/`).
  - Criação de Pull Requests (`gh pr create`).
  - Criação de pastas em `specs/`.
- **Justificativa**: Atende diretamente aos requisitos FR-009 e SC-003 da especificação, assegurando que o repositório de código permaneça inalterado ao gerenciar tarefas puramente operacionais.
- **Alternativas consideradas**: Nenhuma; foi um requisito mandatório do usuário.

---

## 3. Conclusão da Pesquisa

Todas as dúvidas técnicas e de integração foram sanadas. O desenho técnico seguirá para a Phase 1 com a modelagem de entidades, contratos de CLI e prompts, e elaboração do guia de validação rápida.
