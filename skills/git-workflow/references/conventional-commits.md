# Conventional Commits v1.0.0 Specification Reference

This document provides the complete reference for the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification used across FK projects.

---

## 1. Specification Overview

The Conventional Commits specification is a lightweight convention on top of commit messages. It provides an explicit commit history that communicates intention and maps directly to [Semantic Versioning (SemVer)](https://semver.org).

### Commit Structure

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

---

## 2. Structural Elements

### 2.1 Type (Mandatory)
The commit type communicates the intent of the change. Allowed types:

| Type | SemVer Impact | Description |
| :--- | :--- | :--- |
| `feat` | **MINOR** | Introduces a new feature or user-facing capability to the codebase. |
| `fix` | **PATCH** | Patches a bug or defect in the codebase. |
| `docs` | None | Documentation changes only (e.g., README, docstrings, markdown). |
| `style` | None | Changes that do not affect the meaning of the code (formatting, white-space, semi-colons). |
| `refactor` | None | Code changes that neither fix a bug nor add a feature. |
| `perf` | **PATCH** | Code changes that improve runtime performance or resource usage. |
| `test` | None | Adding missing tests, golden files, or correcting existing test suites. |
| `build` | None / **PATCH** | Changes affecting build tooling, build scripts, or external dependencies (pubspec, package.json). |
| `ci` | None | Changes to continuous integration configurations and pipeline scripts (GitHub Actions). |
| `chore` | None | Routine maintenance, tooling tasks, and repo hygiene that do not modify `src` or test code. |
| `revert` | **PATCH** / Varies | Reverts a previous commit. Should include the SHA of the reverted commit in the header/body. |

### 2.2 Scope (Optional)
- Enclosed in parentheses immediately following the type: `type(scope): description`.
- Must be a concise noun describing the module, package, widget, or component affected.
- Examples:
  - `feat(auth): add OAuth2 token refresh support`
  - `fix(navigation): resolve route redirect loop when unauthenticated`
  - `test(widgets): add golden tests for CoreButton`

### 2.3 Description (Mandatory)
- Immediate summary following the colon and space.
- Written in the **imperative, present tense**:
  - Use "add" (not "added" or "adds").
  - Use "fix" (not "fixed" or "fixes").
  - Use "change" (not "changed" or "changes").
- Start with a **lowercase** letter (unless starting with a proper noun or code identifier).
- Do **NOT** end with a period (`.`).
- Keep under **72 characters** (recommended 50 characters).

### 2.4 Body (Optional)
- Must be preceded by a blank line after the description.
- Written in imperative, present tense.
- Explains the **motivation** for the change and contrasts with previous behavior (the "why" rather than just the "what").
- Can contain multiple paragraphs separated by blank lines.

### 2.5 Footers (Optional)
- Must be preceded by a blank line after the body (or description if body is omitted).
- Follows the [git trailer format](https://git-scm.com/docs/git-interpret-trailers).
- Each footer consists of a token, followed by `:<space>` or `<space>#`, followed by a string value:
  - `BREAKING CHANGE: <explanation>`
  - `Closes #123`
  - `Fixes #456`
  - `Refs #789`
  - `Co-authored-by: Caio Coelho <caio@example.com>`

---

## 3. Breaking Changes

A breaking change communicates that consumers must adjust their code due to incompatible API or contract changes. It triggers a **MAJOR** version bump.

Breaking changes can be signaled in two ways (both are permitted, and using both is best practice):

1. **Exclamation Mark (`!`) in Header**:
   - Immediately before the colon: `<type>!: <description>` or `<type>(<scope>)!: <description>`.
   - Example: `feat(api)!: drop support for legacy v1 authentication endpoints`

2. **`BREAKING CHANGE:` Footer**:
   - A dedicated footer block starting with `BREAKING CHANGE: ` followed by a detailed description of the breaking change and the migration steps.
   - Example:
     ```text
     feat(client): migrate HTTP client to dio v5

     BREAKING CHANGE: The `HttpClient.sendRequest()` method now returns a `Result<T>` instead of throwing `HttpException`.
     ```

---

## 4. Canonical Examples

### Simple Feature Commit
```text
feat(cart): add support for applying discount coupon codes
```

### Bug Fix with Scope and Issue Reference
```text
fix(auth): prevent session timeout during token renewal

When renewing the JWT token, an expired timestamp was incorrectly evaluated before the network response completed.

Closes #342
```

### Breaking Change with Exclamation and Footer
```text
refactor(theme)!: migrate all color palettes to Material 3 tokens

Update CoreTheme and all downstream widget tokens to use ColorScheme from Material 3.

BREAKING CHANGE: `CoreThemeData.primaryDark` has been removed. Use `Theme.of(context).colorScheme.primary` instead.
```

### Revert Commit
```text
revert: let clients handle network timeout retries

This reverts commit 7a8b9c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b.
```
