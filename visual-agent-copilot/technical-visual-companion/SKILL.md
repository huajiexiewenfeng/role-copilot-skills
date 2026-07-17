---
name: technical-visual-companion
description: Use this skill whenever the user asks to turn a confirmed technical design into a polished offline static HTML visual, including architecture, system boundaries, service interactions, sequence flows, deployment topology, state transitions, failure recovery, or multiple complementary technical diagrams. Do not use it to invent or complete an unconfirmed design, build a product UI, or produce Mermaid, slides, PDF, or PNG-only output.
---

# Technical Visual Companion

## Purpose

Turn confirmed technical facts and decisions into one polished, self-contained static HTML visual companion.

The skill consumes confirmed input. It does not invent missing architecture, silently complete an unconfirmed design, or replace design discussion.

The user-facing deliverable is exactly one verified HTML file that works offline.

## Required Reads

Before generation, read these files completely:

- `references/diagram-selection.md`
- `references/visual-language.md`
- `references/html-contract.md`

## Compatibility

Execution requires:

- filesystem write access to the requested output directory;
- Python 3.11 or newer for deterministic validation;
- a browser capable of desktop inspection and an explicit 390px viewport inspection.

If browser capability is unavailable, the candidate HTML may remain on disk, but do not claim completion. Report `visual verification pending` and state which visual reviews remain.

## Workflow

### 1. Confirmed Input Gate

Use only:

- technical facts and decisions already confirmed in the conversation; or
- local files explicitly named by the user for this visual.

For this task, do not scan a repository, deployment tree, or unrelated documentation to fill gaps. If additional sources are needed, ask the user to name or approve them.

Stop before generation when:

- the input contains unchosen alternatives;
- named sources conflict;
- sequence, state, recovery, boundary, or ownership facts needed by the requested visual are missing;
- the output would expose sensitive content that the user has not approved for the artifact.

### 2. Visual Fact Model

Write a compact internal fact model before choosing a diagram. Capture:

- theme and the question the visual must answer;
- actors and system boundaries;
- responsibilities and ownership;
- connections, directions, and interaction types;
- execution order and gates;
- states, waits, retries, success, failure, and rollback or recovery;
- explicit exclusions;
- names, counts, versions, ports, and other values that must be preserved exactly.

Separate confirmed facts from presentation choices. If any required relationship remains uncertain, stop and ask rather than infer it.

### 3. Diagram Selection

Apply `references/diagram-selection.md` to the fact model. Automatically choose one to three complementary diagrams, selecting one diagram when it answers the full question. Respect an explicit user diagram type or count unless it conflicts with confirmed facts.

Record the selected diagram types and the distinct question each one answers. Reject duplicate diagrams that add decoration but no new relationship.

### 4. Generate One HTML

Create exactly one new static HTML file. Use the user's explicit output path when provided; otherwise use:

`docs/visuals/<topic-slug>.html`

The file must:

- be self-contained and work offline;
- use semantic HTML and accessible inline SVG for relationships;
- follow the adaptive Superpowers Visual Companion language without a fixed template;
- preserve every fact-model name, count, version, state, and exclusion;
- contain no JavaScript, iframe, CDN, external font, or network dependency.

For the output, do not overwrite an existing file without explicit user approval. Do not emit PNG, PDF, slides, Mermaid, a product UI, or multiple user-facing files in this version.

### 5. Deterministic Validation

Run the validator from the skill root. Pass every preserved fact-model term as a repeated `--required-term` argument:

```text
python scripts/validate_html.py --html <absolute-html-path> --required-term <term> --required-term <term>
```

Read the JSON result. Fix every structural error and rerun until `overall` is `passed`. Structural validation does not replace factual or visual review.

### 6. Desktop Visual Review

Open the actual local HTML in a browser at a desktop viewport. Inspect the full page, not just the first screen. Verify:

- hierarchy and reading order are clear;
- labels, arrows, lanes, and boundaries are not clipped or ambiguous;
- diagram relationships match the fact model;
- colors, spacing, and typography remain restrained and legible;
- no accidental horizontal overflow or placeholder content exists.

Fix the HTML and repeat deterministic validation after every material edit.

### 7. 390px Mobile Review

Inspect the same HTML at an explicit 390px viewport. Verify the mobile semantic alternative rather than accepting a uniformly scaled desktop canvas. Confirm:

- text remains readable without zoom;
- horizontal relationships become a clear vertical order where necessary;
- labels, direction, states, and exclusions remain present;
- no content overlaps, clips, or requires horizontal scrolling.

Fix and rerun both deterministic and desktop review when a mobile change affects shared markup or styles.

### 8. Completion Gate

Claim completion only when all of these are true:

- the fact model contains no unresolved technical choice;
- exactly one final HTML exists at the approved path;
- deterministic validation passed;
- desktop visual review passed;
- 390px mobile review passed;
- the final artifact preserves required facts and contains no unapproved content;
- no unapproved overwrite or repository scan occurred.

If any condition is unmet, report the precise pending gate. Browser absence must be reported as `visual verification pending`.

## Output

On success, respond concisely with:

- the result;
- the final absolute HTML path;
- selected diagram types and count;
- deterministic, desktop, and 390px mobile verification summary.

Do not expose staging files, screenshots, validator fixtures, or other temporary artifacts as user deliverables.
