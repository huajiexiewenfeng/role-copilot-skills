# Role Copilot Skills

Role-based Agent Copilot skills for enterprise team productivity.

English | [简体中文](./README.zh.md)

## What Is This?

Role Copilot Skills is a collection of domain-specific Agent Copilot skills.

The repository is organized around practical enterprise roles instead of isolated prompts. Each top-level directory is an Agent Copilot role, and each child directory is an installable Codex skill.

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

## Repository Structure

```text
role-copilot-skills/
  devops-agent-copilot/
    devops-package-copilot/
  hr-agent-copilot/
    hr-resume-screening-copilot/
    hr-candidate-detail-report-copilot/
    hr-interview-question-generator-copilot/
```

Current repository contents:

```text
devops-agent-copilot/
  devops-package-copilot/
hr-agent-copilot/
  hr-resume-screening-copilot/
  hr-candidate-detail-report-copilot/
  hr-interview-question-generator-copilot/
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

### HR Agent Copilot

[Role README](./hr-agent-copilot/README.md) | [简体中文](./hr-agent-copilot/README.zh.md)

| Skill | Use When |
|---|---|
| `hr-resume-screening-copilot` | First-stage resume screening against a JD with candidate ranking and 100-point scoring. |
| `hr-candidate-detail-report-copilot` | Candidate detail reports with score reasons, strengths, weaknesses, risks, and interview verification points. |
| `hr-interview-question-generator-copilot` | Candidate-specific interview questions, reference answer points, follow-up probes, and weak-answer signals. |

## Installation

Install one skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

Install an HR skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/hr-agent-copilot/hr-resume-screening-copilot
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

