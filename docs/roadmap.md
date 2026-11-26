# Roadmap: features 002 to 004 (outline only)

Detailed specs come later, one feature at a time (`/speckit-specify` → clarify → plan → checklist →
tasks → analyze). Each feature follows the constitution, the architect skill and the beginner guide.
Effort sizes are relative `ESTIMATE`s, not commitments.

| Feature | One-line goal | Depends on | Size |
|---|---|---|---|
| 001 mcp-tracing | Permissioned tools, audit chain, traces, 12-case eval baseline | none | M (in progress: planned) |
| 002 gateway-guardrails | A cost-controlled model gateway with guardrails; first cloud deploy | 001 | L |
| 003 rag-evals | Policy question answering with measured retrieval and answer quality | 001, 002 | L |
| 004 audit-viewer | Read-only React viewer for traces, audit log and eval results | 002 API | M |
| later: human approval | LangGraph step that pauses high-risk actions for a person | 003 | S–M |

## 002 gateway-guardrails

**Goal**: all model calls go through one FastAPI gateway that routes, falls back, caches, meters
spend, and applies guardrails. This is the first deployed service.

**Scope (outline)**
- Provider interface gets two real adapters: Claude Sonnet (primary) and Claude Haiku (fallback);
  routing and a bounded fallback (no retry storms); response cache; record/replay of provider calls
  so CI stays keyless.
- Per-key quotas, rate limits, per-key and global spend caps; cost per request in traces.
- Guardrails: PII redaction on the way in and out, prompt-injection test suite with a measured block
  rate, tool allow-lists carried over from 001.
- HTTP API: health and readiness endpoints, OpenAPI contract tests that fail CI on breaking changes,
  CORS limited to the viewer origin, Bearer-token auth reusing the 001 token logic.
- Deploy: Cloud Run (min instances 0, low max-instances), Neon, Secret Manager, Artifact Registry,
  Terraform apply, budget alert live, deploy on tag, runbook and 2–3 SLOs measured.

**Decisions to research before planning**: Anthropic API terms and prices (verify), prompt caching
use, injection test sources (public datasets only), best cache key design, Cloud Run cold-start
numbers (measure), whether Neon free tier suits the load.

**Success signals (to be measured, not promised)**: injection block rate against the stored
baseline, fallback works when the primary is forced to fail, spend cap stops calls, p50/p95 recorded.

**Risks**: real API cost (mitigate with caps, replay, cheap model for tests), vendor API changes,
cold starts, free-tier limits.

**Branches (indicative)**: `FEAT-AGENT/model-gateway`, `FEAT-AGENT/injection-suite`,
`FEAT-APP/http-api-contracts`, `FEAT-INFRA/cloud-run-deploy`.

## 003 rag-evals

**Goal**: answer "does this expense report violate policy?" with cited clauses, and measure how good
the answers are, with CI failing on regression.

**Scope (outline)**
- Chunk and index the synthetic policy document: embeddings (local `fastembed` default, Voyage
  optional) in pgvector, plus BM25 keyword search, merged, then reranked by a small local reranker.
- Answer step through the gateway, citing clause ids; refuse when evidence is missing.
- Eval datasets in `/evals` (questions with expected clauses and verdicts): recall@k, faithfulness,
  LLM-judge score (run in CI only against recorded outputs), injection resistance of retrieved text.
- Stored baseline and thresholds; ablation table (vector only, BM25 only, hybrid, hybrid plus rerank)
  with real measured numbers.

**Decisions to research**: pgvector on Neon Free (verify first), embedding model and dimension, chunk
size, reranker model size versus cold start, judge prompt design and bias checks, dataset size (small
but varied).

**Success signals**: hybrid plus rerank beats the simpler variants on recall@k (measured), faithfulness
and judge score above stored thresholds, the CI gate fails on a deliberately degraded retriever.

**Risks**: small dataset gives noisy scores (state confidence honestly), judge model drift (pin and
record), storage growth on the free database.

**Branches (indicative)**: `FEAT-AGENT/policy-index`, `FEAT-AGENT/hybrid-retrieval`,
`FEAT-AGENT/rag-evals`, `FEAT-INFRA/eval-gate-ci`.

## 004 audit-viewer

**Goal**: a minimal read-only viewer for reviewers: trace list, trace detail, audit-log verification
status and eval results. Built last, after the API is stable. This is the only place React and
TypeScript are allowed (ADR-0001).

**Scope (outline)**
- `/web` with React + TypeScript + Vite; API client generated from the FastAPI OpenAPI spec; no
  business logic and no Node backend.
- Screens: trace list (paged), trace detail (spans, calls, cost, redactions, verification badge),
  eval results and baseline comparison.
- Loading, error and empty states; keyboard navigation; CORS limited to the viewer origin; viewer
  holds no secrets (read-only token with minimal scope).
- Deploy on Vercel Hobby (personal, non-commercial only).

**Decisions to research**: read-only token scheme for a browser, pagination shape, generated-client
tooling, accessibility basics for keyboard use, how much of the trace to show without leaking data.

**Success signals**: all four states present on every screen, full keyboard operation, generated
client compiles against the current OpenAPI spec, no secrets in the bundle (scan).

**Risks**: exposing audit data through a public URL (use auth, keep the deployment private to the
owner), API changes after the client is generated (CI regenerates and diffs).

**Branches (indicative)**: `FEAT-APP/viewer-shell`, `FEAT-APP/trace-views`, `FEAT-APP/eval-views`,
`FEAT-INFRA/vercel-deploy`.

## Later: human approval (optional)

A LangGraph step that pauses high-risk actions (for example flagging above a threshold) until a
person approves, with the decision written to the audit chain. Decide after 003 whether it earns its
complexity (architect skill rubric).

## Cross-cutting, every feature

- Constitution check, NFR table (criterion + task + test), analyze before code.
- Costs stay near $0; any recurring cost needs an ADR and approval.
- Only measured numbers are recorded in `docs/measurements.md`.
- One branch per change, emoji commit format, CI green before merge.
