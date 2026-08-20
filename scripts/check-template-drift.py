#!/usr/bin/env python3
"""Verify this repo's almanac README is still an instance of the shipped template.

The template at templates/almanac/README.md is canonical. This repo's own almanac at
docs/almanac/README.md is an instance of it: identical everywhere except inside the
block delimited by the `almanac:local` markers, which is where a repository states its
own destinations for content that does not belong in the almanac.

Divergence anywhere outside that block means the two copies have drifted, and drift is
exactly the failure the precedence rule exists to prevent. Fail loudly.
"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path

TEMPLATE = Path("templates/almanac/README.md")
INSTANCE = Path("docs/almanac/README.md")

OPEN = "<!-- almanac:local -->"
CLOSE = "<!-- /almanac:local -->"


def shared_text(path: Path) -> str:
    """Return the file with its local block collapsed to the markers alone."""
    text = path.read_text()
    if text.count(OPEN) != 1 or text.count(CLOSE) != 1:
        sys.exit(f"{path}: expected exactly one {OPEN} ... {CLOSE} block")
    head, _, rest = text.partition(OPEN)
    _, _, tail = rest.partition(CLOSE)
    return f"{head}{OPEN}{CLOSE}{tail}"


def main() -> int:
    for path in (TEMPLATE, INSTANCE):
        if not path.is_file():
            sys.exit(f"{path}: missing")

    template, instance = shared_text(TEMPLATE), shared_text(INSTANCE)
    if template == instance:
        print(f"{INSTANCE} matches {TEMPLATE} outside the local block")
        return 0

    diff = difflib.unified_diff(
        template.splitlines(keepends=True),
        instance.splitlines(keepends=True),
        fromfile=str(TEMPLATE),
        tofile=str(INSTANCE),
    )
    sys.stdout.writelines(diff)
    sys.stdout.flush()
    print(
        f"\nerror: {INSTANCE} has drifted from {TEMPLATE} outside the local block.\n"
        "The template is canonical. Either port the change to it, or move the text "
        f"inside the {OPEN} block if it is genuinely repo-local.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
