# ADR-0009: Hosting split: Cloud Run + Neon + Vercel Hobby

**Status**: Proposed (awaiting owner approval) | **Date**: 2026-11-26 | **Feature**: 001

## Context
Near-$0 budget; GCP chosen for compute; owner wants a fallback if GCP costs more.

## Decision
Compute on Cloud Run (min instances 0, low max-instances, from 002). Database on Neon. Viewer on Vercel Hobby (personal, non-commercial). 001 is local only and not deployed. Budget alert via Terraform (alerts only, does not cap).

## Alternatives considered
Cloud SQL (recurring floor); everything on one free host.

## Consequences and cost
Estimated $0 at 5 users `ESTIMATE`. Escalation ladder in the architect skill if costs appear.

## Revisit when
A budget alert fires or a free-tier term changes.
