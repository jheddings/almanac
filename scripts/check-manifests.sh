#!/usr/bin/env bash
# Verify the plugin and marketplace manifests agree with each other.
#
# `claude plugin validate` checks each manifest on its own and passes even when the two
# disagree. A name mismatch between them breaks installation, and it does so only for
# whoever installs the published release — so it has to be caught here.
set -euo pipefail

plugin=".claude-plugin/plugin.json"
marketplace=".claude-plugin/marketplace.json"

jq -e '(.version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$")) and .license == "MIT"' \
    "$plugin" >/dev/null || {
    echo "error: $plugin needs an N.N.N version and an MIT license" >&2
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

echo "manifests agree: $(jq -r .name "$plugin") $(jq -r .version "$plugin")"
