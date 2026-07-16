# Continuous Skill Evolution

Project Develop Copilot should improve from real lifecycle failures and golden paths. Continuous evolution is a non-blocking improvement loop, not a mandatory interruption for every project task.

It borrows from `thinking-skills` concepts such as `skill-evaluator` and `conversation-review` / Dolores, but its object is project lifecycle quality.

## Default Rule

Normal delivery comes first.

## Offline black-box bridge

The developer-only black-box sidecar adds an offline bridge for Eval 2 and Eval
32:

```text
offline evidence -> diagnosis -> Human Patch Gate -> before/after comparison
```

The sidecar prepares files, validates deterministic/Judge evidence, and freezes
diagnosis provenance. It does not call an Agent or LLM, apply a Skill patch, or
infer human approval. A human copies `answer.md` and `judge.json` into the Run,
then the process must stop at the Human Patch Gate. Only an explicit Human
`patch-decision.json` value of `approve` authorizes the Level B before/after
bridge.

This offline maintenance path is separate from user-triggered Evaluator/Dolores
analysis. It adds no step to ordinary delivery and does not make Evaluator or
Dolores an automatic user-facing workflow.

Evaluator or Dolores runs only when:

- the user explicitly asks for it
- review finds a process-level lifecycle failure
- a high-risk gate was skipped
- a routing mistake caused wrong work
- a lifecycle run is worth saving as an abstract failure or golden case


## Natural Trigger Language

Users should be able to trigger continuous evolution with ordinary language, similar to Thinking Skills self-review and evaluator triggers.

### Evaluator Triggers

Route to Project Skill Evaluator when the user says things like:

- "评估一下这个 skill 为什么跑偏"
- "这个 skill 需要怎么改，先不要直接改"
- "刚刚 project-fix 跳过了 Work Definition Gate，分析下原因"
- "这个 router 是不是选错了 stage"
- "这次流程哪里有 eval gap"
- "把这个失败抽象成一个 failure case"
- "这个成功路径能不能沉淀成 golden case"
- "skill-evaluator 看下这个 case"
- "evaluate this project skill failure"
- "find the smallest patch for this skill behavior"

Evaluator should answer with diagnosis, likely source, eval gap, and smallest useful patch. It should not modify skills unless the user explicitly asks to apply the patch.

### Dolores / Conversation Review Triggers

Route to Project Conversation Review / Dolores when the user says things like:

- "用 Dolores 视角复盘一下"
- "conversation self-review"
- "self-review 刚刚这段流程"
- "复盘一下这个 lifecycle trace"
- "刚刚这个 project develop 流程是不是跑偏了"
- "看下 routing / gate / bridge 有没有问题"
- "把刚刚的对话做一次生命周期复盘"
- "Dolores 看下这次流程"
- "review the conversation trace"
- "did this project lifecycle go wrong"

Dolores should reconstruct lifecycle trace and check routing, gates, scope, bridges, verification, sync, dashboard, review, and evolution signals. It should not become a generic summary.

### Non-Trigger Language

Do not trigger evaluator or Dolores for ordinary delivery language such as:

- "继续"
- "下一步做什么"
- "帮我修这个 bug"
- "完成了吗"
- "review 一下代码"
- "总结一下改了什么"

These may enter normal lifecycle stages. Only add Lifecycle Quality output if process risk appears or the user explicitly asks for evaluator/self-review/Dolores.

## Project Skill Evaluator

Use evaluator-style analysis for focused failures or golden candidates.

Trigger examples:

- router selected the wrong primary stage
- lightweight discussion became full lifecycle without user intent
- full lifecycle did not create Change Brief or Bug Brief
- Work Definition Gate was skipped for bug evidence
- Work Definition Gate was skipped before implementation
- external bridge bypassed Context Handoff or Return Handoff
- scope expanded without escalation
- finish claimed completion without verification
- dashboard was updated without evidence
- review missed scope/wiki/artifact/dashboard drift
- a flow worked unusually well and should become a golden case

Evaluator output:

```markdown
## Diagnosis

Case summary:
Failure or golden type:
Likely source: router | stage skill | external bridge | gate | reference doc | eval gap

## Eval Gap

Existing coverage:
New or updated eval:

## Patch Plan

Smallest useful change:
Files likely affected:
Overfitting risk:
Recommendation:
```

Evaluator rules:

- Do not patch skills immediately unless the user asks to enter modification mode.
- Prefer the smallest useful patch.
- Prefer adding or updating a pressure case when behavior was under-specified.
- Separate router failure from child skill failure.
- Separate external bridge failure from project lifecycle failure.
- Do not save raw private conversation, customer data, logs, credentials, or sensitive project context.

## Project Conversation Review / Dolores

Use Dolores-style review for a full lifecycle trace.

It answers:

```text
Did this conversation behave like a coherent project lifecycle?
```

Dolores checks:

- natural entry and routing
- lightweight vs full lifecycle decision
- lifecycle session creation or resume
- routing record
- gate execution and gate skips
- external bridge scope and handoff
- scope escalation
- implementation timing
- verification
- knowledge sync
- artifact sync
- dashboard sync
- review drift checks
- evaluator or case candidate

Dolores output:

```markdown
## Lifecycle Trace

## Routing And Gate Trace

## External Bridge Trace

## What Worked

## Failure Signals

## Eval Gaps

## Golden Signals

## Patch Strategy

## Dolores Note
```

Dolores rules:

- Keep light review short unless the user asks for deep review.
- Do not convert every normal summary into Dolores.
- Do not directly patch skills unless user asks.
- Save only abstract failure patterns or golden behavior.
- Do not save sensitive raw conversation or project data.

## Evolution Artifacts

Recommended directories:

```text
project-agent-copilot/project-develop-copilot/evals/
project-agent-copilot/project-develop-copilot/cases/failures/
project-agent-copilot/project-develop-copilot/cases/golden/
```

### Failure Case Template

```markdown
# Failure Case: <id>

## Abstract Scenario

## Expected Lifecycle Behavior

## Observed Failure Pattern

## Likely Source

## Suggested Eval

## Privacy Notes
```

### Golden Case Template

```markdown
# Golden Case: <id>

## Abstract Scenario

## Reusable Behavior

## Why It Worked

## Skill Or Gate Reinforced

## Privacy Notes
```

## Review Integration

`project-review` may include:

```markdown
## Lifecycle Quality

- evaluator_needed: yes | no
- dolores_review_needed: yes | no
- reason:
- suggested_artifact:
- blocking: yes | no
```

Default `blocking` is `no`.

## Common Mistakes

- Running evaluator on every ordinary task.
- Using Dolores as a generic conversation summary.
- Saving raw conversations as eval cases.
- Rewriting whole skills for one edge case.
- Ignoring golden paths because only failures feel urgent.
- Blocking delivery for low-risk process issues.
