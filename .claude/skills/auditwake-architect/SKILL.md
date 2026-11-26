---
name: "auditwake-architect"
description: "Use before any architecture, tech-stack, hosting, vendor, dependency or cost decision in Auditwake, and when writing plan.md, ADRs or Terraform. Applies the project's budget-first, impact-aware decision rubric."
user-invocable: true
disable-model-invocation: false
---

# Auditwake Architect: budget- and impact-aware decisions

Act as a pragmatic architect for a **solo-owner portfolio project** (owner + at most 5 users,
near $0/month, runs fully local). The constitution (`.specify/memory/constitution.md`) wins on
any conflict. This skill explains *how to choose*; it does not override it.

## 1. Decision rubric (apply in order, stop at the first decisive answer)

1. **Constitution fit.** Violates a principle? Reject, or propose an amendment. Never work around it.
2. **Cost.** Recurring cost > $0? Needs an ADR and the owner's explicit approval. Prefer: free tier
   with a hard cap > usage-based with a spend cap > fixed monthly fee (avoid).
3. **Local-first.** Must run with `docker compose` + uv, fake provider, no account or key.
   If a choice breaks that, it is optional and must sit behind an interface.
4. **Reversibility.** Prefer choices that are cheap to swap (interface, OTLP, plain SQL, Docker).
   Lock-in is acceptable only when the switch cost is small and written in the ADR.
5. **Blast radius / impact.** Who is hurt if it fails or surprises us (bill, leaked data, broken
   CI, lost audit log)? Weigh impact over elegance. Protect the audit log and spend caps first.
6. **Simplicity.** The fewest moving parts that meet the requirement. No new service, queue,
   cache server or framework unless a measured need exists.
7. **Learnability.** The builder is a beginner. Prefer the option that is easier to understand and
   explain (fewer concepts, good docs, clear errors). If a concept is new, it needs a backlog task
   that teaches it (see `auditwake-beginner-guide`).
8. **Portfolio value.** Between equals, pick the option that demonstrates the target skills
   (evals, observability, MCP/agents, guardrails, vector search).

## 2. Hard guardrails

- Never choose anything with a recurring fee, a paid scanner/WAF/pen-test, or autoscaling
  headroom "just in case".
- Never state prices, free-tier limits, quotas or model names from memory. **Verify against the
  provider's current docs at decision time**, cite the date checked in the ADR, and mark unverified
  figures `[UNVERIFIED]`.
- Never record an invented metric. Estimates must be labelled `ESTIMATE`.
- Never claim compliance; Auditwake produces audit evidence.
- Synthetic or public data only.

## 3. Standing decisions (revisit only via ADR)

| Area | Decision | Why |
|---|---|---|
| Stack | Python 3.12, uv, FastAPI, Pydantic, httpx, psycopg 3 async, Alembic | Python-first; thin DB layer fits the size |
| Exemption | React + TS in `/web` only, read-only | Owner skill; viewer has no logic (ADR) |
| Tracing | OpenTelemetry only, OTLP export, backend-neutral | Standard; swappable backend |
| LLM | Anthropic Sonnet via **API key** (a claude.ai subscription gives no API access) | Owner choice |
| 2nd provider | Claude Haiku (fallback), behind the provider interface; same Anthropic billing account (owner confirmed) | Required fallback, simplest and cheap |
| CI/tests | Deterministic fake provider, record/replay, no keys, no cost | Constitution III |
| Embeddings | Local `fastembed` default; Voyage AI optional provider | $0, offline, deterministic |
| Reranker | Small local cross-encoder; Voyage rerank optional; evals decide any upgrade | $0 |
| Keyword search | `rank_bm25` in memory (corpus is tiny); hybrid with vectors, then rerank | Simplicity |
| Judge | LLM-judge runs in CI only against recorded outputs | Keyless CI |
| Scale | Owner + ≤ 5 users. Do not design for more | Cost and simplicity |

## 4. Hosting policy: split compute and database to control cost

Default topology: **compute and database are separate, replaceable pieces.**

- **Database (default): Neon Postgres + pgvector**, not Cloud SQL (Cloud SQL has a recurring
  floor). Keep the connection string in `DATABASE_URL` only. No Neon-specific features in app code,
  so any Postgres with pgvector can replace it. Local dev uses a docker Postgres.
- **Backend compute: GCP Cloud Run**, min instances 0, a low max-instances cap, low concurrency
  cap, Terraform, Secret Manager, Artifact Registry. Accept cold starts.
- **Viewer: Vercel Hobby** (non-commercial use only).
- **Traces:** local Jaeger/Grafana in docker for dev; for the deployed demo choose a free hosted
  OTLP backend or ship traces to the audit DB. Decide by ADR after checking limits.

### Cost tripwires (act, don't just note)

| Signal | Action |
|---|---|
| GCP budget alert fires, or forecast > $0 beyond owner's agreed ceiling | Pause deploys, inspect cost drivers, apply the escalation ladder below |
| Neon free limits (storage/compute hours/branches) near exhausted `[UNVERIFIED: check current]` | Prune old traces per retention policy, reduce embedding dimensions, then consider another free Postgres |
| LLM per-key or global spend cap reached | Fail closed with a clear error; never raise the cap silently |
| Cold starts or timeouts hurt the owner's use | Prefer a longer client timeout over `min-instances > 0` |

### Escalation ladder if GCP cost exceeds budget (cheapest reversible step first)

1. Tighten Cloud Run caps (max instances, CPU only during requests, smaller memory).
2. Cut logging/trace volume and retention; sample non-error traces.
3. Move the backend to another free or cheap container host (the Docker image is the portable
   unit); keep Neon and Secret handling unchanged. Record the move in an ADR.
4. Run the backend locally and expose it only when demoing; keep the viewer static.

Terraform and CI must not hard-code GCP-only assumptions beyond the deploy layer.

## 5. How to use this skill

- Before proposing a choice, list 2 to 3 options with: monthly cost (verified or marked), lock-in
  and swap cost, failure impact, and local-first impact.
- Recommend one, say why in 1 to 3 lines, and name the tripwire that would change the decision.
- Write the choice as an ADR in `docs/adr/NNNN-title.md` (context, options, decision, cost,
  consequences, revisit trigger). Touching a standing decision above requires an ADR and an update
  to this file.
- If a choice would add recurring cost or break a constitution principle, stop and ask the owner.
