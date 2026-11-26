# ADR-0008: Deterministic fake model provider behind an interface

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Constitution III: CI must run with no keys and no cost.

## Decision
All model calls go through a provider interface. 001 ships only the scripted fake; real Sonnet and Haiku adapters, record/replay arrive in 002.

## Alternatives considered
Mocking HTTP calls ad hoc; calling real models in CI.

## Consequences and cost
$0 CI, repeatable evals. Risk: fake behaviour diverging from real models; mitigated later by recorded real responses.

## Revisit when
Real-provider behaviour differs from the fake in ways evals miss.
