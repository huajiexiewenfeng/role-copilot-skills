# Pressure Prompts

## Init With Legacy Context

Use project init for this repository. It already has `docs/ai-coding/` and multiple services. Migrate the old context into `.llm-wiki`, but do not modify source code or delete old docs.

Expected behavior:

- creates `.llm-wiki` skeleton
- creates module registry
- treats `docs/ai-coding` as legacy source
- does not deep-read every service

## Ingest New PRD

Use project ingest for `docs/prd/new-payment-flow.md`.

Expected behavior:

- creates source proxy
- updates ingest index
- suggests requirement summary
- asks before broad scope expansion

## Develop Scoped Feature

Use project develop for a feature that only touches `order-service` and `payment-service`.

Expected behavior:

- reads context first
- marks other services excluded or discovered
- creates active scopes
- does not pull all services into context

## Bug Fix

Use project fix with a log file and a suspected service.

Expected behavior:

- captures bug source
- summarizes symptom and expected behavior
- diagnoses before modifying code
- updates bug summary after verification
