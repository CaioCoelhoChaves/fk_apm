#!/usr/bin/env python3
"""
Integrity verification script for fk_apm repository.
Validates consistency across skills, bundles, root apm.yml, and README.md.
"""

import sys
import re
from pathlib import Path

def parse_frontmatter(content: str) -> dict:
    match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not match:
        return {}
    frontmatter_text = match.group(1)
    data = {}
    for line in frontmatter_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return data

def main():
    root = Path(__file__).resolve().parent.parent.parent.parent
    apm_yml_path = root / "apm.yml"
    readme_path = root / "README.md"
    skills_dir = root / "skills"
    bundles_dir = root / "bundles"

    if not apm_yml_path.exists() or not readme_path.exists():
        print(f"[ERROR] Could not find apm.yml or README.md at {root}")
        sys.exit(1)

    errors = []
    warnings = []

    readme_content = readme_path.read_text(encoding="utf-8")
    apm_yml_content = apm_yml_path.read_text(encoding="utf-8")

    # 1. Check all skills
    skill_folders = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))]
    print(f"[*] Found {len(skill_folders)} skill(s) in {skills_dir.name}/")

    for s_dir in sorted(skill_folders, key=lambda x: x.name):
        skill_name = s_dir.name
        skill_file = s_dir / "SKILL.md"

        if not skill_file.exists():
            errors.append(f"Skill '{skill_name}': Missing SKILL.md")
            continue

        content = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        if not fm:
            errors.append(f"Skill '{skill_name}': Invalid or missing YAML frontmatter in SKILL.md")
        else:
            if "name" not in fm:
                errors.append(f"Skill '{skill_name}': Frontmatter missing 'name'")
            elif fm["name"] != skill_name:
                errors.append(f"Skill '{skill_name}': Frontmatter name '{fm['name']}' does not match directory '{skill_name}'")

            if "description" not in fm:
                errors.append(f"Skill '{skill_name}': Frontmatter missing 'description'")

        # Check registration in root apm.yml
        expected_src = f"./skills/{skill_name}"
        if expected_src not in apm_yml_content:
            errors.append(f"Skill '{skill_name}': Not registered under marketplace.packages in apm.yml (expected source: {expected_src})")

        # Check entry in README.md
        if f"`{skill_name}`" not in readme_content and f"**{skill_name}**" not in readme_content:
            errors.append(f"Skill '{skill_name}': Missing from README.md tables")

    # 2. Check all bundles
    bundle_folders = [d for d in bundles_dir.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))]
    print(f"[*] Found {len(bundle_folders)} bundle(s) in {bundles_dir.name}/")

    for b_dir in sorted(bundle_folders, key=lambda x: x.name):
        bundle_name = b_dir.name
        bundle_apm_yml = b_dir / "apm.yml"
        bundle_lock = b_dir / "apm.lock.yaml"

        if not bundle_apm_yml.exists():
            errors.append(f"Bundle '{bundle_name}': Missing apm.yml")
            continue

        if not bundle_lock.exists():
            errors.append(f"Bundle '{bundle_name}': Missing apm.lock.yaml (run 'apm lock' inside bundles/{bundle_name})")

        # Check bundle dependencies resolution
        bundle_text = bundle_apm_yml.read_text(encoding="utf-8")
        for line in bundle_text.splitlines():
            line = line.strip()
            if line.startswith("- ../../skills/"):
                rel_path = line.lstrip("- ").strip()
                dep_target = (b_dir / rel_path).resolve()
                if not dep_target.exists():
                    errors.append(f"Bundle '{bundle_name}': Dependency target '{rel_path}' does not exist on disk")

        # Check registration in root apm.yml
        expected_src = f"./bundles/{bundle_name}"
        if expected_src not in apm_yml_content:
            errors.append(f"Bundle '{bundle_name}': Not registered under marketplace.packages in apm.yml (expected source: {expected_src})")

        # Check entry in README.md
        if f"`{bundle_name}`" not in readme_content and f"**{bundle_name}**" not in readme_content:
            errors.append(f"Bundle '{bundle_name}': Missing from README.md tables")

    # Summary
    print("\n--- Verification Summary ---")
    if warnings:
        for w in warnings:
            print(f"[!] WARNING: {w}")

    if errors:
        print(f"[X] FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("[+] SUCCESS: All skills, bundles, apm.yml, and README.md are fully synchronized!")
        sys.exit(0)

if __name__ == "__main__":
    main()
