# Implementation Plan: Remoção do Rito de Aprovação Final (Consent Gate) nas Etapas Spec Kit

**Branch**: `feat/FAL-74-remove-consent-gate-rite` | **Date**: 2026-11-23 | **Spec**: [spec.md](spec.md) | **Linear Issue**: [FAL-74](https://linear.app/fallkey/issue/FAL-74/featlinear-workflow-remover-rito-de-aprovacao-final-nas-etapas-speckit) | **Pull Request (Draft)**: [#23](https://github.com/CaioCoelhoChaves/fk_apm/pull/23)

**Input**: Feature specification from `specs/055-remove-consent-gate-rite/spec.md`

---

## Summary

Remover o rito formal de aprovação final (*3-Stage Consent Gate* via `ask_question` / `AskUserQuestion` com opções `"(Recommended) Sim, aprovar"` / `"Editar..."`) das etapas `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` e `/speckit-implement` na skill `linear-workflow`, substituindo-o por um fluxo fluido orientado a diálogo natural entre desenvolvedor e LLM com **Pre-Render obrigatório** no chat e execução atômica direta no GitHub (Draft PR) e no Linear (`Backlog` ➔ `Planned` ➔ `Todo` ➔ `In Progress` ➔ `In Review`) via arquivos UTF-8 sanitizados. O *3-Stage Consent Gate* permanece ativo apenas em `/speckit-taskstoissues` (criação de múltiplos sub-cards em lote), e a transição para `Done` continua exclusivamente manual após revisão e merge do Pull Request.

---

## Technical Context

**Language/Version**: Markdown / YAML / Python 3.8+ (Standard Library + `unittest`)  
**Primary Dependencies**: Zero dependências externas em `linear_api.py`; APM CLI (`apm install`) para sincronização multi-harness em `.agents/`.  
**Storage**: N/A (documentação Spec Kit em `specs/055-remove-consent-gate-rite/`, definições de skills/prompts em `skills/linear-workflow/` e estado remoto via Linear GraphQL API).  
**Testing**: Python `unittest` (`python -m unittest skills/linear-workflow/tests/test_linear_api.py`) e validação estática (`python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-74`).  
**Target Platform**: Multi-harness (Google Antigravity, Claude Code, Cursor, GitHub Copilot e OpenCode) em Windows PowerShell e POSIX.  
**Project Type**: Pacote APM de Skills, Prompts e CLI Tooling (`fk_apm`).  
**Performance Goals**: Zero interrupções burocráticas por rito final nas 4 etapas alvo; execução direta de criação/transição no Linear imediatamente após Pre-Render.  
**Constraints**: Manter Pre-Render completo no chat (tabela de card(s) ou Executive Briefing com Título Revisado, Descrição Atualizada e 5 seções obrigatórias), payloads UTF-8 file-first (`--description-file`, `--comment-file`, `--body-file`), paridade `.apm/skills/` vs `.apm/prompts/` vs `.agents/skills/`, bloqueio estrito de transição automatizada para `Done`, e preservação do Consent Gate em `/speckit-taskstoissues`.  
**Scale/Scope**: 10 comandos `/speckit-*` sob `skills/linear-workflow/`, documentação constitucional/raiz, suíte de testes unitários e avaliações (`evals.json`).

---

## Constitution Check

*GATE: Checked against `.specify/memory/constitution.md` (Pre-Research & Post-Phase-1 Design)*

| Princípio Constitucional | Status | Justificativa / Validação |
| :--- | :---: | :--- |
| **I. Multi-Harness Parity & Bundled Distribution** | ✅ PASS | Todos os pares `.apm/skills/<cmd>/SKILL.md`, `.apm/prompts/<cmd>.prompt.md` e `.apm/instructions/` serão atualizados em conjunto e sincronizados para `.agents/` via `apm install`. |
| **II. Living Specs, Draft PR Lifecycle & 6-Stage State Machine** | ⚠️ EMENDA PLANEJADA (`1.1.0` ➔ `1.2.0`) | A Constituição v1.1.0 atualmente descreve `(with 3-Stage Consent Gate)` para `specify`, `plan` e `tasks`. Conforme a seção `Governance` da própria Constituição, a implementação incluirá a emenda formal para `v1.2.0` tanto em `.specify/memory/constitution.md` quanto em `skills/linear-workflow/assets/.specify/memory/constitution.md`, mantendo Draft PRs, os 6 estágios e `Done` exclusivamente manual. |
| **III. Zero Shell-Escaping Corruption (File-First Payloads)** | ✅ PASS | Nenhuma alteração no modelo file-first UTF-8 (`--description-file`, `--comment-file`, `--body-file` e `sanitize_markdown_payload()`). |
| **IV. Deterministic Verification & Test Coverage** | ✅ PASS | `skills/linear-workflow/tests/test_linear_api.py` será atualizado e ampliado para validar ausência de rito final nas 4 etapas, Pre-Render obrigatório, paridade skills/prompts e preservação do gate em `taskstoissues`. |
| **V. Semantic Versioning & Keep a Changelog** | ✅ PASS | Mudança registrada em `CHANGELOG.md` sob `## [Unreleased]` (`Changed`). |

---

## Project Structure

### Documentation (this feature)

```text
specs/055-remove-consent-gate-rite/
├── spec.md                                 # Especificação funcional (concluída)
├── checklists/
│   └── requirements.md                     # Checklist de qualidade da spec
├── research.md                             # Decisões arquiteturais (Fase 0)
├── plan.md                                 # Este arquivo (Plano de Implementação)
├── data-model.md                           # Entidades de política de execução e Pre-Render (Fase 1)
├── quickstart.md                           # Cenários executáveis de verificação (Fase 1)
└── contracts/
    └── skill-execution-modes.md            # Contratos normativos por comando e invariantes de teste (Fase 1)
```

### Source Code (repository root)

```text
.specify/memory/constitution.md
apm.yml
apm.lock.yaml
README.md
CHANGELOG.md
skills/linear-workflow/
├── SKILL.md
├── .apm/
│   ├── instructions/
│   │   └── linear-lifecycle-commands.instructions.md
│   ├── prompts/
│   │   ├── speckit-specify.prompt.md
│   │   ├── speckit-plan.prompt.md
│   │   ├── speckit-tasks.prompt.md
│   │   └── speckit-implement.prompt.md
│   └── skills/
│       ├── speckit-specify/SKILL.md
│       ├── speckit-plan/SKILL.md
│       ├── speckit-tasks/SKILL.md
│       └── speckit-implement/SKILL.md
├── assets/.specify/memory/constitution.md
├── evals/evals.json
├── references/
│   ├── multi-harness-commands.md
│   └── states-and-labels.md
└── tests/test_linear_api.py
```

**Structure Decision**: Toda a mudança concentra-se nos contratos de instrução, prompts, referências, constituição, documentação e testes da skill `skills/linear-workflow/` e artefatos raiz de catálogo/governança (`apm.yml`, `README.md`, `CHANGELOG.md`, `apm.lock.yaml`), sem exigir alterações na lógica GraphQL de `linear_api.py`.

---

## 1. Diagnóstico e Contexto

1. **Fricção Burocrática do Rito de Aprovação em 3 Etapas**: Atualmente, `/speckit-specify`, `/speckit-plan` e `/speckit-tasks` obrigam o agente a parar em uma Etapa 2 rígida (`ask_question` / `AskUserQuestion` com opções `"(Recommended) Sim, aprovar"` e `"Editar..."`) antes de criar ou avançar o card no Linear, interrompendo três vezes seguidas o fluxo do mesmo card mesmo quando não há dúvidas técnicas ou divergências.
2. **Acoplamento Textual Multi-Harness**: O contrato de *3-Stage Consent Gate* está replicado de forma transversal em `skills/linear-workflow/SKILL.md`, `.apm/instructions/linear-lifecycle-commands.instructions.md`, nos pares `.apm/skills/<cmd>/SKILL.md` e `.apm/prompts/<cmd>.prompt.md`, nas referências (`multi-harness-commands.md`, `states-and-labels.md`), em `evals/evals.json`, na Constituição (`.specify/memory/constitution.md` e cópia em `assets/.specify/memory/constitution.md`), em `apm.yml` e em `README.md`.
3. **Asserções de Teste Legadas**: Em `skills/linear-workflow/tests/test_linear_api.py`, o teste `test_skill_files_enforce_prerender_and_tooling_labels` ainda verifica literalmente a presença da string `"Proibição de Consent Gate Cego"` em `SKILL.md`, exigindo atualização para refletir o modelo *Pre-Render Obrigatório + Execução Direta Orientada a Diálogo*.
4. **Escopo Seletivo**: `/speckit-implement` já declara ausência de Consent Gate (precisando apenas alinhar linguagem de diálogo natural em ambiguidades bloqueantes), `/speckit-taskstoissues` deve manter o *3-Stage Consent Gate* por criar múltiplos sub-cards em lote, e `fk-new-manual-issue` permanece inalterada por ser skill independente.

---

## 2. Arquitetura da Solução & Desenho Técnico

```text
[Developer <-> LLM (Diálogo Natural)]
        │
        ├── 1. /speckit-specify ─────────► Pre-Render Tabela no Chat ─► Branch + Draft PR + Card Backlog (Direto)
        │
        ├── 2. /speckit-plan <CARD-ID> ──► Artefatos + Commit PR ─► Pre-Render Executive Briefing ─► Linear Planned (Direto)
        │
        ├── 3. /speckit-tasks <CARD-ID> ─► tasks.md + validate-plan + Commit PR ─► Pre-Render Briefing ─► Linear Todo (Direto)
        │
        ├── 4. /speckit-implement <CARD> ► Todo ─► In Progress ─► Código/Testes ─► gh pr ready ─► In Review (Autônomo)
        │
        └── Exceção: /speckit-taskstoissues ► Pre-Render Tabela ─► 3-Stage Consent Gate (Lote) ─► Sub-cards Backlog
```

### Pilares do Desenho Técnico

1. **Execução Direta com Pre-Render Obrigatório (`specify`, `plan`, `tasks`)**:
   - Manter intacto o **Pre-Render** no texto visível do chat: tabela completa de card proposto em `/speckit-specify` e **Executive Briefing** completo (**Título Revisado**, **Descrição Atualizada** e resumo das **5 seções arquiteturais obrigatórias**) em `/speckit-plan` e `/speckit-tasks`.
   - Eliminar a Etapa 2 obrigatória (`ask_question` / `AskUserQuestion` com `"Sim, aprovar"` / `"Editar..."`) desses três comandos, executando imediatamente a criação/transição no Linear via `--title`, `--description-file` e `--comment-file` (UTF-8 sanitizado) junto ao push no Draft PR.
2. **Execução 100% Autônoma com Diálogo Natural em Ambiguidades (`implement`)**:
   - Confirmar em `speckit-implement` (skill + prompt) que não existe rito final de aprovação antes de iniciar (`In Progress`), promover o PR (`gh pr ready`) ou finalizar (`In Review`). Caso surja ambiguidade bloqueante genuína em `spec.md` ou `plan.md`, o agente esclarece via diálogo natural ou documenta decisão técnica fundamentada.
3. **Preservação Seletiva do Consent Gate em Lote (`taskstoissues`) e Rito Humano (`Done`)**:
   - Manter `/speckit-taskstoissues` sob o protocolo completo de 3 etapas (`Stage 1 Pre-Render` ➔ `Stage 2 ask_question` ➔ `Stage 3 create-issue` em lote).
   - Preservar o bloqueio incondicional de `--state "Done"` em `linear_api.py` (rito exclusivo humano após merge do PR).
4. **Governança Constitucional, Paridade Multi-Harness e Sincronização `.agents/`**:
   - Emendar `.specify/memory/constitution.md` e `skills/linear-workflow/assets/.specify/memory/constitution.md` da versão `1.1.0` para `1.2.0`, documentando no *Sync Impact Report* a remoção do rito final nas 4 etapas.
   - Atualizar todos os pares `.apm/skills/` e `.apm/prompts/` em paridade exata e executar `apm install` para regenerar `.agents/` e `apm.lock.yaml` sem divergências (`SC-003`).

---

## 3. Checklist de Arquivos Impactados

- [ ] `skills/linear-workflow/SKILL.md` (modificar: substituir 3-Stage Consent Gate por execução direta com Pre-Render em specify, plan e tasks, mantendo Consent Gate apenas em taskstoissues)
- [ ] `skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md` (modificar: atualizar regra global multi-harness para execução direta com Pre-Render nas 4 etapas e exceção em taskstoissues)
- [ ] `skills/linear-workflow/.apm/skills/speckit-specify/SKILL.md` (modificar: remover Stage 2 de confirmação final e criar branch, Draft PR e card em Backlog diretamente após Pre-Render)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-specify.prompt.md` (modificar: sincronizar prompt multi-harness de speckit-specify sem rito de aprovação final)
- [ ] `skills/linear-workflow/.apm/skills/speckit-plan/SKILL.md` (modificar: remover Stage 2 de confirmação final e avançar card diretamente para Planned após commit no Draft PR e Executive Briefing no chat)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-plan.prompt.md` (modificar: sincronizar prompt multi-harness de speckit-plan sem rito de aprovação final)
- [ ] `skills/linear-workflow/.apm/skills/speckit-tasks/SKILL.md` (modificar: remover Stage 2 de confirmação final e avançar card diretamente para Todo após validate-plan, commit no Draft PR e Executive Briefing no chat)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-tasks.prompt.md` (modificar: sincronizar prompt multi-harness de speckit-tasks sem rito de aprovação final)
- [ ] `skills/linear-workflow/.apm/skills/speckit-implement/SKILL.md` (modificar: reforçar execução 100% autônoma sem rito de aprovação final e diálogo natural apenas em ambiguidade bloqueante)
- [ ] `skills/linear-workflow/.apm/prompts/speckit-implement.prompt.md` (modificar: sincronizar prompt multi-harness de speckit-implement)
- [ ] `skills/linear-workflow/references/multi-harness-commands.md` (modificar: atualizar tabela de modos de execução e seção de protocolo Pre-Render + execução direta vs Consent Gate em taskstoissues)
- [ ] `skills/linear-workflow/references/states-and-labels.md` (modificar: atualizar stateDiagram-v2 e tabela de estados sem Consent Gate em specify, plan e tasks)
- [ ] `skills/linear-workflow/evals/evals.json` (modificar: atualizar expected_output do eval 1 para criação direta em Backlog após Pre-Render sem rito de aprovação final)
- [ ] `skills/linear-workflow/tests/test_linear_api.py` (modificar: atualizar asserções de Pre-Render e adicionar testes garantindo ausência de rito de aprovação final em specify, plan, tasks e implement, paridade .apm/skills vs .apm/prompts, e preservação do Consent Gate em taskstoissues)
- [ ] `.specify/memory/constitution.md` (modificar: emendar Constituição para v1.2.0 ratificando fluxo orientado a diálogo com Pre-Render sem rito de aprovação final nas 4 etapas)
- [ ] `skills/linear-workflow/assets/.specify/memory/constitution.md` (modificar: sincronizar Constituição empacotada em assets para v1.2.0)
- [ ] `apm.yml` (modificar: atualizar descrição do pacote linear-workflow no catálogo marketplace)
- [ ] `README.md` (modificar: atualizar descrição da skill linear-workflow na tabela Individual Skills)
- [ ] `apm.lock.yaml` (modificar: atualizar hashes de implantação em .agents/ via apm install)
- [ ] `CHANGELOG.md` (modificar: documentar alteração em Unreleased sob Changed)

---

## 4. Estratégia de Testes

### 4.1 Testes Unitários (`unittest` em `skills/linear-workflow/tests/test_linear_api.py`)
- Atualizar `test_skill_files_enforce_prerender_and_tooling_labels` para validar o contrato de **Pre-Render Obrigatório** e execução direta sem exigir a expressão legada `"Proibição de Consent Gate Cego"`.
- Preservar `test_skill_files_enforce_mandatory_title_and_description_in_tech_analysis` garantindo continuidade de `Título Revisado`, `Descrição Atualizada`, `--title`, `--description-file`, `--comment-file` e `--body-file`.
- Adicionar testes de contrato verificando:
  1. Ausência de instruções exigindo rito final de aprovação (`"Sim, aprovar"` / `"Editar..."`) em `speckit-specify`, `speckit-plan`, `speckit-tasks` e `speckit-implement` (tanto em `.apm/skills/` quanto em `.apm/prompts/`).
  2. Paridade de conteúdo entre `.apm/skills/<cmd>/SKILL.md` e `.apm/prompts/<cmd>.prompt.md` e entre fonte `skills/linear-workflow/` e cópias implantadas em `.agents/skills/`.
  3. Preservação explícita do *3-Stage Consent Gate* em `speckit-taskstoissues`.

### 4.2 Validação Estática e Sincronização APM
- Execução integral da suíte: `python -m unittest skills/linear-workflow/tests/test_linear_api.py`.
- Validação estática dos artefatos da feature: `python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-74`.
- Sincronização e verificação APM: `apm install` e verificação de integridade entre `skills/linear-workflow/` e `.agents/`.

---

## 5. Plano Gitflow

- **Branch de Trabalho**: `feat/FAL-74-remove-consent-gate-rite`
- **Branch Base**: `develop`
- **Pull Request Associado**: [#23 — feat(linear-workflow): remover rito de aprovação final nas etapas speckit (FAL-74)](https://github.com/CaioCoelhoChaves/fk_apm/pull/23) (Draft)
- **Commits Convencionais Planejados**:
  - `docs(spec): specify FAL-74 - remove-consent-gate-rite` (já comitado em `a1a4564`)
  - `docs(plan): technical plan and architecture for FAL-74`
  - `docs(tasks): task breakdown for FAL-74`
  - `feat(linear-workflow): remove final consent gate rite from speckit commands (FAL-74)`
  - `test(linear-workflow): update contract tests for dialogue-driven workflow (FAL-74)`
- **Rito de Finalização**: Promoção do PR Draft `#23` para pronto via `gh pr ready 23` ao final de `/speckit-implement FAL-74`, revisão humana e merge em `develop`. Transição para `Done` no Linear exclusivamente manual pelo desenvolvedor.
