"""The `python3 -m tools` entry point.

Pre-commit hooks and the justfile both call this, so the contract that matters is the
exit code: zero when the repo is clean, non-zero when it is not.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from tools import harnesses
from tools.harnesses import REPO_ROOT


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "tools", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("command", ["check-manifests", "drift"])
def test_repo_checks_pass(command):
    result = run(command)
    assert result.returncode == 0, f"{command} exited {result.returncode}\n{result.stderr}"


@pytest.mark.parametrize("name", sorted(harnesses.load()))
def test_check_manifests_accepts_each_harness_by_name(name):
    assert run("check-manifests", name).returncode == 0


def test_an_unknown_harness_is_an_error():
    result = run("check-manifests", "nope")
    assert result.returncode != 0
    assert "nope" in result.stdout + result.stderr


def test_no_command_is_an_error():
    assert run().returncode != 0


def test_manifest_paths_lists_one_path_per_harness():
    """The release recipe reformats what it rewrote; it should not hardcode the list."""
    result = run("manifest-paths")
    assert result.returncode == 0, result.stderr
    printed = result.stdout.split()
    assert len(printed) == len(harnesses.load())
    for path in printed:
        assert (REPO_ROOT / path).is_file(), f"{path} is not a file"


def test_bundling_a_harness_that_builds_no_archive_fails_cleanly():
    """Codex consumes the repo tree directly. Asking for its archive is a mistake."""
    result = run("bundle", "codex")
    assert result.returncode != 0
    assert "Traceback" not in result.stderr, "expected a message, got a stack trace"
    assert "codex" in result.stderr
