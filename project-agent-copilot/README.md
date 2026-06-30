# Project Agent Copilot

Role container for project engineering skill collections.

English | [简体中文](./README.zh.md)

## What Is This?

Project Agent Copilot is the project engineering role container in Role Copilot Skills.

It is designed for teams that already have source code, project documents, development conventions, and recurring engineering workflows. This directory is not itself one monolithic skill. It groups project-facing skill collections such as development, PRD, UI, testing, release, and future domains.

The first implemented collection is `project-develop-copilot`.

Project collections should follow two principles: bridge mature top-level skills and tools instead of rebuilding them, and internalize project LLM Wiki as a small project context layer rather than depending on a separate knowledge-base workflow.

For `project-develop-copilot`, use `project-develop-copilot/references/north-star.md` as the alignment document before completing or changing the skill collection.

## Current Collections

| Collection | Contains |
|---|---|
| [`project-develop-copilot`](./project-develop-copilot/README.md) | `project-develop-copilot`, `project-init`, `project-ingest`, `project-query`, `project-develop`, `project-fix`, `project-finish`, `project-review`, `project-maintain`, `llm-wiki-doctor`, `project-base-init`, `project-graph-candidates-scan`, `project-graph-auto-edge`, `project-graph-human-edge` |

Planned collections:

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

## Install

Install the project development router skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot
```

For local development from the repository root:

```bash
npx skills add .
```

## Typical Workflow

```text
project-agent-copilot/
  project-develop-copilot/
    project-init/
    project-ingest/
    project-query/
    project-develop/
    project-fix/
    project-finish/
    project-review/
    project-maintain/
    llm-wiki-doctor/
    project-base-init/
    project-graph-candidates-scan/
    project-graph-auto-edge/
    project-graph-human-edge/
```

## Project Graph Maintenance

Use the Project Graph skills when cross-project relationships need explicit maintenance instead of ordinary read-only lookup. `project-graph-candidates-scan` updates only candidate findings, `project-graph-auto-edge` creates human-reviewable proposals through Base Graph/source evidence, and `project-graph-human-edge` is the only normal flow that writes confirmed edges and cross-ref pins. The collection also includes `llm-wiki-doctor`, `scripts/llm_wiki_doctor.py`, and scaffold templates that `project-init` installs into consuming projects so repositories can enforce wiki/graph hygiene at local commit, project finish, and CI/PR boundaries.

## Read-Only Project Questions

Use `project-query` when the user asks what exists in a project, how a module or API is called, what prior requirements or design notes say, or which `.llm-wiki` evidence relates to a topic. It should recover project wiki context first, then verify key facts against source code when needed.

Example:

```text
这个项目里面，大疆 API 适配，直播相关的内容有哪些？如何通过 API 调用
```

That kind of question should stay read-only and route to `project-query`, not directly to implementation, debugging, or review.

## Role Boundary

Keep this directory as a role container. Put installable workflow skills inside a collection directory. Shared references for a collection should stay with that collection instead of being shared globally by the whole role container.
