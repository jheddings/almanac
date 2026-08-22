# Cursor packaging for the almanac plugin.
#
# Recipes in a just module run with the working directory set to the module's own
# directory (.cursor-plugin/), while justfile_directory() resolves to the *root*
# justfile's directory. Every path below is built from `root` for that reason.

root := justfile_directory()

# What ships inside the plugin archive.
#
# An allowlist, deliberately, not a set of zip exclusions: the repo root doubles
# as the plugin root, so a denylist means every new repo-only directory ships
# until somebody notices. templates/ is load-bearing — `init` reads the contract
# from the plugin root. docs/ is absent on purpose: docs/almanac/ is this repo's
# own live almanac, not an adopter's. Commands live under .cursor-plugin/ so a
# Claude marketplace install (source: "./") does not auto-discover them.
payload := ".cursor-plugin/plugin.json .cursor-plugin/commands skills templates README.md LICENSE"

# confirm the two manifests agree and match VERSION
manifests:
    cd {{ root }} && ./scripts/check-cursor-manifest.sh

# stage the plugin payload, structurally validate it, and archive it
bundle: manifests
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root }}"

    version=$(tr -d '[:space:]' < VERSION)
    stage="dist/almanac-cursor"
    out="$(pwd)/dist/almanac-cursor-plugin-${version}.zip"

    rm -rf "$stage"
    mkdir -p "$stage"
    for path in {{ payload }}; do
        [ -e "$path" ] || { echo "error: payload entry missing: $path" >&2; exit 1; }
        mkdir -p "$stage/$(dirname "$path")"
        cp -R "$path" "$stage/$(dirname "$path")/"
    done

    # No Cursor archive validator assumed. Structural checks on the stage:
    test -f "$stage/templates/almanac/README.md"
    test -f "$stage/.cursor-plugin/commands/init.md"
    test ! -e "$stage/docs"

    # zip appends to an existing archive rather than replacing it
    rm -f "$out"
    (cd "$stage" && zip -rXq "$out" . -x '.DS_Store')

    # An archive that lost .cursor-plugin/ still loads: the session starts clean
    # and the plugin is simply absent, with no error on the way in. Prove it is
    # there rather than assuming the copy worked.
    #
    # Capture the listing first. Piping straight into `grep -q` races: grep exits
    # on the first match, unzip takes SIGPIPE, and `pipefail` reports 141 for a
    # perfectly good archive. See docs/almanac/.
    listing=$(unzip -l "$out")
    grep -q '\.cursor-plugin/plugin\.json' <<<"$listing" \
        || { echo "error: archive has no .cursor-plugin/plugin.json" >&2; exit 1; }
    if grep -q '[[:space:]]docs/' <<<"$listing"; then
        echo "error: archive must not contain docs/" >&2
        exit 1
    fi

    echo
    echo "built $out"
    unzip -l "$out"

# remove this harness's build output
clean:
    rm -rf {{ root }}/dist/almanac-cursor {{ root }}/dist/almanac-cursor-plugin-*.zip
