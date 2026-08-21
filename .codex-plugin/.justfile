# Codex packaging checks for the almanac plugin.

# Recipes in a just module run with the working directory set to the module's own
# directory (.codex-plugin/), while justfile_directory() resolves to the root
# justfile's directory. Every path below is built from `root` for that reason.

root := justfile_directory()

# Check the Codex manifest's cross-file and filesystem invariants.
manifests:
    cd {{ root }} && ./scripts/check-codex-manifest.sh
