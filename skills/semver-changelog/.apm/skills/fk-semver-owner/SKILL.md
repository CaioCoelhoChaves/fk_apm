---
name: fk-semver-owner
description: Interface interativa para gerenciar o CHANGELOG.md e versionamento SemVer (editar textos em Unreleased, reorganizar categorias, ou disparar release bump).
allowed-tools: Read,Glob,Grep,Bash
---

# /fk-semver-owner: Gerenciamento Interativo de CHANGELOG & SemVer

Este comando permite ao desenvolvedor intervir diretamente na seção `## [Unreleased]` do `CHANGELOG.md` e conduzir ações de release bump de forma interativa.

---

## Modos de Operação

### 1. Customização Textual de Entradas
Quando o usuário solicitar alteração de textos (ex: `/fk-semver-owner Quero mudar o texto da mudança X e da Y para... Fim /`):
1. Extraia o texto-alvo e o novo texto solicitado.
2. Utilize o script determinístico:
   ```bash
   python skills/semver-changelog/scripts/changelog_manager.py edit --target "<texto-antigo>" --replacement "<texto-novo>"
   ```
3. Apresente ao desenvolvedor o diff ou o bloco atualizado de `## [Unreleased]`.

### 2. Remoção de Entradas
Para remover itens obsoletos ou duplicados em `## [Unreleased]`:
```bash
python skills/semver-changelog/scripts/changelog_manager.py remove --target "<texto-a-remover>"
```

### 3. Release Bump
Para fechar a versão atual e gerar a nova tag SemVer:
```bash
python skills/semver-changelog/scripts/changelog_manager.py bump [auto|patch|minor|major|<versao>]
```

Consulte a skill base para especificações completas: [semver-changelog](../../SKILL.md).
