# Lossless Task-package Protocol

The prepared package is authoritative. Delivery transports its exact content; it
does not summarize or reinterpret the design.

## Human-readable Task Header

Every child initial prompt starts with:

```markdown
# {{parent_task_name}} - {{child_task_name}}

> {{one_sentence_purpose}}
```

Use the user's language and meaningful names rather than IDs. This header helps
Codex present a readable child task title. It is outside the checksummed package
documents.

Derive the header from the same objective and owned scope as the package. Before
delivery, compare the header to the project task specification; a semantic mismatch blocks delivery.

`TASK_PACKAGE_BEGIN` comes after this header. Never use a protocol marker,
dispatch ID, checksum, UUID, or project ID as the first line.

## Lightweight Direct Message

Hello/connectivity tests, acknowledgements, simple notifications, and other
short tasks without shared contracts, dependencies, repository changes, or
tracked receipts do not use this package protocol.

Deliver the complete prepared human-readable message as the initial task prompt:

```markdown
# {{parent_task_name}} - {{child_task_name}}

## <goal>
...

## <what to do>
...

## <do not do>
...

## <completion>
...
```

Do not create package files, a manifest, document checksums, chunk messages, or
`TASK_PACKAGE_*` markers for lightweight delivery. The task message should
normally remain under 30 lines.

## Canonical Form

Before delivery, canonicalize every generated Markdown document to:

- UTF-8 without BOM;
- LF line endings;
- stable filenames and document order;
- no whitespace rewriting after the manifest is built.

Human-facing headings and prose follow the user's language. Protocol markers,
filenames, identifiers, paths, and checksums remain exact. Generated documents
must not contain template guidance, unused sections, or repeated
`Not applicable` filler.

Calculate an uppercase SHA-256 for every canonical document and the deterministic
bundle. Use `scripts/task_package.py` to build and verify the manifest.

## Parent Visibility Boundary

The lossless package is child-task transport, not default parent-task display.
Send the full Markdown documents and checksum envelope to the child.

In the parent task, show only the objective, target responsibilities, dependency
order, material risks, and delivery result. Do not paste documents, checksums,
project IDs, host IDs, absolute paths, branches, or chunk details unless the user
explicitly requests a full package or audit preview.

## Small Package Envelope

When the complete package fits in one task message:

```text
# {{parent_task_name}} - {{child_task_name}}

> {{one_sentence_purpose}}

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
# {{parent_task_name}} - {{child_task_name}}

> {{one_sentence_purpose}}

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
- Treat the delivered package as authoritative.
- Use parent file paths only as secondary evidence.

## Sender Rules

- Freeze bytes and checksums before task creation.
- Send exactly the prepared bytes.
- Verify the initial prompt starts with the human-readable parent-child title
  and that `TASK_PACKAGE_BEGIN` appears below it.
- Verify the title and one-sentence purpose match the packaged objective and
  owned scope.
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
