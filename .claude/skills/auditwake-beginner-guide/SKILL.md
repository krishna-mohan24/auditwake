---
name: "auditwake-beginner-guide"
description: "Use when writing or reviewing any spec, plan, checklist, task list, backlog item, README or doc for Auditwake. Ensures a complete beginner can follow it and learns each technical concept."
user-invocable: true
disable-model-invocation: false
---

# Auditwake beginner-friendly planning guide

The person building Auditwake is a **complete beginner** to most of this stack (MCP, OpenTelemetry,
evals, guardrails, pgvector, Terraform). Everything you write must teach as well as instruct.
Constitution Principle XII makes this mandatory.

## Writing rules

- Plain language first, jargon second. Define a term at first use in one sentence, then add it to
  `docs/glossary.md`.
- Explain the *why* in terms of Auditwake ("we hash-chain the log so edits are detectable"), not
  generic theory.
- Use a tiny concrete example or analogy for every new concept.
- Never assume a prior task's concept is known unless that task is listed as a prerequisite.
- Order the backlog so concepts build up: run locally, then tests, then fake provider, then MCP tool,
  then audit log, then tracing, then eval, then CI, and so on. Nothing uses a concept before it is taught.
- Exact commands, exact file paths, expected output. No "set up X appropriately".
- Prefer small tasks (about 30 to 90 minutes). If a task needs more, split it.
- Verified facts only; mark unverified numbers `[UNVERIFIED]`.

## Task format (use for every item in `tasks.md`)

```
### T0xx [P?] Short action title            (mark [P] only if parallelizable)
**Goal:** one sentence in plain language.
**Concept you'll learn:** name, then 2-4 sentences: what it is, why Auditwake needs it, a tiny example.
**Prerequisites:** task IDs and tools required.
**Steps:** numbered, with exact commands and file paths.
**Test first:** the failing test or check to write before the code (what it asserts, why).
**Done when:** observable result (command output, passing test, trace visible in the UI).
**If it goes wrong:** the 1 to 3 most likely errors and fixes.
**Learn more:** an official doc link or a glossary entry.
```

## Concept checklist (each needs a teaching task or glossary entry before first use)

MCP and tools, allow-list, Pydantic validation, async I/O, provider interface and fake provider,
record/replay, OpenTelemetry spans and trace IDs, structured logs, hash-chained audit log,
Postgres and migrations, embeddings, BM25, hybrid search and reranking, evals (recall@k,
faithfulness, judge score, injection block rate), baselines and thresholds, prompt injection,
PII redaction, CI gates, Docker and compose, Terraform, secrets, SLI/SLO, ADRs.

## Review checklist before approving a plan or backlog

- [ ] Could someone who has never seen this stack complete each task from the text alone?
- [ ] Does every new concept have a plain-language explanation and an example?
- [ ] Is there any forward reference to a concept taught later?
- [ ] Does each task have a test-first step and a "done when" that can be checked?
- [ ] Are terms defined in the glossary?

## Asking the owner questions (clarify, specify, plan, any decision)

Questions must be quick to read and easy to review. Use this format every time:

- **One question at a time**, one line, plain words, ending in `?`.
- **Why it matters**: one short sentence, no jargon (or define the term inline).
- **Options**: 2 to 4 rows, each at most about 12 words, in a table. Say what happens, not theory.
- **Recommended**: one option letter plus one short reason (a single line).
- **How to reply**: end with "Reply with a letter, or 'yes' for the recommendation."
- No long paragraphs, no stacked sub-questions, no background lecture. If a concept is needed,
  explain it in one sentence and add it to `docs/glossary.md`.
- After the answer, state in one line what changed in the spec, then ask the next question.
