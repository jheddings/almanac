---
title: Repository Markdown prose is wrapped by prettier, never by hand
kind: rule
recorded: 2026-08-25
source: "AGENTS.md § Conventions, migrated 2026-08-25"
tags: [markdown, formatting, prettier, conventions]
---

**Applies when:** you are about to edit prose in a repository `.md` file.

`.prettierrc.json` sets `proseWrap: always` at `printWidth: 88`, enforced by
`just check` and the prettier pre-commit hook. Do not hand-wrap or hand-align prose —
write the paragraph however it comes out, run `just tidy`, and let prettier own the line
breaks.

**Why:** the formatter reflows every paragraph it touches, so hand-wrapping is work that
gets discarded and then shows up as diff noise in lines you did not mean to change.
Expect `just tidy` to rewrap paragraphs you edited.

Two neighbouring rules run the other way, because neither text passes through prettier:
[`pr-and-issue-prose-is-written-unwrapped`](pr-and-issue-prose-is-written-unwrapped.md)
and
[`commit-messages-use-conventional-commit-format`](commit-messages-use-conventional-commit-format.md),
which sets its own width.
