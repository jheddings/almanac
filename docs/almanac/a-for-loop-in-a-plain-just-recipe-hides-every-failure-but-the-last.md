---
title: A `for` loop in a plain `just` recipe hides every failure but the last
kind: fact
recorded: 2026-09-11
source:
    "The `validate` recipe looped over `skills/*/` and exited 0 with a failing skill in
    an earlier directory; reproduced on `feat/assess-skill` with a two-line justfile"
verify:
    "`{ echo 'x:'; echo '    for i in a b; do test $i = b; done'; } > /tmp/jf && just -f
    /tmp/jf x` exits 0 although the first iteration fails; flipping the comparison to `=
    a`, so the last iteration is the failing one, exits 1"
verified: 2026-09-11
tags: [just, justfile, shell, ci, checks, silent-failure]
---

`just` runs a plain recipe under `sh -cu` — no `-e` — and a `for` loop exits with the
status of its **last** iteration alone. A command that fails in any earlier iteration
leaves no trace in the recipe's exit status.

**Why it matters:** it fails as success. The `validate` recipe ran
`for dir in skills/*/; do npx skills-ref validate "$dir"; done`, so an invalid skill in
any directory but the last one passed `just check` and would have shipped. The validator
printed its complaint and `just` printed nothing, because from `just`'s side nothing
went wrong. Loops over directories, packages, or harnesses are exactly where this bites,
and they are exactly the recipes whose whole job is to fail on one bad member.

**What to do:** make any looping recipe a shebang recipe with `set -euo pipefail`, so
`-e` turns the failing iteration into a failing recipe.

```just
validate:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in skills/*/ .claude/skills/*/; do
        [ -d "$dir" ] || continue
        npx skills-ref validate "$dir"
    done
```

`set -e` does not reach into the loop from a `set -e` written on a preceding line of a
plain recipe either — `just` runs each line of a non-shebang recipe as its own shell, so
the shebang form is what makes the setting apply to the loop at all.

Related:
[`piping-into-grep-q-under-pipefail-fails-on-sigpipe`](piping-into-grep-q-under-pipefail-fails-on-sigpipe.md)
is the same class from the other direction — there the shell reported a failure that was
not one, here it reports a success that was not one.
