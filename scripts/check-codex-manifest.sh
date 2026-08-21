#!/usr/bin/env bash
# Verify the Codex manifest agrees with the shared version and can load its skills.
set -euo pipefail

manifest=".codex-plugin/plugin.json"
version=$(cat VERSION)

jq -e --arg version "$version" \
    '(.version == $version) and ($version | test("^[0-9]+\\.[0-9]+\\.[0-9]+$"))
    and (.skills | type == "string")' "$manifest" >/dev/null || {
    echo "error: $manifest needs the shared N.N.N version and a skills path" >&2
    exit 1
}

skills=$(jq -r .skills "$manifest")
case "$skills" in
    ./*) ;;
    *)
        echo "error: $manifest skills path must begin with ./" >&2
        exit 1
        ;;
esac

test -d "$skills" || {
    echo "error: $manifest skills path does not exist: $skills" >&2
    exit 1
}

echo "Codex manifest agrees: $(jq -r .name "$manifest") $version"
