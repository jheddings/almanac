---
title: Rejected dependencies are named in the commit
kind: rule
recorded: 2026-08-25
source: "Project conventions, set when this repository was initialized"
tags: [dependencies, licensing, commits, conventions]
---

**Applies when:** you chose one package over another that you rejected for its license.

Record it in the commit message as a trailer — one line, comma separated, naming the
package and the license that disqualified it:

```text
Rejected-for-license: Unidecode (GPL)
```

If you rejected nothing, omit the trailer. Do not write "none".

**Why:** `pyproject.toml` records what was chosen and never what was considered. Without
the trailer the next person evaluates the same package and reaches the same dead end,
and a reviewer cannot tell a deliberate choice from an accident that happened to land
well.
