---
description: Gerenciamento interativo de CHANGELOG.md e versionamento SemVer (editar textos em Unreleased, reorganizar categorias ou release bump).
argument-hint: "<instrução ou texto de alteração>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

Execute a instrução solicitada no `CHANGELOG.md` do projeto utilizando o utilitário determinístico `skills/semver-changelog/scripts/changelog_manager.py`:

1. Se for uma edição ou substituição de texto: execute `edit --target "..." --replacement "..."`.
2. Se for uma remoção: execute `remove --target "..."`.
3. Se for uma nova entrada: execute `add <category> "..."`.
4. Se for um bump de versão: execute `bump <auto|patch|minor|major>`.

Apresente o resultado ao usuário com o sumário das alterações efetuadas em `## [Unreleased]`.
