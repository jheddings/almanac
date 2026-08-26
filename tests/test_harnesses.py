"""The harness table, and its agreement with the filesystem.

The table is the single place a harness is declared, which holds only while it matches
the repo. These catch a harness present on disk with no row, and a row naming a harness
that is not there.
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


def test_trial_create_is_optional():
    """Claude names the session as a flag; a missing create must not be an error."""
    loaded = harnesses._harness(
        "paper",
        {
            "manifest": "harnesses.toml",
            "trial": {
                "first": ["echo", "{prompt}"],
                "resume": ["echo", "{prompt}"],
                "transcript": "{session}.jsonl",
            },
        },
    )
    assert loaded.trial is not None
    assert loaded.trial.create == ()


def test_trial_create_is_loaded_when_present():
    loaded = harnesses._harness(
        "paper",
        {
            "manifest": "harnesses.toml",
            "trial": {
                "create": ["agent", "create-chat"],
                "first": ["echo", "{session}"],
                "resume": ["echo", "{session}"],
                "transcript": "{session}.jsonl",
            },
        },
    )
    assert loaded.trial.create == ("agent", "create-chat")


def test_trial_required_fields_stay_required():
    """create is the new optional; first, resume, and transcript are not."""
    row = {
        "manifest": "harnesses.toml",
        "trial": {
            "resume": ["echo", "{prompt}"],
            "transcript": "{session}.jsonl",
        },
    }
    with pytest.raises(KeyError, match="first"):
        harnesses._harness("paper", row)
