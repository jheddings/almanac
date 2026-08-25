# justfile for the almanac skills.
#
# Harnesses are declared in `harnesses.toml`. The recipes read that table, so a harness
# is named in one place and the recipes below stay the same as harnesses are added.
#
# Everything Python runs through `uv run` against the environment `venv` syncs. Recipes
# that need it depend on `venv`, so the environment is current before anything runs.

basedir := justfile_directory()

# sync the environment, install hooks, and run the full preflight
default: setup preflight

# set up the local development environment
setup: venv
    uv run pre-commit install --install-hooks --overwrite

# sync the virtual environment
venv:
    uv sync --all-extras

# auto-format all files
tidy: venv
    npx prettier --write .

# run all static checks
check: style validate manifests drift

# run unit tests
test: venv
    uv run pytest

# full static checks and unit tests
preflight: check test

# check formatting
style:
    npx prettier --check .

# validate all skills against the vendor-neutral Agent Skills spec
validate:
    for dir in skills/*/; do npx skills-ref validate "$dir"; done

# confirm the manifests agree — a mismatch breaks installation for whoever installs
manifests harness="": venv
    uv run python -m tools check-manifests {{ harness }}

# confirm this repo's almanac README is an instance of the shipped template
drift: venv
    uv run python -m tools drift

# stage a harness payload, validate it, and archive it for distribution
bundle harness: venv
    uv run python -m tools bundle {{ harness }}

# build a harness archive and install it through that harness's own CLI
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
    #!/usr/bin/env bash
    set -euo pipefail
    # Hooks live in the shared common git dir, so uninstalling from a linked worktree
    # would disarm them for the main checkout too. See docs/almanac/.
    if [ "$(git rev-parse --git-dir)" = "$(git rev-parse --git-common-dir)" ]; then
        uv run pre-commit uninstall || true
    else
        echo "skipping pre-commit uninstall: hooks are shared, and this is a worktree"
    fi
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
release bump="patch": release-guard preflight
    #!/usr/bin/env bash
    set -euo pipefail
    version=$(uv run python -m tools set-version "{{ bump }}")
    echo "releasing $version"
    # Prettier infers a parser from the extension, so it takes the manifests only.
    npx prettier --write $(uv run python -m tools manifest-paths)
    git add -u
    git commit -m "chore(release): $version"
    git tag -a "$version" -m "$version"
    git push && git push --tags

# scaffold a harness-test run from the skel fixture
skel-new label out="": venv
    uv run python -m tools skel-new {{ label }} {{ if out == "" { "" } else { "--out " + out } }}

# print a prompt to paste into the harness under test
skel-prompt name="01-first-feature": venv
    uv run python -m tools skel-prompt {{ name }}

# scaffold a run and print the prompt to paste
skel-run label out="" name="01-first-feature": (skel-new label out) (skel-prompt name)

# score a completed harness-test run
skel-check label dir="": venv
    uv run python -m tools skel-check {{ label }} {{ if dir == "" { "" } else { "--from " + dir } }}

# remove harness-test runs
skel-clean:
    rm -rf "{{ basedir }}/runs"
