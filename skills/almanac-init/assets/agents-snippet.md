## The almanac

`docs/almanac/` records durable facts discovered the hard way: silent failure modes, tools that
behave differently than documented, and constraints not visible from the code.

Consult it when starting work in an unfamiliar area, when something behaves unexpectedly, or before
an operation whose failure would be silent or costly. List the directory once, then grep by keyword
when relevant; the filenames state the claims.

Record an entry after resolving a genuine surprise that is durable, empirically discovered,
and costly to rediscover. Follow `docs/almanac/README.md`. Before finishing a branch, say
whether the work taught an almanac-worthy fact, even when the answer is no.
