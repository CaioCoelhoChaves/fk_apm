# Implementation Plan: Criação de Cards Manuais no Linear com comando fk-new-manual-issue

**Branch**: `feat/FAL-59-fk-new-manual-issue` | **Date**: 2026-10-31 | **Spec**: [spec.md](specs/055-manual-linear-cards/spec.md) | **Linear Issue**: [FAL-59](https://linear.app/fallkey/issue/FAL-59/featskills-add-fk-new-manual-issue-command-for-manual-linear-cards)

**Input**: Feature specification from `specs/055-manual-linear-cards/spec.md`

---

## Summary

Disponibilizar o comando `/fk-new-manual-issue` no ecossistema `fk_apm` para permitir a criação rápida de um ou múltiplos cards estritamente operacionais/humanos no Linear. O comando opera sob um portão de consentimento com pré-visualização tabular (Pre-Render Gate), força o estado inicial em `Backlog` e a etiqueta `manual`, e garante isolamento total de código-fonte (zero branches Git, zero worktrees e zero Pull Requests). A solução estende `skills/linear-workflow/scripts/linear_api.py` com o subcomando `create-manual-issues` (suportando entrada individual e `--batch-file` JSON), adiciona prompts e declarações de skills multi-harness em `.apm/` e `.agents/`, e adiciona testes unitários automatizados.

---

## Technical Context

**Language/Version**: Python 3.8+ (Standard Library: `argparse`, `urllib.request`, `json`, `pathlib`, `re`, `unittest`)  
**Primary Dependencies**: Zero dependências externas de runtime (padrão arquitetural `fk_apm`). Linear GraphQL API.  
**Storage**: N/A (Linear GraphQL API como fonte de verdade remota; arquivos JSON temporários em disco).  
**Testing**: Python `unittest` (`python -m unittest skills/linear-workflow/tests/test_linear_api.py`).  
**Target Platform**: Multi-plataforma (Windows PowerShell e POSIX/Linux/macOS) compatível com Google Antigravity, Claude Code, Cursor, Copilot e OpenCode.  
**Project Type**: Tooling CLI / Package de Skills & Prompts de IA.  
**Performance Goals**: Criação de lote de até 10 cards em < 5 segundos.  
**Constraints**: Zero mutações na árvore Git (zero branches, zero commits para os cards manuais); estado `Backlog` e tag `manual` obrigatórios e imutáveis; sanitização e proteção contra escape de shell.  
**Scale/Scope**: Criação de 1 a dezenas de tarefas operacionais em um único comando; aplicável a qualquer time ou projeto no Linear.

---

## Constitution Check

*GATE: Checked against `.specify/memory/constitution.md`*

| Princípio Constitucional | Status | Justificativa / Validação |
| :--- | :---: | :--- |
| **I. Multi-Harness Parity & Bundled Distribution** | ✅ PASS | O comando `/fk-new-manual-issue` é empacotado no `linear-workflow` e distribuído para todos os 5 harnesses suportados, utilizando apenas scripts da standard library Python. |
| **II. Spec-Driven Linear Lifecycle & State Machine** | ✅ PASS | Os cards manuais são criados estritamente no estado `Backlog`. Não afetam o ciclo de desenvolvimento de software de código (não geram branch nem Draft PR), preservando a esteira canônica. |
| **III. Zero Shell-Escaping Corruption (File-First Payloads)** | ✅ PASS | Suporte mandatório a `--batch-file` e `--description-file` em formato UTF-8 com passagem obrigatória por `sanitize_markdown_payload`. |
| **IV. Deterministic Verification & Test Coverage** | ✅ PASS | Suíte de testes unitários automatizados com `unittest` cobrindo o subcomando `create-manual-issues`, validação de lote e injeção de labels. |
| **V. Semantic Versioning & Keep a Changelog** | ✅ PASS | Mudanças documentadas seguindo Conventional Commits sob a issue FAL-59. |

---

## 1. Diagnóstico e Contexto

### Estado Atual e Gaps Identificados
1. **Ausência de Fluxo para Atividades Estritamente Manuais**: Atualmente, a criação de cards no Linear via Spec Kit (`/speckit-specify` ou `/speckit-taskstoissues`) pressupõe itens de desenvolvimento de software, gerando branches Gitflow (`feat/<ID>-*`), abrindo Draft PRs no GitHub e exigindo especificações e testes de código.
2. **Poluição de Árvore Git por Tarefas Não-Técnicas**: Demandas operacionais (ex: contratação de provedor, pagamento de taxas, registro em console da Apple/Google, assinatura de contratos Docusign) não possuem código-fonte associado. Submetê-las ao ciclo convencional de software cria branches vazias e branches abandonadas.
3. **Falta de Criação em Lote para Setup Inicial**: No kick-off de projetos, dezenas de atividades operacionais precisam ser cadastradas simultaneamente. Hoje não há subcomando no `linear_api.py` para processar uma lista unificada de tarefas em lote.
4. **Padronização de Tags e Colunas**: É necessário garantir que todas essas tarefas operacionais recebam categoricamente a etiqueta `manual` e caiam em `Backlog`, sem risco de irem para colunas incorretas.

---

## 2. Arquitetura da Solução & Desenho Técnico

### Visão Geral da Arquitetura

```
[ Usuário / Desenvolvedor ]
         │
         ▼
[ /fk-new-manual-issue "lista de tarefas manuais" ]
         │
         ▼
[ Stage 1: Pre-Render Gate ] ──► Tabela de Pré-Visualização no Chat (Zero Mutação)
         │
         ▼
[ Stage 2: Confirmação ] ──────► ask_question / Confirmação Interativa
         │
         ▼ (Sim, aprovar)
[ Stage 3: Execução Atômica ] ─► .tmp-manual-issues.json (UTF-8)
         │
         ▼
[ linear_api.py create-manual-issues --batch-file ]
         │
         ├── 1. Resolve Team & Project (se não informados)
         ├── 2. Resolve ou Cria etiqueta "manual" (idempotente)
         ├── 3. Resolve stateId para "Backlog"
         ├── 4. Sanitiza descrições via sanitize_markdown_payload
         └── 5. Executa issueCreate mutations em sequência
         │
         ▼
[ Linear GraphQL API ] ────────► Cards criados em Backlog com tag "manual"
         │
         ▼
[ Retorno no Chat ] ───────────► URLs diretas dos cards criados (Zero Branches Git)
```

### Componentes Técnicos

1. **Subcomando CLI `create-manual-issues` (`linear_api.py`)**:
   - Adicionado ao parser de `linear_api.py`.
   - Aceita `--batch-file <json>` ou parâmetros diretos (`--title`, `--description-file`, `--description`).
   - Força o estado `Backlog` independente de entradas externas.
   - Força a tag `manual` (usando `resolve_or_create_label_id`).
   - Retorna payload JSON estruturado contendo lista das issues criadas.
2. **Prompt e Skill Multi-Harness (`fk-new-manual-issue`)**:
   - Arquivo `.apm/prompts/fk-new-manual-issue.prompt.md` contendo as diretrizes do comando e o fluxo do Consent Gate.
   - Declaração em `.apm/skills/fk-new-manual-issue/SKILL.md` e `.agents/skills/fk-new-manual-issue/SKILL.md`.
3. **Estrutura de Descrição Padrão**:
   - Gera descrições estruturadas com: `Contexto da Tarefa Manual`, `Ações Manuais a Executar` (checklist) e `Critérios de Conclusão`.
4. **Isolamento Absoluto de Código**:
   - Zero operações Git (`git checkout`, `git commit`, `gh pr`).

---

## 3. Checklist de Arquivos Impactados

- [ ] `skills/linear-workflow/scripts/linear_api.py` (modificar: implementar subcomando create-manual-issues com suporte a lote, injeção de Backlog e tag manual)
- [ ] `skills/linear-workflow/tests/test_linear_api.py` (modificar: testes unitários para o subcomando create-manual-issues)
- [ ] `skills/linear-workflow/.apm/prompts/fk-new-manual-issue.prompt.md` (criar: prompt de sistema para o comando fk-new-manual-issue)
- [ ] `skills/linear-workflow/.apm/skills/fk-new-manual-issue/SKILL.md` (criar: declaração da skill fk-new-manual-issue no pacote linear-workflow)
- [ ] `.agents/skills/fk-new-manual-issue/SKILL.md` (criar: manifesto da skill instalado para execução imediata no workspace)
- [ ] `skills/linear-workflow/SKILL.md` (modificar: documentação e registro do comando /fk-new-manual-issue)
- [ ] `skills/linear-workflow/references/multi-harness-commands.md` (modificar: inclusão do comando /fk-new-manual-issue na tabela de comandos)
- [ ] `specs/055-manual-linear-cards/research.md` (criar: artefato de pesquisa Fase 0)
- [ ] `specs/055-manual-linear-cards/data-model.md` (criar: modelo de dados e ciclo de vida Fase 1)
- [ ] `specs/055-manual-linear-cards/contracts/linear_api_cli.md` (criar: contrato de interface CLI Fase 1)
- [ ] `specs/055-manual-linear-cards/contracts/skill_command.md` (criar: contrato do comando do agente Fase 1)
- [ ] `specs/055-manual-linear-cards/quickstart.md` (criar: guia de validação executável Fase 1)

---

## 4. Estratégia de Testes

### 4.1 Testes Unitários (`unittest`)
- `test_create_manual_issues_single`: Valida a criação de um único card manual via parâmetros CLI com estado `Backlog` e tag `manual`.
- `test_create_manual_issues_batch`: Valida o processamento em lote a partir de arquivo JSON temporário.
- `test_create_manual_issues_ensures_backlog_state`: Garante que o estado seja invariavelmente forçado para `Backlog`.
- `test_create_manual_issues_ensures_manual_label`: Garante que a etiqueta `manual` seja resolvida e anexada a todos os cards.
- `test_create_manual_issues_sanitizes_markdown`: Valida que o payload de descrição passe por `sanitize_markdown_payload`.
- `test_create_manual_issues_missing_team_or_auth`: Valida o comportamento amigável de erro caso não haja credenciais ou time resolvido.

### 4.2 Testes de Integração e Verificação Estática
- Execução da suíte completa: `python -m unittest skills/linear-workflow/tests/test_linear_api.py`.
- Validação estática de artefatos do Spec Kit: `python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-59`.

---

## 5. Plano Gitflow

- **Branch de Trabalho**: `feat/FAL-59-fk-new-manual-issue`
- **Branch Base**: `develop`
- **Pull Request Associado**: [#21 — feat(skills): add fk-new-manual-issue command for manual linear cards](https://github.com/CaioCoelhoChaves/fk_apm/pull/21) (Draft)
- **Commits Convencionais**:
  - `docs(spec): add specification for FAL-59`
  - `docs(plan): add implementation plan and phase 1 design artifacts for FAL-59`
  - `feat(skills): implement create-manual-issues subcomand in linear_api.py`
  - `test(workflow): add unit tests for create-manual-issues subcomand`
  - `feat(skills): add fk-new-manual-issue prompt and skill declarations`
- **Rito de Finalização**: Promoção do PR Draft para pronto via `gh pr ready 21`, revisão humana e merge em `develop`. Transição manual para `Done` no Linear.
