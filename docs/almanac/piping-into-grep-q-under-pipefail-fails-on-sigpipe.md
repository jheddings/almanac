---
title: Piping into `grep -q` under `set -o pipefail` fails intermittently on SIGPIPE
kind: fact
recorded: 2026-08-20
source:
    "Diagnosing an intermittent `just cursor bundle` failure on `feat/cursor-plugin`,
    which an agent had already dismissed as flaky"
verify: "running `seq 1000000 | grep -q 1` under `set -o pipefail` exits 141, not 0"
verified: 2026-08-20
tags: [bash, pipefail, packaging, justfile, silent-failure, intermittent]
---

`grep -q` exits as soon as it matches. The command still writing into the pipe then
takes SIGPIPE and exits 141, and `set -o pipefail` makes 141 the status of the whole
pipeline — so a pipeline that found what it was looking for reports failure. Whether it
fires depends on how much the producer had left to write, so the same command passes and
fails on the same input.

**Why it matters:** the bundle recipes check a built archive with
`unzip -l "$out" | grep -q ...` under `set -euo pipefail`. The failure is intermittent
and the error message points at the wrong thing —
`error: archive has no .claude-plugin/plugin.json` on an archive that contains it. It
cost one agent a diagnosis: it hit the failure, re-ran after a clean, saw it pass,
concluded "first bundle failure looks flaky", and moved on.

The direction that matters more is the quiet one. In a guard written as
`if unzip -l "$out" | grep -q 'docs/'; then ...`, a SIGPIPE 141 reads as "no match" — so
an exclusion check silently passes while the thing it forbids is present in the archive.

**What to do:** capture the output first and match against a herestring, so nothing is
left writing into a closed pipe.

```bash
listing=$(unzip -l "$out")
grep -q '\.claude-plugin/plugin\.json' <<<"$listing" || { ...; }
```

Reaching for `grep -c`, or dropping `-q`, works for the same reason — the reader
consumes all its input. Do not "fix" it by removing `pipefail`.
