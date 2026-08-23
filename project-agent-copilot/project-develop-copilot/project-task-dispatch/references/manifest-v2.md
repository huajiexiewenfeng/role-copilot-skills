# Manifest v2 and Management Directory

The public structural contract is
`schemas/dispatch-manifest-v2.schema.json`. The dependency DAG, reverse
references, single-writer-per-Project rule, binding guards, Approval Gate, and
revision constraints are additionally enforced by `scripts/manifest_v2.py`.

## Directory

```text
dispatches/<dispatchId>/
├─ manifest.json                 durable PDC authority
├─ runtime-cache.json            rebuildable native observations/cursors
├─ manager.md                    generated status table
├─ notes.md                      only human-editable control document
├─ project-sessions/*/session.md generated summaries
├─ work-items/*.md               generated acceptance/review summaries
├─ findings/*.md                 generated finding summaries
└─ views/
   ├─ live/
   │  ├─ index.html              static last-known-good shell
   │  ├─ snapshot.json           current escaped projection
   │  ├─ assets/*                local-only JS/CSS
   │  ├─ server-state.json       replaceable process state, never tokens
   │  └─ client-state.json       replaceable ready/revision acknowledgement
   ├─ status-rNNNN.svg/.png      immutable revision views
   └─ current-status.svg/.png    latest copies
```

The formal transport package uses `task-package-manifest.json`, never this
directory's `manifest.json`.

## Persistence

Write a same-directory temporary file, flush/fsync, then `os.replace`. Supply the
expected previous revision when overwriting to prevent two Manager turns from
silently losing updates. UTF-8 without BOM and LF are required.

`runtime-cache.json` has schema version `2.0-cache`, Dispatch ID, update time,
and per-Project-Session native snapshot including thread/host, afterCursor,
native status, latest turn/assistant phase, summary, and observation time. It may
be deleted and reconstructed.

## Lifecycle policy

`policies.archive` defaults to `explicit-only`. Closing a real Dispatch unpins
bound Sessions but does not archive them. `canary-dispatch-close` is permitted
only for disposable Canary/Smoke runs. A user-requested cleanup is an explicit
runtime action; it is not inferred from `status=CLOSED`.

## Views

`scripts/status_view.py` creates deterministic Markdown, optionally creates SVG,
and delegates the
default `views/live/` HTML projection to `scripts/dashboard_view.py`. The HTML projection is
regenerated atomically from the same manifest revision and remains readable as
a static last-known-good snapshot.

`scripts/dashboard_runtime.py` owns only loopback presentation state. It never
writes the manifest. `server-state.json` and `client-state.json` are replaceable
observations; the private control token is not included in either JSON file.

SVG/PNG are opt-in exports. `render_status_png.mjs` accepts SVG path, PNG path,
and the discovered bundled `sharp` module path. Never hard-code a user
cache/runtime path. Universal fallback is HTML static snapshot, then Markdown;
rendering does not control business state.
