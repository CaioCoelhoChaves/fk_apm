# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Adicionar comando /fk-new-manual-issue e subcomando CLI create-manual-issues para criação rápida e isolada de cards operacionais no Linear em Backlog com tag manual e salvaguardas estritas de zero mutações Git (FAL-59)
- Modernizar linear-workflow com ciclo de vida de Living Specs acoplado a GitHub Draft PRs abertos na etapa de especificação (/speckit-specify) e vinculados ao card no Linear (FAL-58)
- Implementar máquina de estados canônica de 6 estágios (Backlog ➔ Planned ➔ Todo ➔ In Progress ➔ In Review ➔ Done + Canceled) com avanço para Planned no /speckit-plan e para Todo no /speckit-tasks (FAL-58)
- Adicionar subcomandos sync-boards e setup-board em linear_api.py para reconciliação automática de quadros, migração de Technical Analysis para Planned, e suporte a --dry-run (FAL-58)
- Adicionar isolamento operacional via Git Worktrees efêmeros (.worktrees/<CARD-ID>) com validação obrigatória de <CARD-ID> em todos os comandos pós-especificação (FAL-58)
- Adicionar promoção automática de PR Draft para pronto para revisão via gh pr ready ao concluir a implementação em /speckit-implement (FAL-58)
- Adicionar convergência autônoma de code review em /speckit-converge com ciclo de transição In Review ➔ In Progress ➔ correções ➔ In Review e comentários estruturados no PR (FAL-58)
- Persistir especificacao tecnica integral no Linear durante technical analysis e adicionar flags --description e --description-file no helper CLI (FAL-34)
- Integrar perguntas interativas aos Consent Gates de /fk-new-issue, /fk-technical-analysis e /fk-develop com suporte a loopback ("Editar...") e fallback multi-harness (FAL-27)
- Adicionar comando /fk-fix para aplicação autônoma de feedback de code review no PR e Linear (FAL-28)
- Adicionar skill semver-changelog para gerenciamento de CHANGELOG e SemVer 2.0.0 (FAL-23)
- Enforce mandatory card title and description update in /fk-technical-analysis and support --title in linear_api.py (FAL-39)
- Integrate official `github/spec-kit` package (`.specify/` runtime, `specs/<feature>/` pipeline, and 10 `/speckit-*` skills coupled to Linear state transitions), `bootstrap-specify`, `validate-plan`, Executive Briefing Pre-Render Gate, and `sanitize_markdown_payload` into `linear-workflow` and `bundles/default`, replacing legacy `/fk-*` lifecycle commands (FAL-53)

### Changed
- Priorizar leitura da especificacao tecnica completa persistida no /fk-develop garantindo transferencia de contexto sem degradacao (FAL-34)
- Tornar /fk-develop autônomo sem Consent Gate, iniciando imediatamente em In Progress e avançando para In Review ao abrir o PR (FAL-29)
- Padronizar criação de cards em Backlog por padrão no /fk-new-issue e linear-workflow, permitindo Todo apenas como exceção explícita (FAL-33)

### Deprecated

### Removed
- Expurgar completamente referências e menções legadas aos comandos /fk-* em prompts, instruções, documentação e templates (FAL-58)
- Remover aliases curtos (fk-dev, fk-ta e fk-issue) das sub-skills e documentação do linear-workflow (FAL-26)

### Fixed
- Garantir exibição prévia do plano de tarefas/análise no chat antes do Consent Gate (ask_question) com resumo embutido na pergunta e suportar label Feature/sem tag em projetos de tooling/skills (FAL-32)
- Prevent shell backtick and quote corruption in GitHub CLI and Linear Markdown payloads by enforcing UTF-8 file flags (--description-file, --comment-file, --body-file) (FAL-40)

### Security
- Implementar bloqueio estrito na CLI linear_api.py impedindo transições automatizadas para o estado Done, reservando o fechamento exclusivamente para desenvolvedores humanos após merge do PR (FAL-58)
