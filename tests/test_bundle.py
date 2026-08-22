"""Staging and archiving, once, for every harness.

Every harness stages and archives through the same code, so these run against each
harness the table declares. The trees are real: staging is exercised against a fixture
repo, and the archive assertions read the finished zip.
"""

from __future__ import annotations

import zipfile

import pytest

from tools import bundle, harnesses

BUNDLED = sorted(n for n, h in harnesses.load().items() if h.bundle)


@pytest.fixture
def fake_repo(tmp_path):
    """A tree carrying everything every declared payload asks for."""
    for name in harnesses.load():
        directory = tmp_path / f".{name}-plugin"
        directory.mkdir()
        (directory / "plugin.json").write_text('{"name": "almanac"}')
    (tmp_path / ".cursor-plugin" / "commands").mkdir()
    (tmp_path / ".cursor-plugin" / "commands" / "init.md").write_text("stub")
    (tmp_path / "skills" / "init").mkdir(parents=True)
    (tmp_path / "skills" / "init" / "SKILL.md").write_text("stub")
    (tmp_path / "templates" / "almanac").mkdir(parents=True)
    (tmp_path / "templates" / "almanac" / "README.md").write_text("contract")
    (tmp_path / "README.md").write_text("readme")
    (tmp_path / "LICENSE").write_text("MIT")
    (tmp_path / "docs" / "almanac").mkdir(parents=True)
    (tmp_path / "docs" / "almanac" / "README.md").write_text("live almanac")
    return tmp_path


def test_every_bundling_harness_was_discovered():
    assert BUNDLED, "no harness in the table declares a bundle"


@pytest.mark.parametrize("name", BUNDLED)
def test_stage_holds_the_manifest_at_its_declared_destination(name, fake_repo, tmp_path):
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    assert (into / harness.bundle.manifest_dest).is_file()


@pytest.mark.parametrize("name", BUNDLED)
def test_stage_never_carries_docs(name, fake_repo, tmp_path):
    """docs/almanac/ is this repo's live almanac, not an adopter's."""
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    assert not (into / "docs").exists()


@pytest.mark.parametrize("name", BUNDLED)
def test_missing_payload_entry_is_an_error(name, fake_repo, tmp_path):
    harness = harnesses.get(name)
    (fake_repo / "LICENSE").unlink()
    with pytest.raises(bundle.BundleError):
        bundle.stage(harness, fake_repo, tmp_path / "stage")


@pytest.mark.parametrize("name", BUNDLED)
def test_archive_carries_the_manifest(name, fake_repo, tmp_path):
    """An archive that lost its manifest still loads, with no error on the way in."""
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    out = bundle.archive(into, tmp_path / "out.zip")
    assert bundle.verify(out, harness) == []
    assert harness.bundle.manifest_dest in zipfile.ZipFile(out).namelist()


def test_verify_rejects_an_archive_missing_its_manifest(tmp_path):
    out = tmp_path / "empty.zip"
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("README.md", "readme")
    assert bundle.verify(out, harnesses.get("claude"))


def test_verify_rejects_an_archive_carrying_docs(tmp_path):
    out = tmp_path / "leaky.zip"
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr(".claude-plugin/plugin.json", "{}")
        archive.writestr("docs/almanac/README.md", "live almanac")
    assert bundle.verify(out, harnesses.get("claude"))


@pytest.mark.parametrize("name", BUNDLED)
def test_required_stage_paths_are_checked(name, fake_repo, tmp_path):
    harness = harnesses.get(name)
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    missing = harness.bundle.require[0]
    target = into / missing
    if target.is_dir():
        for child in sorted(target.rglob("*"), reverse=True):
            child.unlink() if child.is_file() else child.rmdir()
        target.rmdir()
    else:
        target.unlink()
    assert bundle.check_stage(into, harness)


def test_archive_replaces_rather_than_appends(fake_repo, tmp_path):
    """`zip` appends to an existing archive; rebuilding must not accumulate."""
    harness = harnesses.get("claude")
    into = tmp_path / "stage"
    bundle.stage(harness, fake_repo, into)
    out = tmp_path / "out.zip"
    bundle.archive(into, out)
    first = set(zipfile.ZipFile(out).namelist())
    bundle.archive(into, out)
    assert set(zipfile.ZipFile(out).namelist()) == first


def test_install_command_is_declared_for_harnesses_that_have_a_cli(tmp_path):
    """`agy plugin install` reads the stage directory, so the stage path is the argument."""
    harness = harnesses.get("agy")
    command = bundle.install_command(harness, tmp_path / "stage")
    assert command[:3] == ["agy", "plugin", "install"]
    assert str(tmp_path / "stage") in command


def test_install_is_an_error_for_a_harness_with_no_installer(tmp_path):
    with pytest.raises(bundle.BundleError):
        bundle.install_command(harnesses.get("claude"), tmp_path / "stage")
