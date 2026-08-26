---
title: Branch names carry the commit type as a prefix
kind: rule
recorded: 2026-08-24
source: "Project conventions, set when this repository was initialized"
tags: [git, branches, conventions]
---

**Applies when:** you are about to create a branch.

Use the same type prefixes as commits, followed by a short description of the intended
change:

```text
<type>/<change-slug>
```

Examples: `feat/config-loader`, `fix/sidebar-delete-width`, `chore/update-deps`.
Optionally include the issue number: `feat/279-email-notifications`.

**Why:** the prefix states the kind of change before anyone opens the diff, and it keeps
branch listings sorted by intent. The types are the ones in
[`commit-messages-use-conventional-commit-format`](commit-messages-use-conventional-commit-format.md);
they do not diverge.
