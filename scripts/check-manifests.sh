#!/usr/bin/env bash
# Verify all plugin and marketplace manifests agree with each other across harnesses.
#
# A name or version mismatch between manifests breaks installation or creates version
# drift across harnesses, and it does so only for whoever installs the published
# release — so it has to be caught here.
set -euo pipefail

claude_plugin=".claude-plugin/plugin.json"
claude_marketplace=".claude-plugin/marketplace.json"
agy_plugin=".agy-plugin/plugin.json"
version_file="VERSION"

[ -f "$version_file" ] || {
    echo "error: $version_file is missing" >&2
    exit 1
}

version=$(tr -d '[:space:]' < "$version_file")

[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
    echo "error: $version_file must contain an N.N.N semantic version" >&2
    exit 1
}

for manifest in "$claude_plugin" "$agy_plugin"; do
    jq -e --arg version "$version" \
        '(.version == $version) and .license == "MIT"' \
        "$manifest" >/dev/null || {
        echo "error: $manifest must match VERSION ($version) and have an MIT license" >&2
        exit 1
    }
done

jq -e '.plugins | length == 1 and .[0].source == "./"' "$claude_marketplace" >/dev/null || {
    echo "error: $claude_marketplace must list exactly one plugin sourced at ./" >&2
    exit 1
}

for field in name description; do
    claude_val=$(jq -r ".$field" "$claude_plugin")
    agy_val=$(jq -r ".$field" "$agy_plugin")
    if [ "$claude_val" != "$agy_val" ]; then
        echo "error: $field disagrees between Claude and AGY manifests" >&2
        echo "  $claude_plugin: $claude_val" >&2
        echo "  $agy_plugin:    $agy_val" >&2
        exit 1
    fi
done

for field in name description; do
    a=$(jq -r ".$field" "$claude_plugin")
    b=$(jq -r ".plugins[0].$field" "$claude_marketplace")
    if [ "$a" != "$b" ]; then
        echo "error: $field disagrees between Claude plugin and marketplace" >&2
        echo "  $claude_plugin:      $a" >&2
        echo "  $claude_marketplace: $b" >&2
        exit 1
    fi
done

echo "manifests agree: $(jq -r .name "$claude_plugin") $version (claude, agy)"
