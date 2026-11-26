# Auditwake Constitution

Auditwake is a flight recorder and governance layer for AI agents. It produces audit
evidence; it never claims compliance.

## Core Principles

### I. Python-First, One Documented Exemption
Backend, evals, tracing, guardrails and infra tooling MUST be Python 3.12 managed with uv.
Go, Rust and Ruby MUST NOT be used. React + TypeScript is permitted ONLY under `/web`, as a
read-only thin client using a client generated from the FastAPI OpenAPI spec; no Node
backend logic is allowed. This exemption MUST be recorded as an ADR. Any further language
exemption requires a new ADR and a constitution amendment.
Rationale: depth in one stack; the single exemption exists because the author already
knows JS/TS and the viewer carries no business logic.

### II. Test-First (NON-NEGOTIABLE)
Acceptance tests and evals MUST be written, and seen failing, before implementation.
The test pyramid is: unit (pytest) > integration (containerized Postgres) > small e2e >
evals. Every bug fix MUST add a regression test. One command MUST run the full suite
locally.
Rationale: regression safety is the core claim of a governance product.

### III. Deterministic, Keyless CI
All LLM calls MUST go through a provider interface with a deterministic fake provider.
CI MUST run with no API keys and no cost. Provider calls MUST support record/replay.
MCP tools and the OpenAPI spec MUST have contract tests; CI MUST fail on breaking API
changes.

### IV. Evals Gate the Build
Eval datasets MUST be versioned in `/evals` with a stored baseline. CI MUST fail if
recall@k, faithfulness, judge score or injection block rate drops below its threshold.
Thresholds change only via a reviewed commit that explains why.

### V. Least Privilege and Defense in Depth
Each agent MUST have an explicit tool allow-list; default is deny. Inputs MUST be
validated with Pydantic. PII MUST be redacted before anything is logged or traced. Secrets
live in Secret Manager only. No commit may contain a secret: a pre-commit secret scan (gitleaks)
MUST pass locally and the same scan MUST run in CI on every push and pull request; a finding
blocks the merge and the leaked credential MUST be revoked, not just deleted. CORS MUST be limited to the viewer
origin. Per-key rate limits are required. Only low-cost controls are adopted; paid
scanners, WAFs and pen tests are out of scope.

### VI. Trace and Audit Every Call
Every model call and tool call MUST emit an OpenTelemetry span and an entry in an
append-only, hash-chained audit log. Instrumentation MUST use OpenTelemetry only and stay
backend-neutral (OTLP export); the trace backend is chosen in the plan via an ADR and MUST
be swappable without application code changes. Logs MUST be structured JSON carrying
trace IDs. Cost per request MUST appear in traces.

### VII. Cost Control
Spend MUST stay near $0/month. Per-key and global LLM spend caps, response caching and
GCP budget alerts are required. No feature may add recurring cost without an ADR and
explicit approval.

### VIII. Simplicity: Modular Monolith
One deployable backend with modules `src/auditwake/{agent,tools,model_access,retrieval,
guardrails,telemetry}`. No microservices without an ADR showing a measured need. Design
target is a single owner plus at most 5 users; scaling beyond that is a non-goal. Keep the
cheap reliability basics: stateless containers, async I/O, pooling, timeouts, retries with
backoff and jitter, bounded fallback, a low max-instance cap, indexes, pagination. A small
load test records real numbers for that target only.

### XI. Local-First
The whole system MUST run locally with one command (docker compose plus uv) using the fake
provider and a local Postgres, with no cloud account or API key. Cloud deployment is an
optional layer on top, never a prerequisite for development or testing.

### IX. Honest Metrics and Claims
Only real, measured numbers MAY be recorded (load tests, eval scores, costs). Numbers MUST
NOT be invented or estimated without being labelled as estimates. Documentation MUST NOT
claim compliance or scale that was not demonstrated; limits MUST be documented.

### X. Synthetic Data and Privacy
Only synthetic or public data is allowed: no employer code, data or credentials. Test PII
MUST be fake. Log retention MUST be documented.

### XII. Beginner-Friendly and Teachable
Plans, specs, tasks and docs MUST be written as if a complete beginner is building the
project. Every task MUST be small (one sitting), state its goal in plain language, explain
each new technical concept it introduces (what it is, why Auditwake needs it, a simple
example), list prerequisites and exact commands, and end with a way to verify success.
Jargon MUST be defined at first use or linked to `docs/glossary.md`. Tasks MUST be ordered
so no task needs a concept that is introduced later. Follow the `auditwake-beginner-guide`
skill for the task format.
Rationale: the author is learning these topics; a backlog that teaches is the deliverable.

## Technical Constraints

- Deploy: backend on GCP Cloud Run (min instances 0) via Terraform, with Secret Manager and
  Artifact Registry; UI on Vercel Hobby (non-commercial); Postgres + pgvector on a free-tier
  host chosen from options verified against current limits in the plan.
- Maintainability: ruff, mypy or pyright, pre-commit, ADRs per major choice, architecture
  diagram in README, reproducible builds (uv lock, Docker), documented rollback.
- CI (GitHub Actions): lint, test, evals, build, terraform plan, deploy on tag; pip-audit
  and Dependabot enabled.
- Reliability: health and readiness endpoints, graceful degradation, 2–3 SLIs/SLOs, a
  one-page runbook, and a short STRIDE-lite threat model.
- Viewer (feature 004): loading, error and empty states; keyboard navigation.

## Development Workflow & Quality Gates

Work follows Spec Kit order: constitution → specify → clarify → plan → checklist → tasks →
analyze → implement, one feature at a time (001 mcp-tracing, 002 gateway-guardrails,
003 rag-evals, 004 audit-viewer). Each NFR MUST map to a spec criterion, a task and a test.
Definition of Done: tests pass, evals pass, traces visible, docs updated, ADR recorded,
costs within budget.

## Governance

This constitution supersedes other practices. Amendments require a written proposal, an
ADR where a principle changes, and a version bump: MAJOR for removed or redefined
principles, MINOR for added principles or materially expanded guidance, PATCH for
clarifications. Every PR MUST be reviewed for compliance; added complexity MUST be
justified in the PR or an ADR. `/speckit-analyze` is run before implementation to detect
drift between constitution, spec, plan and tasks.

**Version**: 1.2.1 | **Ratified**: 2026-11-24 | **Last Amended**: 2026-11-24
