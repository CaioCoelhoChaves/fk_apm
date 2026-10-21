# Multi-Harness Architecture: SemVer & Changelog

This reference documents how `semver-changelog` commands and triggers are deployed and consumed across different AI coding harnesses (Google Antigravity, OpenCode, Claude Code, Cursor, Copilot).

---

## 1. Harness Distribution

| Harness | Trigger Mechanism | APM Integration Point | Location |
| :--- | :--- | :--- | :--- |
| **Google Antigravity** | Slash commands & sub-skills | Sub-skill promotion to `.agents/skills/` | `.agents/skills/fk-semver-owner/SKILL.md`<br>`.agents/skills/semver/SKILL.md` |
| **OpenCode** | Standard skill execution | Skill discovery via APM catalog | `skills/semver-changelog/SKILL.md` |
| **Claude Code** | Slash commands & prompt files | `.claude/commands/` | `.claude/commands/fk-semver-owner.md`<br>`.claude/commands/semver.md` |
| **Cursor** | Custom commands & MDC rules | `.cursor/commands/` & `.cursor/rules/` | `.cursor/commands/fk-semver-owner.md` |
| **GitHub Copilot** | Prompt files & instructions | `.github/prompts/` & `.github/instructions/` | `.github/prompts/fk-semver-owner.prompt.md` |

---

## 2. Supported Commands & Aliases

| Canonical Command | Quick Alias | Description | Example Usage |
| :--- | :--- | :--- | :--- |
| `/fk-semver-owner` | `/semver` | Interactively modify, adjust wording, or bump changelog entries | `/fk-semver-owner Quero mudar o texto da mudança X e da Y para... Fim /` |
| `semver-changelog` | `changelog` | Autonomous changelog maintenance during feature/fix development | Triggered automatically when developing cards |

---

## 3. Delimiter Syntax Tolerance

Users may pass custom instructions wrapped in delimiter phrasing:
```text
/fk-semver-owner Quero mudar o texto da mudança X e da Y para... Fim /
```

The agent strips prefix `/fk-semver-owner` and suffix `Fim /` (or similar closing delimiters), extracts the actionable intent, applies updates via `changelog_manager.py edit` or `changelog_manager.py remove`, and presents the revised `## [Unreleased]` diff to the user.
