<!-- What this file is: HOW: tech choices, project layout, risks and design decisions. -->
# Implementation Plan: MCP Tools, Audit Log and Tracing

**Branch**: `001-mcp-tracing` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-mcp-tracing/spec.md`

## Summary

Build the first slice of Auditwake: a Python MCP server with three demo tools, a per-agent
allow-list identified by hashed tokens, one global hash-chained audit log in Postgres, OpenTelemetry
spans on every call, a scripted demo agent that uses a deterministic fake model, and a 12-case eval
set with a stored baseline. Everything runs locally with one command; CI runs keyless.
Research and decisions: [research.md](research.md). ADRs: [docs/adr/](../../docs/adr/).

## Technical Context

**Language/Version**: Python 3.12, managed with uv (`uv.lock` committed)

**Primary Dependencies**: `mcp` (official SDK, 2.x), `opentelemetry-sdk` and OTLP/HTTP exporter,
`pydantic` v2, `psycopg` 3 with pool, `structlog`, `pyyaml`. Dev: `pytest`, `pytest-asyncio`,
`testcontainers`, `ruff`, `mypy`, `pip-audit`, `pre-commit`

**Storage**: Postgres (local container for dev and tests; Neon free tier when hosted). Synthetic
reports and policy clauses are JSON files in `data/`, loaded in memory

**Testing**: pytest (unit, integration with containerized Postgres, contract, small e2e), plus the
eval runner in `evals/`

**Target Platform**: macOS/Linux dev machine via `docker compose` + uv; Linux container for Cloud Run
later

**Project Type**: single Python project (modular monolith), CLI + MCP server

**Performance Goals**: auditing and tracing add under 50 ms median per tool call (SC-006), eval set
under 60 s (SC-005). Real numbers are measured and recorded in `docs/measurements.md`

**Constraints**: no cloud account or API key needed to develop or test; near $0/month; fail closed
if the audit log is unavailable; trace backend failure must never stop a run

**Scale/Scope**: owner plus at most 5 users; tens of reports, a handful of policy clauses

## Constitution Check

*GATE: passed before research; re-checked after design (all still pass).*

| # | Principle | Status | How this plan complies |
|---|---|---|---|
| I | Python-first | Pass | All code Python 3.12; `/web` not touched until feature 004 (ADR-0001) |
| II | Test-first | Pass | Every task writes the failing test first (see tasks later); pyramid in this plan |
| III | Keyless CI | Pass | Fake provider only in 001; contract tests snapshot MCP tool schemas |
| IV | Evals gate build | Pass | 12 cases, baseline file, CI step fails below 90% / 100% security |
| V | Least privilege | Pass | Hashed per-agent tokens, default deny, Pydantic validation, redaction, gitleaks |
| VI | Trace and audit | Pass | One span per call, one audit entry per call, shared run id, JSON logs |
| VII | Cost control | Pass | $0 expected; no LLM spend in 001; budget alert Terraform written for later |
| VIII | Modular monolith | Pass | One package, one process. Extra `storage/` module justified below |
| IX | Honest metrics | Pass | Overhead and eval scores are measured and logged; no invented numbers |
| X | Synthetic data | Pass | Fake names, emails, cards (Luhn-valid test numbers) only |
| XI | Local-first | Pass | `docker compose up` + `uv run` is the whole setup |
| XII | Beginner-friendly | Pass | Tasks follow the beginner guide format; glossary added |

**Deferred to 002 by design** (not forgotten): `terraform plan` and deploy-on-tag in CI, HTTP
health/readiness endpoints, per-key rate limits, CORS, OpenAPI diff and record/replay.

**NFR coverage map** (every NFR has a spec criterion, a task and a test; 001 covers the rows marked
"001", the rest are scheduled and checked by `/speckit-analyze`):

| NFR | 001 coverage | Later |
|---|---|---|
| 1 Testability | 001: pyramid, fake provider, baseline, contract tests, one-command run | record/replay (002), OpenAPI diff (002) |
| 2 Scalability (right-sized) | 001: pooled DB connections, async I/O, timeouts, small load check | Cloud Run caps (002) |
| 3 Security | 001: tokens, validation, redaction, hash chain, gitleaks, pip-audit, STRIDE-lite | CORS, rate limits (002) |
| 4 Observability | 001: spans, JSON logs, run id, health check command | SLOs and runbook (002) |
| 5 Cost control | 001: budget alert Terraform, $0 LLM | per-key caps (002) |
| 6 Maintainability | 001: ruff, mypy, pre-commit, ADRs, diagram, CI, uv lock, Docker, rollback doc | deploy on tag (002) |
| 7 Data and privacy | 001: synthetic data, retention rule (90 days), fake PII | |
| 8 Viewer UX | not in 001 | 004 |

## Architecture

```
 Demo agent (scripted, fake model)
        │  MCP (in-memory for tests, stdio for demo; HTTP bearer later)
        ▼
 MCP server ── tools/  get_expense_report · get_policy_clause · flag_expense_report
        │         │
        │         ▼ every call goes through one gate:
        │   guardrails/  authenticate(token) → allow-list → validate → redact
        │         │
        ▼         ▼
 telemetry/  span + JSON log (run id = trace id)      storage/  Postgres
        │                                              ├─ audit_entries (hash chain, append-only)
        ▼ OTLP                                         ├─ flags
 Jaeger (local) / optional hosted backend              └─ runs
```

## Project Structure

### Documentation (this feature)

```text
specs/001-mcp-tracing/
├── plan.md  research.md  data-model.md  quickstart.md
├── contracts/ (mcp-tools.md, audit-log.md)
├── checklists/requirements.md
└── tasks.md            # created by /speckit-tasks
```

### Source Code (repository root)

Layout follows ADR-0011: two Python projects under `src/`, one process in 001.

```text
src/
├── backend/                        # own pyproject.toml + uv.lock; never imports agents
│   ├── auditwake_backend/
│   │   ├── config.py               # settings from environment (pydantic)
│   │   ├── storage/                # Postgres pool, migrations, repositories
│   │   └── telemetry/              # tracing setup, JSON logging, audit chain, verifier
│   └── tests/unit/
├── agents/                         # own pyproject.toml + uv.lock; depends on backend (local path)
│   ├── auditwake_agents/
│   │   ├── cli.py                  # commands: run-agent, verify-log, eval, create-token
│   │   ├── agent/                  # profiles, scripted demo agent, run status
│   │   ├── tools/                  # MCP server, three tools, input schemas
│   │   ├── model_access/           # provider interface + deterministic fake (real providers in 002)
│   │   └── guardrails/             # token auth, allow-list gate, redaction
│   ├── evals/                      # cases/*.yaml (12 versioned cases), baseline.json, run_evals.py
│   └── tests/unit/
└── frontend/                       # created in 004, not in 001
tests/                              # cross-project: integration/ contract/ e2e/ fixtures/ conftest.py
data/                               # synthetic reports.json, policy.json
config/agents.yaml                  # profiles + token hashes (never raw tokens)
infra/                              # compose.yaml, Dockerfile, terraform/ (written in 001, applied from 002)
pipelines/                          # check_services.py, bench_overhead.py, load_check.py,
                                    # check_commit_msg.py, check_pr_meta.py
Makefile  ruff.toml  .dockerignore  .env.example
docs/ adr/ glossary.md measurements.md runbook.md threat-model.md retention.md rollback.md
     branching.md dev-tooling.md spikes/mcp-sdk.md
.github/workflows/                  # ci.yml (lint, type, test, evals, build, audit); GitHub requires this path
```

**Structure Decision**: two projects, one process (ADR-0011). `agents` imports `backend`, never the
reverse. `storage/` stays on the backend side because Postgres access needs a home that is not
telemetry or tools. `retrieval/` (003) will be added under `src/agents/` later so nothing unused is built.

## Key Design Decisions (each has an ADR)

1. **Identity**: random 256-bit token per agent; store SHA-256 hash; constant-time compare. A fast
   hash is right here because tokens are random, not guessable passwords (ADR-0006).
2. **One gate**: every tool call passes `guardrails.gate()` which authenticates, checks the
   allow-list, validates input, runs the tool, redacts, then writes span + audit entry. No tool can
   skip it (ADR-0005).
3. **Audit chain**: `entry_hash = SHA-256(canonical JSON of entry + prev_hash)`. Appends take a
   Postgres advisory lock so concurrent calls form one ordered chain. Update/delete are blocked by
   a trigger and by a database role with insert/select only. `verify-log` re-walks the chain
   (ADR-0005).
4. **Fail closed**: the flag record and its audit entry are written in one transaction. If the audit
   write fails, the tool result is withheld and the call is reported failed.
5. **Run id = trace id**: one identifier across span, log lines and audit entries (FR-008). It is
   generated at run start in trace-id format (32 hex characters) so the same value is later used as
   the trace id; no rework when tracing arrives.
6. **Telemetry never blocks**: bounded span queue, short export timeout, drop on failure (FR-010).
7. **Redaction**: regex for emails and phones, Luhn check for card numbers, fixed fake-name list
   (ADR-0007).
8. **Run status**: completed / completed with denials / failed (FR-018).

## Deployment, Cost and Risks

Facts below were checked on 2026-11-26 from vendor pages; items without a source are
`[UNVERIFIED]` and are tasks to confirm before relying on them. Details in [research.md](research.md).

**Scope for 001:** the demo is a local CLI/MCP process, not a web service, so 001 is **not deployed**.
We ship the Dockerfile, compose file, CI and Terraform (validated, not applied). First deploy happens
with the HTTP gateway in 002 (ADR-0009).

| Piece | Choice | Free limit (verified date) | Expected monthly cost |
|---|---|---|---|
| Backend (later) | GCP Cloud Run, min instances 0 | 2M requests, 180k vCPU-s, 360k GiB-s free (request-based, Tier 1), 2026-11-26 | ~$0 `ESTIMATE` at 5 users |
| Images | Artifact Registry | first 0.5 GB free, then $0.10/GB-month | $0 if image history stays < 0.5 GB; keep last 3 images `ESTIMATE` |
| Secrets | Secret Manager | 6 active versions and 10k accesses free; $0.06/version after | $0 if ≤ 6 active versions |
| Database | Neon free plan | 1 GB storage and 100 CU-hours per project; no overage billing; scale to zero after 5 min (neon.com, Nov 2026) | $0. pgvector on free plan `[UNVERIFIED]` |
| Traces (deployed) | Optional Grafana Cloud free | 14-day trace retention likely; sources conflict (14 vs 30), ingest cap not confirmed `[UNVERIFIED]` | $0 if used; otherwise local Jaeger only |
| Viewer (004) | Vercel Hobby | non-commercial personal use only | $0 |
| LLM | Fake provider in 001 | n/a | $0 (real Sonnet/Haiku spend begins in 002 under per-key caps) |
| **Total 001** | | | **$0 `ESTIMATE`** |

**Budget alerts:** Terraform defines a GCP billing budget with alert thresholds. A budget only sends
alerts; it does not stop spending. Hard stop is the low Cloud Run instance cap plus app-level
spend caps (002).

**Risks**

| Risk | Impact | Mitigation |
|---|---|---|
| `mcp` SDK is on major version 2; APIs may differ from older tutorials | Wasted time, wrong code | Spike task first: confirm server, in-memory client and auth hook against the installed version |
| Neon free storage (1 GB) fills with audit/trace rows | Writes fail | 90-day retention job; small summaries only; tripwire in architect skill |
| Hash chain pruning breaks verification | Cannot verify old log | Retention archives a checkpoint hash, then prunes before it (designed in data-model) |
| Free-tier terms change | Surprise cost | Re-verify limits at each ADR revisit; budget alerts |
| Cold starts on Cloud Run | Slow first call | Accept; longer client timeout |
| Fake-name redaction misses real names | Name leakage in future real data | Out of scope for 001 (synthetic only); note in threat model |

## Complexity Tracking

| Item | Why needed | Simpler alternative rejected because |
|---|---|---|
| Postgres in 001 | Ordered global chain with concurrency-safe appends; reused for pgvector in 003 | SQLite would be simpler but forces a migration and loses the real-database integration tests |
| `storage/` module | Keeps SQL out of tools and telemetry | Putting SQL in telemetry mixes concerns and hurts testability |
