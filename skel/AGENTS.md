# AGENTS.md

Always-applicable instructions for agents working in this repository. This is the
top-level instruction file.

## Project

`skinner` is a Python package. `uv` manages the application, `just` manages the project:
`just setup` syncs the environment, `just check` lints and checks formatting,
`just test` runs the suite, and `just preflight` runs both.

## The almanac

[`docs/almanac/`](docs/almanac/) is this repository's operating knowledge: the facts it
learned the hard way and the rules it holds you to, one claim per file. It is
authoritative, and [docs/almanac/README.md](docs/almanac/README.md) governs the details.

**Run `ls docs/almanac/` before anything else, every session.** The filenames state the
claims, so the listing alone tells you both what this repository knows and what it
requires of you. Carry the titles; load a body only when one bears on what you are about
to do.

That listing is the index and there is no other. Conventions this repository requires
are entries, not sections in this file — so do not look for them here, and do not
restate one here when you find it there. Two copies of a rule diverge, and the stale one
wins whichever is read first.

Beyond the startup listing, consult it when:

- Something isn't behaving as expected. Grep it _before_ you start investigating, not
  after you're stuck — it's one command and it may end the investigation.
- You're about to do something whose failure would be silent or costly to undo.

One keyword grep is enough — `grep -rl --exclude=README.md <keyword> docs/almanac/`, or
`rg -l --glob '!README.md'`. Skip `README.md`: it is the contract rather than a claim,
and its worked examples match almost any probe. If nothing hits, move on.

**Record an entry when** you finish being surprised — a debugging session that ended in
"oh, _that's_ why," or a green build that hid a real failure — or when a convention
becomes binding here and an agent would otherwise meet it too late. Follow
[docs/almanac/README.md](docs/almanac/README.md).

Before you finish a branch, ask explicitly: _did this teach us anything an entry should
carry?_ Answer it out loud, even when the answer is no. Most branches produce no entry —
zero is a normal outcome, and an invented one is worse than none.
