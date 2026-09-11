"""The template-drift check.

`templates/almanac/README.md` is canonical; `docs/almanac/README.md` is an instance of
it, identical outside the `almanac:local` block. Drift between them is the exact failure
the precedence rule exists to prevent, so the check needs the drifting pair that must
fail it — not only the matching pair it sees every day.
"""

from __future__ import annotations

import pytest

from tools import drift

OPEN, CLOSE = drift.OPEN, drift.CLOSE


def document(shared: str, local: str) -> str:
    return f"# Almanac\n\n{shared}\n\n{OPEN}\n{local}\n{CLOSE}\n\nTail.\n"


def test_the_live_almanac_still_matches_the_shipped_template():
    assert drift.check() == []


def test_identical_outside_the_local_block_is_no_drift(tmp_path):
    template = tmp_path / "template.md"
    instance = tmp_path / "instance.md"
    template.write_text(document("Shared prose.", "template-local"))
    instance.write_text(document("Shared prose.", "totally different local text"))
    assert drift.compare(template, instance) == []


def test_divergence_outside_the_local_block_is_drift(tmp_path):
    template = tmp_path / "template.md"
    instance = tmp_path / "instance.md"
    template.write_text(document("Shared prose.", "same"))
    instance.write_text(document("Shared prose, edited.", "same"))
    assert drift.compare(template, instance)


def test_a_missing_local_block_is_an_error(tmp_path):
    template = tmp_path / "template.md"
    instance = tmp_path / "instance.md"
    template.write_text(document("Shared.", "local"))
    instance.write_text("# Almanac\n\nNo markers here.\n")
    with pytest.raises(drift.DriftError):
        drift.compare(template, instance)


def test_every_declared_instance_is_compared(tmp_path, monkeypatch):
    """A second instance that drifts must fail the check, not be skipped."""
    template = tmp_path / "template.md"
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    template.write_text(document("Shared prose.", "t"))
    good.write_text(document("Shared prose.", "g"))
    bad.write_text(document("Shared prose, edited.", "b"))

    monkeypatch.setattr(drift, "TEMPLATE", template)
    monkeypatch.setattr(drift, "INSTANCES", (good, bad))
    assert drift.check()


def test_the_fixture_almanac_is_a_declared_instance():
    """Guard the guard: the fixture must actually be in the list."""
    names = [str(p) for p in drift.INSTANCES]
    assert any(p.endswith("skel/docs/almanac/README.md") for p in names), names
