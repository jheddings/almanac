"""Stage a harness payload, validate it, and archive it.

The repo root doubles as the plugin root, so each harness names the paths it ships as
an allowlist. A directory added to the repo stays out of every archive until a payload
names it.

Archives are written and read back with `zipfile`, so the contents of a finished archive
are checked against the file itself rather than against the staging directory it came
from.
"""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

from tools.harnesses import REPO_ROOT, Harness, version

# Excluded from every archive. docs/almanac/ holds this repo's own entries; an adopter
# gets the template and writes their own.
FORBIDDEN = ("docs",)


class BundleError(Exception):
    pass


def stage(harness: Harness, root: Path, into: Path) -> Path:
    """Copy the declared payload into a clean staging directory."""
    spec = harness.bundle
    if spec is None:
        raise BundleError(f"{harness.name} declares no bundle")

    if into.exists():
        shutil.rmtree(into)
    into.mkdir(parents=True)

    for entry in spec.payload:
        source = root / entry
        if not source.exists():
            raise BundleError(f"{harness.name}: payload entry missing: {entry}")
        destination = into / entry
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)

    # A payload that already names the manifest has copied it. When the declared
    # destination differs from the repo path, copy it there as well.
    manifest = into / spec.manifest_dest
    if not manifest.exists():
        manifest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / harness.manifest.relative_to(REPO_ROOT), manifest)

    return into


def check_stage(staged: Path, harness: Harness) -> list[str]:
    """Paths the archive would be useless without."""
    problems = [
        f"{harness.name}: stage is missing {required}"
        for required in harness.bundle.require
        if not (staged / required).exists()
    ]
    problems += [
        f"{harness.name}: stage must not carry {forbidden}/"
        for forbidden in FORBIDDEN
        if (staged / forbidden).exists()
    ]
    return problems


def archive(staged: Path, out: Path) -> Path:
    """Write the stage to `out`, overwriting any archive already there."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as bundled:
        for path in sorted(staged.rglob("*")):
            if path.name == ".DS_Store":
                continue
            bundled.write(path, path.relative_to(staged))

    return out


def verify(out: Path, harness: Harness) -> list[str]:
    """What the archive actually contains, read back from the finished file."""
    names = set(zipfile.ZipFile(out).namelist())

    problems = []
    if harness.bundle.manifest_dest not in names:
        problems.append(f"{harness.name}: archive has no {harness.bundle.manifest_dest}")
    for forbidden in FORBIDDEN:
        if any(name.startswith(f"{forbidden}/") for name in names):
            problems.append(f"{harness.name}: archive must not contain {forbidden}/")

    return problems


def validate(staged: Path, harness: Harness) -> None:
    """Run the harness's own validator, when it ships one.

    These validators read a directory, so they run against the stage. Handing one an
    archive fails as a JSON parse error on the zip's PK signature. See docs/almanac/.
    """
    if not harness.bundle.validate:
        return
    command = [part.format(stage=str(staged)) for part in harness.bundle.validate]
    subprocess.run(command, check=True)


def install_command(harness: Harness, staged: Path) -> list[str]:
    """The harness's own install command, pointed at a staged directory.

    Only some harnesses ship a CLI that installs from a local tree. Asking for one that
    does not raises, so the caller hears about it.
    """
    spec = harness.bundle
    if spec is None or not spec.install:
        raise BundleError(f"{harness.name} declares no install command")
    return [part.format(stage=str(staged)) for part in spec.install]


def install(harness: Harness, staged: Path) -> None:
    """Hand a staged directory to the harness's own install command."""
    subprocess.run(install_command(harness, staged), check=True)


def build(harness: Harness, *, root: Path = REPO_ROOT, dist: Path | None = None) -> Path:
    """Stage, check, validate, archive, and read the result back."""
    spec = harness.bundle
    if spec is None:
        raise BundleError(f"{harness.name} builds no archive")

    dist = dist or root / "dist"
    staged = stage(harness, root, dist / spec.stage)

    problems = check_stage(staged, harness)
    if problems:
        raise BundleError("\n".join(problems))

    validate(staged, harness)

    out = archive(staged, dist / spec.archive.format(version=version()))

    problems = verify(out, harness)
    if problems:
        raise BundleError("\n".join(problems))

    return out
