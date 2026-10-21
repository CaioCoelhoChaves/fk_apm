# Keep a Changelog 1.1.0 Reference Guide

This reference provides the principles and guidelines for maintaining `CHANGELOG.md` according to [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

---

## 1. Guiding Principles

- **Changelogs are for humans, not machines**: Make entry descriptions clear, concise, and focused on user-facing value or architectural changes.
- **Single Source of Truth**: There should be one `CHANGELOG.md` per repository or per package in monorepos.
- **Reverse Chronological Order**: The latest changes are always at the top (`## [Unreleased]`, followed by the latest released version).
- **ISO 8601 Dates**: All release dates must use the standard format `YYYY-MM-DD` (e.g., `2026-10-21`).
- **Semantic Versioning Compliance**: Version headers strictly follow [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html).

---

## 2. Standard Header Structure

Every `CHANGELOG.md` file must begin with:

```markdown
# Changelog

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
```

---

## 3. Allowed Category Types

Keep a Changelog specifies exactly six types of changes under each version section:

| Category | Description | Conventional Commit Types |
| :--- | :--- | :--- |
| `### Added` | New user-facing features, modules, or APIs | `feat`, `add` |
| `### Changed` | Changes in existing functionality, refactors, dependencies | `refactor`, `perf`, `style`, `chore`, `docs`, `build` |
| `### Deprecated` | Features or endpoints soon-to-be removed in upcoming versions | `deprecate`, `deprecated` |
| `### Removed` | Features, APIs, or dependencies that have now been removed | `remove`, `removed` |
| `### Fixed` | Bug fixes and resolutions for unexpected behaviors | `fix`, `bugfix` |
| `### Security` | Vulnerability fixes, patch CVEs, and security hardening | `security`, `sec` |

---

## 4. Entry Formatting Rules

1. **Bullet Points**: Every entry is a bullet starting with `- `.
2. **Imperative or Descriptive**: Use clear, concise language (e.g., `- Add biometric authentication fallback`).
3. **Task Tracking**: Append the issue or card identifier when available:
   ```markdown
   - Support OAuth2 PKCE login flow (FAL-23)
   ```
4. **Breaking Changes**: Clearly highlight breaking changes at the start of the bullet:
   ```markdown
   - **BREAKING CHANGE**: Remove legacy v1 authentication endpoints (FAL-10)
   ```
5. **No Duplication**: Avoid inserting duplicate items for identical changes.
