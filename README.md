# fk_apm

**Central APM Repository & Skill Collection for the FK Ecosystem**

[![APM](https://img.shields.io/badge/managed%20by-APM-blue.svg)](https://github.com/microsoft/apm)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`fk_apm` is the centralized repository for AI coding agent dependencies, skills, prompts, and standards across FK projects (`fk_projects`, `fk_packages`, `fk_games`, `fk_sites`).

Built upon the [Microsoft Agent Package Manager (APM)](https://github.com/microsoft/apm), this repository provides a single, reproducible source of truth for agent configurations across **GitHub Copilot**, **Claude Code**, **Cursor**, **Windsurf**, **Gemini**, and more.

---

## Table of Contents

- [Overview](#overview)
- [Skill Bundles & Skills](#skill-bundles--skills)
- [How to Use in Your Projects](#how-to-use-in-your-projects)
  - [1. Install the `flutter` Bundle](#1-install-the-flutter-bundle)
  - [2. Install Individual Skills](#2-install-individual-skills)
  - [3. Declare in Consumer `apm.yml`](#3-declare-in-consumer-apmyl)
  - [4. Install via APM Marketplace](#4-install-via-apm-marketplace)
  - [5. Local Development (Sibling Packages)](#5-local-development-sibling-packages)
- [Repository Structure](#repository-structure)
- [Adding New Skills or Bundles](#adding-new-skills-or-bundles)
- [APM CLI Reference](#apm-cli-reference)
- [Publishing to GitHub](#publishing-to-github)

---

## Overview

When developing across multiple Dart and Flutter packages (such as `fk_booster`), maintaining agent rules, coding guidelines, and skills manually in each repository quickly causes configuration drift.

With `fk_apm`:
1. **Declare Once:** Define your AI skills, prompts, and bundles in this repository.
2. **Reproduce Everywhere:** Consumer projects install bundles or skills via `apm install`, automatically deploying them into client harnesses (`.github/skills/`, `.claude/skills/`, `.cursor/`, etc.).
3. **Lock & Audit:** Reproducible lockfiles (`apm.lock.yaml`) and security scanning via `apm audit`.

---

## Skill Bundles & Skills

### Available Bundles

| Bundle | Description | Included Skills | Path |
| :--- | :--- | :--- | :--- |
| **`flutter`** | Complete Flutter development bundle | `flutter-widgets`, `flutter-navigation`, `flutter-testing`, `flutter-accessibility`, `flutter-internationalization` | [`bundles/flutter/`](bundles/flutter/apm.yml) |

### Individual Skills

| Skill | Description | Allowed Tools | Location |
| :--- | :--- | :--- | :--- |
| **`flutter-widgets`** | Architecture rules for `Page`, `PageSection`, `CoreComponent`, and `PageComponent` using `ViewState` | `Read`, `Glob`, `Grep` | [`skills/flutter-widgets/`](skills/flutter-widgets/SKILL.md) |
| **`flutter-navigation`** | GoRouter & GoRouterBuilder routing, path/query parameters, redirects, and testing | `Read`, `Glob`, `Grep` | [`skills/flutter-navigation/`](skills/flutter-navigation/SKILL.md) |
| **`flutter-testing`** | Unit, widget, and golden file testing standards with `mocktail` and `bloc_test` | `Read`, `Glob`, `Grep` | [`skills/flutter-testing/`](skills/flutter-testing/SKILL.md) |
| **`flutter-accessibility`** | WCAG 2.1 (A, AA, AAA) auditing, semantics, touch target minimums, and contrast | `Read`, `Glob`, `Grep` | [`skills/flutter-accessibility/`](skills/flutter-accessibility/SKILL.md) |
| **`flutter-internationalization`** | Flutter i18n & l10n best practices with ARB single-source-of-truth and RTL support | `Read`, `Glob`, `Grep` | [`skills/flutter-internationalization/`](skills/flutter-internationalization/SKILL.md) |

---

## Adding Bundles & Skills to Your Projects

This step-by-step guide explains how to add the `flutter` bundle (or individual skills) to any of your third-party or sibling projects (`fk_booster`, client apps, games, packages).

---

### Step 1: Initialize APM in Your Project (If Not Already Done)

Navigate to your target project root and run:

```bash
cd /path/to/your/project
apm init
```
This scaffolds an `apm.yml` manifest in your project.

---

### Step 2: Add the Bundle to Your Project

You can add the bundle either **automatically via the CLI** or **manually inside your project's `apm.yml`**:

#### Method A: Automatic Addition via CLI (Recommended)

Running `apm install` with the bundle repository path will automatically resolve the skills, deploy them into your agent folders, and **record the dependency inside your project's `apm.yml` and `apm.lock.yaml`**:

```bash
# Install the Flutter bundle from GitHub:
apm install CaioCoelhoChaves/fk_apm/bundles/flutter

# Or install from a local sibling directory (during local development):
apm install ../fk_apm/bundles/flutter
```

> [!TIP]
> If your project does not have harness markers configured yet (e.g. `CLAUDE.md`, `.github/copilot-instructions.md`, or `.cursor/`), tell APM which AI assistants to deploy to using `--target`:
> ```bash
> apm install CaioCoelhoChaves/fk_apm/bundles/flutter --target copilot,claude,cursor
> ```

---

#### Method B: Manual Declaration in your `apm.yml`

Open your project's `apm.yml` and declare the bundle under the `dependencies.apm` list:

```yaml
name: my_app
version: 1.0.0

# 1. Specify which AI agent platforms you want APM to configure:
targets:
  - copilot      # Deploys skills to .github/skills/
  - claude       # Deploys skills to .claude/skills/
  - cursor       # Deploys skills to .cursor/skills/ (or .agents/skills/)

# 2. Declare APM dependencies:
dependencies:
  apm:
    # Install the full Flutter bundle (widgets, navigation, testing, a11y, i18n):
    - CaioCoelhoChaves/fk_apm/bundles/flutter

    # Pin to a specific version or git branch:
    # - CaioCoelhoChaves/fk_apm/bundles/flutter#v0.1.0
    # - CaioCoelhoChaves/fk_apm/bundles/flutter#main

    # Or reference a local sibling path during monorepo / offline work:
    # - ../fk_apm/bundles/flutter

    # Or install a single individual skill instead of the full bundle:
    # - CaioCoelhoChaves/fk_apm/skills/flutter-widgets
  mcp: []
```

Once declared in `apm.yml`, run:

```bash
apm install
```

**What APM does during install:**
1. Resolves the `flutter` bundle and all 5 transitive skills: `flutter-widgets`, `flutter-navigation`, `flutter-testing`, `flutter-accessibility`, and `flutter-internationalization`.
2. Deploys the skills directly into your project's target directories (e.g. `.claude/skills/`, `.github/skills/`).
3. Generates or updates `apm.lock.yaml`, pinning the exact content hash and commit SHA for reproducible agent environments.

---

### Step 3: Verify the Installed Skills

Verify the installed skills in your project:

```bash
# Check lockfile consistency and drift:
apm audit

# Verify deployed files in your client harness:
ls .claude/skills/      # for Claude Code
ls .github/skills/      # for GitHub Copilot
ls .cursor/skills/      # for Cursor
```

---

### Step 4: Updating the Bundle in the Future

When you add new skills or make updates in `fk_apm`, update your consumer project by running:

```bash
apm update
```

---

### Alternative: Install via APM Marketplace

You can also register `fk_apm` as a named marketplace in your local APM environment:

```bash
# Register marketplace
apm marketplace add fk CaioCoelhoChaves/fk_apm

# Browse available packages and bundles
apm marketplace browse fk

# Install the flutter bundle from the marketplace
apm install flutter@fk

# Or install an individual skill
apm install flutter-widgets@fk
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
├── bundles/
│   └── flutter/                       # 'flutter' bundle manifest & lockfile
│       ├── apm.yml
│       └── apm.lock.yaml
├── skills/
│   ├── _template/                     # Starter template for new skills
│   ├── flutter-accessibility/         # Accessibility auditing skill & references
│   ├── flutter-internationalization/  # i18n & l10n skill & references
│   ├── flutter-navigation/            # GoRouter skill & references
│   ├── flutter-testing/               # Testing skill & references
│   └── flutter-widgets/               # Flutter widget architecture skill
├── .gitignore                         # Configured for APM caches & build artifacts
├── apm.yml                            # Primary APM manifest & marketplace catalog
├── apm.lock.yaml                      # Root lockfile
├── CONTRIBUTING.md                    # Guidelines for authoring skills and bundles
├── LICENSE                            # MIT License
└── README.md                          # Documentation
```

---

## Adding New Skills or Bundles

### Adding a Skill
1. Copy the starter template:
   ```bash
   cp -r skills/_template skills/my-new-skill
   ```
2. Edit `skills/my-new-skill/SKILL.md` (ensure `name:` matches folder name).
3. If applicable, add it to a bundle in `bundles/<bundle-name>/apm.yml` or create a new bundle.
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
