# Plano Técnico — FAL-53

- **Issue**: `FAL-53`
- **Título Revisado**: `feat(workflow): integrar spec-driven development (spec-kit) e sanitizacao de markdown ao linear-workflow`
- **Constituição Base**: `.speckit/constitution.md`

---

## 1. Diagnóstico e Contexto

O ecossistema `linear-workflow` no `fk_apm` precisava evoluir de um modelo centrado apenas em comentários remotos no Linear para uma arquitetura **Spec-Driven Development (SDD)** inspirada no `spec-kit`:
- **Gargalo Cognitivo**: Sem Cognitive Scaffolding ancorado em `.speckit/constitution.md` e artefatos locais (`plan.md` e `tasks.md`), análises técnicas complexas perdiam profundidade ou omitiam validações de arquivos.
- **Fragilidade de Renderização Markdown**: Mesmo utilizando `--description-file` e `--comment-file`, payloads gerados por LLMs podem conter quebras `\r\n` mistas, caracteres de controle residuais (`\x0c`, `\x08`), blocos cercados ```` ``` ```` não fechados ou tabelas Markdown com pipes desalinhados, degradando a visualização no Linear e no GitHub.
- **Execução `/fk-develop` sem Estado Local**: O agente não possuía um artefato `.specs/<issue-key>/tasks.md` local para ler e marcar o progresso atômico durante a codificação.

---

## 2. Arquitetura da Solução & Desenho Técnico

1. **Sanitizador Determinístico (`sanitize_markdown_payload` em `linear_api.py`)**:
   - Normaliza `\r\n` e `\r` para `\n`.
   - Remove caracteres de controle ASCII não imprimíveis (`[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]`), preservando `\n` e `\t`.
   - Rastreia cercas de código (```` ``` ```` ou ```` ~~~ ````) linha a linha; caso uma cerca permaneça aberta ao final do documento, anexa automaticamente o fechamento correspondente em nova linha.
   - Detecta blocos de tabelas Markdown e normaliza cada linha garantindo pipes nas extremidades (`| ... |`), espaçamento limpo nas células e alinhamento do número de colunas conforme o cabeçalho da tabela.
   - Integrado automaticamente em `cmd_create_issue`, `cmd_update_issue` e exposto via subcomando CLI `sanitize-markdown`.

2. **Validador Estático de Planos (`validate_spec_plan` & subcomando `validate-plan` em `linear_api.py`)**:
   - Opera localmente (sem exigir `LINEAR_API_KEY` na inicialização do CLI).
   - Verifica a existência de `.specs/<issue-key>/plan.md` e `.specs/<issue-key>/tasks.md` (e inspeciona `spec.md` se presente).
   - Valida a presença das 5 seções obrigatórias em `plan.md`:
     1. `Diagnóstico e Contexto`
     2. `Arquitetura da Solução`
     3. `Checklist de Arquivos Impactados`
     4. `Estratégia de Testes`
     5. `Plano Gitflow`
   - Extrai os caminhos de arquivos listados no checklist de `plan.md` e valida que não são placeholders genéricos (`<arquivo-1>`, `path/to/file`, `TODO`) e que os caminhos relativos pertencem à estrutura válida do repositório.
   - Verifica que `tasks.md` possui itens de checklist Markdown (`- [ ]` ou `- [x]`).

3. **Cognitive Scaffolding, Executive Briefing & Fluxo SDD nas Skills**:
   - `/fk-new-issue`: suporte opcional à criação de `.specs/<issue-key>/spec.md` e apresentação enxuta.
   - `/fk-technical-analysis`: lê `.speckit/constitution.md`, gera `.specs/<issue-key>/plan.md` e `.specs/<issue-key>/tasks.md`, executa `validate-plan <issue-key>` antes do Consent Gate, e apresenta no chat e no Linear o **Executive Briefing** (10-15 linhas com métricas-chave, Título Revisado, Descrição Atualizada e síntese das 5 seções apontando para `.specs/<issue-key>/`).
   - `/fk-develop`: lê prioritariamente `.specs/<issue-key>/tasks.md` e `.specs/<issue-key>/plan.md` (com fallback para comentário/descrição no Linear), atualizando os checkboxes (`- [x]`) em `tasks.md` conforme avança.

---

## 3. Checklist de Arquivos Impactados

- `.speckit/constitution.md` (criar)
- `.specs/FAL-53/spec.md` (criar)
- `.specs/FAL-53/plan.md` (criar)
- `.specs/FAL-53/tasks.md` (criar)
- `skills/linear-workflow/scripts/linear_api.py` (modificar)
- `.agents/skills/linear-workflow/scripts/linear_api.py` (modificar)
- `skills/linear-workflow/SKILL.md` (modificar)
- `.agents/skills/linear-workflow/SKILL.md` (modificar)
- `skills/linear-workflow/.apm/skills/fk-technical-analysis/SKILL.md` (modificar)
- `.agents/skills/fk-technical-analysis/SKILL.md` (modificar)
- `skills/linear-workflow/.apm/skills/fk-develop/SKILL.md` (modificar)
- `.agents/skills/fk-develop/SKILL.md` (modificar)
- `skills/linear-workflow/.apm/skills/fk-new-issue/SKILL.md` (modificar)
- `.agents/skills/fk-new-issue/SKILL.md` (modificar)
- `skills/linear-workflow/.apm/prompts/fk-technical-analysis.prompt.md` (modificar)
- `skills/linear-workflow/.apm/prompts/fk-develop.prompt.md` (modificar)
- `skills/linear-workflow/.apm/prompts/fk-new-issue.prompt.md` (modificar)
- `skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md` (modificar)
- `.agents/rules/linear-lifecycle-commands.md` (modificar)
- `skills/linear-workflow/references/multi-harness-commands.md` (modificar)
- `skills/linear-workflow/references/states-and-labels.md` (modificar)
- `skills/linear-workflow/tests/test_linear_api.py` (modificar)
- `.agents/skills/linear-workflow/tests/test_linear_api.py` (modificar)
- `CHANGELOG.md` (modificar)

---

## 4. Estratégia de Testes

- Execução da suíte unitária com `python -m unittest discover -s skills/linear-workflow/tests -p "test_*.py" -v`:
  - Testes de `sanitize_markdown_payload`:
    - Fechamento automático de blocos de código cercados (` ```python ` sem fechamento).
    - Normalização e alinhamento de tabelas Markdown com pipes desalinhados ou faltantes.
    - Remoção de caracteres de controle (`\x0c`, `\x08`, `\x00`) e normalização de `\r\n` para `\n`.
  - Testes de `validate_spec_plan` / `validate-plan`:
    - Plano válido com `plan.md` (5 seções + caminhos válidos) e `tasks.md` (itens `- [ ]` / `- [x]`).
    - Detecção de falha quando faltam seções obrigatórias, quando `tasks.md` não tem checkboxes ou quando há placeholders inválidos (`<arquivo-1>`).
- Validação determinística real no próprio artefato `.specs/FAL-53/`:
  - `python skills/linear-workflow/scripts/linear_api.py validate-plan FAL-53`

---

## 5. Plano Gitflow

- **Branch**: `feat/FAL-53-spec-driven-development-linear-workflow`
- **Base Branch**: `main`
- **Commits**: Conventional Commits 1.0.0 (`feat(workflow): ...`)
- **Status Alvo**: `In Progress` ➔ `In Review`
