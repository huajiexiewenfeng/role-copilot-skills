---
name: hr-candidate-detail-report-copilot
description: Use this skill when the user asks for candidate details, score reasons, personnel detail reports, strengths and weaknesses, education/company/stability analysis, risk analysis, or why candidates were ranked in a certain order after resume screening. This skill explains candidate fit in detail and should usually follow hr-resume-screening-copilot.
---

# HR Candidate Detail Report

## Purpose

Explain why each candidate received a score and hiring recommendation.

Use this skill after an initial ranking, or when the user wants detailed candidate-by-candidate analysis.

## Inputs

Accept:

- JD text or JD file.
- Resume text or extracted resume files.
- Existing candidate ranking output.
- Candidate names selected by the user.

If the ranking score is already available, preserve it unless the user asks to rescore.

## Shared Resources

Use HR Agent Copilot shared files:

- `../references/scoring-rubric.md`
- `../references/report-template.md`

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

For each candidate:

1. Re-read the JD's must-have and nice-to-have requirements.
2. Extract candidate facts from the resume.
3. Explain the score by dimension:
   - Role match.
   - Technical/professional depth.
   - Education and major.
   - Stability.
   - Project and company quality.
   - Risk control.
4. Identify strengths.
5. Identify weaknesses.
6. Identify risk signals.
7. List interview verification points.
8. Give a recommendation:
   - Strongly recommend interview.
   - Recommend interview.
   - Backup interview.
   - Do not prioritize.
   - Reject for this role.

## Detail Report Structure

Use this structure:

```markdown
## [Candidate Name]

Overall recommendation: [...]

Score: [x]/100

### Why This Score

- Role match:
- Technical depth:
- Education and major:
- Stability:
- Project/company quality:
- Risk control:

### Strengths

1. ...

### Weaknesses

1. ...

### Risk Signals

1. ...

### Verification Points

1. ...

### One-Sentence Summary

...
```

## Analysis Rules

- Separate resume facts from judgments.
- Treat ambiguous claims as verification points.
- Do not automatically reject outsourcing or short tenure; explain the risk.
- Do not use protected attributes as hiring reasons.
- Use age only if the user explicitly asks and only as role-level or career-stage fit.
- Keep the summary practical for HR or hiring managers.

## Output Style

When comparing multiple candidates, use a compact table first, then details.

When the user asks for a short answer, provide one-sentence summaries only.


