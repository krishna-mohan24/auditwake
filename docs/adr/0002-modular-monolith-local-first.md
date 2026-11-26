# ADR-0002: Modular monolith, local-first

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
One owner plus at most 5 users, near-zero budget, beginner builder.

## Decision
One process (code layout refined by ADR-0011), run locally with docker compose + uv. Cloud is an optional layer.

## Alternatives considered
Microservices; cloud-only development.

## Consequences and cost
Fewer moving parts, easy to learn, free to run. Cost: modules must be kept clean by discipline, not by network boundaries.

## Revisit when
A measured need for independent scaling or deployment appears.
