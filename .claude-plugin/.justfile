# Claude Code packaging for the almanac plugin.
#
# Recipes in a just module run with the working directory set to the module's own
# directory (.claude-plugin/), while justfile_directory() resolves to the *root*
# justfile's directory. Every path below is built from `root` for that reason.

root := justfile_directory()

# What ships inside the plugin archive.
#
# An allowlist, deliberately, not a set of zip exclusions: the repo root doubles
# as the plugin root, so a denylist means every new repo-only directory ships
# until somebody notices. templates/ is load-bearing — `init` reads the contract
# from ${CLAUDE_PLUGIN_ROOT}/templates/almanac/README.md. docs/ is absent on
# purpose: docs/almanac/ is this repo's own live almanac, not an adopter's.
payload := ".claude-plugin/plugin.json skills templates README.md LICENSE"

# confirm the two manifests agree — a name mismatch breaks installation
manifests:
    cd {{ root }} && ./scripts/check-manifests.sh

# stage the plugin payload, validate it, and archive it for distribution
bundle: manifests
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root }}"

    version=$(jq -r .version .claude-plugin/plugin.json)
    stage="dist/almanac"
    out="$(pwd)/dist/almanac-plugin-${version}.zip"

    rm -rf "$stage"
    mkdir -p "$stage"
    for path in {{ payload }}; do
        [ -e "$path" ] || { echo "error: payload entry missing: $path" >&2; exit 1; }
        mkdir -p "$stage/$(dirname "$path")"
        cp -R "$path" "$stage/$(dirname "$path")/"
    done

    # `claude plugin validate` reads a directory and cannot read an archive — it
    # parses the zip as JSON and fails on the "PK" signature. Validate the stage.
    claude plugin validate "$stage"

    # zip appends to an existing archive rather than replacing it
    rm -f "$out"
    (cd "$stage" && zip -rXq "$out" . -x '.DS_Store')

    # An archive that lost .claude-plugin/ still loads: the session starts clean
    # and the plugin is simply absent, with no error on the way in. Prove it is
    # there rather than assuming the copy worked.
    unzip -l "$out" | grep -q '\.claude-plugin/plugin\.json' \
        || { echo "error: archive has no .claude-plugin/plugin.json" >&2; exit 1; }

    echo
    echo "built $out"
    unzip -l "$out"

# remove build output
clean:
    rm -rf {{ root }}/dist
