# Project Domain Skill Contract

Project domain skills must be easy for the lifecycle router to choose, easy for an agent to execute, and hard to misuse. This contract adapts the Superpowers / Thinking Skills style to project lifecycle skills.

Every child skill under Project Develop Copilot should expose the same router-friendly structure.

## Required Structure

```markdown
---
name:
description:
---

# Skill Name

## Purpose

## When to Use

## When Not to Use

## Owned Gates

## Required First Check

## Core Process

## Mode / Entry Selection

## Inputs

## Outputs

## Context Handoff

## Return Handoff

## Boundaries

## Common Mistakes
```

## Frontmatter Rules

The `description` field is for triggering conditions only. It should not summarize the workflow.

Good:

```yaml
description: Use when diagnosing or fixing a project bug, error, failed test, regression, incident, log symptom, or unexpected behavior with scoped project context and LLM Wiki bug summaries.
```

Bad:

```yaml
description: Use when fixing bugs by gathering evidence, creating a bug brief, running debugging, writing tests, updating wiki, syncing dashboard, and preparing review.
```

Why: agents may follow the description shortcut instead of reading the full skill.

## Section Guidance

### Purpose

Say what the skill owns in the lifecycle and what it does not own.

### When to Use

List natural language signals, project state signals, and evidence types that should route here.

Examples:

- PRD, requirement, feature request, implementation plan.
- Bug, log, failed test, incident, regression.
- Finish, done, sync, update progress.
- Review, before commit, risk, merge readiness.

### When Not to Use

List likely false positives.

Examples:

- Lightweight file lookup.
- Design discussion without execution.
- External skill request outside project context.
- Finish request before any work exists.

### Owned Gates

Name the gates this skill must execute or check. Use `lifecycle-gates.md` as the source of gate names.

### Required First Check

State the first few checks before ordinary execution. Keep them operational.

Examples:

- Is project root clear?
- Is there a lifecycle session?
- Is this lightweight-answer?
- Is active scope known?
- Is verification evidence available?

### Core Process

Write the main flow as short steps. Keep stage execution here, not router logic.

### Mode / Entry Selection

Define internal modes for the skill.

Examples:

- `project-develop`: requirement discussion, plan confirmation, execution handoff.
- `project-fix`: evidence intake, reproduction, diagnosis, fix, verification.
- `project-review`: quick diff review, full lifecycle review, Dolores-triggered review.

### Inputs

List expected inputs. Do not require all inputs for every mode.

### Outputs

List what the skill returns or updates.

### Context Handoff

If this skill calls another skill or external tool, define what context it passes.

### Return Handoff

If this skill is called by the router or returns from a bridge, define what must be returned to lifecycle state.

### Boundaries

State safety and scope boundaries.

Examples:

- Do not edit code during discussion mode.
- Do not deep-read every module by default.
- Do not bypass verification.
- Do not update dashboard without evidence.

### Common Mistakes

List failure modes that cause lifecycle fragmentation.

Examples:

- Over-eager implementation.
- Missing Change Brief or Bug Brief.
- Skipping Context Recovery Gate.
- Letting an external skill own scope.
- Forgetting Return Handoff.
- Treating `.llm-wiki` as raw source storage.

## Minimum Compliance Checklist

A child skill is contract-compliant when:

- It has all required headings.
- Its description is trigger-only.
- It names owned gates.
- It has a Required First Check.
- It distinguishes lightweight or partial modes from full execution when relevant.
- It can receive Context Handoff.
- It can produce Return Handoff.
- It lists boundaries and common mistakes.

## Router Relationship

The root router chooses the primary stage. The child skill should not fight the router by re-routing from scratch unless the handoff is clearly wrong.

If a child skill detects wrong routing, it should return a short correction:

```markdown
## Routing Correction

- received_stage:
- recommended_stage:
- reason:
- safe_next_action:
```

Do not silently proceed under the wrong stage.
