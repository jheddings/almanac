"""Command line for the repo tooling.

`just` recipes and pre-commit hooks both call this, so it is the single invocation path
for every check. It stays thin on purpose: the rules live in the modules, and this only
chooses which to run and how to report them.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile

from tools import bundle, drift, harnesses, manifests, release


def _report(problems) -> int:
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if problems else 0


def check_manifests(args) -> int:
    selected = [harnesses.get(args.harness)] if args.harness else harnesses.load().values()

    problems = []
    for harness in selected:
        problems += manifests.check(harness)

    if not problems:
        for harness in selected:
            print(f"{harness.name} manifest agrees: {harnesses.version()}")
    return _report(problems)


def check_drift(args) -> int:
    diff = drift.check()
    if diff:
        sys.stdout.writelines(diff)
        sys.stdout.flush()
        return _report(
            [
                f"{drift.INSTANCE.name} has drifted from {drift.TEMPLATE}. The template "
                "is canonical: port the change to it, or move the text inside the "
                f"{drift.OPEN} block if it is genuinely repo-local."
            ]
        )
    print(f"{drift.INSTANCE} matches {drift.TEMPLATE} outside the local block")
    return 0


def build(args) -> int:
    harness = harnesses.get(args.harness)
    out = bundle.build(harness)
    print(f"built {out}")
    for name in sorted(zipfile.ZipFile(out).namelist()):
        print(f"  {name}")
    return 0


def manifest_paths(args) -> int:
    """Print every declared manifest, so callers stop keeping their own copy of the list."""
    for harness in harnesses.load().values():
        print(harness.manifest.relative_to(harnesses.REPO_ROOT))
    return 0


def install(args) -> int:
    """Build the archive, then hand the staged directory to the harness's own CLI."""
    harness = harnesses.get(args.harness)
    bundle.build(harness)
    staged = harnesses.REPO_ROOT / "dist" / harness.bundle.stage
    subprocess.run(bundle.install_command(harness, staged), check=True)
    print(f"installed {harness.name} from {staged}")
    return 0


def set_version(args) -> int:
    """Resolve the bump and write it everywhere, printing the version for the caller."""
    target = release.next_version(harnesses.version(), args.bump)
    release.set_version(
        target,
        harnesses.VERSION_FILE,
        [harness.manifest for harness in harnesses.load().values()],
    )
    print(target)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="tools")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check-manifests", help="manifest invariants")
    check.add_argument("harness", nargs="?", help="one harness, or all when omitted")
    check.set_defaults(run=check_manifests)

    commands.add_parser("drift", help="template drift").set_defaults(run=check_drift)

    bundle_command = commands.add_parser("bundle", help="build a harness archive")
    bundle_command.add_argument("harness")
    bundle_command.set_defaults(run=build)

    commands.add_parser(
        "manifest-paths", help="print every declared manifest path"
    ).set_defaults(run=manifest_paths)

    install_command = commands.add_parser(
        "install", help="build and install a harness plugin via its own CLI"
    )
    install_command.add_argument("harness")
    install_command.set_defaults(run=install)

    version_command = commands.add_parser(
        "set-version", help="write a version to VERSION and every manifest"
    )
    version_command.add_argument("bump", help="major, minor, patch, or a literal N.N.N")
    version_command.set_defaults(run=set_version)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (bundle.BundleError, drift.DriftError, release.ReleaseError) as failure:
        # These carry a diagnosis. A stack trace on top of one buries it.
        return _report(str(failure).splitlines())
    except subprocess.CalledProcessError as failure:
        return _report([f"{' '.join(failure.cmd)} exited {failure.returncode}"])


if __name__ == "__main__":
    raise SystemExit(main())
