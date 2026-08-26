"""Shared helpers for the structural suite.

These parse the repository's own artifacts — skills, the template, the almanac — so the
tests can assert on structure rather than prose. Nothing here talks to a model; every
check in this suite is deterministic and free to run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

ALMANAC_README = "README.md"
TEMPLATE_ALMANAC = REPO_ROOT / "templates" / "almanac" / "README.md"
LIVE_ALMANAC = REPO_ROOT / "docs" / "almanac"

# Frontmatter contract for an almanac entry. The template states this in prose; here it
# is executable, which is what makes the "no other fields" invariant enforceable rather
# than merely asserted.
ENTRY_REQUIRED = {"title", "kind", "recorded", "source"}
ENTRY_ALLOWED = ENTRY_REQUIRED | {"verify", "verified", "tags"}

# The two kinds behave differently under maintenance, so the split is enforced rather
# than trusted: only a fact can be re-checked, so only a fact may carry the fields an
# audit reads. A `verify` line on a rule would measure compliance and be reported as
# truth.
ENTRY_KINDS = {"fact", "rule"}
FACT_ONLY_FIELDS = {"verify", "verified"}

# Docs that carry example entry frontmatter inside fenced blocks. An example is what
# adopters copy, so it has to satisfy the same contract the entries do.
DOCS_WITH_EXAMPLES = (
    REPO_ROOT / "templates" / "almanac" / "README.md",
    REPO_ROOT / "docs" / "almanac" / "README.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "CONTRIBUTING.md",
)

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCED_BLOCK_RE = re.compile(r"```([a-z]*)\n(.*?)```", re.DOTALL)
BACKTICKED_RE = re.compile(r"`([^`]+)`")


@dataclass(frozen=True)
class Skill:
    path: Path
    name: str
    frontmatter: dict
    body: str


def parse_frontmatter(text: str) -> dict | None:
    """Return the leading YAML frontmatter mapping, or None when absent."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    loaded = yaml.safe_load(match.group(1))
    return loaded if isinstance(loaded, dict) else None


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, text
    return parse_frontmatter(text), text[match.end() :]


def skills() -> list[Skill]:
    found = []
    for skill_md in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        frontmatter, body = split_frontmatter(skill_md.read_text())
        found.append(
            Skill(
                path=skill_md,
                name=skill_md.parent.name,
                frontmatter=frontmatter or {},
                body=body,
            )
        )
    return found


def entry_paths() -> list[Path]:
    """Every almanac entry in this repo — deliberately empty most of the time."""
    if not LIVE_ALMANAC.is_dir():
        return []
    return sorted(p for p in LIVE_ALMANAC.glob("*.md") if p.name != ALMANAC_README)


def example_blocks() -> list[tuple[Path, str, str]]:
    """Every fenced block that opens with entry frontmatter, as (doc, language, body).

    Language-agnostic on purpose. The fence language is a formatting decision — the
    example is tagged `text` so no formatter parses and rewrites it — and which examples
    the contract tests cover must not move when that decision changes.
    """
    examples = []
    for doc in DOCS_WITH_EXAMPLES:
        if not doc.is_file():
            continue
        for language, block in FENCED_BLOCK_RE.findall(doc.read_text()):
            if FRONTMATTER_RE.match(block):
                examples.append((doc, language, block))
    return examples


def example_frontmatter() -> list[tuple[Path, str]]:
    """Every fenced block that opens with entry frontmatter, as (doc, body)."""
    return [(doc, block) for doc, _, block in example_blocks()]


def platform_manifests() -> list[Path]:
    """Every per-platform plugin manifest present in the repo.

    Today this is only `.claude-plugin/`. Codex, Cursor, and others place a manifest at
    `.<platform>-plugin/plugin.json` pointing at the same `skills/` directory, so a new
    platform becomes data here rather than a new test.
    """
    return sorted(REPO_ROOT.glob(".*-plugin/plugin.json"))


# ---- Resolution rule -------------------------------------------------------------
#
# The skills describe how to locate the almanac in prose. This is that rule as code, so
# it can be exercised against real trees. It is a test-only proxy for the prose: if the
# two disagree, one of them is wrong, and the prose is the one that ships.

RESOLUTION_EXCLUDED = ("templates", "node_modules", "vendor")


class AlmanacNotFound(Exception):
    pass


class AlmanacAmbiguous(Exception):
    def __init__(self, candidates):
        self.candidates = sorted(candidates)
        super().__init__(f"ambiguous: {[str(c) for c in self.candidates]}")


def resolve_almanac(root: Path) -> Path:
    """Locate the almanac directory under `root`, per the documented rule.

    1. Prefer `docs/almanac/README.md`.
    2. Otherwise glob `**/almanac/README.md`, discarding excluded paths and nested
       checkouts.
    3. Require exactly one survivor.
    """
    conventional = root / "docs" / "almanac" / ALMANAC_README
    if conventional.is_file():
        return conventional.parent

    candidates = []
    for readme in root.glob(f"**/almanac/{ALMANAC_README}"):
        relative = readme.relative_to(root)
        if set(relative.parts) & set(RESOLUTION_EXCLUDED):
            continue
        if _inside_nested_checkout(readme, root):
            continue
        candidates.append(readme.parent)

    if not candidates:
        raise AlmanacNotFound(str(root))
    if len(candidates) > 1:
        raise AlmanacAmbiguous(candidates)
    return candidates[0]


def _inside_nested_checkout(path: Path, root: Path) -> bool:
    """True when a `.git` sits between `path` and `root` — a checkout within a checkout."""
    for parent in path.parents:
        if parent == root:
            return False
        if (parent / ".git").exists():
            return True
    return False
