# Progress Dashboard

Read `flow-record.md` when changing the development flow board or dashboard card model.

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

The skill template is:

```text
../references/progress-dashboard-template.html
```

`project-init` should create the dashboard when missing. `project-query` can refresh it on explicit user request. `project-finish` should update it after verified lifecycle progress. `project-review` should check dashboard drift. Users should not need to manually edit this file during normal development.

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
- verification trust level
- main risk
- next action

### Development Flow Board

Shows Flow Record cards grouped by lifecycle step:

- Source / Requirement
- Design
- Plan / Execute
- Development
- Testing
- Archive

Each card should represent one stable `flow_id` / Change Brief / Bug Brief, not an unrelated loose task. The same `flow_id` may appear in multiple lanes only when each lane shows a different evidence-backed step.

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

## Verification Trust Level Rule

Dashboard state must preserve verification trust. A green-looking status must not hide that verification is only agent-local, partially blocked, or accepted with limitation.

Trust levels:

- `agent-local`: tests/checks were run or summarized by the agent only.
- `ci-backed`: CI or another deterministic external runner passed and raw output/URL is recorded.
- `reviewed`: a human or external reviewer checked the verification or test integrity.
- `user-accepted-limitation`: verification is partial/blocked, and the user/project owner explicitly accepted the limitation.
- `blocked`: verification failed, could not run, lacks required provenance, or limitation was only proposed by the agent.
- `unknown`: existing evidence does not expose provenance yet.

Do not promote `agent-local` or `unknown` testing evidence to final done without explicit limitation acceptance, CI, or review evidence.

## Flow Record Rule

The dashboard's flow board should be generated from Flow Records stored in Change Briefs, Bug Briefs, or working-context pages.

Minimum card fields:

```text
flow_id:
title:
step: source | design | plan | development | testing | archive
status: pending | active | done | blocked | skipped
trust_level: agent-local | ci-backed | reviewed | user-accepted-limitation | blocked | unknown
source:
evidence:
updated:
```

The user-facing effect should be:

```text
one design/source document
-> one linked flow record
-> visible progress across execute/develop/test/archive
```

If a source document contains multiple separable changes, split them into multiple flow records only when the implementation or verification path is meaningfully different. Otherwise keep one record and use notes/open questions.

## Update Rules

Update dashboard only when one of these happens:

- lifecycle session status changes
- active scope changes
- verification status changes
- finish sync changes project state
- user asks for dashboard-only refresh from existing evidence
- review finds or clears drift
- user explicitly asks to update progress page
- evaluator/Dolores creates a lifecycle quality artifact worth surfacing

Do not update dashboard during ordinary lightweight discussion.

## Direct Dashboard Refresh Rules

Use direct dashboard refresh when the user explicitly says:

- update dashboard
- refresh dashboard
- update progress page
- 更新看板
- 刷新 dashboard
- 同步项目状态页

This route does not mean development is finished. It should:

- read `.llm-wiki/README.md`, `.llm-wiki/log.md`, `.llm-wiki/artifacts/index.md`, active Change Briefs, Bug Briefs, working-context pages, verification notes, and module/source indexes as needed
- update only `.llm-wiki/dashboard/progress.html` plus dashboard artifact metadata/log when needed
- keep unsupported items as `candidate`, `incomplete`, `unknown`, `blocked`, or `not verified`
- preserve existing dashboard layout and update `dashboardData` or marked sections
- avoid creating Change Briefs, Bug Briefs, implementation plans, or code changes

Direct refresh is appropriate after `project-init`, `project-ingest`, requirement discussion, planning, partial verification, review feedback, or any point where the team wants the visible status page to catch up.

Direct refresh should prefer existing Flow Records. If a new source/design document has no Flow Record yet, show it as a `candidate` or `pending` card and recommend creating or confirming the related Change Brief instead of silently inventing an execution plan.

## Flow Board Projection

When refreshing the dashboard, build the flow board in this order:

1. Read Flow Records from:
   - `.llm-wiki/requirements/*.md`
   - `.llm-wiki/bugs/*.md`
   - `.llm-wiki/working-context/*.md`
2. Read supporting context from:
   - `.llm-wiki/artifacts/index.md`
   - `.llm-wiki/ingest/index.md`
   - `.llm-wiki/sources/registry.md`
   - `.llm-wiki/log.md`
3. For each Flow Record row, create a card only when:
   - status is not empty, or
   - evidence is present, or
   - the step is currently active/blocked.
4. Put cards into lanes:

| Flow step | Dashboard lane |
|---|---|
| `source` | 需求/来源 |
| `design` | 设计 |
| `plan` | 执行计划 |
| `development` | 开发 |
| `testing` | 测试 |
| `archive` | 归档 |

5. Preserve one stable `flow_id` across cards.
6. Link card evidence to the source `.md` page whenever possible.
7. If evidence is missing, keep status `pending`, `candidate`, `unknown`, or `blocked`; do not promote to `done`.

Candidate source/design documents without Flow Records may be shown in the 需求/来源 lane, but they must be clearly labeled `candidate` and must not appear in plan/development/testing/archive lanes.

### Parent / Child Flow Projection

When a Change Brief or Bug Brief contains `parent_flow_id`, `child_flow_id`, or any linked child Flow Record, the dashboard must treat the child as a separate `flow_id`.

Rules:

- Do not collapse a child Flow Record into the parent card text only.
- For every Flow Record page with its own `flow_id`, create lane cards for every evidence-backed row in that Flow Record.
- Preserve `parent_flow_id` in structured data as `parentFlowId` when present.
- In the visible board, child cards may use a compact style or child marker, but they must still be visible in the same lifecycle lanes as parent cards.
- Parent cards may mention child scope in summary text, but that does not replace child cards.

Regression check after refresh:

```text
for each distinct flow_id discovered in Flow Records:
  visible board card count for flow_id == count of eligible Flow Record rows
  dashboardData.flowRecords count for flow_id == count of eligible Flow Record rows
  each lane count == number of visible cards in that lane
```

If any check fails, the dashboard refresh is incomplete. Fix the board and `dashboardData` before reporting completion.

## Dashboard Data Contract

The template should keep a structured data section that is easy for LLMs to update:

```javascript
window.dashboardData = {
  flowRecords: [
    {
      flowId: "",
      title: "",
      step: "source",
      lane: "需求/来源",
      status: "pending",
      source: "",
      evidence: "",
      trustLevel: "unknown",
      updated: ""
    }
  ]
};
```

Agents should prefer updating this data and the marked `BOARD_START` / `BOARD_END` section over rewriting the full page.

## Init Rules

During `project-init` or `project-init refresh`:

- create `.llm-wiki/dashboard/` when missing
- create `.llm-wiki/dashboard/progress.html` from `progress-dashboard-template.html` when missing
- use the detected project/user language for visible labels when practical
- create or preserve `.llm-wiki/artifacts/index.md`
- register the dashboard as `dashboard-progress`
- do not overwrite an existing dashboard layout during refresh
- do not mark a project feature-ready only because dashboard exists

Starter dashboard values should be conservative:

```text
stage: init or refresh
progress: 0-10%
active_scope: project
risk: context incomplete until scoped context exists
next_action: ingest a requirement or complete a scoped context
```

## Finish Update Rules

During `project-finish`, update only evidence-backed sections:

- current lifecycle session
- active requirement or bug
- current stage/status
- progress percentage when justified by completed gates
- Flow Record cards
- risk and evidence gap cards
- evidence list
- last update timestamp
- next suggested action

Prefer editing `window.dashboardData` or clearly delimited sections such as:

```html
<!-- LLM_SUMMARY_START -->
<!-- LLM_SUMMARY_END -->
<!-- BOARD_START -->
<!-- BOARD_END -->
<!-- EVIDENCE_START -->
<!-- EVIDENCE_END -->
```

Do not rewrite the full page for small status updates.

## Review Rules

During `project-review`, check:

- dashboard file exists when registered as an artifact
- dashboard stage/status is supported by Change Brief, Bug Brief, working-context, verification, or `.llm-wiki/log.md`
- dashboard Flow Record cards reference existing evidence
- each card's `flow_id`, step, and status match the linked Change Brief/Bug Brief/working-context
- dashboard does not hide blocked or high-risk active work
- dashboard does not claim verification success without verification evidence
- dashboard language matches the project/user-facing language

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
- When linking to local Markdown evidence, avoid raw navigation that depends on browser/server charset detection. Prefer the template's inline Markdown viewer, which fetches bytes and decodes as UTF-8 with `TextDecoder("utf-8")`.

## Common Mistakes

- Treating dashboard as the source of truth.
- Updating progress visually without updating `.llm-wiki` or artifact registry.
- Marking work done without verification evidence.
- Hiding blocked or risky work to make the page look clean.
- Creating a complex app when a static evidence-backed page is enough.
