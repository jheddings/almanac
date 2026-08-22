"""Write the shared version into every manifest the table declares.

`VERSION` is the single source of truth, and a release writes it into one file per
harness. Three write sites for one fact is how a version silently diverges: a release
that updates `VERSION` and only some manifests ships a plugin whose reported version is
a lie, and nothing at install time contradicts it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
PARTS = ("major", "minor", "patch")


class ReleaseError(Exception):
    pass


def next_version(current: str, part: str) -> str:
    """Resolve a bump keyword against the current version, or accept a literal."""
    if part not in PARTS:
        if not SEMVER.match(part):
            raise ReleaseError(
                f"{part!r} is neither a version nor one of: {', '.join(PARTS)}"
            )
        return part

    matched = SEMVER.match(current)
    if not matched:
        raise ReleaseError(f"current version {current!r} is not N.N.N")

    major, minor, patch = (int(g) for g in matched.groups())
    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def set_version(version: str, version_file: Path, manifests) -> None:
    """Write `version` to the shared file and into each manifest's `version` field."""
    if not SEMVER.match(version):
        raise ReleaseError(f"{version!r} is not N.N.N")

    version_file.write_text(f"{version}\n")

    for path in manifests:
        manifest = json.loads(path.read_text())
        manifest["version"] = version
        path.write_text(json.dumps(manifest, indent=4) + "\n")
