# Manager Runtime and Native Task Adapter

## Native calls

| PDC operation | Codex capability |
|---|---|
| resolve exact destination | `list_projects` |
| create peer Project Session | `create_thread(project + local + title)` |
| compact observation | `wait_threads` with `hostId + afterCursor`, 1–8 targets |
| deep inspection | `read_thread` at completion/attention/error/Review boundary |
| next batch or findings | `send_message_to_thread` to original thread |
| recovery | `list_threads`, `list_archived_threads`, then ID-based reconciliation |
| lifecycle | `set_thread_pinned`, `set_thread_archived` |
| user-requested navigation | `navigate_to_codex_page` |
| in-window code review | `open_in_codex` branch/unstaged/staged/last-turn review |
| explicit continued monitoring | `automation_update` heartbeat on Manager thread |

Use `scripts/native_thread_adapter.py` for deterministic request/decision
planning. Python does not call Codex; the Manager Agent executes native tools.

## Control loop

1. Load/validate manifest and load or rebuild runtime cache.
2. Reconcile exact saved Projects, durable bindings, and Git baselines.
3. Apply user intent, recompute dependencies, and group READY work by Project Session.
4. Create an UNBOUND Worker or send one batch to a BOUND native-idle Worker.
5. Wait in groups of at most eight for 30–60 seconds; store cursors.
6. Deep-read completed/attention/error Sessions; classify delivery/blocker.
7. Review SUBMITTED items, send findings or approve, unlock dependencies, repeat.
8. Regenerate view only on meaningful business/native changes.
9. After all required approvals, run the final cross-repository check.

## HTML dashboard runtime

After Revision 1 exists, run:

```text
python scripts/dashboard_runtime.py start --dispatch-root <dispatch-directory>
```

`start` creates or recovers the PDC-owned loopback server and opens the Windows
default external browser. If it is already running, `start` requests a fresh
one-time bootstrap and reopens it. The explicit equivalent is:

```text
python scripts/dashboard_runtime.py reopen --dispatch-root <dispatch-directory>
```

The runtime listens only on `127.0.0.1`, exchanges a one-time query token for an
HttpOnly SameSite cookie, removes the token by redirect, validates Host and
Origin, applies a local-only CSP, and escapes all projected task text. Tokens
must never appear in the manifest, manager Markdown, logs, or final response.

The watcher broadcasts meaningful snapshot changes by WebSocket. The client
fetches `snapshot.json`, updates the DOM without raw `innerHTML`, and sends a
`revision-applied` acknowledgement. Polling and the generated static HTML are
the fallback. `server-state.json` and `client-state.json` are replaceable
observations; neither is PDC business authority. A browser/server failure does
not stop Manager coordination.

The HTML is read-only. All pause, rework, approval, close, and archive commands
still occur in the Manager conversation through native Codex capabilities.

Ordinary commentary does not require JSON. An unchanged timeout is cached but is
not a new status revision. Native attention/permission stays with the user.

## Create and pending

Ready creation saves `threadId + hostId`. Pending creation saves only
`clientThreadId`; it is not eligible for wait/read/send and must not be recreated
automatically. The current high-level tools have no general pending-status or
hard turn-interrupt call.

## Recovery

Match only by `threadId`; title is not identity. BOUND but absent tasks become
`MISSING`. Rebuild cache with `read_thread` and `wait_threads(timeoutMs=0)`.
Never repeat a reducer event for an already-consumed cursor/final.

## Lifecycle and monitoring

Do not pin, unpin, or archive Project Sessions automatically. Creation,
approval, and Dispatch close leave native pin/archive state untouched. Execute
`set_thread_pinned` or `set_thread_archived` only after an explicit user request
for that action. Archive is not cancel, and CLOSED is independent from native
pin/archive state. Use heartbeat only after explicit user request for continued
monitoring, manage it with `automation_update`, and stop it at terminal state.

`send_message_to_thread` controls future work and requests rework but is not a
guaranteed mid-turn interrupt. State this limitation accurately.

Native request details matter: `send_message_to_thread` uses the `prompt` field;
`set_thread_pinned` accepts `threadId + pinned` without `hostId`, while
`set_thread_archived` may include `hostId`. `handoff_thread` can interrupt while
moving a task between checkout/worktree, but that migration side effect makes it
unsuitable as a general cancel primitive.

## Native capabilities intentionally not used as the dispatch backend

- `fork_thread` copies completed history into a same-directory/worktree child;
  it does not bind a peer Session to another saved Project, so it is not the
  cross-Project creation path.
- `handoff_thread` and `get_handoff_status` migrate another task and associated
  Git state. Use them only for an explicit migration request, never ordinary
  scheduling, rework, or cancellation.
- `share_thread` creates an immutable share link and is presentation-only; use
  it only when the user asks to share.
- `set_thread_title` may repair a display title, but identity remains threadId.
