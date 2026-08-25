"""Command line for the repo tooling.

`just` recipes and pre-commit hooks both call this, so it is the single invocation path
for every check. The rules live in the sibling modules; this layer chooses which to run
and turns their results into output and an exit code.
"""

from __future__ import annotations

import subprocess
import zipfile

import click

from tools import bundle, drift, harnesses, manifests, release, skel

ALL_HARNESSES = sorted(harnesses.load())
BUNDLING = sorted(name for name, h in harnesses.load().items() if h.bundle)
INSTALLABLE = sorted(
    name for name, h in harnesses.load().items() if h.bundle and h.bundle.install
)


def _fail(problems) -> None:
    """Raise the collected problems as a single non-zero exit."""
    if problems:
        raise click.ClickException("\n".join(problems))


class ToolsGroup(click.Group):
    """Turns the modules' exceptions into a message and a non-zero exit.

    Each module raises an exception carrying its diagnosis. Click renders a
    ClickException as `Error: <message>` on stderr and exits 1.
    """

    LIBRARY_ERRORS = (
        bundle.BundleError,
        drift.DriftError,
        release.ReleaseError,
        harnesses.UnknownHarness,
        skel.SkelError,
    )

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except self.LIBRARY_ERRORS as failure:
            raise click.ClickException(str(failure)) from None
        except subprocess.CalledProcessError as failure:
            command = " ".join(str(part) for part in failure.cmd)
            raise click.ClickException(
                f"{command} exited {failure.returncode}"
            ) from None


@click.group(cls=ToolsGroup)
def cli():
    """Checks and packaging for the almanac skills."""


@click.command("check-manifests")
@click.argument("harness", type=click.Choice(ALL_HARNESSES), required=False)
def check_manifests_cmd(harness):
    """Check manifest invariants, for one harness or all of them."""
    selected = [harnesses.get(harness)] if harness else harnesses.load().values()

    problems = []
    for entry in selected:
        problems += manifests.check(entry)
    _fail(problems)

    for entry in selected:
        click.echo(f"{entry.name} manifest agrees: {harnesses.version()}")


@click.command("drift")
def drift_cmd():
    """Check every almanac README against the shipped template."""
    diff = drift.check()
    if diff:
        click.echo("".join(diff), nl=False)
        raise click.ClickException(
            f"an almanac README differs from {drift.TEMPLATE} outside the local "
            f"block. The template is canonical: port the change to it, or move the "
            f"text inside the {drift.OPEN} block when it is genuinely repo-local."
        )
    for instance in drift.INSTANCES:
        click.echo(f"{instance} matches {drift.TEMPLATE} outside the local block")


@click.command("bundle")
@click.argument("harness", type=click.Choice(BUNDLING))
def bundle_cmd(harness):
    """Stage a harness payload, validate it, and archive it."""
    entry = harnesses.get(harness)
    out = bundle.build(entry)

    click.echo(f"built {out}")
    for name in sorted(zipfile.ZipFile(out).namelist()):
        click.echo(f"  {name}")


@click.command("install")
@click.argument("harness", type=click.Choice(INSTALLABLE))
def install_cmd(harness):
    """Build a harness archive and install it through that harness's own CLI."""
    entry = harnesses.get(harness)
    bundle.build(entry)

    staged = harnesses.REPO_ROOT / "dist" / entry.bundle.stage
    bundle.install(entry, staged)
    click.echo(f"installed {entry.name} from {staged}")


@click.command("manifest-paths")
def manifest_paths_cmd():
    """Print the manifest path declared by each harness, one per line."""
    for entry in harnesses.load().values():
        click.echo(entry.manifest.relative_to(harnesses.REPO_ROOT))


@click.command("set-version")
@click.argument("bump")
def set_version_cmd(bump):
    """Write a version to VERSION and every manifest.

    BUMP is `major`, `minor`, `patch`, or a literal N.N.N version. The resolved version
    is printed on stdout so a caller can capture it.
    """
    target = release.next_version(harnesses.version(), bump)
    release.set_version(
        target,
        harnesses.VERSION_FILE,
        [entry.manifest for entry in harnesses.load().values()],
    )
    click.echo(target)


@click.command("skel-new")
@click.argument("label")
@click.option("--stamp", default=None, help="Date stamp; defaults to today.")
def skel_new_cmd(label, stamp):
    """Scaffold a harness-test run as a standalone repository."""
    import datetime

    stamp = stamp or datetime.date.today().isoformat()
    run = skel.new_run(skel.FIXTURE, skel.RUNS, label, stamp)
    click.echo(f"run ready: {run}")


@click.command("skel-prompt")
@click.argument("name", default="01-first-feature")
def skel_prompt_cmd(name):
    """Print a prompt for pasting into the harness under test."""
    path = skel.PROMPTS / f"{name}.md"
    if not path.is_file():
        raise click.ClickException(f"{path}: no such prompt")
    click.echo(path.read_text().strip())


@click.command("skel-check")
@click.argument("label")
def skel_check_cmd(label):
    """Score a completed run against the almanac's rules."""
    matches = sorted(skel.RUNS.glob(f"*{label}*"))
    if not matches:
        raise click.ClickException(f"no run matching {label!r} under {skel.RUNS}")
    run = matches[-1]

    click.echo(f"{run.name}")
    for finding in skel.score(run):
        mark = {"pass": "PASS", "fail": "FAIL", "unrecoverable": "----"}[finding.status]
        click.echo(f"  {mark}  {finding.check}: {finding.detail}")


cli.add_command(check_manifests_cmd)
cli.add_command(drift_cmd)
cli.add_command(bundle_cmd)
cli.add_command(install_cmd)
cli.add_command(manifest_paths_cmd)
cli.add_command(set_version_cmd)
cli.add_command(skel_new_cmd)
cli.add_command(skel_prompt_cmd)
cli.add_command(skel_check_cmd)
