# HR Agent Copilot

Role-focused skills for resume screening, candidate detail reports, and interview question generation.

English | [简体中文](./README.zh.md)

## What Is This?

HR Agent Copilot is the HR recruiting role group in Role Copilot Skills.

It helps HR teams, hiring managers, and technical interviewers turn recruiting workflows into reusable AI-assisted skills. The current skills come from the earlier `hr-recruiting-screening-skill` project and are reorganized here as an Agent Copilot role.

## Current Skills

| Skill | Use When |
|---|---|
| `hr-resume-screening` | First-stage screening: compare resumes against a JD, rank candidates, score them out of 100, and recommend interview candidates. |
| `hr-candidate-detail-report` | Explain candidate score reasons, strengths, weaknesses, risks, education/company/stability signals, and interview verification points. |
| `hr-interview-question-generator` | Generate candidate-specific interview focus areas, questions, reference answer points, follow-up probes, and weak-answer signals. |

## Shared Resources

```text
hr-agent-copilot/
  references/
    scoring-rubric.md
    report-template.md
    interview-template.md
  scripts/
    extract_resumes.py
    requirements.txt
  examples/
    sample-jd.md
    sample-output.md
```

## Install

Install one skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening
```

Install all HR skills one by one:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-candidate-detail-report
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-interview-question-generator
```

## Typical Workflow

```text
JD + resumes
-> hr-resume-screening
-> hr-candidate-detail-report
-> hr-interview-question-generator
-> interview plan and verification focus
```

## PDF Extraction

If resumes are PDFs and text is not already extracted, use:

```bash
python scripts/extract_resumes.py --input "D:/resumes/backend" --output output/hr-resume-extracts
```

## Safety And Judgment

- Do not replace final hiring decisions.
- Separate resume facts from judgments.
- Treat ambiguous claims as interview verification points.
- Do not make discriminatory decisions based on protected attributes.
- Use age only if the user explicitly asks and only as career-stage or role-level context.
