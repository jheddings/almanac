---
title: Commit messages use Conventional Commits format
kind: rule
recorded: 2026-08-24
source: "Project conventions, set when this repository was initialized"
tags: [git, commits, conventions]
---

**Applies when:** you are about to write a commit message.

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <description>
```

Types are `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, and `perf`. Scope
is optional but encouraged — `fix(cli): ...`, `feat(config): ...`. Include the issue
number where one applies — `feat: add the config loader (#3)`.

Wrap the message body at about 72 columns.

**Why:** the type prefix is what makes the history scannable and what release tooling
reads. The wrap width matters because commit messages are read in terminals that do not
reflow them.
