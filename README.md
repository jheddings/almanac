# almanac

A Claude Code plugin for keeping an **almanac** — a directory of facts your agents
discovered the hard way, recorded so nobody learns them twice.

An almanac entry is a silent failure mode, a tool that lies, a constraint that isn't
visible from the code. Not documentation, not a plan: a claim a future agent will act on
without re-deriving it. One fact per file, filename states the claim, and the directory
listing is the index.

This plugin carries the two procedures that keep such a directory honest. Consulting the
almanac is deliberately **not** one of them — see [Design positions](#design-positions).

## Skills

| Skill            | Use it when                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `almanac:record` | You just finished being surprised, and something durable came out of it |
| `almanac:audit`  | You want to know whether the recorded facts are still true              |

`record` owns the admission tests, the category gate, and how to write a `verify` line
that fails when its claim fails. `audit` re-runs every entry's `verify` line and sorts
the results into `holds` / `falsified` / `unverifiable`, then proposes corrections
behind a confirmation gate.

## Installation

```bash
/plugin marketplace add jheddings/almanac
/plugin install almanac@almanac
```

## Setup

The skills require an almanac to work on: a directory named `almanac` containing a
`README.md`. They Glob for `**/almanac/README.md` and stop if there isn't one, rather
than creating it as a side effect.

Bootstrap it by asking Claude, from the repo you want the almanac in:

> Copy the almanac plugin's template from
> `${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md` to `docs/almanac/README.md`.

The plugin's install path isn't something you can resolve from a shell, which is why
this is a request rather than a `cp` you can paste. `${CLAUDE_PLUGIN_ROOT}` expands only
inside the plugin's own context.

Then do two things:

1. **Fill in the local block.** Inside `docs/almanac/README.md` is a block marked
   `<!-- almanac:local -->`. Replace it with a table naming where non-almanac content
   goes _in your repo_ — design intent, required rules, in-flight status, personal
   preferences. Keep only rows whose destination actually exists. This is the one part
   of the contract the plugin cannot write for you, and it is the part that decides what
   stays out.
2. **Add the consult trigger** to `AGENTS.md` (or `CLAUDE.md`). Recording and auditing
   are procedures and live in these skills; _consulting_ is a trigger, and belongs in
   the instructions every tool already reads. See this repo's own [AGENTS.md](AGENTS.md)
   for wording you can lift.

Leave the `<!-- almanac-template: N -->` comment on the first line alone. It records
which revision of the contract text your copy came from, so a later release can tell you
whether yours is stale. It is bumped only when the shared text changes — not on every
plugin release — and your local block is excluded from it by definition.

An `almanac:init` skill that does all of this is planned; see
[Not in this release](#not-in-this-release).

## Design positions

These are choices, not accidents. Each of them costs something, and the cost is stated.

**Consulting is a trigger, not a skill.** A skill only fires when something in context
suggests loading it, and the entries worth most are silent failures you'd never think to
search for — so the moment you most need the almanac is the moment nothing prompts you
to look. That has to live in always-on instructions. It also has to work under Codex,
Cursor, and anything else that reads `AGENTS.md` but cannot load a skill. There is
deliberately no `almanac:consult`, and deliberately no session-start hook: a hook that
lists entries would be Claude-only, which is the fragmentation an almanac exists to fix.

**The skill owns the method; the repo's README owns local convention.** Where they
disagree about the admission tests, verification, or procedure, the skill wins. Where
they disagree about something the README claims as repo-local — the file format, the
wrap width, destinations — the README wins. This is the reverse of the obvious
anti-drift instinct, and the reason matters: if each repo's README outranked the shared
method, one stale local copy would silently override a corrected rule, and drift would
resolve with the _worse_ copy winning. The two barely overlap by design, so there is
little to drift.

The cost, plainly: agents on tools that read `README.md` but cannot load skills get the
local rules and not the method. The template is written so that file stands alone as a
usable contract for them.

**No skill depends on a gated tool.** `audit` verifies entries by fanning them out to
ordinary subagents, or sequentially in the main thread when none are available —
parallelism is an optimization, never a runtime dependency. An earlier draft bundled a
Claude Code Workflow script for the fan-out and accepted the resulting asymmetry as a
cost; that was the wrong trade. The almanac exists because `.claude/CLAUDE.md` was
Claude-only and other tools saw nothing, and an audit that only some harnesses can run
reintroduces exactly that one layer up.

The price of dropping it is real and worth naming: the script hard-validated the verdict
schema at the subagent boundary, which is what stopped a worker returning `holds`
without evidence. That enforcement is now prose in the skill — four rules it instructs
you to restate in every worker prompt. Prose that holds everywhere beats a guarantee
that holds on one tool, but it is a guarantee downgraded to an instruction, and the
skill says so.

**Nothing writes to the almanac automatically.** No background summarizer, no
session-end capture, no auto-generated index. An agent cannot validate its own entry,
because whatever led it to write something wrong would equally lead it to approve it —
so every entry, every correction, and every deletion rides in a PR diff and gets
reviewed like code. `audit`'s analysis is read-only for the same reason; it proposes,
and a human approves.

**`verified` is only ever set by something that actually re-ran the check.** The entry
format has an optional `verified:` date meaning exactly one thing: someone ran the
`verify` line on that date and the claim held. `audit` is the only process licensed to
set it, since it is the only one that runs those lines — and it still goes through the
confirmation gate and the PR, quoting the command and its verbatim output per entry. A
freshness signal that decouples from an actual re-check is worse than no signal, because
it launders a stale fact as a current one.

**No index, and no frontmatter beyond the specified fields.** A shared index is a merge
conflict between concurrent sessions that silently duplicates or drops content;
filenames state claims, so `ls` and `grep` are the index. Git supplies history and
modification times, and every extra field rots — in particular there is no `confidence`
and no `status`, because an entry you aren't confident about should not exist.

## Not in this release

- **`almanac:init`** — bootstrapping is two manual steps today (copy the template, add
  the trigger). Making it a skill is the plan for the next release, and it is also what
  makes template drift detectable rather than silent.
- **Adapters for other tools.** The skills are written repo-agnostic and stack-neutral,
  but packaging for Codex or Gemini waits until something needs it.

## Development

`docs/almanac/` in this repo is a live almanac, not a copy of the template for
demonstration — the plugin is expected to work on itself. It starts empty, and that is
the expected outcome: most branches teach you nothing worth recording.

The canonical contract text is `templates/almanac/README.md`; this repo's copy is an
instance of it, and `just drift` fails if they diverge outside the local block. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
