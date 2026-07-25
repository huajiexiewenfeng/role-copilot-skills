---
name: hr-interview-question-generator-copilot
description: Use this skill when the user has selected interview candidates and asks for interview questions, interview focus areas, reference answers, follow-up probes, risk verification points, weak-answer signals, or candidate-specific technical interview plans. This skill should generate targeted questions based on the JD and each candidate's resume claims.
---

# HR Interview Question Generator

## Purpose

Generate candidate-specific interview plans after resume screening.

The goal is to verify whether the candidate truly has the experience claimed in the resume and whether they fit the JD.

## Inputs

Accept:

- JD text or JD file.
- Candidate resume text.
- Candidate detail report.
- Candidate names selected by the user.
- Specific interview focus requested by the user.

If candidate resumes are missing, ask for them or ask the user to run `hr-resume-screening-copilot` first.

## Shared Resources

Use HR Agent Copilot shared files:

- `../references/interview-template.md`
- `../references/scoring-rubric.md`

If installed in a flattened environment, locate equivalent `references/` paths near the skill root.

## Optional LLM Wiki Augmentation

This skill declares its memory contract in `scp.yml`. Before the main business
workflow, read `../references/llm-wiki-integration.md`, run the
`resolve-config` preflight, and apply the declared query flow when HR memory is
enabled. If any runtime step fails, follow the shared fallback contract and
complete the original workflow.

## Workflow

When the user names a candidate without supplying the resume again, apply the
shared Candidate Resolution flow before concluding that the resume is missing.
Do not search Graph output or candidate directories as a fallback.

For each selected candidate:

1. Read the JD requirements.
2. Identify the candidate's strongest matching claims.
3. Identify the candidate's highest-risk or most ambiguous claims.
4. Turn those claims into targeted validation questions.
5. Prefer scenario and project-depth questions over textbook questions.
6. Provide reference answer points.
7. Provide follow-up probes.
8. Provide weak-answer and rejection signals.
9. End with a concise interview recommendation focus.

## Question Types

Use a mix of:

- Resume-claim validation questions.
- Scenario design questions.
- Incident debugging questions.
- Trade-off questions.
- "What did you personally build?" questions.

Avoid relying only on:

- Textbook definitions.
- Generic "tell me about your project" questions.
- Questions unrelated to the JD.

## Output Structure

Use this structure for each candidate:

```markdown
# [Candidate Name] Interview Plan

## Candidate Positioning

...

## Interview Focus

1. ...

## Questions, Reference Answers, And Follow-Ups

### 1. [Question]

Why ask:

- ...

Reference answer points:

- ...

Follow-up probes:

- ...

Weak answer signals:

- ...

## Risk Signals

1. ...

## Post-Interview Scoring Guide

- Strong pass:
- Pass:
- Weak pass:
- No pass:
```

## Reference Answer Rules

Reference answers should be answer points, not rigid scripts.

Good answers usually include:

- System boundary.
- Data model.
- State transitions.
- Failure modes.
- Idempotency and retry.
- Security and permission checks.
- Observability.
- Trade-offs.
- Concrete examples from the candidate's own work.

## Risk Verification

Always include questions that verify:

- Whether the candidate personally built the claimed module.
- Whether the candidate can explain design trade-offs.
- Whether the candidate has handled failures in production.
- Whether keyword claims are shallow or deep.


