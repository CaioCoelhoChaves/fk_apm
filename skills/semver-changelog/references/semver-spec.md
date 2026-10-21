# Semantic Versioning 2.0.0 Specification Reference

This document summarizes the [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) specification and the automated bump calculation rules used by `semver-changelog`.

---

## 1. SemVer Format: `X.Y.Z` (`MAJOR.MINOR.PATCH`)

Given a version number `MAJOR.MINOR.PATCH`, increment the:

1. **`MAJOR`** version when you make incompatible API changes (Breaking Changes).
2. **`MINOR`** version when you add functionality in a backward compatible manner.
3. **`PATCH`** version when you make backward compatible bug fixes.

Additional labels for pre-release and build metadata are available as extensions to the `MAJOR.MINOR.PATCH` format (e.g., `1.0.0-alpha.1`, `1.0.0+20261021`).

---

## 2. Special Rules for Initial Development (`0.y.z`)

According to SemVer 2.0.0 item 4:
> *Major version zero (0.y.z) is for initial development. Anything MAY change at any time. The public API SHOULD NOT be considered stable.*

In `0.y.z` projects:
- Breaking changes or new features typically bump `MINOR` (`0.1.0` -> `0.2.0`).
- Bug fixes bump `PATCH` (`0.1.0` -> `0.1.1`).
- The transition from `0.y.z` to `1.0.0` signals the first stable, production-ready public API.

---

## 3. Automated Increment Decision Matrix

When performing an automated bump (`bump auto`), the script assesses the accumulated entries in `## [Unreleased]`:

| Unreleased Contents | Current Version >= 1.0.0 | Current Version == 0.y.z | Suggested Bump |
| :--- | :--- | :--- | :--- |
| Any `BREAKING CHANGE`, `!:`, or `Removed` | `MAJOR` (`1.2.0` ➔ `2.0.0`) | `MINOR` (`0.2.0` ➔ `0.3.0`) | Major / Breaking Minor |
| Entries in `### Added` | `MINOR` (`1.2.0` ➔ `1.3.0`) | `MINOR` (`0.2.0` ➔ `0.3.0`) | Minor (Feature) |
| Only `### Fixed`, `### Changed`, `### Security` | `PATCH` (`1.2.0` ➔ `1.2.1`) | `PATCH` (`0.2.0` ➔ `0.2.1`) | Patch (Fix/Refactor) |

---

## 4. Conventional Commits 1.0.0 Mapping

| Conventional Commit Prefix | Keep a Changelog Section | SemVer Bump Impact |
| :--- | :--- | :--- |
| `feat:` / `feat(...):` | `### Added` | `MINOR` |
| `feat!:` / `fix!:` / `BREAKING CHANGE:` | Corresponding category + breaking tag | `MAJOR` (or `MINOR` in 0.x) |
| `fix:` / `fix(...):` | `### Fixed` | `PATCH` |
| `perf:` / `refactor:` | `### Changed` | `PATCH` |
| `docs:` / `style:` / `chore:` | `### Changed` | `PATCH` |
| `sec:` / `security:` | `### Security` | `PATCH` |
| `deprecate:` | `### Deprecated` | `PATCH` / `MINOR` |
| `remove:` | `### Removed` | `MAJOR` (or `MINOR` in 0.x) |
