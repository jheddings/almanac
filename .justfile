# single source of truth for the plugin version
plugin := ".claude-plugin/plugin.json"

# auto-format all supported files
tidy:
    npx prettier --write .

# run all checks
check: style validate manifests

# check formatting
style:
    npx prettier --check .

# validate every skill against the Agent Skills specification
validate:
    for dir in skills/*/; do npx skills-ref validate "$dir"; done

# validate plugin metadata and internal consistency
manifests:
    jq -e '.name == "almanac" and (.version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$")) and .license == "MIT"' {{plugin}} >/dev/null
    jq -e '.plugins | length == 1 and .[0].name == "almanac" and .[0].source == "./"' .claude-plugin/marketplace.json >/dev/null
    test "$(jq -r .name {{plugin}})" = "$(jq -r '.plugins[0].name' .claude-plugin/marketplace.json)"

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

# bump the plugin version, commit, tag, and push (CI drafts the GitHub release)
release bump="patch": release-guard check
    #!/usr/bin/env bash
    set -euo pipefail
    current=$(jq -r '.version' {{plugin}})
    case "{{bump}}" in
        major|minor|patch)
            IFS=. read -r major minor patch <<< "$current"
            case "{{bump}}" in
                major) major=$((major + 1)); minor=0; patch=0 ;;
                minor) minor=$((minor + 1)); patch=0 ;;
                patch) patch=$((patch + 1)) ;;
            esac
            version="$major.$minor.$patch"
            ;;
        *) version="{{bump}}" ;;
    esac
    echo "releasing $current -> $version"
    jq --arg v "$version" '.version = $v' {{plugin}} > tmp.$$.json && mv tmp.$$.json {{plugin}}
    npx prettier --write {{plugin}}
    git add {{plugin}}
    git commit -m "chore(release): $version"
    git tag -a "$version" -m "$version"
    git push && git push --tags
