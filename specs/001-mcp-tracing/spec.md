# Feature Specification: MCP Tools, Audit Log and Tracing

**Feature Branch**: `001-mcp-tracing`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "MCP server with 2-3 tools, per-agent allow-list, audit log, OpenTelemetry spans, a thin agent run and a 10-15 case eval baseline. Demo domain: synthetic expense reports audited against a policy."

## Plain-Language Primer (for a new developer)

- **AI agent**: a program that asks an AI model what to do next and then uses *tools* (small
  functions) to do it. Example: "look up expense report #12", then "flag it as over the limit".
- **MCP (Model Context Protocol)**: a standard way for an agent to discover and call tools, like
  a USB port for AI. Auditwake's tools are offered through MCP.
- **Allow-list**: a per-agent list of tools it may call. Anything not on the list is refused.
  Example: a "reader" agent can look things up but cannot flag anything.
- **Audit log**: an append-only record of every tool call: who, what, when, result. Each entry is
  chained to the previous one by a fingerprint (hash), so editing history is detectable.
- **Trace / span**: a trace is the story of one agent run; a span is one step in it (one tool or
  model call) with timing and details. Reviewers read traces to see what the agent did.
- **Eval**: a fixed set of test cases that checks the agent behaves correctly, scored the same way
  every time. A *baseline* is the saved score we must not drop below.
- **Fake provider**: a stand-in for the AI model that gives scripted, repeatable answers, so tests
  need no API key and cost nothing.

## Clarifications

### Session 2026-11-26

- Q: How does the system tell which agent is calling a tool? → A: Each agent profile has its own
  secret token; the system finds the profile from the token. Tokens are stored only as hashes.
- Q: Should the audit log be one chain or one per run? → A: One global chain across all agents and
  runs.
- Q: Which kinds of personal data must be hidden before logging or tracing? → A: Names, email
  addresses, phone numbers and card or bank numbers.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent uses tools within its permissions (Priority: P1)

An operator runs a small demo agent that audits a synthetic expense report. The agent can only
call the tools its profile allows. Allowed calls work. Disallowed calls are refused with a clear
reason, and the refusal is recorded.

**Why this priority**: Least-privilege tool access is the core control Auditwake sells. Without it
nothing else is meaningful. It is also the smallest end-to-end slice.

**Independent Test**: Run the demo agent with two profiles (reader and auditor) against the same
synthetic report. Verify the reader can fetch the report but is refused when it tries to flag it,
while the auditor can do both.

**Acceptance Scenarios**:

1. **Given** an agent profile that allows report lookup, **When** the agent requests a known
   report, **Then** it receives that report's synthetic data.
2. **Given** an agent profile that does not allow flagging, **When** the agent tries to flag a
   report, **Then** the call is refused with a "not permitted" reason and no change is made.
3. **Given** a tool call with missing or malformed inputs, **When** the agent makes it, **Then** it
   is rejected with a clear validation message and no side effect occurs.
4. **Given** a tool name that does not exist, **When** the agent calls it, **Then** it is refused
   and recorded like any other denied call.

---

### User Story 2 - Every call is recorded in a tamper-evident audit log (Priority: P1)

A reviewer can see, for any agent run, an ordered record of every tool call: the agent, the tool,
a safe summary of inputs, the outcome (allowed, denied, failed), and when it happened. If someone
edits or deletes an old entry, a verification check reports it.

**Why this priority**: The audit log is the product's evidence. It is required for the allow-list
to be provable after the fact.

**Independent Test**: Run an agent session with a mix of allowed and denied calls, then read the
log and confirm each call appears once, in order. Edit one stored entry by hand and confirm the
verification check fails and names the broken entry.

**Acceptance Scenarios**:

1. **Given** a completed run with allowed and denied calls, **When** the log is read, **Then**
   every call appears exactly once in order with outcome and timestamp.
2. **Given** an untouched log, **When** verification runs, **Then** it reports the chain intact.
3. **Given** a log where one past entry was altered or removed, **When** verification runs, **Then**
   it reports the log as broken and identifies the first bad entry.
4. **Given** a tool call whose inputs contain personal data (fake, for testing), **When** it is
   logged, **Then** the stored record contains the redacted form, not the raw value.

---

### User Story 3 - Every run is visible as a trace (Priority: P2)

A reviewer can open a single agent run and see its steps as spans: each model call and each tool
call, with duration, outcome and the agent that made it, all linked by one run identifier that
also appears in the structured logs and the audit log.

**Why this priority**: Traces explain *why* and *how long*; the audit log proves *what*. Valuable
but the audit log and allow-list work without it.

**Independent Test**: Run the demo agent and confirm the trace backend (or local test collector)
shows one run containing a span per model call and tool call, and that the run identifier matches
the one in the audit log and log lines.

**Acceptance Scenarios**:

1. **Given** a finished agent run, **When** its trace is inspected, **Then** each tool call and each
   model call is one span with name, duration, agent and outcome.
2. **Given** a denied tool call, **When** its span is inspected, **Then** it is marked as denied
   with the reason, not as a crash.
3. **Given** a run, **When** comparing the trace ID in the trace, log lines and audit entries,
   **Then** they are the same.
4. **Given** the trace backend is unreachable, **When** the agent runs, **Then** the run and the
   audit log still complete normally.

---

### User Story 4 - A baseline eval catches regressions (Priority: P2)

A developer runs a small, versioned set of 10 to 15 eval cases against the demo agent and compares
the score to a stored baseline. If behaviour gets worse than the baseline, the run fails.

**Why this priority**: It proves the "test-first, evals gate the build" promise and gives later
features something to extend. Depends on stories 1 to 3.

**Independent Test**: Run the eval command with the fake provider and confirm it reports per-case
results and passes against the baseline; deliberately break the allow-list and confirm it fails.

**Acceptance Scenarios**:

1. **Given** the stored baseline, **When** the evals run with no code changes, **Then** they pass
   and report per-case results.
2. **Given** a change that lets a disallowed tool through, **When** the evals run, **Then** they
   fail and name the failing cases.
3. **Given** the evals run on a machine with no API keys, **When** they execute, **Then** they
   complete using the fake provider with no network use.

---

### Edge Cases

- Missing, invalid or unknown token, or an empty profile: every tool call is refused (default deny).
- A tool call times out or the tool raises an error: recorded as "failed", the agent gets a clear
  error, and the log chain stays valid.
- Two tool calls at nearly the same time: both are recorded one after the other in the single
  chain, in a consistent order, without breaking it.
- Very large or hostile input (oversized text, special characters): rejected or safely truncated
  in the log; never crashes the server.
- Audit log storage is unavailable: tool calls that need auditing are refused rather than running
  unrecorded (fail closed).
- Trace backend down: runs continue; spans are dropped, not queued without bound.
- Sensitive data appears in a tool result: it is redacted before being logged or traced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose exactly three demo tools over MCP: get an expense report by ID,
  look up a policy clause by ID, and flag an expense report with a reason.
- **FR-002**: Each agent MUST have a named profile listing the tools it may call and its own secret
  token. The agent identity MUST be derived from the presented token, never from a name the caller
  claims. A tool not on the profile MUST be refused; a missing, invalid or unknown token MUST be
  refused for all tools (default deny).
- **FR-016**: Agent tokens MUST be stored only as hashes, compared in a way that does not leak
  information through timing, and MUST never appear in logs, traces or audit entries; the audit
  entry records the verified agent name only.
- **FR-003**: System MUST validate every tool input against a defined shape and reject invalid
  input before any tool logic runs.
- **FR-004**: System MUST write one audit entry per tool call (allowed, denied or failed) containing
  agent, tool, redacted input summary, outcome, run identifier and timestamp.
- **FR-005**: Audit entries MUST be append-only and form a single chain across all agents and
  runs, so that altering, removing or reordering any past entry is detectable by a verification
  command that checks the whole chain.
- **FR-006**: System MUST redact personal data from inputs and results before they are written to
  the audit log, structured logs or traces. In scope: person names, email addresses, phone numbers
  and card or bank numbers. Tests use fake values only; names are matched against a fixed list of
  fake names, since arbitrary names cannot be detected reliably. Other kinds (street addresses,
  government IDs) are out of scope for 001.
- **FR-007**: System MUST emit one trace span per tool call and per model call, carrying agent,
  tool or model name, duration and outcome, all under a single run identifier.
- **FR-008**: Structured log lines MUST include the same run identifier as the trace and audit log.
- **FR-009**: System MUST include a thin demo agent that runs a scripted audit of a synthetic
  report using a deterministic fake model by default, so runs need no API key.
- **FR-010**: Failure of the trace backend MUST NOT stop a run or lose audit entries.
- **FR-011**: System MUST ship 10 to 15 versioned eval cases and a stored baseline, runnable with
  one command, that fails when results drop below the baseline thresholds.
- **FR-012**: Eval cases MUST cover: allowed calls, denied calls, invalid inputs, unknown tools,
  unknown agents, redaction, and chain-tamper detection.
- **FR-013**: The whole feature MUST run locally with one command and no cloud account.
- **FR-014**: Tool descriptions and the tool contract (names, inputs, outputs) MUST be covered by
  contract tests so unintended changes fail the build.
- **FR-015**: All demo data MUST be synthetic; test personal data MUST be fake.

### Key Entities

- **Agent Profile**: a named identity with the set of tools it may call, its purpose and the hash
  of its secret token (never the token itself).
- **Expense Report (synthetic)**: an ID, submitter alias, line items (category, amount, date,
  note) and status. Contains fake personal data for redaction tests.
- **Policy Clause (synthetic)**: an ID, title and text of a rule in the demo expense policy.
- **Tool Call Record**: one attempted tool call: agent, tool, redacted input summary, outcome,
  duration, run identifier.
- **Audit Entry**: a tool call record plus the fingerprint of the previous entry in the single
  global chain.
- **Run**: one execution of the demo agent, identified by a run ID shared by logs, trace and audit.
- **Eval Case / Baseline**: a scripted scenario with expected outcome, and the saved scores that
  future runs must meet or beat.

## Non-Goals

- No model gateway, provider routing, caching or spend caps (feature 002).
- No policy search or retrieval over documents (feature 003); the policy lookup tool is by exact ID.
- No prompt-injection test suite beyond basic input validation (feature 002).
- No human-approval step for high-risk actions (later).
- No web viewer (feature 004).
- No multi-tenant users, login, or scaling work beyond one owner and at most 5 users.
- No claim of regulatory compliance; the output is audit evidence only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the eval set, 100% of calls outside an agent's allow-list are refused and none
  produce a side effect.
- **SC-002**: 100% of tool calls in a run (allowed, denied and failed) have exactly one audit entry
  and one trace span with matching run identifier.
- **SC-003**: Altering or deleting any single past audit entry is detected by verification in 100%
  of eval tamper cases.
- **SC-004**: 0 raw values of the fake personal-data fixtures or of agent tokens appear in any
  audit entry, log line or span across the eval set.
- **SC-005**: The full eval set meets or exceeds its stored baseline: at least
  90% of all cases passing and 100% of security cases (allow-list, redaction, tamper detection)
  passing, and completes in under 60 seconds on a laptop with no network.
- **SC-006**: Auditing and tracing add a median delay of under
  50 milliseconds per tool call, measured locally, compared with running the same call without them. The figure recorded in the docs MUST be the
  measured one.
- **SC-007**: Audit entries are kept for
  90 days (synthetic demo data) and the retention rule is documented.
- **SC-008**: A new developer can run the demo agent, the evals and the log verification from the
  README using one documented command each, with no cloud account or API key.

## Assumptions

- Single owner plus at most 5 users; one local process is enough.
- The demo agent's behaviour is scripted through the fake model; real model calls arrive in 002.
- A local, free trace viewer is used during development; the hosted choice is made in the plan.
- Synthetic data volume is tiny (tens of reports, a handful of policy clauses).
- Constitution principles apply: Python-first, test-first, keyless CI, local-first, honest metrics.
