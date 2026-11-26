# ADR-0007: Rule-based redaction (regex, Luhn, fixed fake names)

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
PII must be removed before logging or tracing (FR-006). Data is synthetic.

## Decision
Regex for emails and phones, Luhn check for card/bank numbers, fixed list of fake names. Placeholders such as `[EMAIL]`.

## Alternatives considered
Presidio or ML NER (heavier install, slower, more to learn).

## Consequences and cost
Fast, deterministic, easy to test. Cannot find arbitrary real names; acceptable only because data is synthetic.

## Revisit when
Real or user-provided data ever enters the system.
