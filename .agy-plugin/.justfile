# Antigravity (agy) packaging for the almanac plugin.
#
# Recipes in a just module run with the working directory set to the module's own
# directory (.agy-plugin/), while justfile_directory() resolves to the *root*
# justfile's directory. Every path below is built from `root` for that reason.

root := justfile_directory()

# What ships inside the plugin bundle.
#
# An allowlist: templates/ is load-bearing — `init` reads the contract from
# templates/almanac/README.md. docs/ is absent on purpose: docs/almanac/ is this
# repo's own live almanac, not an adopter's.
payload := "skills templates README.md LICENSE"

# validate the plugin manifest and skills
validate:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root }}"

    manifest=".agy-plugin/plugin.json"
    jq -e '(.version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$")) and .license == "MIT"' \
        "$manifest" >/dev/null || {
        echo "error: $manifest needs an N.N.N version and an MIT license" >&2
        exit 1
    }

    stage="dist/.validate-agy"
    rm -rf "$stage"
    mkdir -p "$stage"
    cp "$manifest" "$stage/plugin.json"
    cp -R skills "$stage/"
    agy plugin validate "$stage"
    rm -rf "$stage"

# stage the plugin payload, validate it, and archive it for distribution
bundle: validate
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root }}"

    version=$(jq -r .version .agy-plugin/plugin.json)
    stage="dist/almanac-agy"
    out="$(pwd)/dist/almanac-agy-${version}.zip"

    rm -rf "$stage"
    mkdir -p "$stage"
    cp .agy-plugin/plugin.json "$stage/plugin.json"
    for path in {{ payload }}; do
        [ -e "$path" ] || { echo "error: payload entry missing: $path" >&2; exit 1; }
        mkdir -p "$stage/$(dirname "$path")"
        cp -R "$path" "$stage/$(dirname "$path")/"
    done

    # `agy plugin validate` reads a directory
    agy plugin validate "$stage"

    # zip appends to an existing archive rather than replacing it
    rm -f "$out"
    (cd "$stage" && zip -rXq "$out" . -x '.DS_Store')

    # An archive that lost plugin.json is invalid. Prove it is at archive root.
    unzip -l "$out" | grep -q '[[:space:]]plugin\.json$' \
        || { echo "error: archive has no root plugin.json" >&2; exit 1; }

    echo
    echo "built $out"
    unzip -l "$out"

# install the plugin locally via agy CLI
install: bundle
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{ root }}"
    stage="dist/almanac-agy"
    agy plugin install "$stage"

# remove build output
clean:
    rm -rf {{ root }}/dist/almanac-agy {{ root }}/dist/almanac-agy-*.zip {{ root }}/dist/.validate-agy
