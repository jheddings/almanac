"""The standalone check scripts, run as part of the suite.

`check-template-drift.py` and `check-manifests.sh` stay standalone so they can be
pre-commit hooks in an image without pytest. Wrapping them here means `just test` is one
command rather than three, and a failure shows up in the same report as everything else.
"""

from __future__ import annotations

import json
import re
import subprocess

import pytest

from tests.support import almanac

def _check_scripts():
    """Every repo check script, discovered rather than listed.

    A per-harness script lands with each new platform. Enumerating them here means the
    suite silently stops covering whichever one somebody forgot to add.
    """
    commands = []
    for script in sorted((almanac.REPO_ROOT / "scripts").iterdir()):
        if script.suffix == ".py":
            commands.append(["python3", f"scripts/{script.name}"])
        elif script.suffix == ".sh":
            commands.append([f"./scripts/{script.name}"])
    return commands


SCRIPTS = _check_scripts()


def test_check_scripts_were_discovered():
    assert SCRIPTS, "no check scripts found under scripts/"


@pytest.mark.parametrize("command", SCRIPTS, ids=lambda c: c[-1])
def test_check_script_passes(command):
    result = subprocess.run(
        command,
        cwd=almanac.REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{' '.join(command)} exited {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


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


def _relative(path):
    return str(path.relative_to(almanac.REPO_ROOT))


def test_platform_manifests_were_discovered():
    """Guard the guard: an empty glob would make the two checks below vacuous."""
    assert almanac.platform_manifests(), "no .<platform>-plugin/plugin.json found"


def test_every_platform_manifest_agrees_on_the_plugin_name():
    """Discovered rather than enumerated, so a new harness is data, not a new test.

    Each harness places a manifest at `.<platform>-plugin/plugin.json` pointing at the
    same `skills/` directory. A name that disagrees between them breaks installation on
    whichever one is wrong.
    """
    names = {
        _relative(m): json.loads(m.read_text()).get("name")
        for m in almanac.platform_manifests()
    }
    assert len(set(names.values())) == 1, f"manifests disagree on name: {names}"


def test_every_platform_manifest_carries_the_shared_version():
    """`VERSION` is the single source of truth, and the release recipe writes N places.

    Three write sites for one fact is how a version silently diverges: a release that
    updates `VERSION` and one manifest ships a plugin whose reported version is a lie,
    and nothing at install time contradicts it.
    """
    version = (almanac.REPO_ROOT / "VERSION").read_text().strip()
    assert version, "VERSION is empty"

    versions = {
        _relative(m): json.loads(m.read_text()).get("version")
        for m in almanac.platform_manifests()
    }
    disagreeing = {k: v for k, v in versions.items() if v != version}
    assert not disagreeing, (
        f"VERSION is {version!r} but these manifests disagree: {disagreeing}"
    )


def test_declared_skills_paths_exist():
    """A manifest may point at a skills directory; if it does, it must be there."""
    for manifest in almanac.platform_manifests():
        declared = json.loads(manifest.read_text()).get("skills")
        if not declared:
            continue
        resolved = (almanac.REPO_ROOT / declared.lstrip("./")).resolve()
        assert resolved.is_dir(), (
            f"{_relative(manifest)} declares skills at {declared!r}, which is not a "
            "directory"
        )
