#!/bin/sh

# ensure we are in the root dir
cd $(dirname $0)/..

# exit upon error
set -e

# remove all dependencies
uv remove pandas requests
uv remove --dev pre-commit pytest pytest-cov ruff

uv lock --upgrade
uv sync --upgrade

# to update uv on macos:
# brew update && brew upgrade uv

uv python upgrade

# re-add all dependencies
uv add pandas requests
uv add --dev pre-commit pytest pytest-cov ruff

uv lock --upgrade
uv sync --upgrade

uv run pre-commit autoupdate

./scripts/run_ruff.sh
./scripts/run_pre-commit.sh

echo DONE
