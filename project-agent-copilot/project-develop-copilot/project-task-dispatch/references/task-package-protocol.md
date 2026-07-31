# Lossless Task-package Protocol

The approved package is authoritative. Delivery transports its exact content; it
does not summarize or reinterpret the design.

## Canonical Form

Before preview, canonicalize every generated Markdown document to:

- UTF-8 without BOM;
- LF line endings;
- stable filenames and document order;
- no whitespace rewriting after approval.

Calculate an uppercase SHA-256 for every canonical document and the deterministic
bundle. Use `scripts/task_package.py` to build and verify the manifest.

## Small Package Envelope

When the complete package fits in one task message:

```text
TASK_PACKAGE_BEGIN
dispatchId: ...
subtaskId: ...
bundleChecksum: ...

DOCUMENT_BEGIN 00-shared-baseline.md
...
DOCUMENT_END checksum=...

DOCUMENT_BEGIN 01-project-task.md
...
DOCUMENT_END checksum=...

DOCUMENT_BEGIN 02-handoff.md
...
DOCUMENT_END checksum=...

TASK_PACKAGE_END bundleChecksum=...
```

## Chunked Package Envelope

For a larger package, send an initial envelope that says not to act, followed by
ordered document chunks:

```text
TASK_PACKAGE_BEGIN
dispatchId: ...
subtaskId: ...
documentCount: 3
chunkCount: ...
bundleChecksum: ...

DOCUMENT_BEGIN 00-shared-baseline.md
CHUNK 1/N
...
CHUNK N/N
DOCUMENT_END checksum=...

DOCUMENT_BEGIN 01-project-task.md
CHUNK 1/N
...
DOCUMENT_END checksum=...

DOCUMENT_BEGIN 02-handoff.md
CHUNK 1/N
...
DOCUMENT_END checksum=...

TASK_PACKAGE_END bundleChecksum=...
```

Chunking is transport-only. Never omit, summarize, reorder, normalize, or rewrite
chunk text.

## Receiver Rules

- Do not begin execution before `TASK_PACKAGE_END`.
- Verify chunk indexes are exactly `1..N` in delivery order.
- Reject missing, duplicate, reordered, or inconsistent chunks.
- Verify each document checksum and `bundleChecksum`.
- Treat the confirmed package as authoritative.
- Use parent file paths only as secondary evidence.

## Sender Rules

- Freeze bytes and checksums when the user approves the batch preview.
- Send exactly the approved bytes.
- Delivery is complete only when every required message succeeds.
- Do not treat successful delivery as a Development receipt.
- Do not create real Codex tasks during automated skill evaluation.

If delivery fails after a partial send, send:

```text
TASK_PACKAGE_ABORT
dispatchId: ...
subtaskId: ...
reason: ...
```

Mark the route `DELIVERY_FAILED`; do not ask the child to execute a partial
package.
