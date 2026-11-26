---
description: "Task list for 001-mcp-tracing"
---

# Tasks: MCP Tools, Audit Log and Tracing

**Input**: `specs/001-mcp-tracing/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Written for a complete beginner.** Each task is one sitting (30–90 minutes) and uses this shape:
the checklist line (ID, `[P]` if it can run alongside others, story label, file path), then **Goal**,
**Concept** (what you will learn), **Test first**, **Done when**, and **If it goes wrong** where useful.
Terms are defined in [docs/glossary.md](../../docs/glossary.md). Constitution II applies: write the
failing test, see it fail, then implement.

**Legend**: `[P]` = safe to do in parallel with other `[P]` tasks in the same phase (different files).
`[US1..US4]` = user story from spec.md. citations to the data model are written `data-model.md Entity.field`.

**Order of ideas** (nothing uses a concept before it is taught): project setup → tests and CI →
database → fake model → MCP → permissions → audit chain → redaction → traces → evals → measurements.

---

## Phase 1: Setup

- [ ] T001 Create the Python project skeleton in `pyproject.toml`, `src/auditwake/__init__.py`, `uv.lock`
  - **Goal**: a project that installs with one command.
  - **Concept**: *uv* is a fast Python package and environment manager; a *lock file* pins exact versions so everyone gets identical installs (reproducible builds).
  - **Test first**: a test `tests/unit/test_import.py` that does `import auditwake` and checks `auditwake.__version__`.
  - **Done when**: `uv sync` then `uv run pytest` passes with 1 test.
  - **If it goes wrong**: "Python 3.12 not found" → `uv python install 3.12`.
- [ ] T002 [P] Add lint, format and type checks in `ruff.toml` (extend), `pyproject.toml`, `Makefile`
  - **Goal**: `make check` runs ruff, mypy and pytest.
  - **Concept**: a *linter* finds mistakes without running code; *type checking* (mypy) catches wrong data types early.
  - **Test first**: add a deliberately bad line, confirm `make check` fails, then remove it.
  - **Done when**: `make check` passes on the clean tree.
- [ ] T003 [P] Add local services in `compose.yaml` (Postgres and Jaeger)
  - **Goal**: `docker compose up -d` starts a database and a trace viewer.
  - **Concept**: *Docker Compose* starts several containers together; this keeps the project *local-first* (constitution XI).
  - **Test first**: a script `scripts/check_services.py` that connects to Postgres on the configured port and fails if it cannot.
  - **Done when**: the script prints OK and http://localhost:16686 shows the Jaeger page.
- [ ] T004 Set up pytest layers and a Postgres test fixture in `tests/conftest.py`, `tests/unit/`, `tests/integration/`, `tests/contract/`, `tests/e2e/`
  - **Goal**: integration tests get a throwaway real Postgres.
  - **Concept**: the *test pyramid*: many fast unit tests, fewer integration tests against real services, very few end-to-end tests. *testcontainers* starts a disposable database container for tests.
  - **Test first**: an integration test that opens a connection and runs `SELECT 1`.
  - **Done when**: `uv run pytest tests/integration` passes using only Docker.
- [ ] T005 Add CI in `.github/workflows/ci.yml` (lint, types, unit tests, pip-audit)
  - **Goal**: every push is checked on GitHub.
  - **Concept**: *CI (continuous integration)* runs your checks automatically; *pip-audit* reports known vulnerable dependencies.
  - **Test first**: push a branch with a failing test and see CI go red, then fix it. Also plant a fake secret on a scratch branch and confirm the local hook and CI both block it (SC-009); save the result in `docs/measurements.md`.
  - **Done when**: CI is green on `main`. (Integration and eval jobs are added in T037.)
- [ ] T006 [P] Add Dependabot in `.github/dependabot.yml`
  - **Goal**: automatic update pull requests for Python and GitHub Actions dependencies.
  - **Concept**: *dependency updates* matter because old libraries collect security holes.
  - **Done when**: the file validates (GitHub shows the Dependabot tab) and a weekly schedule is set.
- [ ] T007 [P] Add settings in `src/auditwake/config.py` and `.env.example`
  - **Goal**: all configuration comes from environment variables with safe defaults.
  - **Concept**: *environment configuration* keeps secrets out of code. `.env` is git-ignored; `.env.example` shows names only.
  - **Test first**: unit test that missing required settings raise a clear error and that secrets are never printed by `repr()`.
  - **Done when**: tests pass; `.env.example` has no real values (gitleaks hook passes).

---

## Phase 2: Foundational (blocks all stories)

- [ ] T008 Create synthetic data and loaders in `data/reports.json`, `data/policy.json`, `src/auditwake/storage/seed.py` (data-model.md ExpenseReport.report_id, data-model.md ExpenseReport.items, data-model.md PolicyClause.clause_id)
  - **Goal**: 10–20 fake expense reports (some with fake emails, phones, card numbers and names) and 5–8 policy clauses.
  - **Concept**: *synthetic data* is invented data that looks real, so we never risk real personal data (constitution X). Card numbers use known test numbers that pass the Luhn check.
  - **Test first**: unit test that every report validates against its schema and that fake-PII fixtures are listed in `tests/fixtures/fake_pii.json`.
  - **Done when**: tests pass; the fixture list is the source for SC-004 later.
- [ ] T009 Create the database schema and migrations in `src/auditwake/storage/migrations/0001_init.sql`, `src/auditwake/storage/db.py` (data-model.md runs.status, data-model.md audit_entries.seq, data-model.md audit_entries.entry_hash, data-model.md flags.report_id, data-model.md chain_checkpoints.through_seq)
  - **Goal**: tables for runs, audit entries, flags and checkpoints, plus a trigger that blocks UPDATE and DELETE on audit entries and a restricted app role.
  - **Concept**: a *migration* is a versioned change to the database structure. A *trigger* is code the database runs automatically; here it makes the log append-only. *Least privilege*: the app role can only INSERT and SELECT.
  - **Test first**: integration test that applies the migration, then asserts an UPDATE and a DELETE on `audit_entries` fail for the app role.
  - **Done when**: `uv run auditwake migrate` applies cleanly twice (idempotent) and the test passes.
- [ ] T010 [P] Create the model provider interface and fake in `src/auditwake/model_access/provider.py`, `src/auditwake/model_access/fake.py`
  - **Goal**: a `ModelProvider` interface with a scripted fake that returns planned tool calls deterministically.
  - **Concept**: an *interface* lets the same code use a fake model in tests and a real one later. A *deterministic* fake gives the same answer every time, so tests are repeatable and free (constitution III).
  - **Test first**: unit test that the same script gives the same outputs on repeated runs and makes no network calls (socket blocked).
  - **Done when**: tests pass.
- [ ] T011 [P] Define shared types in `src/auditwake/guardrails/errors.py`, `src/auditwake/telemetry/audit_types.py` (error codes from `contracts/mcp-tools.md`, `AuditSink` interface, in-memory sink)
  - **Goal**: error codes, outcome values and an `AuditSink` interface so the permission gate (US1) does not depend on Postgres (US2).
  - **Concept**: *dependency inversion*, meaning code depends on an interface, so each story can be built and tested alone.
  - **Test first**: unit test that every error code maps to a stable message and the in-memory sink returns entries in order.
  - **Done when**: tests pass.
- [ ] T012 Spike: confirm how the `mcp` 2.x SDK works in `docs/spikes/mcp-sdk.md`
  - **Goal**: a short note, with a tiny working example, showing how to (a) define a server with a tool, (b) call it from an in-memory client, (c) pass a token on each transport.
  - **Concept**: *MCP (Model Context Protocol)* is a standard for agents to find and call tools. A *spike* is a short experiment to remove a risk before building (Plan risk: SDK is on major version 2).
  - **Done when**: the note records exact package version and how to pass a token on in-memory and stdio transports. If per-call tokens are not possible, record the fallback (token read once at process start and re-verified for each call).
  - **If it goes wrong**: old tutorials use v1 names; trust the installed package's docs.

**Checkpoint**: setup, database, fake model and shared types ready.

---

## Phase 3: User Story 1 — Agent uses tools within its permissions (P1) 🎯 MVP

**Goal**: three tools, per-agent tokens, allow-list, validation, scripted demo agent.
**Independent test**: run the demo as `reader` and as `auditor`; reader is refused on flag; auditor succeeds.

- [ ] T013 [US1] Write failing unit tests in `tests/unit/test_auth.py`, `tests/unit/test_gate.py`, `tests/unit/test_schemas.py`
  - **Goal**: tests for token check, default deny, allow-list, unknown tool, invalid input, a tool that raises or times out, and error shape.
  - **Concept**: *test-first* means a test that fails for the right reason comes before the code.
  - **Done when**: tests exist and fail with "not implemented" (not syntax errors).
- [ ] T014 [P] [US1] Implement token creation, hashing and verification in `src/auditwake/guardrails/auth.py`, `config/agents.yaml` (data-model.md AgentProfile.name (unique), data-model.md AgentProfile.token_sha256, data-model.md AgentProfile.allowed_tools)
  - **Goal**: random tokens, unique agent names, SHA-256 hash stored, constant-time compare, agents loaded from YAML (unknown tool name fails startup).
  - **Concept**: a *hash* is a one-way fingerprint. Random 256-bit tokens can't be guessed, so a fast hash is enough (ADR-0006). *Constant-time compare* avoids leaking information through timing.
  - **Test first**: T013 tests for good token, bad token, missing token, tampered YAML.
  - **Done when**: auth tests pass; no raw token ever appears in YAML or logs.
- [ ] T015 [P] [US1] Implement tool input models in `src/auditwake/tools/schemas.py` (data-model.md ExpenseReport.report_id, data-model.md PolicyClause.clause_id, data-model.md flags.reason; unknown fields rejected; 10 KB limit)
  - **Goal**: Pydantic models for the three tools' inputs.
  - **Concept**: *validation* rejects bad input at the door, before any logic runs. *Pydantic* defines data shapes in Python and checks them.
  - **Test first**: T013 schema tests (bad id pattern, extra field, 501-char reason, oversized input).
  - **Done when**: schema tests pass.
- [ ] T016 [US1] Implement the gate in `src/auditwake/guardrails/gate.py`
  - **Goal**: one function every tool call passes: authenticate → allow-list → validate → run → record outcome through `AuditSink`. A tool that raises an error or times out gives `internal_error` with outcome `failed`. A test-only `bypass` option skips audit and tracing so T039 can measure overhead; it is never enabled in the CLI.
  - **Concept**: a *single choke point* means no tool can skip the safety checks. *Default deny*: anything not explicitly allowed is refused.
  - **Test first**: T013 gate tests including unknown agent, unknown tool, a tool that raises and a tool that times out.
  - **Done when**: gate tests pass using the in-memory sink.
- [ ] T017 [US1] Write failing integration test in `tests/integration/test_demo_agent.py` (reader vs auditor)
  - **Goal**: encode spec Story 1 acceptance scenarios 1–5 as a test against real Postgres.
  - **Concept**: an *acceptance test* checks behaviour the way a user sees it.
  - **Done when**: the test exists and fails.
- [ ] T018 [US1] Implement the three tools in `src/auditwake/tools/expense.py`, `src/auditwake/tools/policy.py`, `src/auditwake/tools/flag.py`, `src/auditwake/storage/flags.py` (data-model.md flags.flag_id, data-model.md flags.agent, data-model.md flags.run_id)
  - **Goal**: get report, get clause (from the JSON data) and flag (inserts a separate flag record; report never modified).
  - **Concept**: *immutability of source data*: the flag is a new record, so tests always start from the same data.
  - **Test first**: unit tests for not-found and for flagging twice creating two records.
  - **Done when**: tool unit tests pass.
- [ ] T019 [US1] Wire the MCP server in `src/auditwake/tools/server.py`
  - **Goal**: expose the three tools over MCP, each routed through the gate.
  - **Concept**: an *MCP server* publishes tools with names and input schemas that agents discover.
  - **Test first**: in-memory MCP client test that lists three tools and calls one.
  - **Done when**: client test passes.
- [ ] T020 [P] [US1] Add the contract snapshot test in `tests/contract/test_mcp_tools.py`, `tests/contract/snapshots/tools.json`
  - **Goal**: freeze tool names, descriptions and schemas; CI fails on unplanned change (FR-014).
  - **Concept**: a *contract test* protects what other programs depend on, so we notice breaking changes.
  - **Done when**: snapshot committed; editing a tool description makes the test fail.
- [ ] T021 [US1] Implement run status and the scripted demo agent in `src/auditwake/agent/runner.py`, `src/auditwake/agent/profiles.py`, `src/auditwake/agent/scripted.py` (data-model.md runs.run_id, data-model.md runs.status)
  - **Goal**: agent that follows a script, continues after a refusal, ends as completed, completed_with_denials or failed (FR-018). The run id is generated here in trace-id format (32 hex characters) so T033 can reuse it as the trace id.
  - **Concept**: an *agent loop* asks a model for the next action, runs a tool, feeds back the result. Ours uses the fake model.
  - **Test first**: T017 integration test.
  - **Done when**: T017 passes.
- [ ] T022 [US1] Add CLI commands `create-token`, `run-agent`, `migrate` in `src/auditwake/cli.py`
  - **Goal**: quickstart steps 3–5 work.
  - **Concept**: a *CLI* is how humans run the program; `create-token` prints the secret once and stores only the hash.
  - **Test first**: e2e test `tests/e2e/test_cli_demo.py` runs both profiles.
  - **Done when**: e2e test passes and `uv run auditwake run-agent --as reader` prints "completed with denials".

**Checkpoint**: US1 works alone (using the in-memory sink). MVP.

---

## Phase 4: User Story 2 — Tamper-evident audit log (P1)

**Goal**: every call recorded in one hash chain; edits detected; redaction before storage.
**Independent test**: run a mixed session, verify OK, edit one row, verify reports BROKEN.

- [ ] T023 [US2] Write failing tests in `tests/unit/test_audit_chain.py`, `tests/unit/test_redaction.py`, `tests/integration/test_audit_log.py`
  - **Goal**: tests for hashing, ordering under 20 parallel calls with no gaps, tamper detection (edit, delete, reorder), trigger blocking, redaction, fail-closed for both the flag tool and a read-only tool (result withheld).
  - **Concept**: *concurrency tests* run many operations at once to expose race conditions.
  - **Done when**: tests exist and fail.
- [ ] T024 [P] [US2] Implement redaction in `src/auditwake/guardrails/redaction.py`
  - **Goal**: replace emails, phone numbers, Luhn-valid card/bank numbers and fixed fake names with placeholders (FR-006).
  - **Concept**: *redaction* removes personal data before it is stored. *Luhn* is a checksum that tells card numbers from random digits (ADR-0007).
  - **Test first**: T023 redaction tests over `tests/fixtures/fake_pii.json`.
  - **Done when**: 0 raw fixture values survive in redacted output.
- [ ] T025 [P] [US2] Implement canonical JSON and hashing in `src/auditwake/telemetry/audit_chain.py`
  - **Goal**: `compute_hash(entry, prev_hash)` with sorted-key compact JSON and a fixed genesis hash.
  - **Concept**: *canonical form* guarantees identical data hashes identically, otherwise verification would fail randomly.
  - **Test first**: T023 hashing tests (same data = same hash; one changed byte = different hash).
  - **Done when**: tests pass.
- [ ] T026 [US2] Implement the Postgres audit sink in `src/auditwake/storage/audit_repo.py` (data-model.md audit_entries.prev_hash, data-model.md audit_entries.input_summary, data-model.md audit_entries.outcome)
  - **Goal**: append takes an advisory lock, reads the last hash, inserts the next entry.
  - **Concept**: an *advisory lock* makes concurrent writers take turns, so the chain has one order (ADR-0005).
  - **Test first**: T023 parallel-append test (20 calls, 20 entries, valid chain).
  - **Done when**: parallel test passes.
- [ ] T027 [US2] Make flag + audit write one transaction and fail closed in `src/auditwake/storage/flags.py`, `src/auditwake/guardrails/gate.py`
  - **Goal**: if the audit write fails, roll back the flag and return `audit_unavailable`.
  - **Concept**: a *transaction* makes several writes succeed or fail together. *Fail closed*: no record means no action.
  - **Test first**: T023 test that stops Postgres writes mid-call and checks nothing was stored and that a read-only tool's result is withheld.
  - **Done when**: test passes.
- [ ] T028 [US2] Implement chain verification and `verify-log` in `src/auditwake/telemetry/verify.py`, `src/auditwake/cli.py`
  - **Goal**: walk the chain; print `OK: N entries verified` or `BROKEN at seq=K: reason`; exit code 1 when broken.
  - **Concept**: *verification* recomputes hashes and compares links, so any past edit shows up.
  - **Test first**: T023 tamper tests (edit, delete, reorder) all produce BROKEN with the right `seq`.
  - **Done when**: tests pass; quickstart step 8 works.
- [ ] T029 [P] [US2] Implement the 90-day retention job with checkpoints in `src/auditwake/storage/retention.py`, `docs/retention.md` (data-model.md chain_checkpoints.entry_hash)
  - **Goal**: prune entries older than 90 days after saving a checkpoint hash; verification can start from the checkpoint (SC-007).
  - **Concept**: *retention* limits how long data is kept; the *checkpoint* keeps the remaining chain verifiable after pruning.
  - **Test first**: integration test with backdated entries; verification still OK after pruning.
  - **Done when**: test passes and `docs/retention.md` states the rule.
- [ ] T030 [US2] Swap the in-memory sink for the Postgres sink in the CLI and demo; rerun T017
  - **Goal**: the whole demo is audited.
  - **Done when**: T017 and T023 pass together; `uv run auditwake verify-log` prints OK after a demo.

**Checkpoint**: US1 + US2 work.

---

## Phase 5: User Story 3 — Every run visible as a trace (P2)

**Goal**: spans, JSON logs, one run id.
**Independent test**: run the demo, see one trace with a span per call in Jaeger; run id equals trace id.

- [ ] T031 [US3] Write failing tests in `tests/unit/test_tracing.py`, `tests/integration/test_tracing_failure.py`
  - **Goal**: using an in-memory span collector: one span per tool and model call, attributes (agent, tool, outcome, duration), denied marked `denied` not error, trace id equals run id, run completes when the backend is unreachable.
  - **Concept**: a *span* is one timed step; a *trace* is all spans of a run; *OTel* is the open standard for them.
  - **Done when**: tests exist and fail.
- [ ] T032 [US3] Set up OpenTelemetry in `src/auditwake/telemetry/tracing.py`
  - **Goal**: tracer with OTLP/HTTP export, bounded queue, short timeout, drops spans on failure (FR-010).
  - **Concept**: *OTLP* is the wire format for sending spans. A *bounded queue* stops memory growing if the backend is down.
  - **Test first**: T031 failure test pointing at a closed port.
  - **Done when**: the run still finishes and the audit chain is intact with the backend down.
- [ ] T033 [US3] Add spans to the gate and model calls; set run id = trace id in `src/auditwake/guardrails/gate.py`, `src/auditwake/agent/runner.py`
  - **Goal**: every call produces one span; the run id printed by the CLI equals the trace id.
  - **Test first**: T031 span tests, plus a cross-check that a run's spans and audit entries match one-to-one (SC-002).
  - **Done when**: tests pass; quickstart step 7 shows the trace in Jaeger.
- [ ] T034 [P] [US3] Add JSON logging with trace id in `src/auditwake/telemetry/logging.py`
  - **Goal**: structured log lines carrying the run id; redaction applied before output (FR-008, FR-006).
  - **Concept**: *structured logs* are JSON, so tools can search them.
  - **Test first**: unit test that a log line parses as JSON, contains the trace id and no fake-PII fixture values.
  - **Done when**: test passes.

**Checkpoint**: US1–US3 work.

---

## Phase 6: User Story 4 — Baseline eval (P2)

**Goal**: 12 cases, a runner, a stored baseline, a CI gate.
**Independent test**: eval passes on clean code; fails when the allow-list is broken on purpose.

- [ ] T035 [US4] Write the 12 eval cases in `evals/cases/*.yaml`
  - **Goal**: cases for allowed (2), denied (2), invalid input (2), unknown tool (1), bad token (1), redaction (1), tamper (2), run status (1). Security categories: denied, unknown tool, bad token, redaction, tamper.
  - **Concept**: an *eval case* is input plus an expected outcome, scored the same way every time. *Versioned data* means the set only changes through reviewed commits.
  - **Test first**: schema test that every case file has id, category, steps and expected result.
  - **Done when**: schema test passes (12 cases).
- [ ] T036 [US4] Implement the runner in `evals/run_evals.py`, `src/auditwake/cli.py` (`auditwake eval`)
  - **Goal**: runs each case with the fake model and real Postgres; prints per-case and per-category results; exits 1 below thresholds.
  - **Concept**: a *threshold* is the minimum score allowed; our rule is 90% overall and 100% for security categories (ADR-0010).
  - **Test first**: unit tests for scoring and threshold logic.
  - **Done when**: `uv run auditwake eval` runs all 12 cases in under 60 s.
- [ ] T037 [US4] Store the baseline and add the CI gate in `evals/baseline.json`, `.github/workflows/ci.yml`
  - **Goal**: baseline created from a real run; CI adds integration and eval jobs with a Postgres service container.
  - **Concept**: a *baseline* is the saved score future runs must match or beat. A *mutation check* proves the gate really catches regressions.
  - **Test first**: mutation check: weaken the allow-list in a scratch branch and confirm CI fails.
  - **Done when**: CI green normally, red on the mutated branch (record the run link in the PR).
- [ ] T038 [P] [US4] Add the fake-PII leak scan in `tests/integration/test_no_leaks.py`
  - **Goal**: after the eval set, search audit entries, log output and spans for every fixture value and every agent token; expect zero (SC-004). Also assert that for every run the number of spans equals the number of audit entries (SC-002).
  - **Done when**: test passes and fails if redaction is disabled.

**Checkpoint**: all four stories work.

---

## Phase 7: Polish and cross-cutting

- [ ] T039 [P] Measure auditing and tracing overhead in `scripts/bench_overhead.py`, `docs/measurements.md`
  - **Goal**: median per-call time with and without auditing and tracing (SC-006, target under 50 ms), using the test-only `bypass` option from T016 as the baseline.
  - **Concept**: *median* is the middle value, so one slow outlier doesn't distort it.
  - **Done when**: the real measured number, date and machine are written in `docs/measurements.md`. If it misses the target, record that and open a follow-up; never edit the number.
- [ ] T040 [P] Run a small load check in `scripts/load_check.py`, `docs/measurements.md`
  - **Goal**: 200 calls, 10 at a time; record real p50, p95 and throughput for owner + 5 users.
  - **Concept**: *p95* means 95% of calls were faster than this value.
  - **Done when**: results recorded as measured, with the limits stated honestly.
- [ ] T041 [P] Build the container image in `Dockerfile`, `.dockerignore`, `.github/workflows/ci.yml`
  - **Goal**: slim reproducible image built from the lock file; CI builds it; record the image size.
  - **Concept**: a *container image* packages the app so it runs the same everywhere; size drives Artifact Registry cost.
  - **Done when**: `docker build` works locally and in CI; size is written into `plan.md` (replaces the `[UNVERIFIED]` entry).
- [ ] T042 [P] Write the STRIDE-lite threat model in `docs/threat-model.md`
  - **Goal**: one page covering Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege for this feature, with the mitigation and the test that covers each.
  - **Concept**: *STRIDE* is a checklist of six threat types. Include the honest limit: a database owner can rewrite the chain.
  - **Done when**: every row links to a test or a stated, accepted risk.
- [ ] T043 [P] Add `auditwake health`, runbook and SLOs in `src/auditwake/cli.py`, `docs/runbook.md`
  - **Goal**: a health command (database reachable, chain verifies) and a one-page runbook with 2–3 SLIs and SLOs.
  - **Concept**: an *SLI* is a measured quality (for example, share of calls recorded); an *SLO* is the target for it.
  - **Test first**: unit test for health output when the database is down.
  - **Done when**: test passes; runbook covers "database down", "chain broken", "traces missing".
- [ ] T044 [P] Add Terraform for a budget alert in `infra/terraform/budget.tf`, `.github/workflows/ci.yml`
  - **Goal**: a GCP billing budget with alert thresholds, validated in CI (`terraform fmt` and `validate`, no apply).
  - **Concept**: *infrastructure as code* describes cloud resources in files. A *budget alert* only notifies; it does not stop spending (ADR-0009).
  - **Done when**: `terraform validate` passes in CI; nothing is applied.
- [ ] T045 [P] Write the README and rollback notes in `README.md`, `docs/rollback.md`
  - **Goal**: architecture diagram, one-command quickstart, and how to roll back (revert commit, re-run migrations down-safe, redeploy previous image).
  - **Done when**: a fresh clone follows the README to a passing quickstart.
- [ ] T046 Final check against the Definition of Done in `specs/001-mcp-tracing/checklists/requirements.md`, `docs/adr/`
  - **Goal**: run quickstart end to end; confirm tests, evals and traces; mark ADRs Accepted; confirm costs are $0.
  - **Done when**: all quickstart steps pass, `make check` is green, CI is green, ADR statuses updated, and you tick the quality checklist yourself.

---

## Branch and commit plan

Each phase is its own branch and pull request, named by the rule in `docs/branching.md`, with commits in
the fixed emoji format (for example `✨🤖 FEAT-AGENT: add allow-list gate`).

| Phase | Branch | Notes |
|---|---|---|
| 1 Setup | `FEAT-INFRA/project-setup` | tooling, compose, CI |
| 2 Foundational | `FEAT-APP/foundation` | schema, fake model, types, spike |
| 3 US1 | `FEAT-AGENT/permissioned-tools` | MVP |
| 4 US2 | `FEAT-APP/audit-log-chain` | |
| 5 US3 | `FEAT-APP/run-tracing` | |
| 6 US4 | `FEAT-AGENT/baseline-evals` | CI gate |
| 7 Polish | `FEAT-INFRA/container-budget-ci`, `DOC-APP/measurements-and-docs` | split by side |

## Dependencies and order

- Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7.
- US1 uses an in-memory audit sink, so it works alone; US2 replaces it with Postgres (T030).
- US3 depends on the gate (T016); US4 depends on US1–US3.
- Inside each story: tests first, then models/helpers, then wiring, then CLI.

**Parallel examples**
- Phase 1: T002, T003, T006, T007 together after T001.
- Phase 2: T010, T011 together after T009.
- US1: T014 and T015 together; T020 once T019 is done.
- US2: T024, T025, T029 together.
- Phase 7: T039 to T045 are mostly independent.

## NFR traceability (nothing without a task and a test)

| NFR | Task | Test or proof |
|---|---|---|
| 1 Testability | T004, T005, T010, T020, T035–T038 | pytest layers, contract snapshot, eval gate, `make check` |
| 2 Scalability (right-sized) | T009, T026, T040 (FR-024, SC-013) | parallel-append test, load check numbers |
| 3 Security | T005, T006, T014–T016, T024, T026, T038, T042 (FR-019 to FR-021, SC-009 to SC-011) | auth, gate, redaction, leak scan, secret-scan trial, pip-audit, threat model |
| 4 Observability | T031–T034, T043 (FR-022, SC-012) | span and log tests, health test, runbook |
| 5 Cost control | T044, T041 (FR-023, SC-014) | `terraform validate`, image size, $0 check in T046 |
| 6 Maintainability | T001, T002, T005, T006, T041, T045 (FR-020, FR-023, SC-010, SC-014) | ruff, mypy, CI, Dependabot, README, rollback rehearsal |
| 7 Data and privacy | T008, T029 | fixture tests, retention test, `docs/retention.md` |
| 8 Viewer UX | not in 001 | assigned to feature 004 |

## Implementation strategy

1. **MVP**: Phases 1–3 (T001–T022). Permissioned tools with a demo agent.
2. Add the audit chain (Phase 4), then traces (Phase 5), then evals (Phase 6).
3. Polish and measure (Phase 7); only then call 001 done.
4. Push after each checkpoint; CI and gitleaks must be green before the next phase.
