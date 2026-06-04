# Progress Dashboard

The progress dashboard is a static HTML status surface maintained by LLM agents. It helps users see project progress quickly, but it is not a source of truth.

Source of truth remains:

- source code and tests
- user decisions
- `.llm-wiki` lifecycle pages
- artifact registry
- verification records
- git diff
- design docs and PRDs

## Default Path

Recommended path inside a target project:

```text
.llm-wiki/dashboard/progress.html
```

A project may choose another static HTML path, but it must be registered in `.llm-wiki/artifacts/index.md`.

## Layout Contract

The first implementation should keep one static HTML page with these regions:

```text
Top half: Project Cockpit
Bottom half: Development Flow Board
Reserved: Document Evidence
Reserved: Skills Maintenance Convention
```

### Project Cockpit

Shows overall project state:

- current lifecycle session
- active requirement or bug
- current status
- current gate
- verification status
- main risk
- next action

### Development Flow Board

Shows work cards grouped by lifecycle state:

- Backlog / Candidate
- Clarifying / Triaging
- Planned
- Executing
- Verifying
- Done
- Blocked

### Document Evidence

Lists important evidence:

- PRDs and design docs
- Change Briefs and Bug Briefs
- implementation plans
- verification reports
- review reports
- generated artifacts

### Skills Maintenance Convention

Reserved area for LLM-maintained notes about:

- which project skills were used
- lifecycle quality issues
- evaluator or Dolores outputs
- recommended skill updates

## Evidence Rule

Every dashboard fact must trace back to evidence.

Allowed evidence:

```text
.llm-wiki page
artifact registry row
verification command or manual check record
git diff or changed-file list
source proxy
user decision recorded in lifecycle session
```

Do not write dashboard-only facts.

Bad:

```text
Status: Done
```

Good:

```text
Status: Verified
Evidence: .llm-wiki/bugs/2026-06-04-payment-callback.md#Verification
```

## Update Rules

Update dashboard only when one of these happens:

- lifecycle session status changes
- active scope changes
- verification status changes
- finish sync changes project state
- review finds or clears drift
- user explicitly asks to update progress page
- evaluator/Dolores creates a lifecycle quality artifact worth surfacing

Do not update dashboard during ordinary lightweight discussion.

## Artifact Registry Row

Register the dashboard itself and important dashboard-related evidence:

```markdown
| id | type | path | owner | related_session | status | last_checked | notes |
|---|---|---|---|---|---|---|---|
| dashboard-progress | dashboard | .llm-wiki/dashboard/progress.html | LLM | project | active | 2026-06-04 | Evidence-backed project progress page. |
```

## Dashboard Drift

Dashboard drift exists when:

- dashboard status is newer than lifecycle evidence but unsupported
- lifecycle session says blocked but dashboard says done
- verification is partial but dashboard implies complete
- artifact registry references a dashboard that no longer exists
- dashboard cards reference missing Change Briefs or Bug Briefs
- dashboard omits a high-risk active lifecycle session

Review should report dashboard drift as a lifecycle finding, not a visual nit.

## Static HTML Constraints

- Keep the page standalone and easy for LLMs to edit.
- Prefer simple semantic HTML, CSS, and data blocks.
- Do not require a build step.
- Do not fetch remote assets by default.
- Keep status data easy to update without rewriting the full layout.
- Preserve evidence links in visible text or `data-evidence` attributes.

## Common Mistakes

- Treating dashboard as the source of truth.
- Updating progress visually without updating `.llm-wiki` or artifact registry.
- Marking work done without verification evidence.
- Hiding blocked or risky work to make the page look clean.
- Creating a complex app when a static evidence-backed page is enough.