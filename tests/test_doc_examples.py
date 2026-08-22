"""The example entries in the docs satisfy the same contract as real entries.

The canonical template's example is what every adopter copies, so a defect there
propagates into repositories we never see. This suite exists because that example
shipped with `source: PR #1129` unquoted, which YAML parses as `PR` — the `#` opens a
comment, nothing warns, and every entry written from the template silently lost its
provenance.
"""

from __future__ import annotations

import pytest
import yaml

from tests.support import almanac
from tests.test_entry_frontmatter import check_entry_frontmatter

EXAMPLES = almanac.example_frontmatter()


def _ids(pair):
    doc, _ = pair
    return str(doc.relative_to(almanac.REPO_ROOT))


def test_the_docs_actually_carry_an_example():
    """Guard the guard: if extraction silently finds nothing, this suite is vacuous."""
    assert EXAMPLES, "no fenced markdown entry examples found — has the format changed?"


@pytest.mark.parametrize("pair", EXAMPLES, ids=_ids)
def test_example_frontmatter_conforms(pair):
    doc, block = pair
    data = almanac.parse_frontmatter(block)
    assert data is not None, f"{doc.name}: example frontmatter did not parse"
    assert check_entry_frontmatter(data) == [], f"{doc.name}"


@pytest.mark.parametrize("pair", EXAMPLES, ids=_ids)
def test_example_values_survive_yaml(pair):
    """Values must mean what they look like.

    `source: PR #1129` looks like it carries the PR number and does not. Any value whose
    parsed form is a strict prefix of its written form lost characters to YAML, and the
    fix is quoting.
    """
    doc, block = pair
    raw = almanac.FRONTMATTER_RE.match(block).group(1)
    data = yaml.safe_load(raw)

    for line in raw.splitlines():
        if ":" not in line or line.startswith((" ", "#", "-")):
            continue
        key, _, written = line.partition(":")
        key, written = key.strip(), written.strip()
        if key not in data or not isinstance(data[key], str):
            continue
        if written.startswith(("'", '"')):
            continue
        if "#" in written:
            pytest.fail(
                f"{doc.name}: `{key}: {written}` — an unquoted '#' opens a YAML "
                f"comment, so this parses as {data[key]!r}. Quote the value."
            )


def test_yaml_comment_trap_is_real():
    """Pin the behavior this suite defends against, so the rule can't be dismissed."""
    assert yaml.safe_load("source: PR #1129") == {"source": "PR"}
    assert yaml.safe_load('source: "PR #1129"') == {"source": "PR #1129"}
