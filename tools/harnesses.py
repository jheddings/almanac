"""The harness table, loaded and validated.

One row per harness, so adding one is data rather than a new script, a new justfile
module, a new pre-commit hook, and four more places that list the same names.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TABLE = REPO_ROOT / "harnesses.toml"
VERSION_FILE = REPO_ROOT / "VERSION"


@dataclass(frozen=True)
class Bundle:
    stage: str
    archive: str
    payload: tuple[str, ...]
    manifest_dest: str
    validate: tuple[str, ...] = ()
    install: tuple[str, ...] = ()
    require: tuple[str, ...] = ()


@dataclass(frozen=True)
class Harness:
    name: str
    manifest: Path
    marketplace: Path | None = None
    path_keys: tuple[str, ...] = ()
    bundle: Bundle | None = field(default=None)


def _harness(name: str, row: dict) -> Harness:
    raw = row.get("bundle")
    bundle = (
        Bundle(
            stage=raw["stage"],
            archive=raw["archive"],
            payload=tuple(raw["payload"]),
            manifest_dest=raw["manifest_dest"],
            validate=tuple(raw.get("validate", ())),
            install=tuple(raw.get("install", ())),
            require=tuple(raw.get("require", ())),
        )
        if raw
        else None
    )
    marketplace = row.get("marketplace")
    return Harness(
        name=name,
        manifest=REPO_ROOT / row["manifest"],
        marketplace=REPO_ROOT / marketplace if marketplace else None,
        path_keys=tuple(row.get("path_keys", ())),
        bundle=bundle,
    )


@cache
def load() -> dict[str, Harness]:
    """Every declared harness, keyed by name."""
    rows = tomllib.loads(TABLE.read_text())
    return {name: _harness(name, row) for name, row in rows.items()}


def get(name: str) -> Harness:
    try:
        return load()[name]
    except KeyError:
        known = ", ".join(sorted(load()))
        raise SystemExit(f"unknown harness {name!r} — the table declares: {known}")


def version() -> str:
    return VERSION_FILE.read_text().strip()
