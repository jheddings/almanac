# Project tasks for skinner.

# List the available recipes.
default:
    @just --list

# Sync the virtual environment.
setup:
    uv sync

# Lint and check formatting.
check: setup
    uv run ruff check .
    uv run ruff format --check .

# Run the test suite.
test: setup
    uv run pytest

# Run every check.
preflight: check test

# Format the tree.
tidy:
    uv run ruff format .
