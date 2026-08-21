#!/usr/bin/env bash
# Verify the Cursor plugin and marketplace manifests agree with each other and VERSION.
#
# Cursor has no archive validator analogous to `claude plugin validate`. A name
# mismatch between the two manifests, or a version that drifted from VERSION, is
# still a silent install-time failure for whoever takes the published tree.
set -euo pipefail

plugin=".cursor-plugin/plugin.json"
marketplace=".cursor-plugin/marketplace.json"
version=$(cat VERSION)

jq -e --arg version "$version" \
    '(.version == $version) and ($version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$"))
    and .license == "MIT"' "$plugin" >/dev/null || {
    echo "error: $plugin needs the shared N.N.N version and an MIT license" >&2
    exit 1
}

jq -e '.plugins | length == 1 and .[0].source == "./"' "$marketplace" >/dev/null || {
    echo "error: $marketplace must list exactly one plugin sourced at ./" >&2
    exit 1
}

for field in name description; do
    a=$(jq -r ".$field" "$plugin")
    b=$(jq -r ".plugins[0].$field" "$marketplace")
    if [ "$a" != "$b" ]; then
        echo "error: $field disagrees between manifests" >&2
        echo "  $plugin:      $a" >&2
        echo "  $marketplace: $b" >&2
        exit 1
    fi
done

for key in skills commands; do
    path=$(jq -r ".$key" "$plugin")
    case "$path" in
        ./*) ;;
        *)
            echo "error: $plugin $key path must begin with ./" >&2
            exit 1
            ;;
    esac
    test -d "$path" || {
        echo "error: $plugin $key path does not exist: $path" >&2
        exit 1
    }
done

echo "Cursor manifests agree: $(jq -r .name "$plugin") $version"
