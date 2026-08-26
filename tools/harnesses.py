"""The harness table, loaded and validated.

Each harness is one row. The checks and the packaging read this table, so a harness is
named here and nowhere else.
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
class Trial:
    """How to drive this harness through the fixture, unattended.

    `first` opens the session and `resume` continues it, so the prompts arrive as one
    conversation rather than several — which is what makes a rule firing on the last
    prompt evidence that it survived the whole session.

    Some harnesses name the session themselves. `create`, when set, is run in the run
    directory first; stripped stdout becomes `{session}` for `first` and `resume`.
    """

    first: tuple[str, ...]
    resume: tuple[str, ...]
    transcript: str
    create: tuple[str, ...] = ()
    version: tuple[str, ...] = ()


@dataclass(frozen=True)
class Harness:
    name: str
    manifest: Path
    marketplace: Path | None = None
    path_keys: tuple[str, ...] = ()
    bundle: Bundle | None = field(default=None)
    trial: Trial | None = field(default=None)


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
    raw_trial = row.get("trial")
    trial = (
        Trial(
            first=tuple(raw_trial["first"]),
            resume=tuple(raw_trial["resume"]),
            transcript=raw_trial["transcript"],
            create=tuple(raw_trial.get("create", ())),
            version=tuple(raw_trial.get("version", ())),
        )
        if raw_trial
        else None
    )
    marketplace = row.get("marketplace")
    return Harness(
        name=name,
        manifest=REPO_ROOT / row["manifest"],
        marketplace=REPO_ROOT / marketplace if marketplace else None,
        path_keys=tuple(row.get("path_keys", ())),
        bundle=bundle,
        trial=trial,
    )


@cache
def load() -> dict[str, Harness]:
    """Every declared harness, keyed by name."""
    rows = tomllib.loads(TABLE.read_text())
    return {name: _harness(name, row) for name, row in rows.items()}


class UnknownHarness(Exception):
    pass


def get(name: str) -> Harness:
    """The named harness, or an error naming the ones that exist."""
    try:
        return load()[name]
    except KeyError:
        known = ", ".join(sorted(load()))
        raise UnknownHarness(
            f"unknown harness {name!r} — the table declares: {known}"
        ) from None


def version() -> str:
    return VERSION_FILE.read_text().strip()
