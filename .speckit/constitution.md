# Constituição de Engenharia (`fk_apm`) — Spec-Kit Constitution

Este documento estabelece os princípios arquiteturais e regras inegociáveis do repositório `fk_apm` (FallKey Agent Package Manager Catalog & Skills Ecosystem). Toda análise técnica (`/fk-technical-analysis`), planejamento (`/fk-new-issue`), implementação (`/fk-develop`) e revisão (`/fk-fix`) deve respeitar esta constituição.

---

## Artigo I — Arquitetura Spec-Driven Development (SDD)

1. **Fonte Única de Verdade Local (`.specs/<issue-key>/`)**:
   - Toda tarefa analisada ou desenvolvida deve manter seus contratos técnicos versionados localmente em `.specs/<issue-key>/`:
     - `spec.md`: Requisitos funcionais, contexto de negócio, histórias/cenários de uso e critérios de aceitação.
     - `plan.md`: Desenho técnico completo nas 5 seções obrigatórias (Diagnóstico e Contexto, Arquitetura da Solução & Desenho Técnico, Checklist de Arquivos Impactados, Estratégia de Testes e Plano Gitflow), alinhado a esta Constituição.
     - `tasks.md`: Checklist atômico, determinístico e sequencial (`- [ ]` / `- [x]`) mapeado diretamente para arquivos e comandos verificáveis.
2. **Validação Determinística Pré-Gate (`validate-plan`)**:
   - Nenhum plano técnico avança para o Consent Gate sem aprovação estática pelo subcomando `validate-plan` do `linear_api.py`, garantindo seções obrigatórias preenchidas, ausência de placeholders vagos e caminhos de arquivos válidos.

---

## Artigo II — Padrão Executive Briefing & Anti-Corrupção de Markdown

1. **Executive Briefing (Chat & Linear)**:
   - Apresentações no chat e comentários de atualização no Linear devem seguir o padrão **Executive Briefing** (10 a 15 linhas objetivas com métricas-chave, decisões centrais, resumo das 5 seções e referência direta aos artefatos em `.specs/<issue-key>/`), evitando despejos massivos de texto que causam truncamento visual ou fadiga de revisão.
2. **File-First & Sanitização Determinística**:
   - É estritamente proibido passar payloads Markdown com crases (`` ` ``), blocos de código ou aspas duplas inline via argumentos de shell (`--description "..."`, `--comment "..."`, `--body "..."`).
   - Todo envio para o Linear (`--description-file`, `--comment-file`) passa obrigatoriamente por `sanitize_markdown_payload` em `linear_api.py` (normalização de `\r\n` para `\n`, remoção de caracteres de controle, fechamento automático de blocos de código órfãos e alinhamento estrutural de tabelas Markdown).

---

## Artigo III — Sincronização Multi-Harness & Primitivas APM

1. **Paridade entre Catálogo Canônico (`skills/`) e Ambiente Local (`.agents/`)**:
   - O repositório `fk_apm` distribui pacotes APM em `skills/<skill-name>/` (incluindo primitivas `.apm/instructions/`, `.apm/prompts/` e `.apm/skills/`) e mantém réplicas ativas em `.agents/skills/` e `.agents/rules/`.
   - Qualquer alteração em uma skill, script ou regra do workflow deve ser sincronizada entre `skills/` e `.agents/`.
2. **Scripts Zero-Dependency & Portabilidade Cross-OS**:
   - Helpers CLI em Python (`linear_api.py`, `changelog_manager.py`) devem utilizar exclusivamente a biblioteca padrão do Python 3 (`urllib`, `json`, `pathlib`, `re`, `argparse`), garantindo execução imediata em Windows (PowerShell), macOS e Linux sem exigir ambientes virtuais externos.

---

## Artigo IV — Governança de Ciclo de Vida (Linear, Gitflow & SemVer)

1. **Consent Gate vs. Execução Autônoma**:
   - Comandos de planejamento e arquitetura (`/fk-new-issue`, `/fk-technical-analysis`) exigem **Consent Gate em 3 Etapas** com Pre-Render Gate visível e resumo embutido na ferramenta nativa de perguntas.
   - Comandos de codificação (`/fk-develop`, `/fk-fix`) executam de forma **100% autônoma (sem Consent Gate)**, consumindo `.specs/<issue-key>/tasks.md`, atualizando o progresso item a item e transicionando o card até `In Review`.
   - O estado `Done` no Linear é **exclusivamente manual pelo desenvolvedor** após o merge do Pull Request.
2. **Qualidade & Rastreabilidade**:
   - Toda modificação em scripts Python deve ser coberta por testes unitários determinísticos (`unittest`) e registrada em `CHANGELOG.md` (`## [Unreleased]`) conforme Keep a Changelog 1.1.0 e Conventional Commits 1.0.0.
