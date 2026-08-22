"""Writing the shared version across every manifest.

`VERSION` is the single source of truth, and a release copies it into one manifest per
harness. A manifest left behind reports a version that is not the one being shipped, and
nothing at install time contradicts it.
"""

from __future__ import annotations

import json

import pytest

from tools import release


def manifest(tmp_path, name, version="0.1.0"):
    path = tmp_path / name
    path.write_text(json.dumps({"name": "almanac", "version": version}, indent=4) + "\n")
    return path


def test_writes_the_version_into_every_manifest(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.1.0\n")
    targets = [manifest(tmp_path, "a.json"), manifest(tmp_path, "b.json")]

    release.set_version("1.4.0", version_file, targets)

    assert version_file.read_text().strip() == "1.4.0"
    for path in targets:
        assert json.loads(path.read_text())["version"] == "1.4.0"


def test_leaves_other_manifest_fields_alone(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.1.0\n")
    target = tmp_path / "plugin.json"
    target.write_text(json.dumps({"name": "almanac", "version": "0.1.0", "license": "MIT"}))

    release.set_version("2.0.0", version_file, [target])

    assert json.loads(target.read_text()) == {
        "name": "almanac",
        "version": "2.0.0",
        "license": "MIT",
    }


def test_rejects_a_version_that_is_not_three_numbers(tmp_path):
    version_file = tmp_path / "VERSION"
    version_file.write_text("0.1.0\n")
    with pytest.raises(release.ReleaseError):
        release.set_version("1.4", version_file, [])


@pytest.mark.parametrize(
    ("current", "part", "expected"),
    [
        ("0.1.0", "patch", "0.1.1"),
        ("0.1.9", "minor", "0.2.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "4.0.0", "4.0.0"),
    ],
)
def test_bump_resolves_the_next_version(current, part, expected):
    assert release.next_version(current, part) == expected


def test_bump_rejects_an_unknown_part():
    with pytest.raises(release.ReleaseError):
        release.next_version("1.2.3", "sideways")
