# README.md Synchronization & Formatting Standards

In `fk_apm`, `README.md` is the central catalog and primary user documentation. Whenever a new skill or bundle is added, modified, or removed, `README.md` **must** be updated synchronously.

---

## 1. Table Formats

### Available Bundles Table

Located under `## Skill Bundles & Skills` -> `### Available Bundles`:

```markdown
| Bundle | Description | Included Skills | Path |
| :--- | :--- | :--- | :--- |
| **`default`** | Default essential skill bundle | `skill-creator`, `skill-bundle-manager` | [`bundles/default/`](bundles/default/apm.yml) |
| **`flutter`** | Complete Flutter development bundle | `flutter-widgets`, `flutter-navigation`, `flutter-testing`, `flutter-accessibility`, `flutter-internationalization` | [`bundles/flutter/`](bundles/flutter/apm.yml) |
| **`<new-bundle>`** | <Concise description> | `<skill-1>`, `<skill-2>` | [`bundles/<new-bundle>/`](bundles/<new-bundle>/apm.yml) |
```

**Formatting Checklist:**
- Bundle name wrapped in bold backticks: `**`bundle-name`**`
- Path column is a markdown link targeting the bundle's `apm.yml`: `[`bundles/<name>/`](bundles/<name>/apm.yml)`
- Included Skills listed as inline code elements separated by commas.

---

### Individual Skills Table

Located under `## Skill Bundles & Skills` -> `### Individual Skills`:

```markdown
| Skill | Description | Allowed Tools | Location |
| :--- | :--- | :--- | :--- |
| **`skill-creator`** | Create, edit, evaluate, and iteratively optimize AI agent skills with benchmarks | Standard Agent Tools | [`skills/skill-creator/`](skills/skill-creator/SKILL.md) |
| **`<new-skill>`** | <Concise description from frontmatter> | `<Tools or Standard Agent Tools>` | [`skills/<new-skill>/`](skills/<new-skill>/SKILL.md) |
```

**Formatting Checklist:**
- Skill name wrapped in bold backticks: `**`skill-name`**`
- Description matches or summarizes frontmatter description.
- Allowed Tools matches frontmatter `allowed-tools` (or `Standard Agent Tools` if empty/all).
- Location is a markdown link targeting the skill's `SKILL.md`: `[`skills/<name>/`](skills/<name>/SKILL.md)`

---

## 2. Repository Structure Tree

Located under `## Repository Structure`. Keep this tree synchronized when adding new primary skills or bundles:

```text
fk_apm/
├── bundles/
│   ├── default/
│   ├── flutter/
│   └── <new-bundle>/
├── skills/
│   ├── _template/
│   ├── flutter-.../
│   ├── skill-creator/
│   └── <new-skill>/
```

---

## 3. Automated Verification

Before concluding any changes, run the repository verification script:

```bash
python skills/skill-bundle-manager/scripts/verify_skills_and_bundles.py
```

If any table row, relative link, or registration was omitted, the script will output a clear error.
