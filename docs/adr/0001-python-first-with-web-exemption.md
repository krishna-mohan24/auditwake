# ADR-0001: Python-first, with React only in /web

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Constitution I requires Python for backend, evals, tracing, guardrails and infra. The owner already knows JS/TS and wants a read-only audit viewer.

## Decision
Python 3.12 + uv everywhere. React + TypeScript is allowed ONLY in `/web` as a read-only thin client using a client generated from the FastAPI OpenAPI spec. No Node backend logic. Built last (feature 004).

## Alternatives considered
Python only (no viewer, or server-rendered Python UI); React with a Node backend.

## Consequences and cost
$0. One documented exemption keeps the backend learning focused while the viewer uses a known skill.

## Revisit when
Any new language or Node server code appears.
