---
title: Anything added to `skills/` ships to adopters, whatever the archive excludes
kind: fact
recorded: 2026-09-11
source:
    "Built, reviewed, and reverted on `feat/assess-skill` — the payload exclusion landed
    in ff7c5c7 and came back out in cfdd565"
verify:
    "`jq -r '.plugins[].source' .claude-plugin/marketplace.json
    .cursor-plugin/marketplace.json` prints `./` twice and `jq -r .skills
    .codex-plugin/plugin.json` prints `./skills/` — every documented install resolves
    the plugin from the repo tree, so no archive stands between `skills/` and an adopter"
verified: 2026-09-11
tags: [distribution, packaging, marketplace, skills, silent-failure]
---

Both marketplace manifests declare `source: "./"`, so the documented Claude Code and
Cursor installs resolve the plugin at the repository root and discover `skills/` from
the cloned tree. `.codex-plugin/plugin.json` points at `./skills/` and declares no
bundle at all. `.github/workflows/release.yml` creates a draft release and attaches
nothing, so there is no published archive to install from either. The payload machinery
governs the archives and the staged tree `just install agy` hands to Antigravity —
nothing else.

**Why it matters:** `harnesses.toml` payloads and every check in `tools/bundle.py`
describe the archive, and the archive is not the route. A directory added to `skills/`
reaches every adopter through the documented install while a payload exclusion, its
stage check, and its archive check all report success. The mistake is invisible:
everything you would think to look at agrees with you.

**What to do:** keep anything that must not ship out of `skills/` by **location**, not
by exclusion. `.claude/skills/` is named by no manifest and no payload, so a
development-only skill lives there. Read the bundler's exclusion list as a guard on one
harness's artifact, never as the thing that decides what an adopter gets.

Related:
[`a-plugin-archive-missing-its-manifest-loads-with-no-error`](a-plugin-archive-missing-its-manifest-loads-with-no-error.md)
is the neighbouring trap — that one is a check examining an artifact nobody installs,
this one is a check guarding a route nobody takes.
