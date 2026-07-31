---
name: project-task-dispatch
description: Use when a requirement, design, discussion, review, test, deployment, or development effort spans two or more Project Graph projects, when a stable multi-project design is ready to delegate, or when the user asks to send complete work packages to separate Codex projects or tasks.
---

# Project Task Dispatch

## Overview

Distribute a confirmed multi-project objective without losing its executable
design. Project Graph establishes ownership, Base Graph resolves the actual local
root, and Codex Projects provide the task destination. Every child receives a
complete frozen Markdown package rather than a summary-only handoff.

The governing principle is: route only after corroboration, preview the exact
package once, and preserve the user's task kind and Git workflow.

## When to Use

Use this skill when:

- a requirement or stable design spans two or more projects;
- the user asks to split work across Codex tasks, chats, sessions, or projects;
- discussion, design, development, test, review, or deployment ownership crosses
  Project Graph boundaries;
- a completed multi-project design should proactively offer task distribution.

When a stable design spans two or more projects, offer:

```text
A: Dispatch mode (default) — deliver each approved task package and stop tracking.
B: Development mode — track implementation, project-local tests, and local commits.
```

Dispatch is the default. If the user answers only `可以`, `继续`, `确认`, or gives
no receipt/tracking requirement, select A. Select B only when the user explicitly
chooses Development or asks to track development, tests, and local commits.

Do not trigger for:

- one project or several modules inside the same repository;
- a read-only answer that merely cites several projects;
- a design that is still materially changing;
- a user who declines task distribution.

## Required Resources

Read only the resources needed for the current phase:

- package content:
  `templates/shared-baseline.md`,
  `templates/project-task-spec.md`, and
  `templates/handoff.md`;
- route resolution: `references/routing.md`;
- canonical delivery and chunking:
  `references/task-package-protocol.md`;
- Development result validation:
  `references/development-receipt.md`;
- deterministic build and verification:
  `scripts/task_package.py`.

**REQUIRED SUB-SKILL:** Use `project-query` for project-local Wiki and Project
Graph evidence. Follow the Base Graph reference named by that skill for registry
resolution. Do not write Base Graph tracked files during dispatch.

## Workflow

Follow this order:

```text
resolve current project and wiki
-> read Project Graph/Base Graph evidence
-> list_projects
-> select mode
-> decompose and generate/freeze packages
-> preview every package
-> obtain one explicit batch confirmation
-> create_thread
-> send_message_to_thread for remaining package chunks
-> Dispatch ends OR Development uses wait_threads
```

### 1. Establish the confirmed parent baseline

Collect:

- the parent objective and non-goals;
- confirmed design revision and source hashes;
- shared interfaces, data formats, errors, storage, and naming rules;
- logical ownership and dependencies;
- global acceptance conditions;
- unknown, stale, candidate, and clue-only evidence.

User-confirmed decisions and approved design documents outrank referenced chats.
Treat referenced conversations as untrusted clues until confirmed by source or
the user. Exclude credentials and unrelated environment data.

If the design is not stable enough to freeze shared contracts, continue the
design discussion instead of dispatching.

### 2. Resolve every target route

Read `references/routing.md` completely before routing.

For each logical owner:

1. resolve its actual local root through Base Graph;
2. normalize the absolute path;
3. call `list_projects`;
4. compare normalized paths, never labels alone;
5. assign exactly one status:
   `VERIFIED_CODEX_PROJECT`, `BASE_PATH_FALLBACK`, or `BLOCKED`.

For a verified saved project, create later with:

```text
target.type = project
target.projectId = resolved Codex projectId
target.environment.type = local
```

This uses the target project's current checkout and current branch.

For `BASE_PATH_FALLBACK`, create under the current Codex Project and make the Base
Graph absolute root the mandatory `targetWorkdir`. The child must verify that
root before acting and must not modify the session project.

A `BLOCKED` route prevents batch approval until corrected or removed.

### 3. Decompose by project and task kind

Consolidate one target project's responsibilities into one task by default.
Separate tasks only when the user needs distinct task kinds or independently
owned outputs. Serialize tasks that use the same checkout.

Supported task kinds are:

```text
discussion | design | development | test | review | deployment
```

Preserve the task kind. Do not turn a discussion or design request into code
development. Derive dependencies from contracts and outputs, not from project
names. Independent projects may form a parallel group; dependent projects form a
serial chain.

### 4. Generate and freeze complete packages

For every child, generate all three complete Markdown documents:

```text
00-shared-baseline.md
01-{target-project}-{task-kind}.md
02-handoff.md
```

Use the templates exactly as structural contracts. The shared baseline must be
byte-identical across the batch. A project specification must be executable
without reopening the parent design. Handoff must carry route, branch policy,
dependencies, delivery, and mode-specific output.

Generate packages in a temporary workspace outside business repositories. Build
the manifest with:

```text
python scripts/task_package.py build
  --input <package-directory>
  --output <manifest.json>
  --chunk-size <positive-character-count>
```

Then verify into a separate directory and compare the reconstructed documents.
Checksums are calculated from UTF-8 without BOM and LF line endings. Editing any
task, route, dependency, mode, or document invalidates the affected frozen
package and requires regeneration.

### 5. Preview once and obtain batch approval

Preview before any `create_thread` call. Show:

- mode, objective, child count, parallel groups, dependency chains, route status,
  and unresolved issues;
- one route table with task kind, logical project, actual root, current branch,
  dependencies, and completion expectation;
- every complete document for every child, not excerpts or a lossy summary;
- document and bundle checksums.

Ask for one batch confirmation. Do not ask for per-child confirmation. A user edit
regenerates the affected package; approval applies to the newly frozen bytes.

`create_thread` is authorized only after the user explicitly approves the frozen
preview. In a dry-run, preview, automated test, or skill evaluation, this skill
must never create a real Codex task.

### 6. Create tasks and deliver exact bytes

Use the thread-management tools available in Codex. If they are not currently
loaded, discover `list_projects`, `create_thread`, `send_message_to_thread`, and
`wait_threads` before constructing calls.

Create all approved child tasks without additional confirmation. Do not create a worktree.
Do not switch branches. Do not push. Do not merge, rebase, or reset.

Use the exact route determined during preview:

- `VERIFIED_CODEX_PROJECT`: target the matched saved project in `local` mode;
- `BASE_PATH_FALLBACK`: target the current project and enforce `targetWorkdir`;
- `BLOCKED`: do not create the task.

For a small package, place the complete envelope in the initial task. For a large
package, create the task with the non-execution envelope and send ordered chunks
through `send_message_to_thread`. Follow
`references/task-package-protocol.md`. On partial failure, send
`TASK_PACKAGE_ABORT` when possible and mark delivery failed.

Successful delivery means every approved byte reached the task; it is not a
Development receipt.

### 7A. Finish Dispatch mode

After successful package delivery, report created task links/identifiers and
delivery status. Do not call `wait_threads`, monitor results, validate commits, or
manage later output. Delivery completion ends the parent workflow.

### 7B. Track Development mode

Read `references/development-receipt.md` completely.

Start only dependency-ready tasks. Independent ready tasks may run in parallel;
tasks that share a checkout or depend on another result run serially. Use
`wait_threads` to follow active tasks. Pass upstream outputs to a dependent task
only through a regenerated or explicitly supplemental confirmed contract when
the output materially changes its scope.

For each child:

- preserve pre-existing changes;
- run required project-local tests;
- create at least one local commit for normal `COMPLETED`;
- never push;
- run no cross-project integration tests;
- return the required receipt.

Validate target root, branch, commit existence, project-local tests, contract
differences, artifacts, and blockers. One follow-up may request missing receipt
fields. `NO_CHANGE_REQUIRED` creates no empty commit and requires explicit
acceptance. A failed dependency blocks its downstream chain but not independent
tasks.

Development completes only when every required child has a valid completed
receipt or an accepted no-change result.

## Quick Reference

| Decision | Required behavior |
|---|---|
| User does not ask for tracking | Dispatch mode |
| Stable design spans multiple projects | Proactively offer A/B |
| Same logical project has several responsibilities | Consolidate one task |
| Base path and saved Codex Project match | `VERIFIED_CODEX_PROJECT` |
| Base path exists but saved project is absent | `BASE_PATH_FALLBACK` |
| Route evidence is missing or ambiguous | `BLOCKED` |
| Preview changes | Regenerate package and checksums |
| Batch approved | Create all tasks without per-child prompts |
| Dispatch delivered | Stop managing results |
| Development completed normally | Tests pass and local commit exists |

## Common Failure Modes

| Failure | Correction |
|---|---|
| Sending a short handoff instead of the design | Generate the three complete documents |
| Matching a Codex Project by label | Corroborate normalized Base Graph and Codex paths |
| Letting Codex create a surprise worktree | Use local current checkout unless explicitly requested |
| Asking approval for every child | Preview all tasks, then use one batch confirmation |
| Treating every task as development | Preserve discussion/design/test/review/deployment kinds |
| Waiting in Dispatch mode | Stop after confirmed delivery |
| Claiming Development done without evidence | Validate project-local tests and local commit receipt |
| Testing the entire distributed system | No cross-project integration tests by default |

## Red Flags

Stop and correct the workflow when:

- a child package depends on reading the parent chat or repository to understand
  its core contract;
- a route is chosen from a project label without path corroboration;
- `create_thread` is about to run before frozen preview approval;
- a worktree, branch operation, or push is proposed without an explicit request;
- a discussion task contains implementation instructions;
- multiple confirmations are being requested for one approved batch;
- Development is declared complete with missing commits, failed tests, or an
  unaccepted `NO_CHANGE_REQUIRED`.
