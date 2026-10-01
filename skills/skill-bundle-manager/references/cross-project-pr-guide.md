# Cross-Project Contribution Guide: Submitting Skills to `fk_apm` via PR

This guide provides step-by-step instructions for when you or an agent are operating inside an external consumer project (such as `fk_booster`, client apps, or any other repo) and want to contribute a skill to `fk_apm` by opening a GitHub Pull Request.

---

## 1. Context Detection

Before taking action, determine whether you are running inside `fk_apm` or an external project:

```bash
# Check if root is fk_apm
cat apm.yml
```
- If `name: fk_apm` is present at the root, you are already in the local repository. Use Workflow 1 or 2 in `SKILL.md`.
- If `name: fk_apm` is absent (or `apm.yml` belongs to another package), you are in **External Project Mode**.

---

## 2. Locating or Cloning `fk_apm`

To make changes and open a PR, a local copy of `fk_apm` is required:

### Option A: Sibling Directory Check (Fastest)
Look for a sibling `fk_apm` directory:
- `../fk_apm`
- `../../fk_apm`
- `../../fk_packages/fk_apm`

If found, use this directory as `<FK_APM_ROOT>`.

### Option B: Clone via GitHub CLI (`gh`)
If no local clone exists, clone the repository using `gh`:

```bash
gh repo clone CaioCoelhoChaves/fk_apm /path/to/workdir/fk_apm
```
*(In Windows PowerShell, you can clone to a temporary scratch folder or sibling directory).*

---

## 3. Creating a Feature Branch in `fk_apm`

Navigate to the `fk_apm` repository root:

```bash
cd <FK_APM_ROOT>
git checkout main
git pull origin main
git checkout -b feat/add-<skill-name>
```

---

## 4. Transferring & Standardizing the Skill

1. Copy the skill from your current project into `<FK_APM_ROOT>/skills/<skill-name>/`.
2. Inspect `skills/<skill-name>/SKILL.md`:
   - YAML frontmatter:
     ```yaml
     ---
     name: <skill-name>
     description: <Description with trigger phrases>
     allowed-tools: Read,Glob,Grep
     ---
     ```
   - Ensure `name:` matches the directory name `<skill-name>`.
   - Ensure the body is under 500 lines (split into `references/` if necessary).

---

## 5. Catalog, Bundle & Documentation Sync

In `<FK_APM_ROOT>`:

1. **Register in `apm.yml`:**
   Add entry under `marketplace.packages`:
   ```yaml
       - name: <skill-name>
         description: <Description>
         source: ./skills/<skill-name>
         version: 0.1.0
   ```
2. **Bundle Wiring (If Applicable):**
   - If adding to an existing bundle (e.g., `bundles/flutter/apm.yml`), append `- ../../skills/<skill-name>`.
   - Navigate to the bundle folder and run `apm lock`.
3. **Update `README.md`:**
   - Add row in `### Individual Skills` table:
     ```markdown
     | **`<skill-name>`** | <Description> | <Allowed Tools> | [`skills/<skill-name>/`](skills/<skill-name>/SKILL.md) |
     ```
   - If added to a bundle, update `Included Skills` in `### Available Bundles`.

---

## 6. Verification & Build

Run the automated verification suite inside `<FK_APM_ROOT>`:

```bash
python skills/skill-bundle-manager/scripts/verify_skills_and_bundles.py
apm marketplace check --offline
apm pack
apm audit
```

Fix any warnings or missing entries reported by the scripts before proceeding.

---

## 7. Commit, Push & Create Pull Request

With all checks passing:

```bash
git add .
git commit -m "feat(skills): add <skill-name> to fk_apm catalog"
git push -u origin feat/add-<skill-name>
```

Create the Pull Request using GitHub CLI:

```bash
gh pr create \
  --repo CaioCoelhoChaves/fk_apm \
  --title "feat(skills): add <skill-name>" \
  --body "## Summary
Adds the \`<skill-name>\` skill to the fk_apm central repository.

### Verification Checklist
- [x] Frontmatter validated (name matches directory, <500 lines)
- [x] Registered in root \`apm.yml\` under \`marketplace.packages\`
- [x] Added to \`README.md\` Individual Skills table
- [x] \`verify_skills_and_bundles.py\` passed
- [x] \`apm marketplace check --offline\` passed
- [x] \`apm pack\` updated marketplace artifacts
- [x] \`apm audit\` reported 0 drift"
```

The CLI will output the created PR URL. Provide this link to the user!
