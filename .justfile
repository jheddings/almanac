# justfile for the almanac skills.
#
# Every harness is declared in `harnesses.toml`, and the recipes below fan out from that
# table rather than naming harnesses here. Adding a harness is a row in the table, not a
# new module, a new script, and four more places that list the same names.
#
# Everything Python runs through `uv run` against the environment `just venv` syncs, so
# there is one environment and one way in. `uv` and `npx` are the only prerequisites.

basedir := justfile_directory()

# sync the virtual environment and install hooks
default: setup check

# setup the local development environment
setup: venv
    uv run pre-commit install --install-hooks --overwrite

# sync the virtual environment
venv:
    uv sync --all-extras

# auto-format all files
tidy: venv
    npx prettier --write .

# run all checks
check: style validate manifests drift test

# check style
style:
    npx prettier --check .

# validate all skills against the vendor-neutral Agent Skills spec
validate:
    for dir in skills/*/; do npx skills-ref validate "$dir"; done

# confirm the manifests agree — a mismatch breaks installation for whoever installs
manifests harness="": venv
    uv run python -m tools check-manifests {{ harness }}

# confirm this repo's almanac README is still an instance of the shipped template
drift: venv
    uv run python -m tools drift

# run the structural test suite
test: venv
    uv run pytest

# stage a harness payload, validate it, and archive it for distribution
bundle harness: venv
    uv run python -m tools bundle {{ harness }}

# build and install a harness plugin locally, via that harness's own CLI
install harness: venv
    uv run python -m tools install {{ harness }}

# remove build output and caches
clean:
    rm -rf "{{ basedir }}/dist"
    rm -rf "{{ basedir }}/.pytest_cache"
    find "{{ basedir }}" -name "*.pyc" -delete
    find "{{ basedir }}" -name "__pycache__" -type d -exec rm -rf {} +

# remove everything, including the virtual environment
clobber: clean
    uv run pre-commit uninstall || true
    rm -rf "{{ basedir }}/.venv"

# refuse to release unless on main with a clean working tree
release-guard:
    #!/usr/bin/env bash
    set -euo pipefail
    branch=$(git rev-parse --abbrev-ref HEAD)
    if [ "$branch" != "main" ]; then
        echo "error: releases must be created from main (currently on '$branch')"
        exit 1
    fi
    test -z "$(git status --porcelain -uno)" || (echo "error: working tree is dirty"; exit 1)

# bump the version across every harness manifest, commit, tag, and push
release bump="patch": release-guard check
    #!/usr/bin/env bash
    set -euo pipefail
    version=$(uv run python -m tools set-version "{{ bump }}")
    echo "releasing $version"
    # Only the manifests: prettier infers no parser for VERSION or a .toml file.
    npx prettier --write $(uv run python -m tools manifest-paths)
    git add -u
    git commit -m "chore(release): $version"
    git tag -a "$version" -m "$version"
    git push && git push --tags
