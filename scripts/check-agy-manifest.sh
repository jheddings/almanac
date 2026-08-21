#!/usr/bin/env bash
# Verify the Antigravity manifest agrees with the shared version and has required metadata.
set -euo pipefail

manifest=".agy-plugin/plugin.json"
version_file="VERSION"

test -f "$version_file" || {
    echo "error: $version_file is missing" >&2
    exit 1
}

version=$(tr -d '[:space:]' < "$version_file")

jq -e --arg version "$version" \
    '(.version == $version) and ($version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$"))
    and .license == "MIT"' "$manifest" >/dev/null || {
    echo "error: $manifest must match VERSION ($version) and have an MIT license" >&2
    exit 1
}

echo "Antigravity manifest agrees: $(jq -r .name "$manifest") $version"
