# almanac

A Claude Code plugin for durable repository memory: facts agents learned the hard way and
should not have to rediscover.

An almanac is a checked-in `docs/almanac/` directory containing one factual claim per Markdown
file. Claim-shaped filenames make the directory listing its index, so every agent can consult it
with ordinary filesystem tools. There is no generated registry, session hook, or background
writer.

## Skills

| Skill            | Use it to                                                                  |
| ---------------- | -------------------------------------------------------------------------- |
| `almanac-init`   | Add the shared instructions and local almanac contract to a repository     |
| `almanac-record` | Record a verified, durable, costly-to-rediscover fact after a surprise      |
| `almanac-audit`  | Re-run entry verification and propose reviewed corrections or freshness updates |

## Installation

```text
/plugin marketplace add jheddings/almanac
/plugin install almanac@almanac
```

After installation, ask Claude to initialize the almanac in the target repository. Initialization
shows the proposed files and instruction changes before writing anything. It is safe to run again:
existing content is preserved and only missing pieces are proposed.

## Cross-agent model

Claude Code is the first packaging target, so the procedures in `skills/` are loaded by Claude.
The durable output is deliberately tool-neutral:

- `AGENTS.md` carries the short trigger telling agents when to consult the almanac.
- `docs/almanac/README.md` carries the repository's local format and destinations.
- `docs/almanac/*.md` contains the facts, readable with any filesystem tool.

Codex and other agents can therefore consult and maintain an initialized almanac even when they
cannot load this Claude plugin. Native packaging for other harnesses is planned separately.

The audit skill uses ordinary reads, searches, and read-only commands. It may parallelize checks
when a harness provides subagents, but it does not depend on Claude Code's gated Workflow runtime.

## Design boundaries

- Consulting is a trigger in shared repository instructions, not a skill or startup hook.
- Recording and auditing are procedures supplied by skills.
- The plugin's method wins over a stale local copy; the local README owns repository-specific
  destinations, formatting, and review conventions.
- Nothing automatically writes entries. Entries and corrections are reviewed like code.
- `docs/almanac/` is the required location in the first release. A single predictable path keeps
  discovery portable and configuration-free.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the entry and skill design principles.
