# Acceptance Cases

Use these cases before claiming the MVP is complete. They are pressure scenarios for checking whether the six project skills work as a real team workflow.

## Case 1: Existing Project With Legacy Context

Prompt:

```text
Use project init for this repository. It has docs/ai-coding, multiple services, and may already have .codegraph. Migrate useful context into .llm-wiki without modifying production code.
```

Expected:

- creates or refreshes `.llm-wiki`
- preserves existing useful wiki content
- records modules with `active`, `reference-only`, `discovered`, or `unknown`
- records `.codegraph` as read-only supporting context when present
- does not delete or grow legacy `docs/ai-coding`

## Case 2: Many Docs, One Active Requirement

Prompt:

```text
I copied many PRDs into docs/prd, but today I only want to develop the payment callback requirement.
```

Expected:

- reports unindexed or changed docs
- activates only the relevant source
- marks other docs as candidate, discovered, or excluded
- creates or updates one requirement page
- avoids loading every PRD deeply

## Case 3: Temporary Source Ingest

Prompt:

```text
Use project ingest for this PDF/log/URL. It may contain sensitive production details.
```

Expected:

- asks before deep reading binary, remote, large, or sensitive material
- path-indexes or cautious-summarizes as appropriate
- creates ingest index row and source proxy
- does not copy secrets or long raw content

## Case 4: Cross-Service Feature

Prompt:

```text
Use project develop for this feature. It should touch order-service and payment-service only. notification-service is reference-only unless evidence requires otherwise.
```

Expected:

- runs Context Enrichment Gate
- outputs Context Handoff
- creates requirement page
- creates working-context page
- records active/read-only/excluded scopes
- asks before expanding scope

## Case 5: Bug With Scope Escalation

Prompt:

```text
Use project fix for this failed callback log. Start with payment-service. If order-service is needed, explain why before editing it.
```

Expected:

- captures bug source
- reproduces or explains why not
- bridges systematic-debugging after scoped evidence
- records scope escalation before editing a new service
- updates bug summary and working-context after verification

## Case 6: Finish After Partial Verification

Prompt:

```text
Use project finish. Tests could not run locally, but compile passed and manual verification was done.
```

Expected:

- records explicit verification limitation
- does not claim full completion
- updates only affected wiki pages
- marks working-context status correctly
- reports residual risk

## Case 7: Review Finds Drift

Prompt:

```text
Use project review before commit.
```

Expected:

- findings first
- checks code risk and verification gaps
- detects changed active scopes that are not in working-context
- detects missing requirement, bug, module, or source proxy updates
- checks tool-bridge consistency
