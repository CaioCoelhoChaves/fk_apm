# SemVer & Changelog Lifecycle Rules

Whenever developing features, fixes, refactorings, or modifications in this project:

1. **Keep CHANGELOG.md Updated**:
   - Check if `CHANGELOG.md` exists. If not, bootstrap it via `python skills/semver-changelog/scripts/changelog_manager.py init`.
   - Maintain all work-in-progress notes under the `## [Unreleased]` section.
   - Categorize entries strictly adhering to Keep a Changelog 1.1.0 (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).

2. **Conventional Mapping**:
   - `feat` ➔ `### Added`
   - `fix` ➔ `### Fixed`
   - `refactor`, `perf`, `style`, `chore`, `docs` ➔ `### Changed`
   - Breaking changes must include `BREAKING CHANGE:` explanation.

3. **Interactive Adjustments**:
   - When the user asks to modify entries or invokes `/fk-semver-owner` or `/semver`:
     - Apply edits via `changelog_manager.py edit` or `changelog_manager.py remove`.
     - Present the updated `## [Unreleased]` diff.

4. **Release Bumping**:
   - Release bumps must calculate the next SemVer 2.0.0 tag based on unreleased changes or explicit developer instruction.
