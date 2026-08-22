"""Cross-file invariants for the harness manifests.

A harness validator checks one manifest on its own and passes when two of them
disagree. A name mismatch between a plugin manifest and its marketplace entry breaks
installation, and only for whoever installs the published release, so these rules cover
the agreements a single-file validator cannot see.

Each rule takes loaded JSON and returns the problems it found, so the suite can hand any
rule a manifest built to break it.
"""

from __future__ import annotations

import json
import re

from tools.harnesses import REPO_ROOT, Harness, version

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
LICENSE = "MIT"

# Fields that must read the same in a plugin manifest and its marketplace entry.
AGREEING_FIELDS = ("name", "description")


def check_manifest(manifest: dict, shared_version: str) -> list[str]:
    """Version and license rules for a single plugin manifest."""
    problems = []

    declared = manifest.get("version")
    if declared != shared_version:
        problems.append(f"version is {declared!r}, but VERSION is {shared_version!r}")
    if not SEMVER.match(str(declared or "")):
        problems.append(f"version {declared!r} is not N.N.N")

    if manifest.get("license") != LICENSE:
        problems.append(f"license is {manifest.get('license')!r}, expected {LICENSE!r}")

    return problems


def check_marketplace(manifest: dict, marketplace: dict) -> list[str]:
    """A marketplace lists exactly this plugin, at the repo root, saying the same things."""
    problems = []

    plugins = marketplace.get("plugins") or []
    if len(plugins) != 1:
        problems.append(f"marketplace lists {len(plugins)} plugins, expected exactly 1")
        return problems

    entry = plugins[0]
    if entry.get("source") != "./":
        problems.append(f"marketplace source is {entry.get('source')!r}, expected './'")

    for field in AGREEING_FIELDS:
        if manifest.get(field) != entry.get(field):
            problems.append(
                f"{field} disagrees: manifest {manifest.get(field)!r}, "
                f"marketplace {entry.get(field)!r}"
            )

    return problems


def check_paths(manifest: dict, path_keys, root) -> list[str]:
    """Declared directories are `./`-relative and actually present."""
    problems = []

    for key in path_keys:
        declared = manifest.get(key)
        if declared is None:
            problems.append(f"manifest declares no {key!r} path")
            continue
        if not isinstance(declared, str):
            problems.append(f"{key} is {type(declared).__name__}, expected a string")
            continue
        if not declared.startswith("./"):
            problems.append(f"{key} path {declared!r} must begin with './'")
            continue
        if not (root / declared[2:]).is_dir():
            problems.append(f"{key} path {declared!r} is not a directory")

    return problems


def check(harness: Harness) -> list[str]:
    """Every manifest rule that applies to one harness, against the real repo."""
    shared = version()
    manifest = json.loads(harness.manifest.read_text())

    problems = check_manifest(manifest, shared)
    problems += check_paths(manifest, harness.path_keys, REPO_ROOT)

    if harness.marketplace:
        marketplace = json.loads(harness.marketplace.read_text())
        problems += check_marketplace(manifest, marketplace)

    return [f"{harness.name}: {p}" for p in problems]
