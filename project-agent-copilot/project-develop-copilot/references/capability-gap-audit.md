# Capability Gap Audit

Use this audit after `north-star.md` when deciding what to implement next. It translates the North Star into concrete MVP gaps across the six project skills.

## Summary

The current collection is installable and directionally aligned. The main remaining work is to turn each skill from a compact workflow description into a reliable operating guide with clear gates, required outputs, and drift checks.

## MVP Status

| Done Means item | Status | Notes |
|---|---|---|
| all six project skills are installable and discoverable | Met | `npx skills add . --list` discovers all six project skills. |
| project init creates a usable `.llm-wiki` | Strengthened | Starter output, refresh behavior, module statuses, and codegraph read-only handling are now in `project-init`. Needs real-project dry run. |
| project ingest captures source material safely | Strengthened | Confirmation prompts, stale-source handling, processing modes, and final report are now in `project-ingest`. Needs file-type dry run. |
| project develop and project fix load only relevant scoped context | Partial | `project-develop` now has handoff, OpenSpec-style summary, escalation, and return handoff. `project-fix` still needs P1 detail. |
| working-context handles complex or cross-module work | Partial | Template and lifecycle hooks exist, but escalation and contract update behavior need examples and review checks. |
| project finish updates wiki only after verification or explicit limitation | Strengthened | Verification gate, changed-file mapping, skipped verification handling, source proxy status, and working-context status are now present. Needs dry run. |
| project review checks code risk, test gaps, scope drift, tool-bridge consistency, and wiki drift | Strengthened | Review checklist, severity, no-finding output, wiki drift, and tool-bridge consistency are now in `project-review`. Needs dry run. |
| real project can run end-to-end without old project-coding-skills | Not yet proven | Needs an acceptance run or dry-run on a real multi-module project. |

## Skill Gaps

### project-init

Already present:

- project root resolution through lifecycle reference
- `.llm-wiki` skeleton creation
- legacy `docs/ai-coding` migration source handling
- conservative module discovery
- `.codegraph/` inspection as a marker

MVP gaps addressed:

- Exact starter/update behavior, refresh mode, module table fields, statuses, and codegraph read-only handling were added.

Remaining:

- Run against a real multi-module project and tune module discovery language.

Priority: dry-run.

### project-ingest

Already present:

- supported source types
- confirmation before deep-reading binary, large, or sensitive sources
- ingest index and source proxy model
- source safety boundaries

MVP gaps addressed:

- Confirmation prompts, stale-source detection, processing modes, and final report fields were added.

Remaining:

- Validate with Markdown, PDF, Word, URL, and log examples.

Priority: dry-run.

### project-develop

Already present:

- context-first workflow
- source of truth order
- scoped context recovery
- Superpowers bridge after context recovery
- requirement and working-context page creation

MVP gaps addressed:

- Context Handoff, Return Handoff, OpenSpec-style summary, scope escalation, and implementation confirmation were added.

Remaining:

- Validate with a cross-service feature.

Priority: dry-run.

### project-fix

Already present:

- evidence-first bug flow
- systematic-debugging bridge
- regression coverage guidance
- verification and bug summary update

MVP gaps addressed:

- Reproduction evidence format, failure-to-reproduce path, bug scope escalation, and final report were added.

Remaining:

- Validate with a real failed test, log, or runtime symptom.

Priority: dry-run.

### project-finish

Already present:

- verification gate
- verification-before-completion bridge
- affected wiki page sync
- handoff report

MVP gaps addressed:

- Changed-file mapping, source proxy status, skipped verification handling, and working-context status transitions were added.

Remaining:

- Validate with a real finished change.

Priority: dry-run.

### project-review

Already present:

- findings-first review stance
- git diff and evidence inputs
- scope drift and wiki drift checks
- requesting-code-review bridge

MVP gaps addressed:

- Tool-bridge consistency checklist, wiki drift checklist, severity definitions, and no-finding output were added.

Remaining:

- Validate against a real diff with wiki drift.

Priority: dry-run.

## Next Implementation Order

1. Use `acceptance-cases.md` to run pressure scenarios.
2. Run one end-to-end dry run on a real multi-module project.
3. Update this audit from dry-run findings.

## Do Not Do Yet

- Do not add automations or reminders.
- Do not require codegraph generation.
- Do not implement a full OpenSpec clone.
- Do not add CI or PR integration.
- Do not expand `.llm-wiki` into a large documentation system.
