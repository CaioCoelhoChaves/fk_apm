# fk_apm

**Central APM Repository & Skill Collection for the FK Ecosystem**

[![APM](https://img.shields.io/badge/managed%20by-APM-blue.svg)](https://github.com/microsoft/apm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`fk_apm` is the centralized repository for AI coding agent dependencies, skills, prompts, and standards across FK projects (`fk_projects`, `fk_packages`, `fk_games`, `fk_sites`).

Built upon the [Microsoft Agent Package Manager (APM)](https://github.com/microsoft/apm), this repository provides a single, reproducible source of truth for agent configurations across **GitHub Copilot**, **Claude Code**, **Cursor**, **Windsurf**, **Gemini**, and more.

---

## Table of Contents

- [Overview](#overview)
- [Included Skills](#included-skills)
- [How to Use in Your Projects](#how-to-use-in-your-projects)
  - [1. Install via APM CLI](#1-install-via-apm-cli)
  - [2. Declare in `apm.yml`](#2-declare-in-apmyl)
  - [3. Register as an APM Marketplace](#3-register-as-an-apm-marketplace)
  - [4. Local Development (Sibling Packages)](#4-local-development-sibling-packages)
- [Repository Structure](#repository-structure)
- [Adding New Skills](#adding-new-skills)
- [APM CLI Reference](#apm-cli-reference)
- [Publishing to GitHub](#publishing-to-github)

---

## Overview

When developing across multiple Dart and Flutter packages (such as `fk_booster`), maintaining agent rules, coding guidelines, and skills manually in each repository quickly causes configuration drift.

With `fk_apm`:
1. **Declare Once:** Define your AI skills, prompts, and standards in this repository.
2. **Reproduce Everywhere:** Consumer projects install dependencies via `apm install`, automatically deploying them into client harnesses (`.github/skills/`, `.claude/skills/`, `.cursor/`, etc.).
3. **Lock & Audit:** Reproducible lockfiles (`apm.lock.yaml`) and security scanning via `apm audit`.

---

## Included Skills

| Skill | Description | Allowed Tools | Location |
| :--- | :--- | :--- | :--- |
| **`flutter-widgets`** | Architecture rules for `Page`, `PageSection`, `CoreComponent`, and `PageComponent` using `ViewState` | `Read`, `Glob`, `Grep` | [`skills/flutter-widgets/`](skills/flutter-widgets/SKILL.md) |
| **`flutter-navigation`** | GoRouter & GoRouterBuilder routing, path/query parameters, redirects, and testing | `Read`, `Glob`, `Grep` | [`skills/flutter-navigation/`](skills/flutter-navigation/SKILL.md) |
| **`flutter-testing`** | Unit, widget, and golden file testing standards with `mocktail` and `bloc_test` | `Read`, `Glob`, `Grep` | [`skills/flutter-testing/`](skills/flutter-testing/SKILL.md) |
| **`flutter-accessibility`** | WCAG 2.1 (A, AA, AAA) auditing, semantics, touch target minimums, and contrast | `Read`, `Glob`, `Grep` | [`skills/flutter-accessibility/`](skills/flutter-accessibility/SKILL.md) |
| **`flutter-internationalization`** | Flutter i18n & l10n best practices with ARB single-source-of-truth and RTL support | `Read`, `Glob`, `Grep` | [`skills/flutter-internationalization/`](skills/flutter-internationalization/SKILL.md) |

---

## How to Use in Your Projects

### 1. Install via APM CLI

To install the entire skill collection into an existing project:

```bash
apm install CaioCoelhoChaves/fk_apm
```

To install an individual skill:

```bash
apm install CaioCoelhoChaves/fk_apm --skill flutter-widgets
```

*(Optional)* If your project does not have harness markers configured yet, specify target platforms directly:

```bash
apm install CaioCoelhoChaves/fk_apm --target copilot,claude,cursor
```

### 2. Declare in `apm.yml`

In your consumer project root, declare `fk_apm` in `apm.yml`:

```yaml
name: my_fk_project
version: 1.0.0

# Pin target harnesses (e.g. copilot, claude, cursor)
targets:
  - copilot
  - claude

dependencies:
  apm:
    # Option A: Pull the full skill collection
    - CaioCoelhoChaves/fk_apm

    # Option B: Pull specific skills only
    # - CaioCoelhoChaves/fk_apm/skills/flutter-widgets
    # - CaioCoelhoChaves/fk_apm/skills/flutter-navigation
```

Then resolve and deploy:

```bash
apm install
```

### 3. Register as an APM Marketplace

You can also register `fk_apm` as a named marketplace in your APM CLI environment:

```bash
# Register marketplace
apm marketplace add fk CaioCoelhoChaves/fk_apm

# Browse available skills
apm marketplace browse fk

# Install skills directly from the marketplace
apm install flutter-widgets@fk
```

### 4. Local Development (Sibling Packages)

When working locally across `fk_packages/` without pushing to GitHub first, you can reference `fk_apm` by relative path:

```bash
cd ../fk_booster
apm install ../fk_apm --target claude
```

---

## Repository Structure

```text
fk_apm/
├── .github/
│   └── workflows/
│       └── apm-ci.yml                 # Automated CI workflow
├── .claude-plugin/
│   └── marketplace.json               # Generated Claude plugin marketplace
├── skills/
│   ├── _template/                     # Starter template for new skills
│   ├── flutter-accessibility/         # Accessibility auditing skill & references
│   ├── flutter-internationalization/  # i18n & l10n skill & references
│   ├── flutter-navigation/            # GoRouter skill & references
│   ├── flutter-testing/               # Testing skill & references
│   └── flutter-widgets/               # Flutter widget architecture skill
├── .gitignore                         # Configured for APM caches & build artifacts
├── apm.yml                            # Primary APM manifest & marketplace catalog
├── apm.lock.yaml                      # Resolved lockfile
├── CONTRIBUTING.md                    # Guidelines for authoring skills
├── LICENSE                            # MIT License
└── README.md                          # Documentation
```

---

## Adding New Skills

1. Copy the starter template:
   ```bash
   cp -r skills/_template skills/my-new-skill
   ```
2. Edit `skills/my-new-skill/SKILL.md`:
   - Set `name: my-new-skill` in YAML frontmatter (must match folder name).
   - Add a concise description under 1,024 characters.
   - Keep the main body under 500 lines, delegating details to `references/`.
3. Register the package in `apm.yml` under `marketplace.packages`.
4. Validate and build artifacts:
   ```bash
   apm marketplace check --offline
   apm pack
   apm audit
   ```

For detailed specifications, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## APM CLI Reference

| Command | Purpose |
| :--- | :--- |
| `apm audit` | Scan installed packages and lockfile for drift and integrity |
| `apm pack` | Build distributable bundles and update `marketplace.json` |
| `apm pack --dry-run` | Preview files that would be packaged |
| `apm marketplace check --offline` | Verify all marketplace entries and local sources |
| `apm lock` | Resolve dependencies and update `apm.lock.yaml` |
| `apm doctor` | Run environment diagnostics (git, auth, network) |

---

## Publishing to GitHub

When you are ready to upload this repository to GitHub, run:

```bash
git remote add origin https://github.com/CaioCoelhoChaves/fk_apm.git
git branch -M main
git push -u origin main
```
