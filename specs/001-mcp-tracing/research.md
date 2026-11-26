<!-- What this file is: Evidence behind the plan's choices: options checked, prices and sources. -->
# Research: 001 MCP Tools, Audit Log and Tracing

Checked 2026-11-26. Every decision follows the `auditwake-architect` rubric (constitution, cost,
local-first, reversibility, impact, simplicity, learnability, portfolio value).

## Verified facts (sources: vendor pages and PyPI, checked today)

| Fact | Source |
|---|---|
| PyPI latest: mcp 2.3.0, opentelemetry-sdk 1.45.2, pydantic 2.14.4, psycopg 3.3.9, structlog 26.1.0, pytest 9.2.0, mypy 2.4.1, ruff 0.17.6, testcontainers 4.15.0 (all need Python ≥ 3.10) | pypi.org JSON API |
| MCP SDK 2.x exposes `from mcp.server import MCPServer` and `from mcp import Client`; stdio and streamable HTTP transports | PyPI README of mcp 2.3.0 |
| Neon Free: 1 GB storage and 100 CU-hours per project, up to 100 projects, no overage billing, writes that grow storage fail at the cap, scale to zero after 5 min | [neon.com free plan FAQ](https://neon.com/faqs/free-plan-limits-and-quotas) |
| Cloud Run free tier: 2M requests; request-based billing Tier 1: 180,000 vCPU-s and 360,000 GiB-s per month | [cloud.google.com/run/pricing](https://cloud.google.com/run/pricing) |
| Artifact Registry: 0.5 GB free, then $0.10/GB-month | [cloud.google.com/artifact-registry/pricing](https://cloud.google.com/artifact-registry/pricing) |
| Secret Manager: 6 active versions and 10,000 accesses free, then $0.06/version and $0.03 per 10k accesses | [cloud.google.com/secret-manager/pricing](https://cloud.google.com/secret-manager/pricing) |
| Vercel Hobby is for personal non-commercial use only | [vercel.com/docs/plans/hobby](https://vercel.com/docs/plans/hobby) |
| Grafana Cloud free trace retention is 14 days per the docs; some pages say 30 | [grafana.com traces docs](https://grafana.com/docs/grafana-cloud/platform/pricing-and-usage/traces/) |

## Unverified (confirm before depending on them)

- pgvector available on Neon Free (almost certainly, but not confirmed by this search; needed in 003).
- Grafana Cloud free trace ingest cap and exact retention.
- Image size of the Auditwake container (decides Artifact Registry cost).
- Exact `mcp` 2.x API for auth/identity on stdio and in-memory transports (spike task).

## Decisions

### D1. Persistence: Postgres for the audit log
- **Decision**: Postgres (local container; Neon when hosted).
- **Why**: one global chain needs ordered, concurrency-safe appends; Postgres gives advisory locks,
  triggers, and later pgvector. Integration tests use a real container.
- **Alternatives**: SQLite (simpler, but migration later and no pgvector); flat file (hard to make
  concurrency-safe and queryable).

### D2. Trace backend
- **Decision**: OTel SDK exporting OTLP/HTTP. Local default: Jaeger all-in-one container. Hosted
  option (later, optional): Grafana Cloud free.
- **Why**: $0, local-first, swappable by changing one endpoint variable.
- **Alternatives**: Langfuse (dropped by owner), Honeycomb free (not evaluated), console exporter
  only (no UI).

### D3. Identity
- **Decision**: per-agent random token, SHA-256 hash stored in `config/agents.yaml`, constant-time
  compare.
- **Why**: real least privilege locally with no services; matches production practice at small scale.
- **Alternatives**: claimed name (no security), one process per agent (clumsy), full OAuth (over
  scope; revisit for the deployed HTTP gateway).
- **Concept for beginners**: passwords need slow hashes (bcrypt) because people choose guessable
  ones. Random 32-byte tokens cannot be guessed, so a fast hash is enough.

### D4. Hash chain
- **Decision**: SHA-256 over canonical JSON plus previous hash; genesis constant; advisory lock on
  append; trigger blocks UPDATE/DELETE; `verify-log` walks the chain and reports the first bad
  entry.
- **Note**: a hash chain proves *internal consistency*. An attacker with full database control could
  rewrite the whole chain. Mitigation for later: publish periodic checkpoint hashes outside the
  database (documented limitation in the threat model, not claimed as solved).

### D5. Redaction
- **Decision**: regex for emails and phone numbers, Luhn-validated card/bank-like numbers, fixed list
  of fake names. Placeholders like `[EMAIL]`.
- **Alternatives**: Presidio or ML NER (heavy install, slower cold start, more to learn; revisit if
  real data ever enters).

### D6. MCP transport for 001
- **Decision**: in-memory client/server for tests, stdio for the demo; the gate takes the token as a
  parameter so HTTP bearer tokens plug in during 002.
- **Spike task** confirms how 2.x passes credentials on each transport.

### D7. Evals
- **Decision**: YAML cases, deterministic runner, `baseline.json` with per-category pass rate.
  Thresholds 90% overall, 100% security categories. Categories: allowed, denied, invalid input,
  unknown tool, bad token, redaction, tamper, run status.
- **Runs in CI** against a Postgres service container; target under 60 s.

### D8. Tooling and CI
- **Decision**: uv, ruff, mypy, pytest, pre-commit (exists), gitleaks (exists), pip-audit,
  Dependabot. CI jobs: lint, types, unit, integration, evals, build image, pip-audit, secret-scan.

### D9. Hosting split
- **Decision**: Cloud Run (compute, from 002) + Neon (database) + Vercel Hobby (viewer, 004).
  001 is local only.
- **Why**: Cloud SQL has a recurring floor, so it is rejected. Neon free is $0.

### D10. Overhead measurement
- **Decision**: a benchmark script runs N calls with auditing/tracing on and off (a test-only
  bypass), reports the median difference. Result recorded in `docs/measurements.md` only after it is
  really run.
