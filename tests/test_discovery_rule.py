"""The almanac resolution rule, exercised against real trees.

This is the only check here that tests a *rule* rather than an artifact. The skills
describe resolution in prose; `support/almanac.resolve_almanac` is that prose as code,
run against trees built to trip it.

The rule exists because the naive one-step glob was ambiguous in this very repository:
from the primary repo root, `**/almanac/README.md` matched four paths — the real
almanac, the shipped template, and one copy per active worktree — so the skills would
have asked the operator to disambiguate on nearly every invocation, in the one repo that
dogfoods the plugin.
"""

from __future__ import annotations

import pytest

from tests.support import almanac
from tests.support.almanac import (
    AlmanacAmbiguous,
    AlmanacNotFound,
    resolve_almanac,
)

STAMP = "<!-- almanac-template: 1 -->\n\n# Almanac\n"


def make_almanac(root, relative):
    directory = root / relative
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "README.md").write_text(STAMP)
    return directory


def test_resolves_in_this_repository():
    """The dogfooding case: exactly one answer, and it is the live almanac."""
    assert resolve_almanac(almanac.REPO_ROOT) == almanac.LIVE_ALMANAC


def test_conventional_location_wins_over_a_template(tmp_path):
    """The four-match regression, minimally reproduced."""
    make_almanac(tmp_path, "docs/almanac")
    make_almanac(tmp_path, "templates/almanac")
    assert resolve_almanac(tmp_path) == tmp_path / "docs" / "almanac"


def test_conventional_location_short_circuits_before_globbing(tmp_path):
    """With docs/almanac/ present, nothing else can create ambiguity."""
    make_almanac(tmp_path, "docs/almanac")
    make_almanac(tmp_path, "templates/almanac")
    make_almanac(tmp_path, "packages/thing/almanac")
    assert resolve_almanac(tmp_path) == tmp_path / "docs" / "almanac"


@pytest.mark.parametrize(
    "decoy", ["templates/almanac", ".worktrees/badger/almanac", "node_modules/x/almanac", "vendor/y/almanac"]
)
def test_excluded_paths_are_never_the_answer(tmp_path, decoy):
    make_almanac(tmp_path, "notes/almanac")
    make_almanac(tmp_path, decoy)
    assert resolve_almanac(tmp_path) == tmp_path / "notes" / "almanac"


def test_a_nested_checkout_is_somebody_elses_tree(tmp_path):
    make_almanac(tmp_path, "notes/almanac")
    nested = make_almanac(tmp_path, "third_party/other-repo/docs/almanac")
    (nested.parents[1] / ".git").mkdir()
    assert resolve_almanac(tmp_path) == tmp_path / "notes" / "almanac"


def test_a_worktree_copy_of_this_repo_does_not_win(tmp_path):
    """The exact shape that broke: sibling worktrees each carrying a full copy."""
    make_almanac(tmp_path, "docs/almanac")
    for name in ("badger", "heron"):
        make_almanac(tmp_path, f".worktrees/{name}/docs/almanac")
        make_almanac(tmp_path, f".worktrees/{name}/templates/almanac")
    assert resolve_almanac(tmp_path) == tmp_path / "docs" / "almanac"


def test_an_enclosing_almanac_is_out_of_reach(tmp_path):
    """Resolution is bounded above as well as below.

    A workspace almanac one level up is a different almanac with a different subject.
    Resolving to it would mean recording into a contract this skill never read.
    """
    make_almanac(tmp_path, "docs/almanac")
    checkout = tmp_path / "project"
    (checkout / "src").mkdir(parents=True)
    with pytest.raises(AlmanacNotFound):
        resolve_almanac(checkout)


def test_the_innermost_almanac_wins_over_an_enclosing_one(tmp_path):
    """Both exist and both are genuine; the one under foot is the one that resolves."""
    make_almanac(tmp_path, "docs/almanac")
    inner = make_almanac(tmp_path, "project/docs/almanac")
    assert resolve_almanac(tmp_path / "project") == inner


def test_no_almanac_raises_rather_than_creating_one(tmp_path):
    (tmp_path / "src").mkdir()
    with pytest.raises(AlmanacNotFound):
        resolve_almanac(tmp_path)


def test_a_template_alone_is_not_an_almanac(tmp_path):
    """A directory named `almanac` is not evidence of an almanac."""
    make_almanac(tmp_path, "templates/almanac")
    with pytest.raises(AlmanacNotFound):
        resolve_almanac(tmp_path)


def test_two_genuine_candidates_are_ambiguous(tmp_path):
    """Real ambiguity must surface, not get silently resolved by ordering."""
    make_almanac(tmp_path, "notes/almanac")
    make_almanac(tmp_path, "wiki/almanac")
    with pytest.raises(AlmanacAmbiguous) as raised:
        resolve_almanac(tmp_path)
    assert len(raised.value.candidates) == 2


def test_exclusion_list_matches_what_the_skills_say():
    """The code proxy and the shipped prose must name the same paths.

    If these drift, the rule the agents follow is not the rule under test — and the
    prose is the one that ships.
    """
    for skill in almanac.skills():
        if "discard matches under" not in skill.body:
            continue
        for excluded in almanac.RESOLUTION_EXCLUDED:
            assert f"`{excluded}/`" in skill.body, (
                f"{skill.name}: prose omits `{excluded}/`, which the rule under test "
                "excludes"
            )


def test_the_upward_bound_is_stated_in_the_skills():
    """The exclusions cover trees nested inside this one; nothing covered the reverse.

    Without it, a checkout under a workspace almanac reads as uninitialized to `init`
    and as already-adopted to whoever runs `record` from the parent — the same tree,
    two answers, neither wrong on its own terms.
    """
    for skill in almanac.skills():
        if "discard matches under" not in skill.body:
            continue
        assert "never look up" in skill.body, (
            f"{skill.name}: resolves the almanac but does not say resolution stops at "
            "this tree's root"
        )
