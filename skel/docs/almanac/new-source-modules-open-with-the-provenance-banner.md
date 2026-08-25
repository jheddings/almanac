---
title: New source modules open with the provenance banner
kind: rule
recorded: 2026-08-24
source: "Project conventions, set when this repository was initialized"
tags: [python, source-layout, conventions]
---

**Applies when:** you are about to create a new `.py` file under `src/skinner/`.

Every source module opens with this exact line, before the module docstring:

```text
# skinner:module
```

Package `__init__.py` files are exempt and carry no banner.

**Why:** the banner marks a file as the package's own source rather than generated or
vendored code. Nothing enforces it, so a module missing the banner produces no error
anyone will see — it is simply wrong and silent.
