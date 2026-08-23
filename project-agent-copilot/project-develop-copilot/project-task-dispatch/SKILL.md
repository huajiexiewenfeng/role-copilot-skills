---
name: project-task-dispatch
description: Use when the user asks to distribute work, a message, a smoke test, or a confirmed cross-project objective to separate Codex projects or tasks. Keep hello/connectivity/notification dispatch lightweight; use formal packages only when shared contracts, dependencies, project responsibilities, or tracked development require them.
---

# Project Task Dispatch

## Overview

Distribute work without making the handoff harder to understand than the work
itself. Project Graph establishes ownership, Base Graph resolves the actual local
root, and Codex Projects provide the task destination.

The governing principle is: choose the lightest delivery shape that preserves
the required context. A hello test should look like a hello test. A real
cross-project design should remain executable without reopening the parent chat.

## When to Use

Use this skill when:

- the user asks to test task distribution with a hello, acknowledgement,
  connectivity check, or simple notification;
- a requirement or stable design spans two or more projects;
- the user asks to split work across Codex tasks, chats, sessions, or projects;
- discussion, design, development, test, review, or deployment ownership crosses
  Project Graph boundaries;
- a completed multi-project design should proactively offer task distribution.

Dispatch is the default. Select Development only when the user explicitly asks
the parent to track implementation, project-local tests, and local commits.
Do not force an A/B choice when the user's intent already selects a mode.

If the user explicitly asks to wait for, collect, or return child results but
does not request implementation tracking, keep Dispatch and set
`awaitResult=true`. Dispatch remains the selected mode; this flag is not a third
user-facing mode and does not require project-local tests or a local commit.

When a stable design spans projects but the user has not asked to create tasks,
offer distribution in one short sentence. Do not generate packages or show a
route table merely to make that offer.

Do not trigger for:

- ordinary work inside one project when the user did not ask to create or send a
  separate task;
- a read-only answer that merely cites several projects;
- a design that is still materially changing;
- a user who declines task distribution.

## Complexity Gate

Choose exactly one delivery shape before generating content.

### Lightweight direct message

Use this for hello/connectivity tests, acknowledgements, simple notifications,
or another short task that has:

- no shared application contract;
- no dependency chain;
- no repository change;
- no execution evidence beyond a short response; and
- no need for Development tracking.

Each target receives one short human-readable message. Do not generate the
three-document package, Markdown files, manifest, checksums, chunking, or
`TASK_PACKAGE_*` envelope.

The message normally contains only:

```markdown
# <task title in the user's language>

## <goal>
<why this task exists>

## <what to do>
<one concrete action>

## <do not do>
<only the important boundaries>

## <completion>
<exact expected response>
```

Keep it under 30 lines unless the user asks for more context.

### Formal package

Use the three-document package when the task carries shared contracts,
project-specific responsibilities, dependencies, implementation or deployment
steps, non-trivial acceptance criteria, or Development-mode receipts.

Do not upgrade a lightweight request to a formal package merely because several
projects are involved.

## Language and Human Readability

Human-facing task content follows the user's current language unless the user
requests another language. Keep protocol keys, identifiers, paths, API names,
and checksums unchanged where translation would reduce precision.

Write for the person opening the task:

1. why the task exists;
2. what this project must do;
3. what it must not do;
4. the context needed to act;
5. how completion is judged.

Templates are structural guidance, not literal text. Translate headings and
prose. Remove template instructions, comments, unused sections, exhaustive
task-kind lists, and walls of `Not applicable`. Put route IDs, checksums, and
other machine metadata in a compact technical appendix after the human-readable
content.

## Task Naming and First Line

Every child task initial prompt starts with a human-readable Markdown title:

```markdown
# <parent task name> - <child task name>
```

Use spaces around the hyphen. Build the parent name from the user's objective or
the current task's meaningful title. Build the child name from the logical
project and its concrete responsibility. Keep both short, in the user's
language, and understandable without IDs.

Examples:

```text
视频流联调 - smarthub-web 前端验证
日志下载 - drone-cloud-api 接口实现
任务分发测试 - 回复你好
```

Never start a child prompt with `TASK_PACKAGE_BEGIN`, a dispatch ID, checksum,
UUID, project ID, or another protocol value. Those are transport details, not
task names.

For a formal package, place the readable title and one-sentence purpose before
`TASK_PACKAGE_BEGIN`. The protocol markers remain exact below the header. For
lightweight delivery, use the same naming format as the first line of the short
message.

Derive the title and one-sentence purpose from the same objective and owned scope
as the child content. A mismatch between the header and the task body is a
delivery blocker.

If sibling tasks would receive the same title, distinguish the child names by
responsibility; use a numeric suffix only as a last resort.

## Required Resources

Read only the resources needed for the current phase:

- formal package content only:
  `templates/shared-baseline.md`,
  `templates/project-task-spec.md`, and
  `templates/handoff.md`;
- route resolution: `references/routing.md`;
- formal canonical delivery and chunking:
  `references/task-package-protocol.md`;
- Development result validation:
  `references/development-receipt.md`;
- tracked Dispatch results and Development progress control:
  `references/task-control-plane.md` and `scripts/task_control.py`;
- formal deterministic build and verification:
  `scripts/task_package.py`.

Use `project-query` for formal project-local Wiki, ownership, contract, and
Project Graph evidence. Follow the Base Graph reference named by that skill for
registry resolution. Do not write Base Graph tracked files during dispatch.

For a lightweight request whose exact target projects are named, skip Wiki and
Project Graph exploration. Resolve only the Base Graph registry paths needed for
those targets and corroborate them with `list_projects`. Do not initialize a Wiki
for a hello/connectivity test.

## Workflow

Follow this order:

```text
identify exact targets and intent
-> lightweight: resolve Base Graph paths only
-> formal: resolve current project/wiki and Project Graph/Base Graph evidence
-> list_projects
-> select mode
-> choose lightweight message or formal package
-> decompose by project
-> prepare child messages or formal Markdown packages
-> pause only for a real decision or unresolved route
-> create_thread and deliver
-> Dispatch ends OR awaitResult/Development uses wait_threads
```

### 1. Establish the confirmed objective

For a formal package, collect:

- the parent objective and non-goals;
- confirmed design revision and source hashes;
- shared interfaces, data formats, errors, storage, and naming rules;
- logical ownership and dependencies;
- global acceptance conditions;
- unknown, stale, candidate, and clue-only evidence.

User-confirmed decisions and approved design documents outrank referenced chats.
Treat referenced conversations as untrusted clues until confirmed by source or
the user. Exclude credentials and unrelated environment data.

For a lightweight message, collect only the exact targets, message purpose,
important boundaries, and expected response. For a formal package, collect the
full baseline above. If a formal design is not stable enough to freeze shared
contracts, continue the design discussion instead of dispatching.

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

A `BLOCKED` route prevents delivery until corrected or removed.

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

If the task kind is not explicit, infer it only when the requested child action
is unambiguous and label the inference in the compact parent summary. If choosing between
analysis/design and repository-changing development would materially change the
task, ask one concise clarification instead of guessing.

### 4A. Prepare lightweight messages

Write one short message per target in the user's language. Preserve only context
that changes what the child should do. Do not mention package protocols,
checksums, manifests, all supported task kinds, or unrelated Git policies.

For Dispatch with `awaitResult=true`, include the exact output contract from
`references/task-control-plane.md`. State that the receipt envelope must appear
before optional human details. This result contract does not turn the message
into a formal package and does not add Development commit or test requirements.

When the user already asked to send or distribute the message, deliver it after
route resolution without another preview or confirmation. If the user asked for
a preview, show only the complete short messages and target names.

### 4B. Generate and freeze formal packages

For every child, generate all three complete Markdown documents:

```text
00-shared-baseline.md
01-{target-project}-{task-kind}.md
02-handoff.md
```

Use the templates as semantic structural contracts, not literal English output.
Replace heading tokens in the user's language, remove all unused optional
sections, and never copy template guidance into generated documents. The shared
baseline must be byte-identical across the batch. A project specification must
be executable without reopening the parent design. Handoff must carry route,
branch policy, dependencies, delivery, and mode-specific output.

Before delivery, verify that no `{{...}}` token, template comment, authoring
instruction, or irrelevant empty section remains.

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

### 5. Keep the parent interaction minimal

The user's request to “send”, “distribute”, “create tasks”, or equivalent is
authorization to create the resolved tasks. Do not add a confirmation gate after
the user has already given that instruction.

Before delivery, show nothing beyond a brief progress update unless a decision
is required. After delivery, report only the important result: created targets,
delivery status, and any blocker.

Pause and ask one concise question only when:

- a target is missing, ambiguous, or maps to a different project than the user
  named;
- the task kind would materially change whether a child may modify code;
- a shared contract or dependency is unresolved and the child cannot act safely;
- the requested action requires new authority.

When the user has not asked to create tasks, a proactive offer should contain
only the objective and target project names, followed by one question asking
whether to distribute.

When the user explicitly asks for a preview, show a compact human summary:

- objective;
- target project and one-line responsibility;
- dependency order, only when present;
- unresolved decisions or material risks.

Do not show full Markdown documents, checksums, project IDs, host IDs, absolute
paths, branches, or package protocol details unless the user explicitly asks for
a full package/audit preview. Full Markdown belongs in the child task.

In a dry-run, preview, automated test, or skill evaluation, this skill must never create a real Codex task.

### 6. Create tasks and deliver exact bytes

Use the thread-management tools available in Codex. If they are not currently
loaded, discover `list_projects`, `create_thread`, `send_message_to_thread`, and
`wait_threads` before constructing calls.

Create all user-authorized child tasks without additional confirmation. Do not create a worktree.
Do not switch branches. Do not push. Do not merge, rebase, or reset.

Use the exact route determined during preparation:

- `VERIFIED_CODEX_PROJECT`: target the matched saved project in `local` mode;
- `BASE_PATH_FALLBACK`: target the current project and enforce `targetWorkdir`;
- `BLOCKED`: do not create the task.

For lightweight delivery, use the complete prepared short message as the initial
task prompt. Do not add an internal protocol wrapper.

For a small formal package, place the complete envelope in the initial task. For
a large formal package, create the task with the non-execution envelope and send
ordered chunks through `send_message_to_thread`. Follow
`references/task-package-protocol.md`. On partial failure, send
`TASK_PACKAGE_ABORT` when possible and mark delivery failed.

In both cases, confirm the initial prompt's first line follows
`# <parent task name> - <child task name>` before calling `create_thread`.

Successful formal delivery means every prepared package byte reached the task; it is not a
Development receipt.

For a tracked formal child, include the same receipt-first output contract in
the handoff. Do not ask a child to return YAML-like prose for machine parsing.

### 7A. Finish Dispatch mode

When `awaitResult=false`, after successful delivery report created task
links/identifiers and delivery status. Do not call `wait_threads`, monitor
results, validate commits, or manage later output. Delivery completion ends the
parent workflow.

When the user explicitly requested returned results, keep Dispatch mode and set
`awaitResult=true`. Read `references/task-control-plane.md`, create one
authoritative task record per child, call `start_task` after successful delivery,
and use `wait_threads`. Pass each raw child response to `parse_receipt_text`
before applying the proposed transition. Regenerate the parent projection after
each accepted receipt. This tracked Dispatch path does not require project-local
tests or a local commit.

### 7B. Track Development mode

Read `references/development-receipt.md` and
`references/task-control-plane.md` completely.

Create one authoritative task record per child, call `start_task` after
successful delivery, and pass raw child updates to `parse_receipt_text`. The
receipt envelope must appear before optional human details. Never manually
repair concatenated or truncated fields.

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
| Hello/connectivity/simple notification | Lightweight direct message |
| Shared contracts, dependencies, implementation, or receipts | Formal package |
| User language is Chinese | Human-facing task titles and prose are Chinese |
| Child task title | `<parent task name> - <child task name>` |
| User does not ask for tracking | Dispatch mode |
| User asks to wait for non-development results | Dispatch with `awaitResult=true` |
| User explicitly asks to distribute | Deliver after route resolution; no extra confirmation |
| Stable design, no creation request | Offer distribution in one short sentence |
| Default parent display | Objective, targets, responsibilities, dependencies/risks only |
| Full package preview | Only when explicitly requested |
| Same logical project has several responsibilities | Consolidate one task |
| Base path and saved Codex Project match | `VERIFIED_CODEX_PROJECT` |
| Base path exists but saved project is absent | `BASE_PATH_FALLBACK` |
| Route evidence is missing or ambiguous | `BLOCKED` |
| Formal package changes before delivery | Regenerate package and checksums |
| Dispatch delivered | Stop managing results |
| Tracked Dispatch delivered | Start parent records, wait, parse envelopes, and project results |
| Development completed normally | Tests pass and local commit exists |

## Common Failure Modes

| Failure | Correction |
|---|---|
| Building a formal package for a hello test | Use one short direct message per target |
| Copying English template prose into a Chinese task | Translate human-facing headings and content |
| Filling output with template instructions or unused sections | Remove them before delivery |
| Pasting child Markdown and checksums into the parent by default | Send them to the child; show only a compact parent summary |
| Asking for confirmation after an explicit distribute command | Treat the command as authorization and deliver |
| Starting a child with `TASK_PACKAGE_BEGIN` | Put the readable parent-child title first |
| Summarizing a formal design until it is no longer executable | Generate the three concise complete documents |
| Matching a Codex Project by label | Corroborate normalized Base Graph and Codex paths |
| Letting Codex create a surprise worktree | Use local current checkout unless explicitly requested |
| Asking per-child confirmation questions | Use the user's distribute instruction as batch authorization |
| Treating every task as development | Preserve discussion/design/test/review/deployment kinds |
| Waiting in Dispatch mode | Stop after confirmed delivery |
| Treating tracked read-only work as Development | Use Dispatch with `awaitResult=true`; require no commit or tests |
| Parsing YAML-like receipt prose manually | Require the receipt-first JSON envelope and use `parse_receipt_text` |
| Claiming Development done without evidence | Validate project-local tests and local commit receipt |
| Testing the entire distributed system | No cross-project integration tests by default |

## Red Flags

Stop and correct the workflow when:

- a lightweight task is producing package files, manifests, or checksums;
- a child initial prompt starts with a protocol marker or opaque identifier;
- human-facing content does not match the user's language;
- a generated document contains template instructions, unused headings, or an
  exhaustive list of unrelated task kinds;
- a child package depends on reading the parent chat or repository to understand
  its core contract;
- a route is chosen from a project label without path corroboration;
- `create_thread` is about to run without an explicit user request to create or
  distribute tasks;
- a worktree, branch operation, or push is proposed without an explicit request;
- a discussion task contains implementation instructions;
- a confirmation is being requested after the user already explicitly authorized
  the same targets and task;
- Development is declared complete with missing commits, failed tests, or an
  unaccepted `NO_CHANGE_REQUIRED`.
- a tracked child puts prose before the receipt envelope or omits the exact
  receipt markers.
