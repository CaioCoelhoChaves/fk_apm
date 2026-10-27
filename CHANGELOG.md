# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Persistir especificacao tecnica integral no Linear durante technical analysis e adicionar flags --description e --description-file no helper CLI (FAL-34)
- Integrar perguntas interativas aos Consent Gates de /fk-new-issue, /fk-technical-analysis e /fk-develop com suporte a loopback ("Editar...") e fallback multi-harness (FAL-27)
- Adicionar comando /fk-fix para aplicação autônoma de feedback de code review no PR e Linear (FAL-28)
- Adicionar skill semver-changelog para gerenciamento de CHANGELOG e SemVer 2.0.0 (FAL-23)
- Enforce mandatory card title and description update in /fk-technical-analysis and support --title in linear_api.py (FAL-39)
- Integrar BMAD v6 como dependência oficial via APM, versionar artefatos de configuração _bmad/, criar bundle bmad e registrar 8 skills modulares (FAL-41)

### Changed
- Priorizar leitura da especificacao tecnica completa persistida no /fk-develop garantindo transferencia de contexto sem degradacao (FAL-34)
- Tornar /fk-develop autônomo sem Consent Gate, iniciando imediatamente em In Progress e avançando para In Review ao abrir o PR (FAL-29)
- Padronizar criação de cards em Backlog por padrão no /fk-new-issue e linear-workflow, permitindo Todo apenas como exceção explícita (FAL-33)

### Deprecated

### Removed
- Remover aliases curtos (fk-dev, fk-ta e fk-issue) das sub-skills e documentação do linear-workflow (FAL-26)

### Fixed
- Garantir exibição prévia do plano de tarefas/análise no chat antes do Consent Gate (ask_question) com resumo embutido na pergunta e suportar label Feature/sem tag em projetos de tooling/skills (FAL-32)
- Prevent shell backtick and quote corruption in GitHub CLI and Linear Markdown payloads by enforcing UTF-8 file flags (--description-file, --comment-file, --body-file) (FAL-40)

### Security
