---
title: A plugin archive missing .claude-plugin/plugin.json loads with no error
kind: fact
recorded: 2026-08-20
source:
    "Building `just claude bundle`; confirmed against a probe plugin and a negative
    control"
verify:
    "`claude plugin validate` on a `.zip` exits non-zero with a JSON parse error on the
    PK signature — it reads directories, never archives"
verified: 2026-08-20
tags: [claude-plugin, packaging, distribution, silent-failure]
---

Claude Code loads a plugin from a `.zip` via `--plugin-dir foo.zip` or `--plugin-url`,
and accepts either archive layout — `.claude-plugin/` at the archive root, or a single
wrapping top-level directory. What it will not do is tell you the manifest is missing:
the session starts normally and the plugin is simply absent.

**Why it matters:** the failure reads as success. `claude plugin validate` cannot
inspect an archive — it parses the zip as JSON and dies on the `PK` signature — so
nothing in the toolchain checks the artifact you actually ship. The usual way to produce
a broken one is `zip -r out.zip . -x '.*'`, whose dotfile glob silently drops
`.claude-plugin/` along with everything else beginning with a dot.

**What to do:** validate the staged directory before archiving, and assert the archive
contains `.claude-plugin/plugin.json` afterwards. `just claude bundle` does both.
