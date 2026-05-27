# Resume Screening Report Template

Use this template for ranking and candidate detail reports.

## Report Title

```markdown
# [Role Name] Resume Screening Report
```

## Executive Summary

Include:

- Number of resumes reviewed.
- Top recommended candidates.
- Main hiring trade-off.
- Any missing information or extraction limitations.

Example:

```markdown
Reviewed 8 resumes against the Senior Java Backend JD. The strongest matches are A and B because they have direct drone/IoT platform experience. C is a strong platform backend candidate but lacks MQTT/device experience.
```

## Ranking Table

Use this table:

```markdown
| Rank | Candidate | Score | Recommendation | Best Fit | Main Risk |
|---:|---|---:|---|---|---|
| 1 | ... | 88 | Strongly recommend interview | ... | ... |
```

## Score Breakdown Table

Use this table:

```markdown
| Candidate | Total | Role Match /40 | Technical Depth /20 | Education /10 | Stability /10 | Project Quality /10 | Risk Control /10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| ... | 88 | 36 | 17 | 8 | 8 | 9 | 10 |
```

## Candidate Detail

For each candidate:

```markdown
## [Candidate Name]

Overall recommendation: [Strongly recommend interview / Recommend interview / Backup / Do not prioritize / Reject]

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
2. ...

### Weaknesses

1. ...
2. ...

### Verification Points

1. ...
2. ...

### Interview Focus

1. ...
2. ...

### One-Sentence Summary

[One concise sentence.]
```

## Recommended Interview List

Use this section:

```markdown
## Recommended Interview List

1. [Candidate] - [reason]
2. [Candidate] - [reason]
```

## Not Prioritized

Use this section:

```markdown
## Not Prioritized For This Role

- [Candidate] - [main reason]
```

## Notes And Assumptions

Include:

- PDF extraction issues.
- Missing resume fields.
- Unverified claims.
- Assumptions made while scoring.

