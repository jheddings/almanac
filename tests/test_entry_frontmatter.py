"""Every almanac entry satisfies the frontmatter contract the template states.

This repo's almanac is deliberately empty, so most of these parametrize over nothing
today. They exist so the contract is enforced the moment an entry lands — and so the
"no frontmatter fields beyond those specified" invariant is a failing build rather than
a sentence somebody has to remember.
"""

from __future__ import annotations

import datetime

import pytest

from tests.support import almanac


def check_entry_frontmatter(data: dict) -> list[str]:
    """Return a list of contract violations. Empty means conforming."""
    problems = []

    missing = almanac.ENTRY_REQUIRED - data.keys()
    if missing:
        problems.append(f"missing required field(s): {sorted(missing)}")

    unknown = data.keys() - almanac.ENTRY_ALLOWED
    if unknown:
        problems.append(
            f"unknown field(s): {sorted(unknown)} — git supplies history, and every "
            "extra field rots"
        )

    for field in ("recorded", "verified"):
        if field in data and not isinstance(data[field], datetime.date):
            problems.append(f"{field} must be a date (YYYY-MM-DD), got {data[field]!r}")

    for field in ("title", "source", "verify"):
        if field in data and not isinstance(data[field], str):
            problems.append(f"{field} must be a string, got {data[field]!r}")

    kind = data.get("kind")
    if "kind" in data and kind not in almanac.ENTRY_KINDS:
        problems.append(
            f"kind must be one of {sorted(almanac.ENTRY_KINDS)}, got {kind!r}"
        )

    if kind == "rule":
        carried = sorted(almanac.FACT_ONLY_FIELDS & data.keys())
        if carried:
            problems.append(
                f"a rule may not carry {carried} — a check that a rule is followed "
                "measures compliance, not truth, and an audit would report the verdict "
                "as if it were about the claim"
            )

    if "title" in data and isinstance(data["title"], str) and not data["title"].strip():
        problems.append("title is empty")

    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            problems.append(f"tags must be a list of strings, got {tags!r}")

    return problems


@pytest.mark.parametrize(
    "path", almanac.entry_paths(), ids=lambda p: p.name if p else "none"
)
def test_entry_frontmatter_conforms(path):
    data = almanac.parse_frontmatter(path.read_text())
    assert data is not None, f"{path.name}: no frontmatter"
    assert check_entry_frontmatter(data) == [], f"{path.name}"


def test_entries_are_one_fact_per_file():
    """Filenames state claims, so a topic-shaped name is a smell worth catching."""
    for path in almanac.entry_paths():
        stem = path.stem
        assert stem == stem.lower(), f"{path.name}: filename must be lowercase"
        assert " " not in stem, f"{path.name}: filename must be kebab-case"
        assert "_" not in stem, f"{path.name}: filename must be kebab-case, not snake"
        assert len(stem.split("-")) >= 3, (
            f"{path.name}: a slug this short is naming a topic, not stating a claim"
        )


# ---- The checker itself must be able to fail -------------------------------------
#
# A validator that accepts everything passes forever. These are the almanac's own
# "write a verify line that fails when the claim fails" rule, applied to this suite.

GOOD = {
    "title": "Out-of-order migrations are silently skipped on deploy",
    "kind": "fact",
    "recorded": datetime.date(2026, 8, 15),
    "source": "PR #1129",
    "verify": "`grep -rn -- '--include-all' .github/workflows/` returns nothing",
    "verified": datetime.date(2026, 8, 16),
    "tags": ["migrations", "deploy"],
}


def test_checker_accepts_a_conforming_entry():
    assert check_entry_frontmatter(GOOD) == []


@pytest.mark.parametrize(
    "mutation, expected_substring",
    [
        ({"title": None}, "must be a string"),
        ({"recorded": "2026-08-15"}, "must be a date"),
        ({"confidence": "high"}, "unknown field"),
        ({"status": "draft"}, "unknown field"),
        ({"tags": "migrations"}, "list of strings"),
        ({"kind": "convention"}, "kind must be one of"),
        ({"kind": "rule"}, "may not carry"),
    ],
    ids=[
        "non-string title",
        "string date",
        "confidence field",
        "status field",
        "scalar tags",
        "unknown kind",
        "rule carrying verify",
    ],
)
def test_checker_rejects_violations(mutation, expected_substring):
    data = {**GOOD, **mutation}
    problems = check_entry_frontmatter(data)
    assert any(expected_substring in p for p in problems), problems


@pytest.mark.parametrize("field", sorted(almanac.ENTRY_REQUIRED))
def test_checker_rejects_missing_required_field(field):
    data = {k: v for k, v in GOOD.items() if k != field}
    assert any("missing required field" in p for p in check_entry_frontmatter(data))


def test_checker_accepts_a_conforming_rule():
    """A rule is a whole entry, not a fact with fields missing."""
    rule = {
        "title": "Branch names carry the commit type as a prefix",
        "kind": "rule",
        "recorded": datetime.date(2026, 8, 15),
        "source": "CONTRIBUTING.md, migrated 2026-08-15",
        "tags": ["git", "branches"],
    }
    assert check_entry_frontmatter(rule) == []


def test_every_entry_declares_a_kind_the_contract_names():
    """Guard against a kind that parses but nothing downstream handles."""
    for path in almanac.entry_paths():
        data = almanac.parse_frontmatter(path.read_text()) or {}
        assert data.get("kind") in almanac.ENTRY_KINDS, (
            f"{path.name}: kind is {data.get('kind')!r}"
        )
