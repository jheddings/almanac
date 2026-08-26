# almanac

Skills for keeping an **almanac** — a directory holding a repository's operating
knowledge, recorded so nobody learns it twice. Packaged for Claude Code, Codex,
Antigravity, and Cursor; the skills themselves assume no particular harness.

Entries come in two kinds. A **fact** is a silent failure mode, a tool that lies, a
constraint that isn't visible from the code — something reality can refute, so it
carries a `verify` line an audit re-runs. A **rule** is something the repository
requires of everyone who works in it: commit format, branch naming, where work happens.
Not documentation, not a plan: a claim a future agent acts on without re-deriving it.
Both are almanac material in the old sense of the word: what was observed here,
alongside what to do about it.

One claim per file, the filename states the claim, and **the directory listing is the
index** — read cold at the start of a session, with bodies loaded only when a title
bears on what you are about to do.

This plugin initializes the repository-level pieces and carries the two procedures that
keep such a directory honest. Consulting the almanac is deliberately **not** a skill —
see [Design positions](#design-positions).

## Skills

| Skill            | Use it when                                                            |
| ---------------- | ---------------------------------------------------------------------- |
| `almanac:init`   | You want to add or repair an almanac in a repository                   |
| `almanac:record` | You just finished being surprised, or a convention became binding here |
| `almanac:audit`  | You want to know whether the recorded facts are still true             |

`record` owns the admission tests, the category gate, the fact/rule decision, and how to
write a `verify` line that fails when its claim fails. `audit` re-runs every _fact's_
`verify` line and sorts the results into `holds` / `falsified` / `unverifiable`, then
proposes corrections behind a confirmation gate. Rules come back `unauditable`; see
below.

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
resolve with the _worse_ copy winning.

The overlap between them is deliberate and bounded: the template states the three
admission tests and the scope question, because an agent has to be able to tell whether
a finding is worth pursuing before it loads anything. The skill carries those tests in
full, with the reasoning and the failure modes. A difference in wording is expected; a
difference in substance is a bug.

**A skill-less agent consults, and reports rather than records.** Consulting runs off
the README alone — read the listing, load an entry, follow a rule — and that is the path
every agent takes every session. Recording does not: the method is not reconstructable
from the contract, an agent cannot review its own entry, and a plausible entry that is
subtly wrong costs more than no entry at all, because it gets trusted instead of
checked. So the template tells an agent that cannot load the skill to name the finding,
say plainly that it belongs in the almanac, and stop.

The cost, plainly: those agents surface findings they cannot file, and somebody with the
plugin has to file them. That is the trade — an unrecorded finding is recoverable from a
transcript, an invented one is not.

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

The one target where that has nothing to attach to is a subject under no version
control, where there is no diff to ride in. The safeguard does not lapse there; it moves
to the writer, who states in their report what they wrote and why, so the operator can
still check it. `almanac:init` says so when it proposes such an almanac. A review a
human has to remember to ask for is weaker than one the tooling forces, and that is the
price of admitting a subject git does not cover.

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

**The almanac carries rules as well as facts.** A convention only helps if it is loaded
at the moment it applies, and an always-on instruction file pays for every rule on every
turn whether or not it is relevant. Entries invert that: the filename index is one line
per claim, always in context, and the body arrives only when the title bears on what is
happening. So a required rule is an entry — `kind: rule` — and the listing becomes the
whole index of how to work here rather than half of it, with the other half in a file
the agent may or may not have read to the bottom.

The cost, plainly, and it is the largest one here: **a rule cannot be audited.** A fact
has a `verify` line, so `audit` re-runs it and a stale fact is caught mechanically. A
rule has nothing to re-run — a check that people follow it measures compliance, not
truth, and reporting that as a verdict would be worse than reporting nothing. So rules
decay in exactly the way this directory exists to prevent: confidently worded after the
decision behind them changed, with only a human reading the listing to catch it. The
schema enforces the split (a `kind: rule` entry may not carry `verify` or `verified`)
and `audit` names every rule it could not reach, so the gap is visible rather than
silent — but visible is not covered.

Two smaller costs. Retrieval now rests entirely on the title: an entry whose slug does
not fire at the right moment is invisible, and that failure is silent too. And a longer
listing is a weaker listing — the directory works as a cold read because every line is
worth reading, and rules dilute a signal that facts alone kept dense.

**The name did not stop fitting when the scope widened.** Admitting rules looks like
drift away from "almanac," and it is the reverse. An almanac was never a book of facts
alone: it pairs what was observed with the practice that follows from it — the tables
and when to plant — for one place, one season, and an audience that consults it before
acting rather than reading it front to back. A directory holding facts and rules,
indexed by filename and opened at the moment one applies, is that shape rather than a
departure from it.

The cost, plainly: the word does not _say_ "binding." A reader meeting it cold hears
weather and trivia, and nothing in the name warns them that half the listing is
enforceable. So the contract carries that weight instead — `kind` is enforced by schema
rather than described in prose, a rule states the moment it applies in its opening line,
and `audit` has to name every rule it could not reach.

**No index, and no frontmatter beyond `title`, `kind`, `recorded`, `source`, `verify`,
`verified`, and `tags`.** A shared index is a merge conflict between concurrent sessions
that silently duplicates or drops content; filenames state claims, so `ls` and `grep`
are the index. Git supplies history and modification times, and every extra field rots —
in particular there is no `confidence` and no `status`, because an entry you aren't
confident about should not exist.

`kind` is the one field admitted since, and it was not free: it exists because facts and
rules need different maintenance, and a field that distinguishes them is the price of
keeping both in one directory. It earns its place by being enforced rather than
descriptive — the schema rejects a rule carrying `verify`, so the two tiers cannot
quietly blur into one.

## Not in this release

- **Codex distribution.** The Codex manifest exposes the shared skills, but marketplace
  publishing and installation guidance are intentionally deferred.
- **Adapters beyond the four harnesses.** `record` and `audit` are repo-agnostic and
  stack-neutral and load from a checkout today; see [Manual setup](#manual-setup).
  Purpose-built packaging for other harnesses, such as Gemini, waits until something
  needs it.
- **Cross-repository entries.** An almanac is shared across agents and harnesses, but
  only within one subject, and for almost every almanac that subject is one repository:
  a fact about a CI runner learned in one repo is learned again in the next. Pooling
  entries is a real gap and not an oversight — `verify` means "run this against this
  tree", and review means "it rides in a PR diff", and both are repository-shaped.
  Nothing here pretends to solve it yet.

## Development

`docs/almanac/` in this repo is a live almanac, not a copy of the template for
demonstration — the plugin is expected to work on itself. It starts empty, and that is
the expected outcome: most branches teach you nothing worth recording.

The canonical contract text is `templates/almanac/README.md`; this repo's copy is an
instance of it, and `just drift` fails if they diverge outside the local block. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
