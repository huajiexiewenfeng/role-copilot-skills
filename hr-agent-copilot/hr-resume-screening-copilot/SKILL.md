---
name: hr-resume-screening-copilot
description: Use this skill whenever the user wants to screen resumes, analyze PDF resumes from one or more folders, compare candidates against a JD, rank candidates, score candidates out of 100, or produce an interview recommendation list. This is the first-stage HR screening skill and should be used before candidate detail reports or interview question generation.
---

# HR Resume Screening

## Purpose

Rank resumes against a job description with an explainable 100-point model.

Use this skill for first-pass screening: read the JD, extract or read resume text, score candidates, and produce a ranked interview recommendation list.

## Inputs

Accept:

- A JD pasted in the conversation.
- A JD file path, preferably `.md` or `.txt`.
- One PDF resume.
- One folder of PDF resumes.
- Multiple folders of PDF resumes.
- Previously extracted `.txt` or `.json` resume files.

If the JD or resume source is missing, ask for it.

## Shared Resources

Use HR Agent Copilot shared files:

- `../scripts/extract_resumes.py`
- `../references/scoring-rubric.md`
- `../references/report-template.md`

If the skill is installed in a flattened environment, locate equivalent `scripts/` and `references/` paths near the skill root.

## Workflow

1. Read the JD and identify:
   - Role title and level.
   - Must-have requirements.
   - Nice-to-have requirements.
   - Business domain.
   - Deal breakers.
   - Hidden priorities implied by the user's wording.
2. Read or extract resumes.
   - If resumes are PDFs and text is not already available, run `scripts/extract_resumes.py`.
   - Use recursive folder scanning when the user provides folders.
3. Extract candidate facts:
   - Name.
   - Years of experience.
   - Age, if present and job-relevant only when the user explicitly asks.
   - Education level, school, and major.
   - Company history.
   - Each job segment duration.
   - Recent job duration.
   - Core technologies.
   - Business domain experience.
   - Project role and responsibility depth.
   - Risk signals and missing information.
4. Score candidates with `references/scoring-rubric.md`.
5. Produce a ranking report using `references/report-template.md`.
6. Separate resume facts, reasoned judgments, and interview verification points.

## PDF Extraction

Example:

```bash
python scripts/extract_resumes.py --input "D:/workspace/ai-workspace/jd" --output output/hr-resume-extracts
```

Multiple folders:

```bash
python scripts/extract_resumes.py --input "D:/resumes/backend" "D:/resumes/ai" --output output/hr-resume-extracts
```

If `pypdf` is unavailable:

```bash
pip install -r scripts/requirements.txt
```

## Output

Always include:

- Candidate ranking table.
- Score breakdown table.
- Recommended interview list.
- Non-prioritized candidates.
- Key risk and verification points.
- Notes about missing or ambiguous information.

## Scoring Discipline

Do not score only by keyword matching.

Reward:

- Direct role/domain match.
- Clear project ownership.
- Production system experience.
- Relevant architecture and problem-solving depth.

Penalize:

- Vague claims.
- Keyword-only experience.
- unclear project ownership.
- unexplained frequent short tenures.

The final score reflects fit for this JD, not general candidate ability.


