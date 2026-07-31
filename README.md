# Role Copilot Skills

Role-based Agent Copilot skills for enterprise team productivity.

English | [简体中文](./README.zh.md)

## What Is This?

Role Copilot Skills is a collection of domain-specific Agent Copilot skills.

The repository is organized around practical enterprise roles instead of isolated prompts. Each top-level directory is an Agent Copilot role container. A role container may hold one or more skill collections, and installable Codex skills live inside those collections.

```text
role copilot
-> role-specific skills
-> project-local rules and tools
-> confirmed execution or structured output
```

The goal is to turn recurring team workflows into reusable AI-assisted capabilities while keeping the real business rules, scripts, and safety boundaries visible.

## Why It Exists

Enterprise teams already have many stable workflows:

- HR teams screen resumes, write candidate reports, and prepare interviews.
- DevOps teams package services, diagnose CI failures, and prepare release notes.
- Engineering teams initialize project context, implement features, and review code.

General-purpose AI can help, but the agent needs role context:

- What is this role responsible for?
- Which information should be collected?
- Which local docs or scripts are the source of truth?
- Which actions require confirmation?
- What should the final report look like?

Role Copilot Skills captures those workflows as installable skills.

The project development collection has a special role: it bridges existing top-level skills and tools into a project lifecycle while internalizing a lightweight project LLM Wiki for context memory.

## Repository Structure

```text
role-copilot-skills/
  devops-agent-copilot/
    devops-package-copilot/
  project-agent-copilot/
    project-develop-copilot/
      project-init/
      project-ingest/
      project-query/
      project-task-dispatch/
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
  hr-agent-copilot/
    hr-resume-screening-copilot/
    hr-candidate-detail-report-copilot/
    hr-interview-question-generator-copilot/
  visual-agent-copilot/
    technical-visual-companion/
```

Current repository contents:

```text
devops-agent-copilot/
  devops-package-copilot/
project-agent-copilot/
  project-develop-copilot/
    project-init/
    project-ingest/
    project-task-dispatch/
    project-develop/
    project-fix/
    project-finish/
    project-review/
hr-agent-copilot/
  hr-resume-screening-copilot/
  hr-candidate-detail-report-copilot/
  hr-interview-question-generator-copilot/
visual-agent-copilot/
  technical-visual-companion/
```

Planned role groups and skills may be added incrementally.

## Available Skills

### DevOps Agent Copilot

[Role README](./devops-agent-copilot/README.md) | [简体中文](./devops-agent-copilot/README.zh.md)

| Skill | Use When |
|---|---|
| `devops-package-copilot` | Package local projects from natural language by reading project-local `docs/docker-build-*.md` rules, reusing session packaging context, generating the exact command, and calling existing build scripts. |

Planned DevOps skills:

- `devops-ci-diagnose-copilot`
- `devops-release-copilot`

### Project Agent Copilot

[Role README](./project-agent-copilot/README.md) | [简体中文](./project-agent-copilot/README.zh.md)

| Skill | Use When |
|---|---|
| `project-develop-copilot` | Route natural project-development requests into the right project lifecycle skill. |
| `project-init` | Initialize or refresh project-local LLM Wiki, discover modules, and migrate legacy `docs/ai-coding`. |
| `project-ingest` | Ingest PRDs, links, Markdown, PDF, Word, logs, meeting notes, or temporary source material into the project LLM Wiki. |
| `project-query` | Answer read-only project questions from `.llm-wiki`, Project Graph pins/edges/candidates, and source evidence when needed. |
| `project-task-dispatch` | Preview and distribute complete project-specific task packages for confirmed multi-project work, using Dispatch mode by default or Development mode for tracked development, tests, and local commits. |
| `project-develop` | Develop a requirement or feature with scoped project context and requirement summaries. |
| `project-fix` | Diagnose and fix project bugs with scoped context, evidence, verification, and bug summaries. |
| `project-finish` | Finish verified work by syncing actual changes back to LLM Wiki and preparing handoff. |
| `project-review` | Review project changes for code risk, test gaps, scope drift, stale context, and wiki sync. |
| `project-maintain` | Audit and repair `.llm-wiki` structure, Project Graph consistency, stale candidates, cross-ref pins, registries, visibility drift, and bundled doctor findings. |
| `llm-wiki-doctor` | Run or explain LLM Wiki Doctor validate/score/report output, including Chinese maturity reports, empty wiki skeleton detection, and Project Graph validator findings. |
| `project-base-init` | Initialize or refresh an independent Base Graph repository for multi-project catalog and overview coordination. |
| `project-graph-candidates-scan` | Scan the current project for Project Graph relationship candidates without writing edges or cross-ref pins. |
| `project-graph-auto-edge` | Resolve candidates through Base Graph and source evidence into human-reviewable edge proposals. |
| `project-graph-human-edge` | Accept, reject, or manually register Project Graph edges and maintain `cross-refs/index.md` pins. |

Project Graph maintenance is split into three explicit skills so agents can call the intended step visibly: scan candidates, generate proposals, then let a human confirm or manually enter edges. `cross-refs/index.md` is maintained only when `project-graph-human-edge` writes a confirmed edge.

Installing `project-develop-copilot` now also ships the `scripts/llm_wiki_doctor.py` validator, tests, the `llm-wiki-doctor` skill, and consuming-project scaffold templates. `project-init` installs the vendored doctor, pre-commit config, and CI workflow into each business project so `validate` can catch structural ERROR findings before project finish or PR merge. Human diagnosis can use `report` and `score`; see `project-agent-copilot/project-develop-copilot/scripts/README.llm-wiki-doctor.md`.

Planned Project skills:

- `project-prd-copilot`
- `project-ui-copilot`
- `project-test-copilot`
- `project-release-copilot`

### HR Agent Copilot

[Role README](./hr-agent-copilot/README.md) | [简体中文](./hr-agent-copilot/README.zh.md)

| Skill | Use When |
|---|---|
| `hr-resume-screening-copilot` | First-stage resume screening against a JD with candidate ranking and 100-point scoring. |
| `hr-candidate-detail-report-copilot` | Candidate detail reports with score reasons, strengths, weaknesses, risks, and interview verification points. |
| `hr-interview-question-generator-copilot` | Candidate-specific interview questions, reference answer points, follow-up probes, and weak-answer signals. |

### Visual Agent Copilot

[Role README](./visual-agent-copilot/README.md) | [简体中文](./visual-agent-copilot/README.zh.md)

| Skill | Use When |
|---|---|
| `technical-visual-companion` | Turn confirmed technical designs into one verified offline Visual Companion HTML with automatically selected diagrams. |

## Installation

Install one skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

Install an HR skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
```

Install a Project skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/project-agent-copilot/project-develop-copilot/project-develop
```

Install the Visual Companion skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/visual-agent-copilot/technical-visual-companion
```

For local development from the repository root:

```bash
npx skills add .
```

After installation, restart Codex or your agent runtime so the skill can be rediscovered.

## Usage Examples

Use the DevOps package skill naturally:

```text
打包 smart-go-file 项目，路径 D:\workspace\drone\develop\smartghub\drone-cloud-api，版本 v1.3.0
```

```text
再打一次
```

```text
这次打 dock-api
```

```text
换成 v1.3.1 再打一次
```

Turn a confirmed technical design into one visual companion:

```text
把这份已确认的部署方案生成一个静态 HTML，自动选择最合适的图。
```

The skill reads project-local packaging docs:

```text
<project-root>/docs/docker-build-*.md
```

It does not invent build parameters. The real command must come from project documentation.

## Design Principles

- **Role first**: skills are grouped by enterprise role, such as DevOps or HR.
- **Skill as capability**: each skill should solve one recurring workflow.
- **Project docs are source of truth**: agents read local docs instead of guessing commands.
- **Reuse session context**: repeated work in the same conversation should not become a form.
- **Confirm risky actions**: first runs, project switches, release builds, deploys, pushes, and destructive actions require confirmation.
- **Do not replace scripts**: skills orchestrate existing tools and scripts instead of rewriting them.
- **Structured output**: results should be easy to hand off, audit, and reuse by later skills.

## Project Status

This repository is in an early stage.

The first implemented skill is `devops-package-copilot`. It is designed to support local enterprise packaging workflows where projects already provide build scripts and `docs/docker-build-*.md` documentation.

Future work may add CI diagnosis, release support, and more role groups.

