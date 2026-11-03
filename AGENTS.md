# AGENTS.md

- Call `uv run` and `uv sync` with `--no-build`. Every dependency ships wheels, and the flag stops package setup scripts from running (SonarCloud shell:S8541).
- Don't leave commented-out code; delete it (SonarCloud python:S125).
