"""The manifest invariants, and the inputs that must fail them.

A check that only ever sees valid input passes forever, so every rule below is given
the broken manifest it exists to reject alongside the good one it accepts.
"""

from __future__ import annotations

import pytest

from tools import harnesses, manifests

VERSION = "1.2.3"


def plugin(**overrides):
    base = {
        "name": "almanac",
        "description": "does the thing",
        "version": VERSION,
        "license": "MIT",
    }
    return base | overrides


def marketplace(**overrides):
    base = {
        "name": "almanac",
        "plugins": [
            {
                "name": "almanac",
                "source": "./",
                "description": "does the thing",
            }
        ],
    }
    return base | overrides


# ---- the real repo -----------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(harnesses.load()))
def test_every_declared_harness_is_clean(name):
    assert manifests.check(harnesses.get(name)) == []


# ---- version -----------------------------------------------------------------------


def test_accepts_a_manifest_carrying_the_shared_version():
    assert manifests.check_manifest(plugin(), VERSION) == []


def test_rejects_a_version_disagreeing_with_the_shared_version():
    problems = manifests.check_manifest(plugin(version="9.9.9"), VERSION)
    assert problems, "a manifest that drifted from VERSION was accepted"


def test_rejects_a_version_that_is_not_three_numbers():
    problems = manifests.check_manifest(plugin(version="1.2"), "1.2")
    assert problems, "a non-N.N.N version was accepted"


def test_rejects_a_non_mit_license():
    problems = manifests.check_manifest(plugin(license="GPL-3.0"), VERSION)
    assert problems, "a non-MIT license was accepted"


# ---- marketplace agreement ---------------------------------------------------------


def test_accepts_agreeing_manifests():
    assert manifests.check_marketplace(plugin(), marketplace()) == []


def test_rejects_a_marketplace_listing_more_than_one_plugin():
    two = marketplace()
    two["plugins"] = two["plugins"] * 2
    assert manifests.check_marketplace(plugin(), two)


def test_rejects_a_marketplace_plugin_not_sourced_at_dot_slash():
    other = marketplace()
    other["plugins"][0]["source"] = "./nested"
    assert manifests.check_marketplace(plugin(), other)


def test_rejects_a_name_disagreeing_between_manifests():
    other = marketplace()
    other["plugins"][0]["name"] = "almanac-cursor"
    assert manifests.check_marketplace(plugin(), other)


def test_rejects_a_description_disagreeing_between_manifests():
    other = marketplace()
    other["plugins"][0]["description"] = "something else"
    assert manifests.check_marketplace(plugin(), other)


# ---- declared paths ----------------------------------------------------------------


def test_accepts_a_declared_path_that_exists(tmp_path):
    (tmp_path / "skills").mkdir()
    assert manifests.check_paths(plugin(skills="./skills/"), ("skills",), tmp_path) == []


def test_rejects_a_declared_path_without_the_dot_slash_prefix(tmp_path):
    (tmp_path / "skills").mkdir()
    assert manifests.check_paths(plugin(skills="skills/"), ("skills",), tmp_path)


def test_rejects_a_declared_path_that_does_not_exist(tmp_path):
    assert manifests.check_paths(plugin(skills="./nope/"), ("skills",), tmp_path)


def test_rejects_a_missing_declared_path_key(tmp_path):
    assert manifests.check_paths(plugin(), ("skills",), tmp_path)
