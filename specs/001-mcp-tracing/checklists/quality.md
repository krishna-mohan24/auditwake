# Requirements Quality Checklist: 001 MCP Tools, Audit Log and Tracing

**Purpose**: "Unit tests for the requirements": are spec.md, plan.md and the contracts complete, clear, consistent and measurable enough to build from?
**Created**: 2026-11-26
**Focus**: security and audit evidence, observability, testability/evals, cost and maintainability (defaults chosen: formal pre-implementation gate, owner as reviewer)
**Note**: Items are unchecked on purpose. The reviewer (you) ticks an item when the requirement text satisfies it. A tick does not mean code is done.

## Requirement Completeness

- [ ] CHK001 Are requirements defined for how an agent's token is issued, rotated and revoked, not only verified? [Gap, Spec §FR-002, FR-016]
- [ ] CHK002 Are requirements stated for what the agent receives when the audit log is unavailable (message, code, retry guidance)? [Completeness, Spec §Edge Cases, Contract §Common behaviour]
- [ ] CHK003 Is the content of `input_summary` specified per tool (which fields are kept, which are redacted)? [Gap, Contract §Entry]
- [ ] CHK004 Are requirements defined for tool results being redacted in logs and traces, separate from inputs? [Completeness, Spec §FR-006]
- [ ] CHK005 Is the retention job's behaviour specified (schedule, what is pruned, how the chain stays verifiable)? [Gap, Spec §SC-007, Data Model §chain_checkpoints]
- [ ] CHK006 Are requirements defined for starting the demo agent with a real model later without changing tool contracts? [Gap, Plan §model_access]

## Requirement Clarity

- [ ] CHK007 Is "safe summary of inputs" (Spec §User Story 2) defined with concrete rules rather than a phrase? [Ambiguity]
- [ ] CHK008 Is "completes in under 60 seconds on a laptop" tied to a reference machine or stated as a CI limit? [Ambiguity, Spec §SC-005]
- [ ] CHK009 Is the overhead baseline for "without auditing and tracing" defined precisely (what is bypassed)? [Clarity, Spec §SC-006]
- [ ] CHK010 Is the meaning of outcome `failed` versus `denied` unambiguous for invalid input and unknown tools? [Clarity, Spec §FR-004, Contract §Common behaviour]
- [ ] CHK011 Is "chain intact" defined for gaps, reordering and duplicated entries? [Clarity, Spec §FR-005, Contract §Verification]

## Requirement Consistency

- [ ] CHK012 Do invalid-input requirements agree between spec (rejected, no side effect) and the contract (outcome `failed`)? [Consistency, Spec §Story 1 AS3, Contract §Common behaviour]
- [ ] CHK013 Do the run statuses in FR-018 match the run states in the data model? [Consistency, Spec §FR-018, Data Model §runs]
- [ ] CHK014 Are redaction scope statements consistent between FR-006, ADR-0007 and the eval categories? [Consistency]
- [ ] CHK015 Does "fail closed" apply consistently to read-only tools and the flag tool? [Consistency, Plan §Key Design Decisions 4]
- [ ] CHK016 Are retention of 90 days (SC-007) and trace retention of the optional hosted backend reconciled? [Conflict, Plan §Deployment]

## Acceptance Criteria Quality

- [ ] CHK017 Can SC-002 ("exactly one audit entry and one span per call") be checked objectively, including for denied calls? [Measurability, Spec §SC-002]
- [ ] CHK018 Is "0 raw values of fake PII fixtures" backed by a defined list of fixtures to search for? [Measurability, Spec §SC-004]
- [ ] CHK019 Are thresholds for the 12 eval cases split into named categories so "security cases" is unambiguous? [Clarity, Spec §SC-005, ADR-0010]
- [ ] CHK020 Is there an acceptance criterion for the quickstart working on a clean machine? [Coverage, Spec §SC-008]

## Scenario and Edge-Case Coverage

- [ ] CHK021 Are recovery requirements defined after a partial failure (tool ran, audit write failed)? [Coverage, Exception Flow, Plan §Key Design Decisions 4]
- [ ] CHK022 Are concurrent-call ordering guarantees quantified (for example, N parallel calls produce N entries with no gaps)? [Measurability, Spec §Edge Cases]
- [ ] CHK023 Are requirements specified for clock skew or identical timestamps in the chain? [Gap, Edge Case]
- [ ] CHK024 Are requirements defined for very large tool results, not only large inputs? [Gap, Data Model §Validation rules]
- [ ] CHK025 Is behaviour specified when `config/agents.yaml` is missing, malformed or lists an unknown tool? [Gap, Data Model §AgentProfile]

## Non-Functional Requirements

- [ ] CHK026 Are security requirements specified for protecting the owner database role versus the app role? [Gap, Plan §Key Design Decisions 3]
- [ ] CHK027 Are logging requirements specified for what must never be logged beyond tokens and PII (for example, full tool results)? [Completeness, Spec §FR-006, FR-016]
- [ ] CHK028 Are observability requirements specified for health and readiness signals and the SLIs/SLOs chosen? [Gap, Plan §NFR coverage map]
- [ ] CHK029 Is a cost requirement stated that makes real-model spend impossible in 001 (not only unlikely)? [Gap, Constitution VII]
- [ ] CHK030 Are accessibility, keyboard and UX requirements explicitly out of scope for 001 and assigned to 004? [Assumption, Spec §Non-Goals]
- [ ] CHK031 Are maintainability requirements (lint, types, pre-commit, CI jobs) each traceable to a task and a pass/fail condition? [Traceability, Plan §NFR coverage map]

## Dependencies and Assumptions

- [ ] CHK032 Is the assumption that the `mcp` 2.x SDK supports per-call credentials validated, with a fallback if not? [Assumption, Plan §Risks]
- [ ] CHK033 Is the dependency on Docker for Postgres and Jaeger documented as a prerequisite and as a CI service? [Dependency, Quickstart §Prerequisites]
- [ ] CHK034 Is the assumption that pgvector is available on the chosen free host recorded with a verification date or task? [Assumption, Plan §Deployment]

## Ambiguities and Traceability

- [ ] CHK035 Does every FR and SC map to at least one task and one test (ID scheme exists and is used)? [Traceability]
- [ ] CHK036 Are the limits of the hash chain (database owner can rewrite everything) stated wherever tamper evidence is claimed? [Ambiguity, Contract §Guarantees and limits]
