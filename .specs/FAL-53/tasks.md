# Checklist de Tarefas — FAL-53

- [x] **T1**: Criar a constituição arquitetural do repositório em `.speckit/constitution.md`.
- [x] **T2**: Estruturar os artefatos SDD de homologação em `.specs/FAL-53/` (`spec.md`, `plan.md`, `tasks.md`).
- [x] **T3**: Implementar `sanitize_markdown_payload` e subcomando `sanitize-markdown` em `skills/linear-workflow/scripts/linear_api.py` e sincronizar com `.agents/skills/linear-workflow/scripts/linear_api.py`.
- [x] **T4**: Implementar `validate_spec_plan` e subcomando CLI `validate-plan` em `skills/linear-workflow/scripts/linear_api.py` e sincronizar com `.agents/skills/linear-workflow/scripts/linear_api.py`.
- [x] **T5**: Atualizar `skills/linear-workflow/SKILL.md` e `.agents/skills/linear-workflow/SKILL.md` com a arquitetura Spec-Driven (`.speckit/constitution.md`, `.specs/<issue-key>/`), Executive Briefing, `sanitize_markdown_payload` e `validate-plan`.
- [x] **T6**: Atualizar `fk-technical-analysis`, `fk-develop`, `fk-new-issue` e `linear-lifecycle-commands` (skills, prompts, instructions, rules e references em `skills/` e `.agents/`).
- [x] **T7**: Adicionar testes unitários em `skills/linear-workflow/tests/test_linear_api.py` (e `.agents/skills/linear-workflow/tests/test_linear_api.py`) para `sanitize_markdown_payload`, `validate-plan` e contratos SDD das skills, e validar `.specs/FAL-53` com `validate-plan`.
- [x] **T8**: Atualizar `CHANGELOG.md` via `changelog_manager.py`, concluir checklist `tasks.md`, realizar commit/push, abrir PR e mover `FAL-53` para `In Review` com Executive Briefing.
