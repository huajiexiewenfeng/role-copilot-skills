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

## Views

`scripts/status_view.py` creates deterministic Markdown and SVG from one status
snapshot. `render_status_png.mjs` accepts SVG path, PNG path, and the discovered
bundled `sharp` module path. Never hard-code a user cache/runtime path. Fallback
is SVG + Markdown, then Markdown only; rendering does not control business state.
