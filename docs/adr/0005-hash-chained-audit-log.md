# ADR-0005: Single global hash-chained, append-only audit log

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Spec FR-005: edits, deletions or reordering of past entries must be detectable.

## Decision
`entry_hash = SHA-256(canonical JSON incl. prev_hash)`. One global chain. Appends under a Postgres advisory lock. UPDATE/DELETE blocked by trigger and a restricted role. `verify-log` walks the chain. Checkpoints support 90-day pruning.

## Alternatives considered
Per-run chains (cannot show a missing run); signed logs (key management overhead).

## Consequences and cost
Detects tampering by anyone who does not rewrite the whole chain. Does not stop a full database owner; external checkpoints are a later improvement. Documented honestly.

## Revisit when
Appends become a bottleneck (measured), or external anchoring is needed.
