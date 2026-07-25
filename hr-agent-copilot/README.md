# HR Agent Copilot

Role-focused skills for resume screening, candidate detail reports, and interview question generation.

English | [简体中文](./README.zh.md)

## What Is This?

HR Agent Copilot is the HR recruiting role group in Role Copilot Skills.

It helps HR teams, hiring managers, and technical interviewers turn recruiting workflows into reusable AI-assisted skills. The current skills come from the earlier `hr-recruiting-screening-skill` project and are reorganized here as an Agent Copilot role.

## Current Skills

| Skill | Use When |
|---|---|
| `hr-resume-screening-copilot` | First-stage screening: compare resumes against a JD, rank candidates, score them out of 100, and recommend interview candidates. |
| `hr-candidate-detail-report-copilot` | Explain candidate score reasons, strengths, weaknesses, risks, education/company/stability signals, and interview verification points. |
| `hr-interview-question-generator-copilot` | Generate candidate-specific interview focus areas, questions, reference answer points, follow-up probes, and weak-answer signals. |

## Shared Resources

```text
hr-agent-copilot/
  SKILL.md
  references/
    scoring-rubric.md
    report-template.md
    interview-template.md
    llm-wiki-integration.md
    llm-wiki-ingest.md
  llm-wiki-profile.yml
  ingest-mapping.yml
  scripts/
    extract_resumes.py
    requirements.txt
  examples/
    sample-jd.md
    sample-output.md
```

## Optional LLM Wiki Runtime

Each HR skill carries an SCP v0.1 manifest and follows the shared
[LLM Wiki integration contract](./references/llm-wiki-integration.md). The
runtime is optional: enabled runs query HR context before work and persist
declared outputs afterward; unavailable or disabled runs keep the original
workflow.

The package-level `SKILL.md` is a discoverable router. It selects one child
skill and does not run SCP operations itself; the selected child owns preflight,
query, ingest, and fallback.

Keep the complete `hr-agent-copilot/` directory together when installing the
package so child skills can resolve shared `references/` and `scripts/`.

### Historical JD Import

The HR package owns the JD semantics in `ingest-mapping.yml` and
`references/llm-wiki-ingest.md`. `llm-wiki-core` supplies the generic init,
ingest, query, and maintenance workflow.

The import previews verbatim JD evidence before writing and excludes resumes,
candidate facts, scores, and interview outcomes in Phase 1.

## Install

Install one skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
```

Install all HR skills one by one:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-candidate-detail-report-copilot
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-interview-question-generator-copilot
```

## Typical Workflow

```text
JD + resumes
-> hr-resume-screening-copilot
-> hr-candidate-detail-report-copilot
-> hr-interview-question-generator-copilot
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

