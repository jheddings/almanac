"""Repo-wide checks that span harnesses.

Per-harness manifest rules live in `test_manifests.py`. What is here holds across the
whole set: agreement between harnesses, and the revision stamp that makes an adopter's
stale copy diagnosable.
"""

from __future__ import annotations

import json
import re

from tests.support import almanac
from tools import drift, harnesses, manifests


def _relative(path):
    return str(path.relative_to(almanac.REPO_ROOT))


def test_every_declared_harness_passes_its_manifest_checks():
    problems = []
    for harness in harnesses.load().values():
        problems += manifests.check(harness)
    assert problems == [], "\n".join(problems)


def test_the_almanac_readme_has_not_drifted_from_the_template():
    assert drift.check() == [], "".join(drift.check())


def test_template_and_instance_carry_the_same_revision_stamp():
    """The stamp is what makes an adopter's stale copy diagnosable.

    It sits outside the local block, so the drift check already compares it — but that
    check would also pass if the stamp vanished from both. This asserts it exists.
    """
    stamp = re.compile(r"<!-- almanac-template: (\d+) -->")

    template = stamp.search(almanac.TEMPLATE_ALMANAC.read_text())
    instance = stamp.search((almanac.LIVE_ALMANAC / "README.md").read_text())

    assert template, "the canonical template has no revision stamp"
    assert instance, "this repo's almanac README has no revision stamp"
    assert template.group(1) == instance.group(1), (
        f"revision mismatch: template {template.group(1)}, instance {instance.group(1)}"
    )


def test_platform_manifests_were_discovered():
    """Guard the guard: an empty glob would make the check below vacuous."""
    assert almanac.platform_manifests(), "no .<platform>-plugin/plugin.json found"


def test_every_platform_manifest_agrees_on_the_plugin_name():
    """Discovered rather than enumerated, so a new harness is data, not a new test.

    Each harness places a manifest at `.<platform>-plugin/plugin.json` pointing at the
    same `skills/` directory. A name that disagrees between them breaks installation on
    whichever one is wrong. The per-harness checks compare a manifest to its own
    marketplace; only this one compares harnesses to each other.
    """
    names = {
        _relative(m): json.loads(m.read_text()).get("name")
        for m in almanac.platform_manifests()
    }
    assert len(set(names.values())) == 1, f"manifests disagree on name: {names}"


def test_declared_skills_paths_exist():
    """A manifest may point at a skills directory; if it does, it must be there.

    Deliberately broader than the table's `path_keys`: this catches a manifest that
    starts declaring `skills` before anyone teaches the table to check it.
    """
    for manifest in almanac.platform_manifests():
        declared = json.loads(manifest.read_text()).get("skills")
        if not declared:
            continue
        resolved = (almanac.REPO_ROOT / declared.lstrip("./")).resolve()
        assert resolved.is_dir(), (
            f"{_relative(manifest)} declares skills at {declared!r}, which is not a "
            "directory"
        )


def test_the_contract_and_the_scope_test_agree_on_the_subject():
    """Scope's *whom* is the one piece of method the contract delegates.

    Two files have to name the same concept for the delegation to work: the template
    tells an adopter to declare a subject, and `record`'s question 6 reads against it.
    If either stops saying so, the skill asks a question nothing answers, and the old
    failure returns — a repo with an unusual shape redefining a test it does not own.

    Match on the concept rather than the exact bytes: prettier reflows this prose and
    emphasis moves around, so a literal `"**subject**"` would fail on a rewrap and pass
    on a rewrite that dropped the delegation.
    """
    template = _prose(almanac.TEMPLATE_ALMANAC.read_text())
    assert "almanac's subject" in template, (
        "the canonical contract no longer names the almanac's subject"
    )
    assert "unless the local block" in template, (
        "the contract names a subject but no longer says the local block declares it, "
        "so an adopter has no way to set one"
    )

    record = _prose(next(s for s in almanac.skills() if s.name == "record").body)
    assert "almanac's subject" in record, (
        "record's scope test no longer reads against the declared subject"
    )


def _prose(text):
    """Collapse emphasis and line breaks so a phrase survives a prettier rewrap."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("_", ""))
