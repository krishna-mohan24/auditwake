# ADR-0010: Eval gate with a stored baseline

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Constitution IV: CI fails on regression.

## Decision
12 versioned YAML cases, deterministic runner, `evals/baseline.json`. Pass thresholds: 90% overall and 100% of security categories. Runs in CI against a Postgres service container in under 60 s.

## Alternatives considered
Manual review only; looser thresholds.

## Consequences and cost
Security regressions cannot merge. Thresholds change only by a reviewed commit that says why.

## Revisit when
Cases grow past the time budget or real models make 100% security cases flaky.
