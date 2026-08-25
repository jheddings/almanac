---
title: Commit messages use Conventional Commits format
kind: rule
recorded: 2026-08-24
source: "AGENTS.md, migrated 2026-08-24"
tags: [git, commits, conventions]
---

**Applies when:** you are about to write a commit message, or a PR title.

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <description>
```

Types are `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, and `perf`. Scope
is optional but encouraged — `fix(audit): ...`, `feat(init): ...`. Include the issue
number where one applies — `feat: add the init skill (#3)`.

Wrap the message body at about 72 columns. Commit messages are read in terminals that do
not reflow, and they are the text that survives a merge.

**Why:** the type prefix is what makes `main`'s history scannable and what release
tooling reads. The wrap width and the care matter more here than they look, because
[`github-composes-a-squash-commit-from-the-commit-messages`](github-composes-a-squash-commit-from-the-commit-messages.md)
— the PR body is discarded at merge, so a sloppy commit message is the permanent record.
