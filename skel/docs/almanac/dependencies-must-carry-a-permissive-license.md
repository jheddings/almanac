---
title: Dependencies must carry a permissive license
kind: rule
recorded: 2026-08-25
source: "Project conventions, set when this repository was initialized"
tags: [dependencies, licensing, conventions]
---

**Applies when:** you are about to add a package to `pyproject.toml`.

Permissive licenses are accepted: MIT, BSD (2- or 3-clause), Apache-2.0, ISC, and the
Python Software Foundation License. Copyleft licenses are not, in any version: GPL,
AGPL, and LGPL.

Check the license before you add a package, not after. When the obvious candidate is
copyleft, find a permissive equivalent or use the standard library.

**Why:** this project ships under MIT, and a copyleft dependency changes the terms
everything here can be used under. Nothing in the build catches it — the package
installs, the tests pass, the checks stay green, and the problem surfaces at review or
later.

Having rejected something, say so:
[`rejected-dependencies-are-named-in-the-commit`](rejected-dependencies-are-named-in-the-commit.md).
