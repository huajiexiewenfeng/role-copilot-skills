# DevOps Agent Copilot

Role-focused skills for packaging, CI diagnosis, release preparation, and DevOps workflow assistance.

English | [简体中文](./README.zh.md)

## What Is This?

DevOps Agent Copilot is the DevOps role group in Role Copilot Skills.

It is designed for teams that already have build scripts, CI/CD workflows, deployment conventions, and release handoff practices. The Copilot does not replace those systems. It helps the agent read project-local rules, assemble context, run safe commands, and summarize results.

## Current Skills

| Skill | Use When |
|---|---|
| `devops-package-copilot` | Package local projects from natural language by reading project-local `docs/docker-build-*.md` rules and calling existing build scripts. |
| `devops-release-copilot` | Prepare release handoff updates by syncing built image tags, Docker Compose files, and application environment variables. |

Planned skills:

- `devops-ci-diagnose-copilot`

## Install

Install the package skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

Install the release skill:

```bash
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-release-copilot
```

## Typical Workflow

```text
User request
-> read project-local packaging docs
-> reuse current packaging session context
-> fill missing critical values
-> generate the real script command
-> confirm when required
-> run existing scripts
-> summarize artifacts or failures
```

## Safety Model

- Project docs are the source of truth.
- The agent must not invent script parameters.
- First execution for a project root requires confirmation.
- Ordinary same-session follow-up builds can reuse context without repeated confirmation.
- Release, deploy, push, publish, cleanup, and all-module builds still require confirmation.

## Examples

```text
打包 smart-go-file 项目，路径 D:\workspace\drone\develop\smartghub\drone-cloud-api，版本 v1.3.0
```

```text
再打一次
```

```text
这次打 dock-api
```
