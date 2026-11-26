# ADR-0011: Two Python projects under `src/` (backend, agents)

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
The owner wants a folder layout like the AuditSphere reference project: `src/backend`,
`src/agents`, `src/frontend`, with `infra/` and `pipelines/` at the root. ADR-0002 said "one
package"; this refines that. Feature 001 has no HTTP API, so the agent's tools write to the audit
log directly in the same process.

## Decision
- `src/backend/` and `src/agents/` are separate uv projects (own `pyproject.toml`, `uv.lock`, tests).
- Import names are distinct: `auditwake_backend` and `auditwake_agents`. Two projects that both use
  one package name fail to import each other (tested), so a shared name is not allowed.
- `agents` depends on `backend` as a local path dependency. `backend` never imports `agents`.
  If a task needs the reverse, move that code into `backend`.
- Integration, contract and end-to-end tests live in root `tests/`; unit tests live in each project.
- `infra/` holds compose, Dockerfile and Terraform; `pipelines/` holds helper scripts.
  `.github/workflows/` stays where GitHub requires it.

## Alternatives considered
One project with sub-folders (simplest, but not the requested layout); HTTP between the two projects
now (matches the reference, but pulls feature 002 work into 001).

## Consequences and cost
Clear boundaries and the requested layout. Cost: two lock files and two test runs; the one-way
import rule is kept by discipline until a check enforces it.

## Revisit when
Feature 002 adds the HTTP API: `agents` may then call `backend` over HTTP like the reference project.
