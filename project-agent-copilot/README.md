# Project Agent Copilot

Role container for project engineering skill collections.

English | [简体中文](./README.zh.md)

## What Is This?

Project Agent Copilot is the project engineering role container in Role Copilot Skills.

It is designed for teams that already have source code, project documents, development conventions, and recurring engineering workflows. This directory is not itself one monolithic skill. It groups project-facing skill collections such as development, PRD, UI, testing, release, and future domains.

The first implemented collection is `project-develop-copilot`.

## Current Collections

| Collection | Contains |
|---|---|
| [`project-develop-copilot`](./project-develop-copilot/README.md) | `project-init`, `project-ingest`, `project-develop`, `project-fix`, `project-finish`, `project-review` |

Planned collections:

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

## Install

Install one project development skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
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
    project-develop/
    project-fix/
    project-finish/
    project-review/
```

## Role Boundary

Keep this directory as a role container. Put installable workflow skills inside a collection directory. Shared references for a collection should stay with that collection instead of being shared globally by the whole role container.
