---
name: conventional-commit
description: Inspect staged git changes and craft a commit message in Conventional Commits format. Use this skill whenever the user asks to commit, write/generate a commit message, "commit my changes", "what should I commit this as", or mentions Conventional Commits, semver-bump commits, or release-please/changeset-style messages. Trigger even when the user does not say the exact phrase "conventional commit" — any request that boils down to "summarize what's staged into a commit" should use this skill. Do NOT use for amending unrelated history, force-pushing, or rewriting non-HEAD commits.
---

# Conventional Commit Message Generator

This skill walks Claude through inspecting the current git staging area and producing a single, well-formed commit message that follows the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification.

## When to use

Use this skill whenever the user wants a commit message for what is currently staged. Typical triggers:

- "commit this"
- "write a commit message"
- "what's a good commit message for these changes"
- "commit the staged changes"
- "make a conventional commit"

If nothing is staged, see the "No staged changes" section below — do not silently fall back to unstaged changes.

## Workflow

Follow these steps in order. Do not skip the inspection step; the message must be grounded in the actual diff, not in assumptions.

### 1. Verify there are staged changes

Run:

```bash
git diff --cached --stat
```

- If the output is empty, jump to the "No staged changes" section.
- Otherwise, note the files touched and the rough scope of the change.

### 2. Read the staged diff

Run:

```bash
git diff --cached
```

If the diff is very large (more than ~500 lines), also run:

```bash
git diff --cached --name-status
git diff --cached --stat
```

…and read the full diff in chunks rather than guessing. The commit message must reflect what actually changed. Do not take into consideration any unstaged changes for that. Treat unstaged changes as if they do not exist yet. This is needed to create compose the commit message from an atomic perspective.

### 3. Check recent history for style conventions

Run:

```bash
git log -n 20 --pretty=format:"%s"
```

Use this to match the repo's existing conventions:

- Are scopes used? (e.g. `feat(api): ...`)
- Lowercase vs. sentence case for the subject?
- Language (English, German, etc.) — match what the repo already uses.
- Any custom types beyond the standard set (e.g. `wip`, `deps`)?

If the repo clearly does not use Conventional Commits and the user did not explicitly ask for it, ask the user whether they still want a Conventional Commits–style message or to match the existing style.

### 4. Classify the change

Pick exactly one type for the subject line. Standard types:

| Type       | Use for                                                                 |
|------------|-------------------------------------------------------------------------|
| `feat`     | A new user-facing feature                                               |
| `fix`      | A bug fix                                                               |
| `docs`     | Documentation only                                                      |
| `style`    | Formatting, whitespace, missing semicolons — no code-behavior change    |
| `refactor` | Code change that neither fixes a bug nor adds a feature                 |
| `perf`     | Performance improvement                                                 |
| `test`     | Adding or correcting tests                                              |
| `build`    | Build system, packaging, or external dependencies                       |
| `ci`       | CI configuration and scripts                                            |
| `chore`    | Other changes that don't modify src or test files                       |
| `revert`   | Reverts a previous commit                                               |

Tie-breakers:

- If the change adds a new capability **and** fixes a bug, prefer `feat` and mention the fix in the body.
- If it's purely an internal cleanup with no behavior change, use `refactor`.
- Dependency bumps go to `build` (or `chore` if the repo uses that convention).
- A breaking change keeps its natural type (`feat`, `fix`, `refactor`, …) and is marked with `!` and a `BREAKING CHANGE:` footer.

### 5. Choose a scope (optional but encouraged)

Look at the file paths in the diff:

- Single top-level area (e.g. all changes in `api/`) → use that as the scope: `feat(api): …`
- Multiple unrelated areas → omit the scope rather than inventing one.
- Match the casing/style used in `git log` history.

### 6. Compose the message

Structure:

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Rules:

- **Subject line ≤ 72 characters.** Hard limit. Imperative mood ("add", "fix", "remove" — not "added"/"adds").
- **Do not end the subject with a period.**
- **Blank line** between subject and body, and between body and footers.
- **Body** wraps at ~72 columns. Use it to explain *why* and *what*, not *how* — the diff already shows how. Skip the body for trivial changes (typo fixes, small renames).
- **Footers**: `BREAKING CHANGE: <description>` for breaking changes; `Refs: #123`, `Closes #123`, `Co-authored-by: ...` etc. as appropriate.
- For breaking changes, also append `!` after the type/scope: `feat(api)!: drop support for Node 18`.

### 7. Present the message

Output the commit message inside a single fenced code block so the user can copy it directly. Then, on a new line, offer to run the commit:

> Want me to commit with this message?

If the user confirms, run:

```bash
git commit -m "<subject>" -m "<body>" -m "<footers>"
```

…using separate `-m` flags per paragraph rather than embedded newlines, which avoids shell-escaping issues across platforms.

Do not commit automatically without confirmation.

## No staged changes

If `git diff --cached --stat` is empty:

1. Run `git status --short` to see what's modified but unstaged.
2. Tell the user nothing is staged and show them the unstaged changes.
3. Ask whether they want to stage everything (`git add -A`), stage specific files, or stage interactively (`git add -p`) — then re-run the workflow.

Do not generate a commit message from unstaged changes without explicit user direction.

## Examples

### Small fix, no body needed

Diff: adds a one-line null check in `src/auth/login.ts`

```
fix(auth): handle missing session token on login
```

### Feature with body

Diff adds a new endpoint and tests across `api/` and `tests/api/`:

```
feat(api): add /users/:id/preferences endpoint

Returns the user's stored UI preferences as JSON. Falls back to the
schema defaults when no row exists yet. Tests cover the empty,
populated, and unauthorized cases.

Refs: #482
```

### Breaking change

Diff removes a deprecated config field across multiple packages:

```
refactor(config)!: remove deprecated `legacyMode` flag

BREAKING CHANGE: The `legacyMode` config flag has been removed.
Migrate to the `compatibility.version` field — see UPGRADING.md.
```

### Dependency bump

```
build(deps): bump axios from 1.6.7 to 1.7.2
```

### Revert

```
revert: feat(api): add /users/:id/preferences endpoint

This reverts commit 9f3a2e1b. The endpoint shipped before the
schema migration landed in production.
```

## Anti-patterns to avoid

- ❌ Vague subjects: `fix: stuff`, `chore: update`, `feat: improvements`.
- ❌ Past tense or third person: `fixed bug`, `adds feature`.
- ❌ Multiple unrelated changes lumped together — suggest splitting the commit instead.
- ❌ Inventing a scope that doesn't reflect the diff.
- ❌ Marking something `feat` when no user-visible behavior changed.
- ❌ Quoting the diff verbatim in the body — summarize the *intent*.

## Quick reference

Spec: https://www.conventionalcommits.org/en/v1.0.0/

Subject formula: `type(scope)!: imperative summary, ≤72 chars, no period`
