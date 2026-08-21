"""Structural conventions the skills must hold to.

`skills-ref validate` covers the Agent Skills spec. These cover the conventions this
plugin adds on top of it — the ones CONTRIBUTING states in prose and that have already
been violated once each.
"""

from __future__ import annotations

import json

import pytest

from tests.support import almanac

SKILLS = almanac.skills()
BASELINES = json.loads((almanac.REPO_ROOT / "tests" / "baselines.json").read_text())


def _ids(skill):
    return skill.name


def test_skills_were_discovered():
    assert SKILLS, "no skills found under skills/*/SKILL.md"


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_directory_name_matches_frontmatter_name(skill):
    assert skill.frontmatter.get("name") == skill.name, (
        f"{skill.path}: directory is {skill.name!r}, frontmatter says "
        f"{skill.frontmatter.get('name')!r}"
    )


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_name_is_unprefixed(skill):
    """The plugin namespace supplies `almanac:`; a prefixed name stutters."""
    assert not skill.name.startswith("almanac-"), (
        f"{skill.name}: drop the prefix — the namespace makes this almanac:{skill.name}"
    )


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_frontmatter_carries_only_name_and_description(skill):
    assert set(skill.frontmatter) == {"name", "description"}, (
        f"{skill.name}: unexpected frontmatter keys "
        f"{sorted(set(skill.frontmatter) - {'name', 'description'})}"
    )


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_description_states_when_to_use_it(skill):
    """A description that summarizes the workflow gets followed instead of the skill."""
    description = skill.frontmatter.get("description", "")
    assert "use when" in description.lower(), (
        f"{skill.name}: description must say when to use the skill, starting with "
        '"Use when" — not what it does'
    )


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_kebab_case_name(skill):
    name = skill.name
    assert name == name.lower(), f"{name}: lowercase only"
    assert not name.startswith("-") and not name.endswith("-"), f"{name}: no edge hyphens"
    assert "--" not in name, f"{name}: no consecutive hyphens"


# ---- The exclusion list must not drift between skills ----------------------------


def _resolution_paths(skill):
    """The excluded paths named in a skill's resolution step."""
    for line_group in skill.body.split("\n\n"):
        if "discard matches under" in line_group:
            return {
                token
                for token in almanac.BACKTICKED_RE.findall(line_group)
                if token.endswith("/")
            }
    return None


RESOLVERS = [s for s in SKILLS if _resolution_paths(s) is not None]


def test_every_skill_that_resolves_the_almanac_names_the_same_exclusions():
    """CONTRIBUTING requires the path list be copied, not reworded.

    Only the path list is load-bearing — the consequence clause after it is legitimately
    per-skill, since recording into the wrong almanac and auditing the wrong one fail
    differently. Three skills resolve the almanac, so this list has already needed
    extending twice; a hand-edit that misses one is silent.
    """
    assert len(RESOLVERS) >= 2, "expected at least two skills to resolve the almanac"
    by_skill = {s.name: _resolution_paths(s) for s in RESOLVERS}
    distinct = {frozenset(v) for v in by_skill.values()}
    assert len(distinct) == 1, (
        "exclusion lists have drifted between skills: "
        + json.dumps({k: sorted(v) for k, v in by_skill.items()}, indent=2)
    )


# ---- Prose length ratchet ---------------------------------------------------------


@pytest.mark.parametrize("skill", SKILLS, ids=_ids)
def test_prose_does_not_grow(skill):
    """A ratchet, not a target.

    CONTRIBUTING asks for well under 500 words; these run several times that, and
    compressing them is deferred work. Freezing the current counts stops the debt
    growing without pretending it is paid — and gives the compression pass a scoreboard.
    """
    ceiling = BASELINES["skill_word_ceilings"].get(skill.name)
    assert ceiling is not None, (
        f"{skill.name}: no baseline recorded. Add one to tests/baselines.json — "
        f"currently {skill.word_count} words."
    )
    assert skill.word_count <= ceiling, (
        f"{skill.name}: {skill.word_count} words exceeds the ceiling of {ceiling}. "
        "Trim it, or raise the ceiling deliberately and say why."
    )


def test_baselines_have_no_stale_entries():
    recorded = set(BASELINES["skill_word_ceilings"])
    actual = {s.name for s in SKILLS}
    assert recorded == actual, (
        f"tests/baselines.json is out of step with skills/: "
        f"only-in-baselines={sorted(recorded - actual)}, "
        f"only-in-skills={sorted(actual - recorded)}"
    )

