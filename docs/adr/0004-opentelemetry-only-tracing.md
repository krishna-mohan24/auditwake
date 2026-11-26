# ADR-0004: OpenTelemetry-only tracing, backend-neutral

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Constitution VI requires a span on every call. Owner chose OTel over a specific vendor.

## Decision
OTel SDK + OTLP/HTTP exporter. Local default: Jaeger container. Optional hosted backend later (Grafana Cloud free, 14-day retention per docs, sources conflict `[UNVERIFIED]`). Backend swap = change an endpoint variable.

## Alternatives considered
Langfuse (dropped), Honeycomb free (not evaluated), console only (no UI).

## Consequences and cost
$0. Spans are never allowed to block a run: bounded queue, short timeout, drop on failure.

## Revisit when
A hosted backend is wanted for the deployed demo, or free limits change.
