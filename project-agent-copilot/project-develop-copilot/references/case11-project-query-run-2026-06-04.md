# Case 11 Project Query Dry Run - 2026-06-04

## User Prompt

> 基于这个项目的 llm wiki，帮我找一下支付回调相关的需求、开发文档和之前的讨论上下文。先不要开发，我们先讨论。

## Expected Route

- Root router selects `read-only-query`.
- Root router delegates to `project-query`.
- No Change Brief, Bug Brief, implementation plan, working-context mutation, dashboard mutation, or code edit is created by default.

## Context Lookup Order

1. Locate project root and `.llm-wiki/` root; treat `.llm-wiki/index.md` as optional.
2. Read available wiki entrypoints such as `.llm-wiki/README.md`, `.llm-wiki/index.md` when present, `.llm-wiki/modules/*`, and `.llm-wiki/ingest/index.md` to identify relevant domains and source proxies.
3. Search requirement, bug, source, artifact, and working-context pages for the user's topic terms.
4. Assemble a Project Context Pack with exact evidence pages and confidence.
5. Return possible next routes only after the read-only answer: continue discussion, ingest missing docs, create Change Brief, create Bug Brief, review scope, or run Lifecycle Quality Review.

## Expected Output Shape

- Answer
- Project Context Pack
- Evidence
- Inference
- Possible Next Routes

## Pass Criteria

- The user receives enough linked context to discuss the project without starting development.
- The response clearly separates evidence from inference.
- The response states when project wiki evidence is missing or stale.
- The lifecycle can naturally upgrade later to `project-develop`, `project-fix`, `project-ingest`, `project-review`, `skill-evaluator`, or Dolores self-review.

## Result

Design-level dry run passes. Real-project validation is still required after installing the updated skills into Codex and running the prompt against an actual `.llm-wiki` project.
