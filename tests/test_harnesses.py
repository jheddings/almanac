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


def test_cursor_declares_a_trial():
    """Guard the guard: a row that does not parse leaves the recipe unwired."""
    cursor = harnesses.get("cursor")
    assert cursor.trial is not None
    assert cursor.trial.create == ("agent", "create-chat")
    assert "{session}" in " ".join(cursor.trial.first)
    assert "{session}" in " ".join(cursor.trial.resume)
    assert "{session}" in cursor.trial.transcript


def test_claude_trial_has_no_create():
    """Claude still names the session as a flag; the new field must not leak onto it."""
    claude = harnesses.get("claude")
    assert claude.trial is not None
    assert claude.trial.create == ()
    assert "{session}" in " ".join(claude.trial.first)


def _row(**trial):
    base = {
        "first": ["echo", "{session}"],
        "resume": ["echo", "{session}"],
        "transcript": "{session}.jsonl",
    }
    return {"manifest": "harnesses.toml", "trial": {**base, **trial}}


def test_create_without_a_session_placeholder_is_rejected():
    """An id nothing interpolates is created, discarded, and then reported as the run's.

    The prompts open their own conversation, the glob finds whatever it finds, and the
    manifest names a session that describes neither.
    """
    for omitted in ("first", "resume"):
        row = _row(create=["agent", "create-chat"], **{omitted: ["echo", "hello"]})
        with pytest.raises(harnesses.InvalidTrial, match=omitted):
            harnesses._harness("paper", row)

    row = _row(create=["agent", "create-chat"], transcript="newest.jsonl")
    with pytest.raises(harnesses.InvalidTrial, match="transcript"):
        harnesses._harness("paper", row)


def test_a_row_without_create_may_omit_the_placeholder():
    """Codex names no session and discovers the id from the rollout instead."""
    loaded = harnesses._harness(
        "paper",
        _row(
            first=["codex", "exec"],
            resume=["codex", "exec"],
            transcript="*.jsonl",
        ),
    )
    assert loaded.trial.create == ()


def test_the_declared_cursor_row_satisfies_the_rule():
    """Guard the guard: the rule is only worth having if the real row passes it."""
    cursor = harnesses.get("cursor")
    assert cursor.trial.create
    assert "{session}" in " ".join(cursor.trial.first)
    assert "{session}" in " ".join(cursor.trial.resume)
    assert "{session}" in cursor.trial.transcript
