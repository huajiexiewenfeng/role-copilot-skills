# Capability Gap Audit

Use this audit after `north-star.md` when deciding what to implement next. It translates the North Star into concrete MVP gaps across the six project skills.

## Summary

The current collection is installable and directionally aligned. The main remaining work is to turn each skill from a compact workflow description into a reliable operating guide with clear gates, required outputs, and drift checks.

## MVP Status

| Done Means item | Status | Notes |
|---|---|---|
| all six project skills are installable and discoverable | Met | `npx skills add . --list` discovers all six project skills. |
| project init creates a usable `.llm-wiki` | Partial | Skeleton and migration rules exist, but module discovery, codegraph handling, and refresh behavior need sharper output requirements. |
| project ingest captures source material safely | Partial | Source types, safety, and proxy requirements exist, but confirmation prompts and stale-source handling need more concrete steps. |
| project develop and project fix load only relevant scoped context | Partial | Context Enrichment Gate exists, but active/candidate/excluded selection should be made more operational. |
| working-context handles complex or cross-module work | Partial | Template and lifecycle hooks exist, but escalation and contract update behavior need examples and review checks. |
| project finish updates wiki only after verification or explicit limitation | Mostly met | Verification gate exists; needs clearer mapping from changed files to affected wiki pages. |
| project review checks code risk, test gaps, scope drift, tool-bridge consistency, and wiki drift | Partial | Review stance exists, but tool-bridge consistency and wiki drift checks need a checklist. |
| real project can run end-to-end without old project-coding-skills | Not yet proven | Needs an acceptance run or dry-run on a real multi-module project. |

## Skill Gaps

### project-init

Already present:

- project root resolution through lifecycle reference
- `.llm-wiki` skeleton creation
- legacy `docs/ai-coding` migration source handling
- conservative module discovery
- `.codegraph/` inspection as a marker

MVP gaps:

- Define exact starter files and update behavior directly enough for a real run.
- Add refresh behavior for existing `.llm-wiki` instead of only init behavior.
- Clarify module table fields, allowed status values, and when a module becomes `active`, `reference-only`, or `discovered`.
- Clarify how existing `.codegraph/` is recorded as read-only supporting context.

Priority: P0.

### project-ingest

Already present:

- supported source types
- confirmation before deep-reading binary, large, or sensitive sources
- ingest index and source proxy model
- source safety boundaries

MVP gaps:

- Define confirmation prompts for PDF, Word, URL, logs, and sensitive files.
- Add stale-source detection rules for files already in `.llm-wiki/ingest/index.md`.
- Add required final report fields.
- Clarify when ingest should only index path and when it may summarize.

Priority: P0.

### project-develop

Already present:

- context-first workflow
- source of truth order
- scoped context recovery
- Superpowers bridge after context recovery
- requirement and working-context page creation

MVP gaps:

- Add explicit Context Handoff and Return Handoff using `superpowers-bridge.md`.
- Add OpenSpec-style change summary fields when no OpenSpec tool is present.
- Add scope escalation behavior inside the main skill, not only in references.
- Clarify when user confirmation is required before implementation.

Priority: P0.

### project-fix

Already present:

- evidence-first bug flow
- systematic-debugging bridge
- regression coverage guidance
- verification and bug summary update

MVP gaps:

- Add reproduction evidence format.
- Add failure-to-reproduce path.
- Add scope escalation rule for bugs that cross module boundaries.
- Add final diagnosis and verification report format.

Priority: P1.

### project-finish

Already present:

- verification gate
- verification-before-completion bridge
- affected wiki page sync
- handoff report

MVP gaps:

- Add changed-file to wiki-page mapping steps.
- Clarify source proxy status updates when a requirement source has been implemented or invalidated.
- Add exact handling for skipped verification.
- Add status transitions for working-context pages.

Priority: P1.

### project-review

Already present:

- findings-first review stance
- git diff and evidence inputs
- scope drift and wiki drift checks
- requesting-code-review bridge

MVP gaps:

- Add concrete checklist for tool-bridge consistency.
- Add concrete checklist for `.llm-wiki` drift.
- Add severity definitions.
- Add "no findings" output expectations.

Priority: P0.

## Next Implementation Order

1. Strengthen `project-init`, `project-ingest`, `project-develop`, and `project-review` because they block first real team use.
2. Then strengthen `project-fix` and `project-finish` because they are already closer to usable.
3. Add `acceptance-cases.md` with real pressure scenarios before claiming MVP complete.
4. Run one end-to-end dry run on a real multi-module project.

## Do Not Do Yet

- Do not add automations or reminders.
- Do not require codegraph generation.
- Do not implement a full OpenSpec clone.
- Do not add CI or PR integration.
- Do not expand `.llm-wiki` into a large documentation system.
