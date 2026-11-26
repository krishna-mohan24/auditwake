# `make check` runs lint, format check, types and tests for the whole repo.
.PHONY: check
check:
	uvx ruff@0.17.6 check .
	uvx ruff@0.17.6 format --check .
	cd src/backend && uv run mypy && uv run pytest -q
	cd src/agents && uv run mypy && uv run pytest -q
	uvx pytest -q tests/unit/test_commit_rules.py
