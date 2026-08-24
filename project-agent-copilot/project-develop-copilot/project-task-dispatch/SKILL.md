---
name: project-task-dispatch
description: Use when the user asks PDC to distribute, monitor, review, or manage work across saved Codex Projects that belong to one Base Graph reality project. Uses peer Codex Project Sessions, not Agent Team Subagents.
---

# Project Task Dispatch 2.0

## Overview

The current Base Graph task is the **Manager Session**. It distributes work to
independent, user-visible **Project Worker Sessions** bound to the saved Codex
Project for each repository. Optional **Reviewer Sessions** provide independent
read-only review. These are peer Codex tasks connected by a PDC Dispatch; they
are not Agent Team Subagents and do not inherit the Manager conversation.

The user normally interacts only with the Manager. The Manager owns routing,
dependency unlock, native task monitoring, findings, repository verification,
approval, the status view, and lifecycle cleanup.

## When to Use

Use this skill when a user asks to send or split work across PDC Projects,
repositories, tasks, chats, or Sessions, including:

- a lightweight hello, notification, or connectivity check;
- an awaited cross-project query or research task;
- a confirmed cross-project design or contract;
- managed implementation, tests, review, and local commits across repositories;
- recovery, monitoring, rework, or closure of an existing PDC Dispatch.

Do not use it for work contained in one Project, ordinary PDC development in the
current checkout, generic non-project research, or Agent Team delegation.

## Mandatory References

For every run, read [routing.md](references/routing.md). For awaited Dispatch or
Managed Development, also read these completely:

- [task-control-plane.md](references/task-control-plane.md)
- [manager-runtime.md](references/manager-runtime.md)
- [manifest-v2.md](references/manifest-v2.md)

For formal packages read [task-package-protocol.md](references/task-package-protocol.md).
For Managed Development read [development-receipt.md](references/development-receipt.md),
whose retained filename now describes delivery and Review rather than a progress receipt.
For the default live status display read [dashboard-runtime.md](references/dashboard-runtime.md).

## 1. Select Mode and Complexity

Choose the mode from user intent; do not force an A/B question when intent is clear.

| Mode | Meaning |
|---|---|
| Dispatch | Deliver and stop after native task creation succeeds. |
| Awaited Dispatch | Deliver read-only/non-development work, then wait/read and aggregate results. |
| Managed Development | Manager tracks implementation through Review and APPROVED. |

Use a lightweight readable prompt for hello/notification/simple isolated work.
Use the three-document formal package only for shared contracts, dependencies,
frozen responsibilities, or substantial development. A lightweight Dispatch
does not need a management directory. Awaited Dispatch and Managed Development
use manifest v2 when coordination state must survive the current turn.

The user command to distribute/create/send is authorization to create the
resolved native tasks. Do not add another confirmation gate. In dry-runs, evals,
or previews, never create a real Codex task.

## 2. Resolve Exact Saved Projects

Use Base Graph repository identity/root plus `list_projects` projectId/path/host.
Normalize paths and require exactly one corroborated saved Project. Never route
by label alone.

Writable work requires `VERIFIED_CODEX_PROJECT`. If the repository path exists
but no exact saved Project exists, record a `PROJECT_ROUTE` blocker and do not
create a path-fallback Worker in the Base Graph Project. `BASE_PATH_FALLBACK` is
allowed only for an explicitly accepted `READ_ONLY` task and must carry
`readOnlyFallback=true`; it cannot later become writable.

For every repository record its own `expectedBranch`, `baselineHead`, and
`dirtyBoundary`. Never assume all repositories use the same branch name. Do not
create/switch branches or worktrees and do not merge, rebase, reset, push, or
clean pre-existing changes unless separately authorized.

## 3. Build the PDC Control Plane

For Managed Development, create:

```text
<PDC_RUNTIME_ROOT>/<realityProjectId>/dispatches/<dispatchId>/
├─ manifest.json
├─ runtime-cache.json
├─ manager.md
├─ notes.md
├─ project-sessions/<projectSessionKey>/session.md
├─ work-items/<taskId>.md
├─ findings/<findingId>.md
└─ views/
   ├─ live/{index.html,snapshot.json,assets/,server-state.json}
   └─ {current-status,status-rNNNN}.{svg,png}
```

The Manager is the only writer. `manifest.json` owns PDC business state;
Codex owns native task/turn state; Git owns code facts; `runtime-cache.json`
owns only replaceable cursor/snapshot observations. The directory is not a
message queue. Human edits are limited to `notes.md`.

Use one write Project Worker Session per saved Project per Dispatch. Several
work items in that Project map to the same `projectSessionKey` and run as serial
batches. Independent Projects may run in parallel. Downstream work unlocks only
after required upstream work is `APPROVED`, not merely after Worker final.

## 4. Create and Bind Project Sessions

Discover and use the native tools `list_projects`, `create_thread`,
`wait_threads`, `read_thread`, `send_message_to_thread`, `set_thread_title`,
`set_thread_pinned`, `set_thread_archived`, `list_threads`, and
`list_archived_threads`. Use `navigate_to_codex_page` only when the user asks to
open a task.

Create each Worker with this exact route shape:

```text
target.type = project
target.projectId = <verified projectId>
target.environment.type = local
title = [PDC][<dispatchId>][<repo>][Worker|Reviewer] <short goal>
prompt = readable complete assignment
```

PDC Managed Development uses the user's established explicit `local` checkout
policy so each repository keeps its own current branch and existing dirty
boundary. If this Skill is used where that direct-checkout authorization has not
been established, obtain it before overriding Codex's normal Git-project
worktree default.

Omit model/thinking unless the user explicitly selected them. Use
[worker-initial-message.md](templates/worker-initial-message.md) for Managed
Development. Tell the Worker to use its local Project PDC context and not to
create a nested Session/Subagent unless authorized.

`create_thread` is asynchronous:

- ready result: save `threadId + hostId`, binding=`BOUND`;
- queued result: save only `clientThreadId`, binding=`CREATE_PENDING`;
- never pass `clientThreadId` to wait/read/send and never repeat create merely
  because pending has no `threadId`;
- after every successful native creation, show the native created-task entry in
  the Manager response.

## 5. Monitor and Communicate

For bound unapproved Sessions, use `wait_threads` in groups of 1–8 with each
target's `hostId` and cached `afterCursor`. Prefer 30–60 second bounded waits in
an active Manager turn. Update runtime cache on snapshots. Do not emit another
Manager panel for an unchanged timeout.

Normal Worker commentary is human-readable and does not need JSON. Deep-read
with `read_thread` at completion, attention, error, or Review boundaries. Leave
native permission/input requests for the user. A Worker final produces a
delivery candidate and can move a work item only to `SUBMITTED`.

Use `send_message_to_thread` for the next batch or Review findings. Rework goes
to the original Worker `threadId`; do not fork or replace it. Sending a message
is not a hard mid-turn interrupt. The current high-level API can stop future
scheduling but cannot guarantee immediate interruption of a running turn.

Use a recurring heartbeat only when the user explicitly requests monitoring
after the Manager turn ends. Create/update it with native `automation_update`,
targeting the Manager thread, and stop it when the Dispatch becomes terminal.

## 6. Review, Rework, and Approval

Managed Development follows this non-bypassable sequence:

```text
Worker final → SUBMITTED → REVIEWING → APPROVED
                                  └→ CHANGES_REQUESTED → same Worker → SUBMITTED
```

The Manager verifies repository root, branch, baseline/final HEAD, dirty-file
boundary, changed files, local commit, actual test results, acceptance IDs,
contract revision, dependency approval, open findings, and cross-repository side
effects. `SUBMITTED → APPROVED` is forbidden. Native idle/final and the word
“completed” are not approval evidence.

Use `open_in_codex` to show branch/unstaged/staged/last-turn Review in the
current Codex window when that makes human verification easier; it is a view,
not the evidence authority.

Use a read-only Reviewer Session for inaccessible repositories, higher-risk
changes, or user-required independent review. Run it after the write Worker is
idle. Findings must include severity, evidence, required change, and a file/line,
contractId, or acceptanceId where applicable. Send findings with
[worker-rework-message.md](templates/worker-rework-message.md).

Normal changes require project-local tests and a local commit; never push.
`NO_CHANGE_REQUIRED` may be submitted without an empty commit but still requires
evidence and explicit Manager approval. Do not run broad cross-project tests by
default; the final cross-repository check validates agreed contracts and declared
integration evidence.

## 7. Status View and Lifecycle

After every meaningful manifest change, increment revision atomically and
regenerate `manager.md`, Session/work-item/finding Markdown, and the static HTML
projection in `views/live/`. Start or recover the PDC-owned loopback runtime
with `scripts/dashboard_runtime.py start --dispatch-root <path>` after Revision
1; it opens the Windows default external browser unless the user selected the
Codex in-window mode. Use `reopen` when the user asks to open the existing board
again. Judge visibility from the client acknowledgement, not process launch.

The dashboard is read-only and fixed to `Manager 1 → Project Sessions N →
Manager final 1`. WebSocket revision notifications update it live; JSON polling
is the reconnect fallback and the generated HTML remains a readable static
snapshot when the server is unavailable. It must show PDC state and native
Codex state separately. A display/runtime failure never blocks dispatch or
Review.

HTML is the default display. Do not generate SVG/PNG on every revision; render
an image only when the user asks for an inline/exported artifact or when HTML
cannot be opened and an in-conversation visual is useful. Markdown remains the
final universal fallback. Use `open_in_codex` only for a user-selected in-window
dashboard or code Review; treat `queued` as not yet visibly opened.

Do not pin or archive created Worker/Reviewer tasks by default. Creation,
approval, and Dispatch close leave their native pin/archive state untouched and
keep real development and read-only Sessions visible. Call `set_thread_pinned`
or `set_thread_archived` only when the user explicitly asks for that specific
lifecycle action. Archive is lifecycle cleanup, not cancellation, and `CLOSED`
never implies pinned, unpinned, or archived.

## 8. Recovery and Idempotency

On resume, load and validate manifest revision, then reconcile saved Projects,
Git baselines, and task bindings. Use `list_threads` and
`list_archived_threads`, matching only durable `threadId`; title is display
metadata and must not auto-bind a task. Rebuild deleted runtime cache using
`read_thread` plus `wait_threads(timeoutMs=0)`.

Do not recreate `CREATE_PENDING` Sessions automatically. Mark a missing bound
thread as `MISSING`, surface it, and require an explicit recovery decision.
Persist cursors so a repeated final cannot repeat a reducer transition.

## 9. Formal Package Compatibility

Keep the existing UTF-8/LF/checksum/chunk protocol. The transport manifest is
named `task-package-manifest.json`; the Dispatch control file is `manifest.json`.
The initial prompt must start with a readable parent-child title, never a
protocol marker. A formal package carries shared contracts and that Project's
responsibility, while local code knowledge comes from the target Project PDC.

New v2 Workers never receive the 1.x receipt-first progress contract. The
compatibility parser in `scripts/legacy_receipt.py` is only for restoring an
already-active 1.x run, and legacy `COMPLETED` maps to a v2 delivery candidate,
never directly to `APPROVED`.

## Completion

Dispatch completes after delivery. Awaited Dispatch completes after requested
results are returned. Managed Development completes only when every required
work item is `APPROVED`, the final cross-repository check passes, generated views
match the manifest revision, and lifecycle actions requested by policy succeed.

Report the outcome, approved/blocked work, Review findings, verification evidence,
and current in-window status view. Do not claim hard interruption, approval, or
cross-project completion without direct evidence.
