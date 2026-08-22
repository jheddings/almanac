"""A `verify` line states a check *and* what would refute it.

`record` teaches that a verify line which merely locates the subject passes forever,
including after the behavior changes — and that a bare command tells the next agent what
to run but not what would count as a refutation. The canonical template violated both
rules, offering almost exactly the string `record` gives as its Bad example. This lint
is that teaching, applied mechanically.
"""

from __future__ import annotations

import pytest

from tests.support import almanac

# Phrases that name an expected observation. Deliberately about *outcomes*, not about
# what was run — "returns nothing" is a refutable claim, "check the workflow" is not.
OBSERVATION_PHRASES = (
    "returns",
    "return ",
    "exits",
    "exit ",
    "prints",
    "print ",
    "outputs",
    "no matches",
    "no match",
    "nothing",
    "no output",
    "no rows",
    "rows",
    "empty",
    "is absent",
    "is present",
    "succeeds",
    "fails",
    "shows",
    "reports",
    "lists",
    "contains no",
)


def lint_verify(value: str) -> list[str]:
    """Return reasons the verify line falls short. Empty means it clears the bar."""
    problems = []

    if not almanac.BACKTICKED_RE.search(value):
        problems.append(
            "no backticked command — state the check as something runnable, not a "
            "description of where to look"
        )

    lowered = value.lower()
    if not any(phrase in lowered for phrase in OBSERVATION_PHRASES):
        problems.append(
            "no expected observation — say what would count as a refutation "
            '("returns nothing", "exits 1", "prints warn")'
        )

    return problems


def _verify_values():
    """Every verify line in the repo: real entries plus the docs' examples."""
    found = []
    for path in almanac.entry_paths():
        data = almanac.parse_frontmatter(path.read_text()) or {}
        if isinstance(data.get("verify"), str):
            found.append((path.name, data["verify"]))
    for doc, block in almanac.example_frontmatter():
        data = almanac.parse_frontmatter(block) or {}
        if isinstance(data.get("verify"), str):
            relative = doc.relative_to(almanac.REPO_ROOT)
            found.append((f"{relative} (example)", data["verify"]))
    return found


VERIFY_VALUES = _verify_values()


def test_there_are_verify_lines_to_lint():
    assert VERIFY_VALUES, "no verify lines found — extraction is broken or vacuous"


@pytest.mark.parametrize("case", VERIFY_VALUES, ids=lambda c: c[0])
def test_verify_line_is_discriminating(case):
    source, value = case
    assert lint_verify(value) == [], f"{source}: {value!r}"


# ---- The lint must reject what the skill calls bad --------------------------------

BAD = [
    # The exact anti-pattern the template shipped with.
    "check the deploy workflow for `--include-all` on the db push step",
    # record's own Bad example: locates the subject, states no observation.
    "`grep -n 'db push' .github/workflows/deploy.yaml`",
    # Prose with no runnable check at all.
    "look at the CI config",
]

GOOD = [
    # record's Good example.
    "`grep -rn -- '--include-all' .github/workflows/` returns nothing",
    "`npx vitest run` exits 1 with `No test files found`",
    "`psql -c 'SELECT 1 FROM cron.job'` returns no rows",
]


@pytest.mark.parametrize("value", BAD)
def test_lint_rejects_non_discriminating_lines(value):
    assert lint_verify(value), f"lint accepted a known-bad verify line: {value!r}"


@pytest.mark.parametrize("value", GOOD)
def test_lint_accepts_discriminating_lines(value):
    assert lint_verify(value) == [], f"lint rejected a known-good line: {value!r}"
