# Role Copilot Skills

Role-based Agent Copilot skills for enterprise team productivity.

## Structure

Each top-level directory is an Agent Copilot role. Each child directory is an installable Codex skill.

```text
role-copilot-skills/
  devops-agent-copilot/
    devops-package-copilot/
  hr-agent-copilot/
    hr-resume-screening/
```

## Available Skills

### DevOps Agent Copilot

- `devops-package-copilot`: Package local projects from natural language by reading project-local `docs/docker-build-*.md` rules, confirming the exact command, and calling existing build scripts.

## Install

Install a single skill:

```powershell
npx skills add huajiexiewenfeng/role-copilot-skills/devops-agent-copilot/devops-package-copilot
```

Install from a local checkout:

```powershell
npx skills add .
```
