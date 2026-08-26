---
title: Prose written outside the repository is left unwrapped
kind: rule
recorded: 2026-08-25
source: "AGENTS.md § Conventions, migrated 2026-08-25"
tags: [markdown, github, pull-requests, issues, conventions]
---

**Applies when:** you are about to write a pull request description, an issue body, or a
review comment.

Write each paragraph as one continuous line and let the browser wrap it. Do not
hard-wrap.

**Why:** that text never passes through prettier, and GitHub renders its line breaks
literally rather than reflowing them, so hard-wrapped paragraphs arrive visibly ragged.
The failure is invisible to the writer — the text looks correct in the editor and wrong
only once it is posted, by which point somebody else is reading it.

This is the exact inverse of
[`markdown-prose-is-wrapped-by-prettier-not-by-hand`](markdown-prose-is-wrapped-by-prettier-not-by-hand.md),
and which rule applies turns only on whether the file passes through the formatter.
