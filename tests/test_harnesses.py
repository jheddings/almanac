"""The harness table, and its agreement with the filesystem.

The table is the single place a harness is declared. That only holds if it cannot
silently fall out of step with the repo, so the first checks here are the ones that
catch a harness present on disk but missing from the table, and vice versa.
"""

from __future__ import annotations

import pytest

from tests.support import almanac
from tools import harnesses


def test_table_is_not_empty():
    assert harnesses.load(), "the harness table declares no harnesses"


def test_table_covers_every_plugin_directory():
    """A harness on disk with no row is a harness nothing checks."""
    on_disk = {
        p.parent.name.removeprefix(".").removesuffix("-plugin")
        for p in almanac.platform_manifests()
    }
    declared = set(harnesses.load())
    assert declared == on_disk, (
        f"table declares {sorted(declared)}, filesystem has {sorted(on_disk)}"
    )
