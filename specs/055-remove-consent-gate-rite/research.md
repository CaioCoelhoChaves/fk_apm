# Research: Remoção do Rito de Aprovação Final (Consent Gate) no Linear Workflow

**Issue**: [FAL-74](https://linear.app/fallkey/issue/FAL-74/featlinear-workflow-remover-rito-de-aprovacao-final-nas-etapas-speckit) | **Branch**: `feat/FAL-74-remove-consent-gate-rite` | **Date**: 2026-11-23

---

## 1. Fluxo Orientado a Diálogo com Execução Direta e Pre-Render Obrigatório

### Decision
Remover a Etapa 2 (`ask_question` / `AskUserQuestion` com opções `"(Recommended) Sim, aprovar"` / `"Editar..."`) de `/speckit-specify`, `/speckit-plan` e `/speckit-tasks`, preservando a obrigatoriedade do **Pre-Render** no texto visível do chat (tabela de card em `/speckit-specify` e Executive Briefing contendo `Título Revisado`, `Descrição Atualizada` e as 5 seções arquiteturais obrigatórias em `/speckit-plan` e `/speckit-tasks`) imediatamente antes/junto da persistência atômica no GitHub Draft PR e no Linear via arquivos UTF-8. Manter `/speckit-implement` 100% autônomo (`Todo` ➔ `In Progress` ➔ `In Review`).

### Rationale
- Elimina 3 paradas burocráticas consecutivas por card sem perder transparência visual no chat nem rastreabilidade versionada no Draft PR.
- Ajustes em especificações, planos ou listas de tarefas passam a ocorrer por meio de diálogo natural com a LLM, enquanto o gate humano definitivo permanece no code review e no merge manual do Pull Request (`In Review` ➔ `Done`).
- Manter o Pre-Render garante que nenhuma mutação no Linear seja opaca ("silent mutation") e preserva os contratos de payload UTF-8 (`--description-file`, `--comment-file`, `--body-file`) processados por `sanitize_markdown_payload()`.

### Alternatives Considered
- *Remover também o Pre-Render no chat*: Rejeitado porque causaria mutações opacas no Linear sem visibilidade imediata para o desenvolvedor sobre título, descrição e arquitetura persistidos.
- *Criar flag opcional `--yes` ou modo dual*: Rejeitado porque o usuário definiu que o comportamento padrão do fluxo deve ser orientado a diálogo sem rito de aprovação final nessas etapas.

---

## 2. Preservação Seletiva do 3-Stage Consent Gate em Lotes (`/speckit-taskstoissues`) e Issues Manuais (`fk-new-manual-issue`)

### Decision
Manter o **3-Stage Consent Gate** exclusivamente em `/speckit-taskstoissues` (dentro de `linear-workflow`) e preservar intacta a skill independente `fk-new-manual-issue`.

### Rationale
- `/speckit-taskstoissues` converte `tasks.md` em múltiplos sub-cards em lote no Linear, apresentando alto potencial de ruído no backlog caso decomponha granularidade indesejada sem revisão prévia pelo desenvolvedor.
- `fk-new-manual-issue` é uma skill independente voltada a demandas estritamente manuais/operacionais e está explicitamente fora das 4 etapas solicitadas (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`).

### Alternatives Considered
- *Remover o Consent Gate de todos os comandos indistintamente*: Rejeitado por violar `FR-001`, `US2` e as premissas explícitas de `specs/055-remove-consent-gate-rite/spec.md`.

---

## 3. Política de Diálogo Natural vs Uso de Ferramenta de Pergunta

### Decision
Distinguir explicitamente nos contratos de prompt e skill entre **rito final de aprovação** (estritamente proibido em `/speckit-specify`, `/speckit-plan`, `/speckit-tasks` e `/speckit-implement`) e **diálogo natural / esclarecimento de ambiguidade bloqueante genuína** (permitido via conversa natural ou `/speckit-clarify`).

### Rationale
- Evita que o agente paralise diante de ambiguidades críticas reais nos requisitos ao mesmo tempo em que impede o retorno de perguntas burocráticas de confirmação disfarçadas (`"Deseja aprovar?"`, `"Sim, aprovar / Editar..."`) ao final de cada etapa.
- Alinha todas as instruções multi-harness a um modelo fluido de colaboração conversacional.

### Alternatives Considered
- *Proibir qualquer pergunta em qualquer circunstância*: Rejeitado porque ambiguidades críticas de escopo ainda podem exigir diálogo natural com o desenvolvedor antes de prosseguir com decisões de alto impacto.

---

## 4. Governança Constitucional (`v1.1.0` ➔ `v1.2.0`), Sincronização Multi-Harness (`.apm/` ➔ `.agents/`) e Contratos de Teste

### Decision
Atualizar simultaneamente:
- A documentação central da skill (`skills/linear-workflow/SKILL.md`), a instrução global (`skills/linear-workflow/.apm/instructions/linear-lifecycle-commands.instructions.md`), os pares `.apm/skills/<cmd>/SKILL.md` e `.apm/prompts/<cmd>.prompt.md` (`speckit-specify`, `speckit-plan`, `speckit-tasks`, `speckit-implement`);
- As referências (`skills/linear-workflow/references/multi-harness-commands.md`, `skills/linear-workflow/references/states-and-labels.md`), avaliações (`skills/linear-workflow/evals/evals.json`), Constituição do repositório e empacotada (`.specify/memory/constitution.md` e `skills/linear-workflow/assets/.specify/memory/constitution.md`, emendadas de `1.1.0` para `1.2.0`);
- Os manifests e documentação raiz (`apm.yml`, `README.md`, `CHANGELOG.md`);
- A suíte de testes unitários (`skills/linear-workflow/tests/test_linear_api.py`), adaptando `test_skill_files_enforce_prerender_and_tooling_labels` (atualmente exige `"Proibição de Consent Gate Cego"`) e adicionando verificações de ausência de rito de aprovação final nas 4 etapas, paridade entre `.apm/skills/` e `.apm/prompts/` e preservação do Consent Gate em `speckit-taskstoissues`;
- Executar `apm install` para sincronizar os artefatos implantados em `.agents/` e atualizar `apm.lock.yaml`.

### Rationale
- Cumpre os Princípios I (*Multi-Harness Parity & Bundled Distribution*) e IV (*Deterministic Verification & Test Coverage*) da Constituição, evitando divergência entre prompts para Copilot/Claude/Cursor e skills para Antigravity/OpenCode.
- Garante `SC-002` (100% da suíte passando) e `SC-003` (zero divergência entre `skills/linear-workflow/` e `.agents/skills/`).

### Alternatives Considered
- *Editar apenas `.apm/skills/` sem atualizar `.apm/prompts/` ou sem executar `apm install`*: Rejeitado por quebrar a paridade multi-harness exigida pela Constituição e deixar `.agents/skills/` dessincronizado com a fonte.
