# ADR-0003: Postgres for the audit log (and later pgvector)

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Need a single ordered, concurrency-safe chain, real-database integration tests, and pgvector in feature 003.

## Decision
Postgres: local container for dev and tests; Neon free plan when hosted. Connection string only through `DATABASE_URL`; no Neon-specific features. Cloud SQL rejected (recurring cost floor).

## Alternatives considered
SQLite (simpler, but later migration, no pgvector); flat files (hard to make safe).

## Consequences and cost
$0 on Neon Free (1 GB, 100 CU-hours, no overage billing; checked 2026-11-26). pgvector on Neon Free `[UNVERIFIED]`.

## Revisit when
Storage near 1 GB, pgvector unavailable, or free terms change.
