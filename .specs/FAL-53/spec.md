# Especificação Funcional — FAL-53

- **Issue**: [FAL-53](https://linear.app/fallkey/issue/FAL-53/featworkflow-integrar-spec-driven-development-spec-kit-e-sanitizacao)
- **Título**: `feat(workflow): integrar spec-driven development (spec-kit) e sanitizacao de markdown ao linear-workflow`
- **Projeto**: FK APM

---

## 1. Contexto & Problema

O fluxo de desenvolvimento atual no Linear e GitHub (`fk-new-issue`, `fk-technical-analysis`, `fk-develop`, `fk-fix`) possui rastreabilidade completa, mas enfrenta três gargalos operacionais:
1. Instruções puramente procedurais no chat geram análises superficiais quando não ancoradas em uma constituição arquitetural e artefatos locais estruturados.
2. Comentários extensos e Markdown em trânsito para o Linear/GitHub sofrem corrupção de formatação (quebras `\r\n`, caracteres de controle de escape do shell, blocos de código abertos sem fechamento e tabelas desalinhadas).
3. A execução autônoma em `/fk-develop` dependia exclusivamente da leitura de comentários remotos no Linear, sem um checklist local versionado (`tasks.md`) para acompanhamento progressivo.

---

## 2. Requisitos Funcionais

1. **RF-01 — Constituição Arquitetural (`.speckit/constitution.md`)**:
   - Definir as regras inegociáveis e padrões arquiteturais do repositório `fk_apm` em `.speckit/constitution.md`.
2. **RF-02 — Camada Local de Especificação (`.specs/<issue-key>/`)**:
   - Padronizar a estrutura `.specs/<issue-key>/` contendo `spec.md` (requisitos funcionais), `plan.md` (desenho técnico nas 5 seções obrigatórias) e `tasks.md` (checklist atômico e ordenado de implementação).
3. **RF-03 — Sanitizador Determinístico de Markdown (`sanitize_markdown_payload`)**:
   - Implementar em `linear_api.py` a função `sanitize_markdown_payload` que normaliza quebras de linha (`\r\n` ➔ `\n`), remove caracteres de controle inválidos, fecha blocos de código cercados (```` ``` ````) não terminados e alinha/normaliza tabelas Markdown antes de qualquer mutação no Linear.
4. **RF-04 — Validador Estático de Planos (`validate-plan`)**:
   - Implementar o subcomando `validate-plan` em `linear_api.py` para inspecionar `.specs/<issue-key>/plan.md` e `tasks.md`, verificando seções obrigatórias, ausência de placeholders vagos, presença de tasks acionáveis e validade sintática/existência dos caminhos de arquivos impactados.
5. **RF-05 — Atualização das Skills e Regras com Executive Briefing & Cognitive Scaffolding**:
   - Atualizar `linear-workflow`, `fk-technical-analysis`, `fk-develop`, `fk-new-issue` e `linear-lifecycle-commands` (em `skills/` e `.agents/`) para operar com Cognitive Scaffolding, Executive Briefing (10-15 linhas com métricas e referência ao `.specs/<issue-key>/`) e consumo/atualização direta de `.specs/<issue-key>/tasks.md`.

---

## 3. Critérios de Aceitação

- [x] `.speckit/constitution.md` criado e documentado.
- [x] `sanitize_markdown_payload` implementado em `linear_api.py` e integrado às mutações de criação/atualização de issues e comentários.
- [x] Subcomando `validate-plan` implementado em `linear_api.py` validando `.specs/<issue-key>/plan.md` e `tasks.md`.
- [x] Skills `/fk-technical-analysis`, `/fk-develop`, `/fk-new-issue`, `linear-workflow` e regras multi-harness atualizadas e sincronizadas.
- [x] Testes unitários cobrindo `sanitize_markdown_payload` (blocos de código abertos, tabelas desalinhadas, `\r\n` e caracteres de controle) e `validate-plan`.
