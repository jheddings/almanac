---
title: Unsetting git's config files does not simulate a machine with no identity
kind: fact
recorded: 2026-08-25
source:
    "Reproducing a CI failure in the skel scaffold locally — the test written to
    reproduce it passed, and said nothing"
verify:
    "`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null git var GIT_AUTHOR_IDENT
    2>&1` names an address git built from the account and the hostname — printed as the
    identity where derivation succeeds, quoted in the `auto-detect` error where it does
    not — rather than reporting the config as unset"
verified: 2026-08-26
tags: [git, ci, testing, silent-failure]
---

With `user.name` and `user.email` unset, git does not give up — it derives an author
identity from the account's full name and the machine's hostname. Whether that
derivation succeeds depends on the host, so pointing `GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` at `/dev/null` reproduces a machine with no configured identity but
not one where git cannot invent a usable one.

The derivation runs either way, which is why the check above works on both kinds of
host: where it succeeds git prints the derived identity, and where it fails git still
quotes the candidate it built —
`unable to auto-detect email address (got 'user@host.(none)')`. What never appears is a
complaint that the config is unset.

**Why it matters:** a test written to prove code does not depend on ambient git identity
will pass locally on that invented identity, which is a green that carries no
information. The code can still fail wherever the derivation does not succeed, and the
test that was supposed to catch it reported success.

**What to do:** assert the identity the code actually produced —
`git log -1 --format='%an <%ae>'` — rather than trying to remove the ambient one. An
assertion about the output holds on every host; an assertion about the environment holds
only on yours.
