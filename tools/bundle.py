"""Stage a harness payload, validate it, and archive it.

The payload is an allowlist rather than a set of zip exclusions, deliberately: the repo
root doubles as the plugin root, so a denylist means every new repo-only directory
ships until somebody notices.

Archives are built and inspected with `zipfile`. The shell version shelled out to `zip`
and then read the listing back through `unzip -l | grep -q`, which fails intermittently
under `set -o pipefail` when grep exits first and unzip takes SIGPIPE — the failure
recorded in docs/almanac/. `namelist()` has no pipeline to race.
"""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

from tools.harnesses import REPO_ROOT, Harness, version

# Never shipped, for any harness. docs/almanac/ is this repo's own live almanac; an
# adopter gets the template and writes their own entries.
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

    # Most harnesses keep the manifest at its repo path, which the payload already
    # copied. Antigravity wants it at the archive root instead.
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
    """Zip the stage, replacing any existing archive rather than appending to it."""
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

    Every such validator reads a directory. Handing one an archive fails in a way that
    reads like a corrupt file — `claude plugin validate` parses the zip as JSON and
    reports a parse error on the PK signature. See docs/almanac/.
    """
    if not harness.bundle.validate:
        return
    command = [part.format(stage=str(staged)) for part in harness.bundle.validate]
    subprocess.run(command, check=True)


def install_command(harness: Harness, staged: Path) -> list[str]:
    """The harness's own install command, pointed at a staged directory.

    Only some harnesses ship a CLI that installs from a local tree; asking for one that
    does not is a mistake worth naming rather than a silent no-op.
    """
    spec = harness.bundle
    if spec is None or not spec.install:
        raise BundleError(f"{harness.name} declares no install command")
    return [part.format(stage=str(staged)) for part in spec.install]


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
