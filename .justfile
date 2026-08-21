# justfile for the almanac skills.
#
# Recipes here are harness-neutral. Anything specific to packaging for a
# particular harness lives in its own module — `just claude ...`, `just agy ...`,
# and a sibling module per harness as they are added.

mod agy '.agy-plugin/.justfile'
mod claude '.claude-plugin/.justfile'

# Single source of truth for the version, shared across all plugin manifests.
version_file := "VERSION"
claude_plugin := ".claude-plugin/plugin.json"
agy_plugin := ".agy-plugin/plugin.json"

# auto-format all files
tidy:
    npx prettier --write .

# run all checks
check: style validate drift manifests

# check style
style:
    npx prettier --check .

# validate all skills against the vendor-neutral Agent Skills spec
validate:
    for dir in skills/*/; do npx skills-ref validate "$dir"; done

# confirm all manifests agree across harnesses — a mismatch breaks installation
manifests:
    ./scripts/check-manifests.sh

# confirm this repo's almanac README is still an instance of the shipped template
drift:
    python3 scripts/check-template-drift.py

# remove all build output across harnesses
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

# bump the plugin version across harnesses, commit, tag, and push (CI drafts the GitHub release)
release bump="patch": release-guard check
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(tr -d '[:space:]' < {{ version_file }})
    case "{{ bump }}" in
        major|minor|patch)
            IFS=. read -r major minor patch <<< "$current"
            case "{{ bump }}" in
                major) major=$((major + 1)); minor=0; patch=0 ;;
                minor) minor=$((minor + 1)); patch=0 ;;
                patch) patch=$((patch + 1)) ;;
            esac
            version="$major.$minor.$patch"
            ;;
        *) version="{{ bump }}" ;;
    esac
    echo "releasing $current -> $version"
    for mf in {{ claude_plugin }} {{ agy_plugin }}; do
        jq --arg v "$version" '.version = $v' "$mf" > tmp.$$.json && mv tmp.$$.json "$mf"
    done
    printf '%s\n' "$version" > {{ version_file }}
    npx prettier --write {{ claude_plugin }} {{ agy_plugin }}
    git add {{ version_file }} {{ claude_plugin }} {{ agy_plugin }}
    git commit -m "chore(release): $version"
    git tag -a "$version" -m "$version"
    git push && git push --tags
