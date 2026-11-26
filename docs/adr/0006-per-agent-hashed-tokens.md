# ADR-0006: Per-agent hashed tokens for identity

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
The allow-list is meaningless if callers can claim any identity.

## Decision
Random 256-bit token per agent; SHA-256 hash in `config/agents.yaml`; constant-time compare; token never logged. Fast hash is fine because tokens are random, not guessable passwords.

## Alternatives considered
Claimed name; one process per agent; full OAuth (revisit for deployed HTTP).

## Consequences and cost
$0, local, testable. Swapping to platform-issued tokens later only changes `authenticate()`.

## Revisit when
The HTTP gateway ships (002) or more than a handful of agents exist.
