#!/usr/bin/env python3
"""
changelog_manager.py - Deterministic Keep a Changelog 1.1.0 & SemVer 2.0.0 manager.

Provides robust operations to:
- Initialize CHANGELOG.md (zero-config bootstrap)
- Add entries under [Unreleased] mapped to Keep a Changelog categories
- Edit or remove entries in [Unreleased]
- Perform SemVer release bumps (auto, patch, minor, major, or explicit)
- Inspect status and detect project version across package ecosystems
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

VALID_CATEGORIES = [
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
]

CONVENTIONAL_MAP = {
    "feat": "Added",
    "add": "Added",
    "fix": "Fixed",
    "bugfix": "Fixed",
    "perf": "Changed",
    "refactor": "Changed",
    "style": "Changed",
    "docs": "Changed",
    "test": "Changed",
    "build": "Changed",
    "ci": "Changed",
    "chore": "Changed",
    "deprecate": "Deprecated",
    "deprecated": "Deprecated",
    "remove": "Removed",
    "removed": "Removed",
    "sec": "Security",
    "security": "Security",
}

HEADER_TEMPLATE = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security
"""

def normalize_category(cat: str) -> str:
    """Normalize user or conventional commit string to standard Keep a Changelog category."""
    cleaned = cat.strip().lower()
    if cleaned in CONVENTIONAL_MAP:
        return CONVENTIONAL_MAP[cleaned]
    for valid in VALID_CATEGORIES:
        if cleaned == valid.lower():
            return valid
    raise ValueError(
        f"Unknown category '{cat}'. Expected one of: {', '.join(VALID_CATEGORIES)} "
        f"or conventional commit types (feat, fix, refactor, perf, docs, chore, etc.)"
    )

def detect_project_version(start_dir: Optional[Path] = None) -> Optional[str]:
    """Detect current project version from common package manifests."""
    base = Path(start_dir or Path.cwd()).resolve()
    for current in [base, *base.parents]:
        # pubspec.yaml
        pubspec = current / "pubspec.yaml"
        if pubspec.is_file():
            content = pubspec.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^version:\s*([0-9]+\.[0-9]+\.[0-9]+)", content, re.MULTILINE)
            if m:
                return m.group(1)

        # package.json
        pkg_json = current / "package.json"
        if pkg_json.is_file():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if "version" in data and isinstance(data["version"], str):
                    m = re.match(r"^([0-9]+\.[0-9]+\.[0-9]+)", data["version"])
                    if m:
                        return m.group(1)
            except Exception:
                pass

        # pom.xml
        pom = current / "pom.xml"
        if pom.is_file():
            content = pom.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"<version>([0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?)</version>", content)
            if m:
                return m.group(1).split("-")[0]

        # pyproject.toml
        pyproject = current / "pyproject.toml"
        if pyproject.is_file():
            content = pyproject.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'version\s*=\s*["\']([0-9]+\.[0-9]+\.[0-9]+)["\']', content)
            if m:
                return m.group(1)

        # Cargo.toml
        cargo = current / "Cargo.toml"
        if cargo.is_file():
            content = cargo.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'version\s*=\s*["\']([0-9]+\.[0-9]+\.[0-9]+)["\']', content)
            if m:
                return m.group(1)

    return None

def detect_git_repo_url(changelog_path: Path) -> Optional[str]:
    """Detect remote origin URL to construct release comparison links."""
    try:
        res = subprocess.run(
            ["git", "-C", str(changelog_path.parent), "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=False,
        )
        url = res.stdout.strip()
        if not url:
            return None
        # Convert SSH to HTTPS
        if url.startswith("git@github.com:"):
            url = "https://github.com/" + url[len("git@github.com:"):]
        if url.endswith(".git"):
            url = url[:-4]
        return url
    except Exception:
        return None

def find_changelog(path_str: Optional[str] = None) -> Path:
    """Resolve CHANGELOG.md file path."""
    if path_str:
        return Path(path_str).resolve()
    cwd = Path.cwd()
    for candidate in [cwd / "CHANGELOG.md", cwd / "changelog.md"]:
        if candidate.is_file():
            return candidate.resolve()
    return (cwd / "CHANGELOG.md").resolve()

def init_changelog(path: Optional[Path] = None, initial_version: Optional[str] = None) -> Dict:
    """Initialize CHANGELOG.md if absent, or return status if present."""
    target = path or find_changelog()
    if target.is_file():
        return {
            "success": True,
            "created": False,
            "path": str(target),
            "message": f"CHANGELOG.md already exists at {target}",
        }

    detected_ver = initial_version or detect_project_version(target.parent)
    today = datetime.date.today().isoformat()

    content = HEADER_TEMPLATE.rstrip() + "\n"

    if detected_ver:
        content += f"\n## [{detected_ver}] - {today}\n\n### Added\n- Initial release.\n"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

    return {
        "success": True,
        "created": True,
        "path": str(target),
        "initial_version": detected_ver,
        "message": f"Created CHANGELOG.md adhering to Keep a Changelog 1.1.0 & SemVer 2.0.0",
    }

class ChangelogParser:
    """Robust Markdown parser specifically for Keep a Changelog structured documents."""

    def __init__(self, content: str):
        self.raw_content = content
        self.lines = content.splitlines()

    def find_unreleased_bounds(self) -> Tuple[int, int]:
        """Find start and end line indices of ## [Unreleased] section."""
        start = -1
        for i, line in enumerate(self.lines):
            if re.match(r"^##\s+\[Unreleased\]", line, re.IGNORECASE):
                start = i
                break

        if start == -1:
            raise ValueError("Could not find '## [Unreleased]' section in CHANGELOG.md")

        end = len(self.lines)
        for i in range(start + 1, len(self.lines)):
            # Next version header or link definitions block at bottom
            if re.match(r"^##\s+\[[0-9a-zA-Z._-]+\]", self.lines[i]) or re.match(r"^\[.*?\]:\s*http", self.lines[i]):
                end = i
                break

        return start, end

    def parse_unreleased_entries(self) -> Dict[str, List[str]]:
        """Parse all bullet points grouped by category under ## [Unreleased]."""
        start, end = self.find_unreleased_bounds()
        entries: Dict[str, List[str]] = {cat: [] for cat in VALID_CATEGORIES}

        current_cat: Optional[str] = None
        for i in range(start + 1, end):
            line = self.lines[i]
            cat_match = re.match(r"^###\s+([A-Za-z]+)", line)
            if cat_match:
                name = cat_match.group(1).capitalize()
                if name in VALID_CATEGORIES:
                    current_cat = name
                else:
                    current_cat = None
                continue

            bullet_match = re.match(r"^[-*]\s+(.*)", line)
            if bullet_match and current_cat:
                entries[current_cat].append(bullet_match.group(1).strip())

        return entries

    def get_all_versions(self) -> List[str]:
        """Extract all released versions in chronological order from top to bottom."""
        versions = []
        for line in self.lines:
            m = re.match(r"^##\s+\[([0-9]+\.[0-9]+\.[0-9]+[^\]]*)\]", line)
            if m and m.group(1).lower() != "unreleased":
                versions.append(m.group(1))
        return versions

def add_entry(
    changelog_path: Path,
    category: str,
    entry_text: str,
    issue: Optional[str] = None,
) -> Dict:
    """Add a bullet point under the given category in ## [Unreleased]."""
    if not changelog_path.is_file():
        init_changelog(changelog_path)

    normalized_cat = normalize_category(category)
    content = changelog_path.read_text(encoding="utf-8")
    parser = ChangelogParser(content)
    lines = list(parser.lines)

    # Format text
    text = entry_text.strip()
    if text.startswith(("- ", "* ")):
        text = text[2:].strip()

    if issue:
        issue_tag = issue.strip()
        if not issue_tag.startswith("(") and not issue_tag.endswith(")"):
            issue_tag = f"({issue_tag})"
        if issue_tag not in text:
            text = f"{text} {issue_tag}"

    new_bullet = f"- {text}"

    unreleased_start, unreleased_end = parser.find_unreleased_bounds()
    unreleased_lines = lines[unreleased_start:unreleased_end]

    # Find the target category header within unreleased lines
    cat_header = f"### {normalized_cat}"
    cat_line_offset = -1
    for idx, l in enumerate(unreleased_lines):
        if re.match(rf"^###\s+{normalized_cat}\b", l, re.IGNORECASE):
            cat_line_offset = idx
            break

    if cat_line_offset != -1:
        # Category exists. Find where to insert (right after last item or right after category)
        insert_offset = cat_line_offset + 1
        abs_insert_idx = unreleased_start + insert_offset

        # Scan forward to see existing items and avoid exact duplicates
        curr = abs_insert_idx
        while curr < len(lines):
            curr_line = lines[curr].strip()
            if curr_line == new_bullet:
                return {
                    "success": True,
                    "already_existed": True,
                    "category": normalized_cat,
                    "entry": text,
                    "message": "Entry already present in changelog",
                }
            if curr_line.startswith("### ") or curr_line.startswith("## ") or (curr_line.startswith("[") and "]:" in curr_line):
                break
            if curr_line.startswith("- ") or curr_line.startswith("* "):
                abs_insert_idx = curr + 1
            curr += 1

        lines.insert(abs_insert_idx, new_bullet)
    else:
        # Category does not exist yet under Unreleased. Insert in standard order.
        target_pos = len(VALID_CATEGORIES)
        for i, c in enumerate(VALID_CATEGORIES):
            if c == normalized_cat:
                target_pos = i
                break

        # Find position relative to other categories
        insert_at = unreleased_start + 1
        for idx in range(unreleased_start + 1, unreleased_end):
            m = re.match(r"^###\s+([A-Za-z]+)", lines[idx])
            if m:
                cat_name = m.group(1).capitalize()
                if cat_name in VALID_CATEGORIES:
                    pos = VALID_CATEGORIES.index(cat_name)
                    if pos > target_pos:
                        insert_at = idx
                        break
                    else:
                        insert_at = idx + 1
            elif lines[idx].strip().startswith(("-", "*")):
                insert_at = idx + 1

        new_block = [f"\n{cat_header}", new_bullet]
        lines[insert_at:insert_at] = new_block

    # Save
    new_content = "\n".join(lines).rstrip() + "\n"
    changelog_path.write_text(new_content, encoding="utf-8")

    return {
        "success": True,
        "already_existed": False,
        "category": normalized_cat,
        "entry": text,
        "path": str(changelog_path),
        "message": f"Successfully added entry to [{normalized_cat}] in CHANGELOG.md",
    }

def edit_entry(
    changelog_path: Path,
    target: str,
    replacement: str,
) -> Dict:
    """Edit or replace an entry within the [Unreleased] section."""
    if not changelog_path.is_file():
        raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")
    parser = ChangelogParser(content)
    lines = list(parser.lines)
    unreleased_start, unreleased_end = parser.find_unreleased_bounds()

    target_clean = target.strip()
    if target_clean.startswith(("- ", "* ")):
        target_clean = target_clean[2:].strip()

    rep_clean = replacement.strip()
    if not rep_clean.startswith(("- ", "* ")):
        rep_clean = f"- {rep_clean}"

    found = False
    for i in range(unreleased_start + 1, unreleased_end):
        line = lines[i].strip()
        if line.startswith(("- ", "* ")):
            bullet_body = line[2:].strip()
            if target_clean.lower() in bullet_body.lower() or target_clean == bullet_body:
                lines[i] = rep_clean
                found = True
                break

    if not found:
        return {
            "success": False,
            "modified": False,
            "message": f"Target entry '{target}' not found in ## [Unreleased]",
        }

    new_content = "\n".join(lines).rstrip() + "\n"
    changelog_path.write_text(new_content, encoding="utf-8")

    return {
        "success": True,
        "modified": True,
        "target": target,
        "replacement": rep_clean,
        "message": "Entry successfully updated in ## [Unreleased]",
    }

def remove_entry(
    changelog_path: Path,
    target: str,
) -> Dict:
    """Remove a bullet point from the [Unreleased] section."""
    if not changelog_path.is_file():
        raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")
    parser = ChangelogParser(content)
    lines = list(parser.lines)
    unreleased_start, unreleased_end = parser.find_unreleased_bounds()

    target_clean = target.strip()
    if target_clean.startswith(("- ", "* ")):
        target_clean = target_clean[2:].strip()

    removed_line = None
    remove_idx = -1
    for i in range(unreleased_start + 1, unreleased_end):
        line = lines[i].strip()
        if line.startswith(("- ", "* ")):
            bullet_body = line[2:].strip()
            if target_clean.lower() in bullet_body.lower() or target_clean == bullet_body:
                removed_line = lines[i]
                remove_idx = i
                break

    if remove_idx == -1:
        return {
            "success": False,
            "removed": False,
            "message": f"Target entry '{target}' not found in ## [Unreleased]",
        }

    lines.pop(remove_idx)
    new_content = "\n".join(lines).rstrip() + "\n"
    changelog_path.write_text(new_content, encoding="utf-8")

    return {
        "success": True,
        "removed": True,
        "entry": removed_line,
        "message": "Entry successfully removed from ## [Unreleased]",
    }

def calculate_next_version(
    current_version: str,
    bump_type: str,
    unreleased_entries: Dict[str, List[str]],
) -> str:
    """Compute the next SemVer 2.0.0 string based on type or unreleased changes."""
    # Match semver X.Y.Z
    m = re.match(r"^([0-9]+)\.([0-9]+)\.([0-9]+)", current_version)
    if not m:
        major, minor, patch = 0, 1, 0
    else:
        major, minor, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))

    b_type = bump_type.lower()
    if b_type == "auto":
        # Check breaking changes in any bullet or Removed category
        has_breaking = False
        for cat, bullets in unreleased_entries.items():
            if cat == "Removed" and bullets:
                has_breaking = True
            for b in bullets:
                if "BREAKING CHANGE" in b or "breaking change" in b.lower() or "!:" in b:
                    has_breaking = True
                    break

        if has_breaking:
            if major >= 1:
                b_type = "major"
            else:
                b_type = "minor"
        elif unreleased_entries.get("Added"):
            b_type = "minor"
        else:
            b_type = "patch"

    if b_type == "major":
        return f"{major + 1}.0.0"
    elif b_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif b_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        # Check if valid semver was passed explicitly
        if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+", bump_type):
            return bump_type
        raise ValueError(f"Invalid bump type '{bump_type}'. Expected auto, patch, minor, major, or X.Y.Z")

def bump_version(
    changelog_path: Path,
    bump_type: str = "auto",
    explicit_date: Optional[str] = None,
) -> Dict:
    """Release bump: converts ## [Unreleased] to ## [X.Y.Z] - YYYY-MM-DD and resets [Unreleased]."""
    if not changelog_path.is_file():
        raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")

    content = changelog_path.read_text(encoding="utf-8")
    parser = ChangelogParser(content)
    unreleased = parser.parse_unreleased_entries()

    total_unreleased = sum(len(bullets) for bullets in unreleased.values())
    if total_unreleased == 0:
        raise ValueError("Cannot perform release bump: ## [Unreleased] section has no entries.")

    released_versions = parser.get_all_versions()
    current_ver = released_versions[0] if released_versions else (detect_project_version(changelog_path.parent) or "0.1.0")

    next_ver = calculate_next_version(current_ver, bump_type, unreleased)
    release_date = explicit_date or datetime.date.today().isoformat()

    # Build new version section
    new_release_lines = [f"## [{next_ver}] - {release_date}"]
    for cat in VALID_CATEGORIES:
        bullets = unreleased.get(cat, [])
        if bullets:
            new_release_lines.append(f"\n### {cat}")
            for b in bullets:
                new_release_lines.append(f"- {b}")

    # Build new unreleased skeleton
    unreleased_skeleton = [
        "## [Unreleased]",
        "",
        "### Added",
        "",
        "### Changed",
        "",
        "### Deprecated",
        "",
        "### Removed",
        "",
        "### Fixed",
        "",
        "### Security",
        "",
    ]

    unreleased_start, unreleased_end = parser.find_unreleased_bounds()

    # Reassemble document
    prefix = parser.lines[:unreleased_start]
    suffix = parser.lines[unreleased_end:]

    # Handle link references at the bottom if present
    repo_url = detect_git_repo_url(changelog_path)
    updated_suffix: List[str] = []
    link_definitions: Dict[str, str] = {}
    is_link_section = False

    for line in suffix:
        m = re.match(r"^\[(.*?)\]:\s*(http.*)", line)
        if m:
            is_link_section = True
            link_definitions[m.group(1)] = m.group(2)
        else:
            if not is_link_section:
                updated_suffix.append(line)

    if link_definitions and repo_url:
        # Update Unreleased link and add next_ver link
        link_definitions["Unreleased"] = f"{repo_url}/compare/v{next_ver}...HEAD"
        if released_versions:
            prev_ver = released_versions[0]
            link_definitions[next_ver] = f"{repo_url}/compare/v{prev_ver}...v{next_ver}"
        else:
            link_definitions[next_ver] = f"{repo_url}/releases/tag/v{next_ver}"

        # Append link definitions to bottom
        updated_suffix.append("")
        for tag, url in link_definitions.items():
            updated_suffix.append(f"[{tag}]: {url}")

    final_lines = prefix + unreleased_skeleton + new_release_lines + [""] + updated_suffix
    final_content = "\n".join(final_lines)
    # Normalize multiple blank lines
    final_content = re.sub(r"\n{3,}", "\n\n", final_content).rstrip() + "\n"

    changelog_path.write_text(final_content, encoding="utf-8")

    return {
        "success": True,
        "previous_version": current_ver,
        "new_version": next_ver,
        "release_date": release_date,
        "items_released": total_unreleased,
        "path": str(changelog_path),
        "message": f"Successfully bumped version to {next_ver} ({release_date})",
    }

def get_status(changelog_path: Path) -> Dict:
    """Inspect CHANGELOG.md and return current status, unreleased counts, and proposed versions."""
    if not changelog_path.is_file():
        return {
            "success": False,
            "exists": False,
            "path": str(changelog_path),
            "message": "CHANGELOG.md does not exist",
        }

    content = changelog_path.read_text(encoding="utf-8")
    parser = ChangelogParser(content)
    unreleased = parser.parse_unreleased_entries()
    versions = parser.get_all_versions()
    current_ver = versions[0] if versions else (detect_project_version(changelog_path.parent) or "0.1.0")

    total_unreleased = sum(len(b) for b in unreleased.values())
    proposed_patch = calculate_next_version(current_ver, "patch", unreleased)
    proposed_minor = calculate_next_version(current_ver, "minor", unreleased)
    proposed_major = calculate_next_version(current_ver, "major", unreleased)
    proposed_auto = calculate_next_version(current_ver, "auto", unreleased) if total_unreleased > 0 else current_ver

    return {
        "success": True,
        "exists": True,
        "path": str(changelog_path),
        "current_version": current_ver,
        "released_versions_count": len(versions),
        "total_unreleased_entries": total_unreleased,
        "unreleased_by_category": {cat: len(bullets) for cat, bullets in unreleased.items()},
        "unreleased_entries": unreleased,
        "proposed_next_version": {
            "auto": proposed_auto,
            "patch": proposed_patch,
            "minor": proposed_minor,
            "major": proposed_major,
        },
    }

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic Keep a Changelog 1.1.0 & SemVer 2.0.0 manager for AI coding agents."
    )
    parser.add_argument("--path", "-p", help="Path to CHANGELOG.md (defaults to current dir)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize CHANGELOG.md if not present")
    p_init.add_argument("--version", "-v", help="Initial version (defaults to project detection or 0.1.0)")

    # add
    p_add = subparsers.add_parser("add", help="Add an entry to ## [Unreleased]")
    p_add.add_argument("category", help="Category (Added, Changed, Fixed, etc.) or Conventional Commit type (feat, fix, refactor...)")
    p_add.add_argument("entry", help="Description of the change")
    p_add.add_argument("--issue", "-i", help="Linear issue identifier (e.g. FAL-23)")

    # edit
    p_edit = subparsers.add_parser("edit", help="Edit an entry in ## [Unreleased]")
    p_edit.add_argument("--target", "-t", required=True, help="Target text to search and replace")
    p_edit.add_argument("--replacement", "-r", required=True, help="New entry text")

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove an entry from ## [Unreleased]")
    p_remove.add_argument("--target", "-t", required=True, help="Target text to match and remove")

    # bump
    p_bump = subparsers.add_parser("bump", help="Perform a SemVer release bump")
    p_bump.add_argument("type", nargs="?", default="auto", help="Bump type: auto, patch, minor, major, or explicit X.Y.Z")
    p_bump.add_argument("--date", "-d", help="Explicit release date YYYY-MM-DD")

    # status
    subparsers.add_parser("status", help="Show changelog status and unreleased changes")

    args = parser.parse_args()
    changelog_path = find_changelog(args.path)

    try:
        if args.command == "init":
            result = init_changelog(changelog_path, initial_version=args.version)
        elif args.command == "add":
            result = add_entry(changelog_path, args.category, args.entry, issue=args.issue)
        elif args.command == "edit":
            result = edit_entry(changelog_path, target=args.target, replacement=args.replacement)
        elif args.command == "remove":
            result = remove_entry(changelog_path, target=args.target)
        elif args.command == "bump":
            result = bump_version(changelog_path, bump_type=args.type, explicit_date=args.date)
        elif args.command == "status":
            result = get_status(changelog_path)
        else:
            raise ValueError(f"Unknown command {args.command}")

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success", False):
                print(f"[+] {result.get('message', 'Operation completed successfully.')}")
                if "new_version" in result:
                    print(f"    Version: {result['previous_version']} -> {result['new_version']}")
                if "total_unreleased_entries" in result:
                    print(f"    Current Version: {result['current_version']}")
                    print(f"    Unreleased Entries: {result['total_unreleased_entries']}")
                    print(f"    Next Suggested (auto): {result['proposed_next_version']['auto']}")
            else:
                print(f"[-] {result.get('message', 'Operation failed.')}")
                sys.exit(1)

    except Exception as exc:
        if args.json:
            print(json.dumps({"success": False, "error": str(exc)}, indent=2))
        else:
            print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
