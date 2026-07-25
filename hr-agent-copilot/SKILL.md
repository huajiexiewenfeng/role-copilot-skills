---
name: hr-agent-copilot
description: Use when the user asks for general HR recruiting assistance without naming a specific child skill, or wants to continue an existing HR hiring workflow whose next stage must be selected.
---

# HR Agent Copilot

## Purpose

Route a natural-language recruiting request into the correct HR child skill.
This parent is a discoverable package entry point, not a recruiting workflow
implementation.

## Routing

| User intent | Child skill |
| --- | --- |
| Screen resumes against a JD, rank candidates, or recommend interviews | `hr-resume-screening-copilot/SKILL.md` |
| Explain scores, strengths, weaknesses, risks, or candidate fit | `hr-candidate-detail-report-copilot/SKILL.md` |
| Generate candidate-specific interview questions, probes, or answer signals | `hr-interview-question-generator-copilot/SKILL.md` |

## Routing Contract

1. Infer the current HR stage from the user's request and available conversation
   context.
2. Read and follow exactly one child skill for the current stage.
3. If the user requests a multi-stage workflow, complete one stage at a time and
   route the next stage only after the current result exists.
4. Ask one short clarification question only when the intended stage or
   required input cannot be inferred.

The parent does not run `resolve-config`, load context, write records, or
register artifacts. It does not own an `scp.yml`. The selected child skill owns
its SCP preflight, query, domain workflow, ingest, and fallback behavior.

Do not perform resume scoring, candidate analysis, or interview-plan generation
directly from this parent skill.
