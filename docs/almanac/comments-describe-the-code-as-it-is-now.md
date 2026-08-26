---
title: Comments describe the code as it is now, not how it got here
kind: rule
recorded: 2026-08-25
source: "AGENTS.md § Conventions, migrated 2026-08-25"
tags: [comments, docstrings, conventions]
---

**Applies when:** you are about to write a comment or a docstring.

State the mechanism, the constraint it satisfies, or the failure it prevents, as a
present-tense fact about the code in front of the reader. Leave out comparisons to an
earlier implementation, justifications framed as history, and references to how other
repositories do it.

**Why:** a reader six months from now has only this code. A comment about what the code
is _not_, or about how some other project solves the same problem, is something they
have to decode before they can use anything it says.

Rationale that is genuinely about a tradeoff belongs in the pull request or in a design
doc under [`docs/design/`](../design/), where it is dated and can be cleared out once it
stops mattering.
