---
title: Unsetting git's config files does not simulate a machine with no identity
kind: fact
recorded: 2026-08-25
source:
    "Reproducing a CI failure in the skel scaffold locally — the test written to
    reproduce it passed, and said nothing"
verify:
    "`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git var GIT_AUTHOR_IDENT`
    prints an identity instead of failing"
verified: 2026-08-25
tags: [git, ci, testing, silent-failure]
---

With `user.name` and `user.email` unset, git does not give up — it derives an author
identity from the account's full name and the machine's hostname. Whether that
derivation succeeds depends on the host, so pointing `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` at `/dev/null` reproduces a machine with no configured identity but
not one where git cannot invent a usable one.

**Why it matters:** a test written to prove code does not depend on ambient git identity
will pass locally on that invented identity, which is a green that carries no
information. The code can still fail wherever the derivation does not succeed, and the
test that was supposed to catch it reported success.

**What to do:** assert the identity the code actually produced —
`git log -1 --format='%an <%ae>'` — rather than trying to remove the ambient one. An
assertion about the output holds on every host; an assertion about the environment holds
only on yours.
