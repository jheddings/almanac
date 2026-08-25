# Harness-test runs built from the `skel/` fixture.
#
# A module's recipes run from the directory holding the module file, which is not
# the repo root, so `python -m tools` would not resolve without this.
set working-directory := '..'

[private]
default:
    @just --list skel

# scaffold a run as a standalone repository
new label out="":
    uv run python -m tools skel-new {{ label }} {{ if out == "" { "" } else { "--out " + out } }}

# print a prompt to paste into the harness under test
prompt name="01-first-feature":
    uv run python -m tools skel-prompt {{ name }}

# scaffold a run and print its prompt
run label out="" name="01-first-feature": (new label out) (prompt name)

# remove runs created in the default location
clean:
    rm -rf runs
