"""Repo-wide checks that span harnesses.

The per-harness manifest rules live in `test_manifests.py`, against `tools.manifests`.
What is left here is what only makes sense across the whole set — agreement between
harnesses, and the revision stamp that makes an adopter's stale copy diagnosable.

This module used to run `scripts/*` as subprocesses and assert on exit codes. The
checks are importable functions now, so the shell is no longer an intermediate layer.
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
