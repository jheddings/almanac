"""Verify this repo's almanac README is still an instance of the shipped template.

The template at templates/almanac/README.md is canonical. This repo's own almanac at
docs/almanac/README.md is an instance of it: identical everywhere except inside the
block delimited by the `almanac:local` markers, which is where a repository states its
own destinations for content that does not belong in the almanac.

Divergence anywhere outside that block means the two copies have drifted, and drift is
exactly the failure the precedence rule exists to prevent.
"""

from __future__ import annotations

import difflib
from pathlib import Path

from tools.harnesses import REPO_ROOT

TEMPLATE = REPO_ROOT / "templates" / "almanac" / "README.md"
# Every copy of the canonical contract in this tree. The live almanac is this repo's
# own; the fixture's is what a harness-test run adopts, and an uncovered fixture goes
# stale against the contract it exists to test.
INSTANCES = (
    REPO_ROOT / "docs" / "almanac" / "README.md",
    REPO_ROOT / "skel" / "docs" / "almanac" / "README.md",
)

OPEN = "<!-- almanac:local -->"
CLOSE = "<!-- /almanac:local -->"


class DriftError(Exception):
    pass


def shared_text(path: Path) -> str:
    """The file with its local block collapsed to the markers alone."""
    text = path.read_text()
    if text.count(OPEN) != 1 or text.count(CLOSE) != 1:
        raise DriftError(f"{path}: expected exactly one {OPEN} ... {CLOSE} block")
    head, _, rest = text.partition(OPEN)
    _, _, tail = rest.partition(CLOSE)
    return f"{head}{OPEN}{CLOSE}{tail}"


def compare(template: Path, instance: Path) -> list[str]:
    """Unified diff of the shared text, empty when the two agree."""
    for path in (template, instance):
        if not path.is_file():
            raise DriftError(f"{path}: missing")

    left, right = shared_text(template), shared_text(instance)
    if left == right:
        return []

    return list(
        difflib.unified_diff(
            left.splitlines(keepends=True),
            right.splitlines(keepends=True),
            fromfile=str(template),
            tofile=str(instance),
        )
    )


def check() -> list[str]:
    problems = []
    for instance in INSTANCES:
        problems += compare(TEMPLATE, instance)
    return problems
