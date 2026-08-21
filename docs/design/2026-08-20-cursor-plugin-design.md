# Almanac Cursor Plugin Adapter — Design

**Date:** 2026-08-20 **Status:** Approved **Extends:**
[2026-08-20-plugin-extraction-design.md](2026-08-20-plugin-extraction-design.md)

## Summary

Add a Cursor Plugin wrapper for the almanac skills so Cursor IDE and Agent CLI can
install the same procedures Claude Code already ships. Other harnesses keep their own
adapters; this work does not produce a portable Agent Plugin as the primary artifact.

Procedures stay shared. Cursor adds only harness packaging: `.cursor-plugin/` manifests,
thin slash-command stubs nested under `.cursor-plugin/commands/`, an allowlisted zip
bundle, and a `just cursor` module parallel to `just claude` / `just agy`. `skills/init`
already shipped in #3 and is already harness-neutral on `main`; this adapter does not
edit it.

Consulting remains a trigger in adopter `AGENTS.md`. No Cursor rule or session hook
lists or injects the almanac.

## Decisions

### Dual-manifest at the repo root

Approach A from design review: the repo root remains the plugin root for both Claude and
Cursor. Skills and templates are not copied into a nested package.

```
.claude-plugin/plugin.json
.claude-plugin/marketplace.json
.cursor-plugin/plugin.json
.cursor-plugin/marketplace.json     # single plugin, source: "./"
.cursor-plugin/.justfile            # just cursor …
.cursor-plugin/commands/            # thin slash stubs; not at repo-root commands/
  init.md
  record.md
  audit.md
skills/
  init/SKILL.md                     # shared; not edited by this adapter
  record/SKILL.md
  audit/SKILL.md
templates/almanac/README.md
```

No `rules/`, no `hooks/`, no MCP. Cursor discovers `skills/` and commands from paths in
`.cursor-plugin/plugin.json`. Commands are not at repo-root `commands/`, because Claude
Code's marketplace install uses `source: "./"` and auto-discovers a top-level
`commands/` directory. `docs/` is not a plugin component; it still must not appear in
the zip payload.

### Shared `VERSION`, one check script per harness

A single `VERSION` file is the source of truth. Every harness `plugin.json` carries that
string, and a per-harness script plus pre-commit hook asserts it. Root `just release`
loops all manifests. There is no independent `just bump` and no two-way claude/cursor
drift guard — a check that names two harnesses goes stale the moment a third exists.

`.cursor-plugin/plugin.json` matches `VERSION` the same way Claude, Codex, and
Antigravity already do. `scripts/check-cursor-manifest.sh` is a sibling of
`scripts/check-manifests.sh` (Claude-only; it requires a marketplace.json) and of the
codex/agy scripts.

### Shared `skills/init`, thin Cursor commands

`skills/init` already exists (#3) and already resolves the template without naming
Cursor. This adapter does not change that skill. Slash-command stubs name
`almanac:init`, `almanac:record`, and `almanac:audit` and instruct the agent to follow
them. Procedure prose is not duplicated there. Unprefixed `name:` fields in the stubs
(`init`, `record`, `audit`) are what Cursor's plugin command discovery namespaces; the
install README records the invocation that actually loaded.

### Template path stays at `templates/`

`init` reads `templates/almanac/README.md` from the plugin install root via the
resolution already in the skill: `${CLAUDE_PLUGIN_ROOT}` if set, else workspace-relative
`templates/`, else the plugin's installed directory as the harness exposes it. The
template must not move into skill assets — adopters without skills still need the
contract text.

### Cursor zip bundle, same allowlist discipline as Claude

Cursor distribution is git URL / team marketplace / local symlink / `--plugin-dir`,
**and** an allowlisted zip for parity with Claude. The `just cursor` module is a sibling
of `just claude`; both stage from an explicit allowlist because the repo root is the
plugin root.

```
just cursor bundle   # stage → structural checks → dist/almanac-cursor-plugin-<ver>.zip
```

Payload allowlist:

```
.cursor-plugin/plugin.json
.cursor-plugin/commands/
skills/
templates/
README.md
LICENSE
```

`docs/` stays out (this repo's live almanac). Marketplace manifest stays out of the
payload. Validate the **stage**: Cursor has no `plugin validate` CLI analogous to
Claude's; assert the allowlist paths and a well-formed `plugin.json`. After zipping,
capture `unzip -l` once and match against a herestring (see
`docs/almanac/piping-into-grep-q-under-pipefail-fails-on-sigpipe.md`) so the archive
contains `.cursor-plugin/plugin.json` and does not contain `docs/`. Silent
load-without-manifest is already recorded for Claude and should be assumed possible for
Cursor until proven otherwise.

`just cursor clean` removes only this harness's stage and zip, not `dist/`.

### Three-halves unchanged

| Kind             | Home                                      |
| ---------------- | ----------------------------------------- |
| Trigger          | adopter `AGENTS.md`                       |
| Procedure        | shared skills (`init`, `record`, `audit`) |
| Local convention | adopter almanac `README.md`               |

A Cursor always-on rule or `sessionStart` hook that lists entries would reintroduce the
Claude-only fragmentation the almanac exists to remove. Out of scope permanently for
this adapter.

## Tooling

```
just cursor manifests    # VERSION + name checks for .cursor-plugin/*
just cursor bundle       # allowlisted stage + zip
just cursor clean        # this harness's dist artifacts only
just check               # root: prettier, skills-ref, drift, harness manifests
just release             # VERSION + every harness plugin.json
```

CI runs pre-commit, not `just`. A Cursor check that exists only as
`just cursor manifests` is local-only; `scripts/check-cursor-manifest.sh` is also a
pre-commit hook.

## Verification

- `skills-ref validate` on `init`, `record`, and `audit`
- Plugin loads via `~/.cursor/plugins/local` symlink and/or `agent --plugin-dir` /
  `cursor agent --plugin-dir`
- Slash commands resolve into the shared skills by name, not by a checkout-relative
  `skills/.../SKILL.md` path
- Built Cursor archive contains `.cursor-plugin/plugin.json` and omits `docs/`
- `just drift` remains green
- `just claude bundle` still works after `just cursor clean`

## Out of scope

- Public Cursor Marketplace submission (local / team / git install first)
- Codex, Gemini, or Agent Plugins-as-primary packaging
- Consult rule or session hook
- Relocating `templates/` into skill assets
- Editing `skills/init` (already harness-neutral)
- Scheduling audits

## Docs

README gains a Cursor install section beside the other harnesses. CONTRIBUTING notes the
per-harness check script, pre-commit hook, and `just cursor bundle`. Design positions in
the README stay harness-neutral.
