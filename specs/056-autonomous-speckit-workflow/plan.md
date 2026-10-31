# Implementation Plan: Fluxo Contínuo e Autônomo do Spec Kit com Revisão Centralizada no GitHub

**Branch**: `feat/FAL-60-autonomous-speckit-github-review` | **Date**: 2026-10-31 | **Spec**: [specs/056-autonomous-speckit-workflow/spec.md](spec.md)

**Input**: Feature specification from `specs/056-autonomous-speckit-workflow/spec.md` (Linear Issue: [FAL-60](https://linear.app/fallkey/issue/FAL-60/featworkflow-eliminar-consent-gates-entre-fases-do-speckit-e-habilitar)).

## Summary

Eliminar os Consent Gates interativos de 3 etapas (`ask_question` síncrono no chat) entre os comandos de ciclo de vida do Spec Kit (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`), estabelecendo uma esteira de execução contínua de ponta a ponta. A governança e revisão do desenvolvedor passam a ocorrer de forma assíncrona diretamente no GitHub por meio dos Living Specs Draft PRs abertos na especificação. O `/speckit-clarify` é atualizado para sincronizar autonomamente com edições remotas e feedbacks no GitHub (`git pull --rebase origin <branch>`), a Constituição do repositório é elevada para a versão 1.2.0, os manifestos de skills de múltiplos harnesses são harmonizados e a salvaguarda de transição para `Done` é mantida estritamente manual pelo desenvolvedor.

## Technical Context

**Language/Version**: Python 3.8+ (Cross-platform standard library scripts, sem dependências externas de runtime além de CLI nativa)  
**Primary Dependencies**: GitHub CLI (`gh`), Linear GraphQL API, `apm` CLI, `unittest` (suite de testes nativa)  
**Storage**: Sistema de arquivos local (`specs/<feature>/`, `.worktrees/<CARD-ID>`), Git commits e branches remotas no GitHub  
**Testing**: `python -m unittest discover -s skills/linear-workflow/tests -p "test_*.py"`  
**Target Platform**: Multi-harness (Google Antigravity, Claude Code, Cursor, GitHub Copilot, OpenCode) em Windows PowerShell e POSIX  
**Project Type**: APM AI Skill Bundle & Workflow CLI Framework  
**Performance Goals**: Execução imediata de transições no Linear sem bloqueios ociosos de chat; avanço de fase em < 5 segundos  
**Constraints**: Zero mutações indevidas para o estado `Done` por agentes; payloads de Markdown transmitidos exclusivamente via arquivos temporários UTF-8; compatibilidade estrita com repositórios consumidores  
**Scale/Scope**: 10 comandos Spec Kit (`speckit-*`), 1 pacote canônico (`skills/linear-workflow`), constituição e documentações  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Princípio I (Multi-Harness Parity & Bundled Distribution)**: PASS. Todos os comandos continuam operando de forma equivalente em Antigravity, Claude Code, Cursor, Copilot e OpenCode através dos prompts e skills em `skills/linear-workflow/.apm/`.
- **Princípio II (Living Specs & Linear State Machine)**: PASS (Atualizado via emenda constitucional 1.2.0). Living Specs via Draft PRs mantidos; estados avançam deterministicamente (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`); Consent Gates interativos eliminados; transição para `Done` mantida estritamente manual pelo desenvolvedor.
- **Princípio III (Zero Shell-Escaping Corruption)**: PASS. Todas as mutações e comentários utilizam arquivos temporários UTF-8 (`--description-file`, `--comment-file`, `--body-file`).
- **Princípio IV (Deterministic Verification & Test Coverage)**: PASS. Cobertura completa de testes automatizados via `test_linear_api.py`.
- **Princípio V (Semantic Versioning & Keep a Changelog)**: PASS. Entradas estruturadas adicionadas em `CHANGELOG.md` sob `## [Unreleased]`.

## Project Structure

### Documentation (this feature)

```text
specs/056-autonomous-speckit-workflow/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan output)
├── research.md          # Phase 0 output (Decisions & Rationale)
├── data-model.md        # Phase 1 output (Entity models & state machines)
├── quickstart.md        # Phase 1 output (Validation scenarios)
├── contracts/           # Phase 1 output (Execution & sync contracts)
│   ├── lifecycle-execution-contract.md
│   └── github-clarify-sync-contract.md
└── checklists/
    └── requirements.md  # Quality checklist
```

---

## 1. Diagnóstico e Contexto

No formato atual, o Spec Kit exige uma confirmação síncrona com caixa de seleção (`ask_question` / `AskUserQuestion`) ao final de cada fase técnica:
1. `/speckit-specify` gera especificação, mas pausa exigindo que o usuário clique para criar o card e Draft PR.
2. `/speckit-plan` desenha a arquitetura, mas pausa exigindo que o usuário clique para enviar ao PR e mover o card para `Planned`.
3. `/speckit-tasks` gera o checklist de tarefas, mas pausa exigindo que o usuário aprove para mover para `Todo`.
4. `/speckit-taskstoissues` também pausa entre lotes.

Essa mecânica foi concebida sob a premissa de prevenir mutações prematuras no Linear. Contudo, na prática moderna de engenharia de software com **Living Specs**, o GitHub Draft PR criado na primeira etapa já funciona como o ambiente primário e centralizado de inspeção humana. O desenvolvedor analisa o diff de código, comenta diretamente nas linhas alteradas ou faz commits na branch do PR. A interrupção no chat da IDE é redundante, quebra o fluxo cognitivo e gera atrasos artificiais.

Além disso, quando o desenvolvedor faz ajustes no GitHub, falta uma conexão fluida para que o comando `/speckit-clarify` absorva essas mudanças remotas de volta para a árvore local de especificações de forma 100% autônoma.

O diagnóstico aponta a necessidade de harmonizar todos os comandos de ciclo de vida para executarem autonomamente (tal qual já operam `/speckit-implement` e `/speckit-converge`), centralizando a revisão no GitHub e preservando exclusivamente a transição manual para `Done`.

---

## 2. Arquitetura da Solução & Desenho Técnico

A solução adota uma arquitetura em 4 pilares:

### 2.1 Esteira Contínua e Autônoma de Ciclo de Vida
Os comandos `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-taskstoissues`, `/speckit-implement` e `/speckit-converge` passam a rodar em modo contínuo:
- **Geração local de artefatos**: especificação, arquitetura, decomposição ou código são gerados no workspace ou worktree efêmero.
- **Sincronização com GitHub**: comita os artefatos com Conventional Commits e envia via `git push origin <branch>` para o Draft PR.
- **Avanço Atômico no Linear**: invoca `linear_api.py update-issue` para avançar o estado correspondente (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`) registrando comentários estruturados com arquivos temporários UTF-8.
- **Executive Report**: emite no chat um resumo conciso contendo links clicáveis para o Pull Request no GitHub, o card no Linear e arquivos locais, sem invocar `ask_question`.

### 2.2 Sincronização Remota Integrada no `/speckit-clarify`
O comando `/speckit-clarify <CARD-ID>` passa a:
1. Executar `git pull --rebase origin <branch>` para absorver commits remotos feitos pelo desenvolvedor.
2. Analisar ambiguidades e pendências (`[NEEDS CLARIFICATION]`).
3. Atualizar `spec.md` e `checklists/requirements.md`.
4. Comitar e enviar para o remote (`git push origin <branch>`).
5. Emitir o relatório executivo indicando prontidão para `/speckit-plan <CARD-ID>`.

### 2.3 Atualização Constitucional (SemVer 1.2.0)
A Constituição em `.specify/memory/constitution.md` e seu template em `skills/linear-workflow/assets/.specify/memory/constitution.md` são elevados para a versão 1.2.0:
- Formalização do fluxo contínuo e autônomo.
- Remoção do requisito de Consent Gate entre fases.
- Reafirmação inegociável da salvaguarda de transição manual para `Done`.

### 2.4 Harmonização Multi-Harness
Os prompts e skills sob `skills/linear-workflow/.apm/` e manifestos de bundles em `apm.yml` e `README.md` são atualizados para remover instruções que orientavam os agentes a chamar ferramentas de perguntas de confirmação antes de avançar fases.

---

## 3. Checklist de Arquivos Impactados

- [ ] `.specify/memory/constitution.md`
- [ ] `skills/linear-workflow/assets/.specify/memory/constitution.md`
- [ ] `skills/linear-workflow/SKILL.md`
- [ ] `skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md`
- [ ] `skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md`
- [ ] `skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md`
- [ ] `skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md`
- [ ] `skills/linear-workflow/.apm/prompts/speckit-clarify.prompt.md`
- [ ] `skills/linear-workflow/.apm/prompts/speckit-taskstoissues.prompt.md`
- [ ] `skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md`
- [ ] `skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md`
- [ ] `skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md`
- [ ] `skills/linear-workflow/.apm/skills/speckit-clarify/SKILL.md`
- [ ] `skills/linear-workflow/.apm/skills/speckit-taskstoissues/SKILL.md`
- [ ] `skills/linear-workflow/references/multi-harness-commands.md`
- [ ] `skills/linear-workflow/references/states-and-labels.md`
- [ ] `skills/linear-workflow/tests/test_linear_api.py`
- [ ] `apm.yml`
- [ ] `README.md`
- [ ] `CHANGELOG.md`

---

## 4. Estratégia de Testes

1. **Testes Unitários Automatizados**:
   - Executar `python -m unittest discover -s skills/linear-workflow/tests -p "test_*.py"` no ambiente de desenvolvimento para assegurar que todas as funcionalidades de `linear_api.py` (validação de planos, formatação de títulos, sanitização Markdown, criação de comentários com idempotência) continuam 100% íntegras.
   - Adicionar casos de teste específicos para assegurar que a validação de planos e integridade não dependem de dados legados de consent gates.

2. **Validação de Sintaxe e Manifestos**:
   - Validar formatação do `apm.yml` e compilação do bundle.
   - Executar `validate-plan` sobre os artefatos de `specs/056-autonomous-speckit-workflow/`.

3. **Verificação de Regressão da Salvaguarda de `Done`**:
   - Assegurar que nenhum script ou instrução permita que agentes transicionem cards para `Done`.

---

## 5. Plano Gitflow

- **Branch de Trabalho**: `feat/FAL-60-autonomous-speckit-github-review`
- **Branch Base**: `main` (ou `develop`)
- **Pull Request**: [#22 — feat(workflow): eliminar consent gates entre fases do speckit e habilitar revisao autonoma via github](https://github.com/CaioCoelhoChaves/fk_apm/pull/22)
- **Commits Seguidos**: Conventional Commits 1.0.0
  - `docs(plan): technical plan and architecture for FAL-60`
  - `feat(workflow): remove consent gates and enable autonomous continuous execution (FAL-60)`
  - `test(workflow): update test suite for autonomous speckit workflow (FAL-60)`
  - `docs(constitution): bump constitution to v1.2.0 and update changelog (FAL-60)`
- **Estratégia de Integração**: Rebase e merge no GitHub após aprovação do PR.

---

## Complexity Tracking

Não há violações de complexidade nem adições de dependências externas. A arquitetura simplifica o fluxo existente ao remover camadas de confirmação desnecessárias.
