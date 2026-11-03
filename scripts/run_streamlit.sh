#!/bin/sh
set -e
cd "$(dirname "$0")/.."

uv run --no-build ruff format
uv run --no-build ruff check --fix
