# Quickstart: validate 001 end to end

Goal: prove the feature works on your laptop with no cloud account and no API key (SC-008).
These are the target commands; tasks create them.

## Prerequisites

- Docker Desktop running, `uv` installed, Python 3.12 (uv installs it).

## Steps

1. `docker compose up -d` — starts Postgres and Jaeger (local trace viewer at http://localhost:16686).
2. `uv sync` — installs locked dependencies.
3. `uv run auditwake create-token --agent reader` and `--agent auditor` — prints each token once and
   writes only its hash to `config/agents.yaml`. Copy tokens into `.env` (git-ignored).
4. `uv run auditwake run-agent --as reader` — expect: report fetched, flag refused, run status
   `completed with denials`.
5. `uv run auditwake run-agent --as auditor` — expect: report fetched, flag stored, status `completed`.
6. `uv run auditwake verify-log` — expect `OK: N entries verified`.
7. Open Jaeger: the run shows one trace with a span per tool and model call; the trace id equals the
   run id printed in step 4.
8. Prove tamper detection: run the documented `psql` edit of one entry (as the owner role), then
   `uv run auditwake verify-log` — expect `BROKEN at seq=K`.
9. `uv run auditwake eval` — expect per-case results and PASS against `evals/baseline.json`.
10. `make check` (or `uv run pytest && uv run ruff check . && uv run mypy .`) — one command for
    everything.

## Expected outcomes (map to success criteria)

| Step | Proves |
|---|---|
| 4, 5 | SC-001 allow-list; FR-018 run status |
| 6, 8 | SC-003 tamper detection |
| 7 | SC-002 span per call, shared run id |
| 9 | SC-005 eval baseline; SC-004 no leaked fake PII |
| overall | SC-008 runs with no account or key |
