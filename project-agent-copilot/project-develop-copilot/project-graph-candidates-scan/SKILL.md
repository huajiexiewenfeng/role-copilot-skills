---
name: project-graph-candidates-scan
description: Use when scanning the current project-local .llm-wiki or source tree for potential Project Graph relationship candidates, including Chinese prompts like 扫描 candidates, project-graph candidates scan, 自动扫描候选关系, or 发现缺失跨项目关系.
---

# Project Graph Candidates Scan

## Purpose

Scan the current project for potential Project Graph relationship candidates and maintain the candidate queue. This skill writes candidate facts only. It must not write confirmed edges, proposals, cross-ref pins, Base Graph files, or remote project files.

Use it when the user explicitly asks to scan `project-graph/candidates.md`, discover missing upstream/downstream relationships, refresh candidate findings, or run a Project Graph candidate scanner.

## Required Reads

Read only as much as needed for the requested scan scope:

- `../references/project-graph.md`
- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`, when present
- `.llm-wiki/project-graph/scan-state.local.json`, when present
- `.llm-wiki/log.md`, when present
- local source/config/wiki files that can reveal relationship signals
- `../references/cross-project-refs.md` only when candidate signals name another project or require registry/Base Graph interpretation

## Allowed Writes

Current project only:

- `.llm-wiki/project-graph/candidates.md`
- `.llm-wiki/project-graph/scan-report.md`
- `.llm-wiki/project-graph/scan-state.local.json`
- `.llm-wiki/log.md`

## Forbidden Writes

- `.llm-wiki/project-graph/edges.md`
- `.llm-wiki/project-graph/proposals.md`
- `.llm-wiki/cross-refs/index.md`
- remote project wiki, source, config, Briefs, registry, or graph files
- Base Graph tracked files

If the scan finds enough evidence for an edge, stop at a `pending` candidate and tell the user to run `project-graph-auto-edge` for proposal generation.

## Process

1. Resolve the current project root and confirm `.llm-wiki` exists.
2. Read `project-graph.md` for current schemas, status values, fingerprint rules, pending timeout, and write boundaries.
3. Read existing `candidates.md` and build a fingerprint set.
4. Collect local relationship signals from:
   - Feign clients and HTTP client interfaces
   - hard-coded or configured HTTP URLs
   - MQ topics, consumer groups, producer names, and queue bindings
   - RPC client names, SDK package names, callback URLs, and webhook handlers
   - shared DB/schema/table names when they imply cross-service ownership
   - config keys naming another service, endpoint, topic, or project id
   - existing wiki mentions of upstream/downstream systems
5. Normalize `candidate_fingerprint` with stable lowercase tokens: `type:current_project:local_signal:remote_hint`. Do not include absolute paths, line numbers, machine names, or local drive letters.
6. Keep only candidates where one side is the current project. Put external-to-external findings in `scan-report.md`, not current `candidates.md`.
7. Add new rows with `status=pending`, `edge_id=` empty, and `source=scan`.
8. Preserve existing manual candidates. Never auto-expire `source=manual` candidates.
9. Archive stale `pending` scan-origin candidates according to `default_candidate_pending_days` in `project-graph.md` by moving them to `scan-report.md` `Archived Candidates`; do not silently delete them.
10. Append a concise `.llm-wiki/log.md` entry unless the user explicitly requested dry-run.

## Candidate Row Rules

- `remote_project` may stay `unknown` when the scanner has only a hint.
- `relation` must explain the suspected dependency in human-readable terms.
- `evidence` should cite repo-relative files, config keys, class names, method names, endpoints, or topics.
- `first_seen` is preserved for existing fingerprints.
- `last_seen` is updated when a candidate is observed again.
- `edge_id` remains empty until `project-graph-human-edge` promotes the candidate.

Example row shape:

```markdown
| cand-YYYYMMDD-001 | http:smart-go-web:streamfeignapi:smarthub-mediakit | smarthub-mediakit | smart-go-web calls media stream change API | smart-go-device-mapping/.../ZLMediakitStreamSendServiceImpl.java#streamChange | pending | scan | 2026-06-23 | 2026-06-23 |  |
```

## Output

Report:

- scan scope and files inspected
- new candidates added
- duplicate fingerprints skipped
- stale scan candidates archived
- external-to-external findings kept out of current candidates
- validation result for candidate column counts, fingerprint uniqueness, statuses, sources, and promoted `edge_id` resolution
- next recommended command, usually `project-graph-auto-edge <candidate_id>` for candidates ready for proposal