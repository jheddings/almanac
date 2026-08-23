# almanac

Skills for keeping an **almanac** — a directory of facts your agents discovered the hard
way, recorded so nobody learns them twice. Packaged for Claude Code, Codex, Antigravity,
and Cursor; the skills themselves assume no particular harness.

An almanac entry is a silent failure mode, a tool that lies, a constraint that isn't
visible from the code. Its subject is as often the CI, the build tooling, or the agent
harness as the code itself — what matters is that the fact holds for anyone working in
that repository. Not documentation, not a plan: a claim a future agent will act on
without re-deriving it. One fact per file, filename states the claim, and the directory
listing is the index.

This plugin initializes the repository-level pieces and carries the two procedures that
keep such a directory honest. Consulting the almanac is deliberately **not** a skill —
see [Design positions](#design-positions).

## Skills

| Skill            | Use it when                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `almanac:init`   | You want to add or repair an almanac in a repository                    |
| `almanac:record` | You just finished being surprised, and something durable came out of it |
| `almanac:audit`  | You want to know whether the recorded facts are still true              |

`record` owns the admission tests, the category gate, and how to write a `verify` line
that fails when its claim fails. `audit` re-runs every entry's `verify` line and sorts
the results into `holds` / `falsified` / `unverifiable`, then proposes corrections
behind a confirmation gate.

## Installation

### Claude Code

```bash
/plugin marketplace add jheddings/almanac
/plugin install almanac@almanac
```

If the skills are not available to the agent immediately after installing, start a new
session. `claude plugin details almanac` inventories what the install actually
registered, so a plugin listing all three skills there but unavailable in the running
session is session state rather than a failed install.

### Cursor

Install from this repository as a Cursor Plugin (IDE or Agent CLI), for example:

- symlink or copy the repo into `~/.cursor/plugins/local/almanac`, or
- `agent --plugin-dir /path/to/almanac` (the Agent CLI also accepts
  `cursor agent --plugin-dir`), or
- import the repo as a team marketplace source pointing at `./`

A distributable archive is produced by `just bundle cursor`
(`dist/almanac-cursor-plugin-<version>.zip`). Commands live under
`.cursor-plugin/commands/` so a Claude marketplace install of the same tree does not
auto-discover them.

### Codex

The Codex manifest packages the shared skills, but this is a distribution stub: it has
no marketplace entry or installation flow yet.

### Antigravity (`agy`)

```bash
just bundle agy
agy plugin install dist/almanac-agy
```

## Setup

From the repository you want to adopt the almanac, ask your agent:

> Initialize the almanac in this repository.

`almanac:init` inspects the repository, proposes a local contract based on the canonical
template, and adds the consult trigger to shared agent instructions. It shows the exact
files and repository-local destinations before writing anything, and a second invocation
should propose no changes. Cursor's `/init` command (when the plugin is loaded) is a
stub that names that skill; it does not duplicate the procedure.

The resulting `docs/almanac/README.md` retains its `<!-- almanac-template: N -->`
comment. It records which revision of the shared contract the repository adopted, while
the `<!-- almanac:local -->` block remains owned by that repository.

### Manual setup

`almanac:init` is a convenience, not a requirement. The contract text is one ordinary
file, so a repository can adopt an almanac on any harness. From a checkout of this
repository:

1. Copy [`templates/almanac/README.md`](templates/almanac/README.md) to
   `docs/almanac/README.md` in the adopting repository.
2. Replace only the `<!-- almanac:local -->` block with destinations that actually exist
   there. Omit any category whose destination is unknown rather than inventing one.
3. Add the consult trigger to the repository's `AGENTS.md`; this repo's
   [almanac section](AGENTS.md#the-almanac) is a starting point.

`record` and `audit` are ordinary [Agent Skills](https://agentskills.io/specification) —
no bundled executables, no hooks, nothing resolved from a plugin root — so a harness
that reads `skills/<name>/SKILL.md` can load them straight from that checkout. `init`
resolves the canonical template from `${CLAUDE_PLUGIN_ROOT}` if set, otherwise
`templates/almanac/README.md` relative to the workspace, otherwise the plugin's
installed directory as the harness exposes it. The steps above remain for checkouts
where none of those apply.

`record` and `audit` prefer `docs/almanac/`, fall back to discovering another live
`almanac/README.md`, and stop if none exists. They never initialize one as a side
effect.

## Design positions

These are choices, not accidents. Each of them costs something, and the cost is stated.

**Consulting is a trigger, not a skill.** A skill only fires when something in context
suggests loading it, and the entries worth most are silent failures you'd never think to
search for — so the moment you most need the almanac is the moment nothing prompts you
to look. That has to live in always-on instructions. It also has to work under Codex,
Cursor, and anything else that reads `AGENTS.md` but cannot load a skill. There is
deliberately no `almanac:consult`, and deliberately no session-start hook: a hook that
lists entries would be Claude-only, which is the fragmentation an almanac exists to fix.

**Initialization proposes shared state; it does not silently install it.** The template
and consult trigger are durable, cross-agent repository state, but the destinations in
the template's local block are decisions only the adopting repository can make.
`almanac:init` inspects real destinations, shows its proposal, and waits for approval.
It never invents a directory or seeds an example entry.

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

**The subject is declared, and defaults to the repository.** Scope — _would this hold
for everyone else?_ — needs an _everyone else_, and for the common case that is CI plus
whoever clones the repo. It is not the only case: a workspace holding several
independent checkouts has agents rediscovering the same environment over and over, and
an almanac whose subject is that workspace is answering a real question. So the
almanac's `README.md` declares its subject inside the local block, and `record`'s scope
test reads against whatever is declared. The default is unchanged, and a fact true only
of one person's machine is still out.

The cost, plainly: scope admission is method, and method is the skill's to own. This is
the one piece of it the shared contract delegates, and the delegation has to be narrow
and explicit — otherwise a repo with an unusual shape quietly redefines a test it does
not control, which is the drift the precedence rule exists to prevent.

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
`verify` line on that date and the claim held. That is the whole rule, and it binds
everyone — an agent who runs a verify line while consulting an entry may bump it, since
the evidence is just as real. What `audit` adds is that it is the only thing which does
this _systematically_, across every entry, so it is what keeps the field from decaying
into decoration. Its bumps still go through the confirmation gate and the PR, quoting
the command and verbatim output per entry.

A freshness signal that decouples from an actual re-check is worse than no signal,
because it launders a stale fact as a current one. Restricting the write to the audit
would not strengthen that rule — it would only discard real evidence when someone else
produced it.

**No index, and no frontmatter beyond the specified fields.** A shared index is a merge
conflict between concurrent sessions that silently duplicates or drops content;
filenames state claims, so `ls` and `grep` are the index. Git supplies history and
modification times, and every extra field rots — in particular there is no `confidence`
and no `status`, because an entry you aren't confident about should not exist.

## Not in this release

- **Codex distribution.** The Codex manifest exposes the shared skills, but marketplace
  publishing and installation guidance are intentionally deferred.
- **Adapters beyond the four harnesses.** `record` and `audit` are repo-agnostic and
  stack-neutral and load from a checkout today; see [Manual setup](#manual-setup).
  Purpose-built packaging for other harnesses, such as Gemini, waits until something
  needs it.
- **Cross-repository entries.** An almanac is shared across agents and harnesses, but
  only within one subject: a fact about a CI runner learned in one repo is learned again
  in the next. Pooling entries is a real gap and not an oversight — `verify` means "run
  this against this tree", and review means "it rides in a PR diff", and both are
  repository-shaped. Nothing here pretends to solve it yet.

## Development

`docs/almanac/` in this repo is a live almanac, not a copy of the template for
demonstration — the plugin is expected to work on itself. It starts empty, and that is
the expected outcome: most branches teach you nothing worth recording.

The canonical contract text is `templates/almanac/README.md`; this repo's copy is an
instance of it, and `just drift` fails if they diverge outside the local block. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
