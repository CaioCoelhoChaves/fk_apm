# Contributing to fk_apm

Welcome to `fk_apm`! This repository is the central package and skill collection for shared AI agent skills, prompts, and dependencies used across FK projects.

---

## Repository Structure

```text
fk_apm/
├── .github/
│   └── workflows/
│       └── apm-ci.yml             # Automated CI auditing
├── .claude-plugin/
│   └── marketplace.json           # Generated marketplace artifact
├── skills/
│   ├── _template/                 # Starter template for new skills
│   ├── flutter-widgets/           # Widget architecture guidelines
│   ├── flutter-navigation/        # GoRouter navigation standards
│   ├── flutter-testing/           # Unit, widget, and golden testing
│   ├── flutter-accessibility/     # WCAG 2.1 auditing & remediation
│   └── flutter-internationalization/ # ARB & l10n patterns
├── apm.yml                        # APM primary manifest & marketplace catalog
├── apm.lock.yaml                  # APM dependency lockfile
├── LICENSE                        # MIT License
└── README.md                      # Main documentation & usage guide
```

---

## Authoring New Skills

### 1. Directory Structure

Every skill lives in its own subdirectory under `skills/`:

```text
skills/<skill-name>/
├── SKILL.md                       # Required: Main skill instructions and frontmatter
├── references/                    # Optional: In-depth guides, specs, and reference docs
│   └── deep-dive.md
├── scripts/                       # Optional: Executable automation scripts
└── assets/                        # Optional: Templates, schemas, or static files
```

### 2. Frontmatter Specifications

The `SKILL.md` file **must** begin with valid YAML frontmatter:

```yaml
---
name: flutter-example-skill
description: Clear, 1-3 sentence summary of what the skill does and when an agent should invoke it.
allowed-tools: Read,Glob,Grep
# argument-hint: "[param1] [param2]"
---
```

**Rules for frontmatter:**
- `name`: Must use lowercase letters, numbers, and hyphens (`kebab-case`), and **must match the parent directory name**.
- `description`: Human and agent-readable summary under 1,024 characters.
- `allowed-tools`: List the tools the agent is permitted to call for this skill.

### 3. Progressive Disclosure Design

To keep AI context windows efficient:
- Keep the `SKILL.md` body under **500 lines**.
- Focus the main body on immediate rules, checklists, and core conventions.
- Move comprehensive documentation, large code examples, and edge-case catalogs into `references/*.md`.
- Link to references from `SKILL.md` using relative markdown links (e.g., `[references/guidelines.md](references/guidelines.md)`).

---

## Registering in `apm.yml`

Whenever you add or update a skill, register it in the `marketplace.packages` block in `apm.yml`:

```yaml
marketplace:
  packages:
    - name: flutter-example-skill
      description: Concise human-facing description
      source: ./skills/flutter-example-skill
      version: 0.1.0
```

---

## Local Verification Checklist

Before committing changes, run the following verification steps:

```bash
# 1. Check marketplace entries and schemas offline
apm marketplace check --offline

# 2. Dry-run package bundling to check for syntax or layout issues
apm pack --dry-run

# 3. Update the Claude marketplace artifact
apm pack

# 4. Verify lockfile and primitive security
apm audit
```
