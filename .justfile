# justfile for the almanac skills.
#
# Every harness is declared in `harnesses.toml`, and the recipes below fan out from that
# table rather than naming harnesses here. Adding a harness is a row in the table, not a
# new module, a new script, and four more places that list the same names.
#
# The checks themselves live in `tools/`, which is stdlib-only — `python3 -m tools` needs
# nothing installed. Only the test suite has dependencies.

# auto-format all files
tidy:
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
manifests harness="":
    python3 -m tools check-manifests {{ harness }}

# confirm this repo's almanac README is still an instance of the shipped template
drift:
    python3 -m tools drift

# run the structural test suite
test:
    uv run --quiet pytest

# stage a harness payload, validate it, and archive it for distribution
bundle harness:
    python3 -m tools bundle {{ harness }}

# build and install a harness plugin locally, via that harness's own CLI
install harness:
    python3 -m tools install {{ harness }}

# remove all build output
clean:
    rm -rf dist

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
    version=$(python3 -m tools set-version "{{ bump }}")
    echo "releasing $version"
    # Only the manifests: prettier infers no parser for VERSION or a .toml file.
    npx prettier --write $(python3 -m tools manifest-paths)
    git add -u
    git commit -m "chore(release): $version"
    git tag -a "$version" -m "$version"
    git push && git push --tags
