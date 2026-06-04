# Case 10 Fixture Run: 2026-06-04

This report records a real fixture dry run for Acceptance Case 10.

Fixture root:

```text
C:\tmp\project-develop-copilot-case10-fixture
```

## Purpose

Validate that the Project Develop Copilot Level 3.5 lifecycle contracts can close an end-to-end fixture path:

```text
init -> ingest -> develop -> finish -> review
```

This fixture does not prove behavior on a real business repository. It proves that the minimal `.llm-wiki`, Change Brief, working-context, artifact registry, dashboard evidence, and verification contracts can be represented consistently and checked mechanically.

## Fixture Structure

```text
.git-like fixture project root
├─ docs/prd/payment-callback.md
├─ payment-service/src/callback.js
├─ payment-service/test/callback.test.js
├─ order-service/src/orders.js
├─ notification-service/src/notify.js
└─ .llm-wiki/
   ├─ index.md
   ├─ ingest/index.md
   ├─ sources/payment-callback-prd.md
   ├─ requirements/payment-callback-compensation.md
   ├─ working-context/payment-callback-compensation.md
   ├─ verification/payment-callback.md
   ├─ artifacts/index.md
   └─ dashboard/progress.html
```

## Simulated Lifecycle

### Init

Created fixture `.llm-wiki` and module index.

Module scope:

- active: `payment-service`
- read-only: `order-service`
- reference-only/excluded: `notification-service`

### Ingest

Created source proxy:

```text
.llm-wiki/sources/payment-callback-prd.md
```

Linked source to requirement:

```text
.llm-wiki/requirements/payment-callback-compensation.md
```

### Develop

Created Change Brief:

```text
.llm-wiki/requirements/payment-callback-compensation.md
```

It includes:

- routing record
- active/read-only/excluded scope
- source artifacts
- acceptance criteria
- verification link
- artifact references

Created working context:

```text
.llm-wiki/working-context/payment-callback-compensation.md
```

It includes Context Lock:

- locked active scope: `payment-service`
- locked read-only scope: `order-service`
- locked excluded scope: `notification-service`
- escalation rule before editing non-active services

### Finish

Created verification record:

```text
.llm-wiki/verification/payment-callback.md
```

Verification command represented by fixture check:

```text
node payment-service/test/callback.test.js
```

Result:

```text
payment callback fixture tests passed
```

Registered artifacts:

```text
.llm-wiki/artifacts/index.md
```

Dashboard evidence:

```text
.llm-wiki/dashboard/progress.html
```

Dashboard uses `data-evidence` attributes that point to:

- `.llm-wiki/verification/payment-callback.md`
- `.llm-wiki/requirements/payment-callback-compensation.md`
- `.llm-wiki/working-context/payment-callback-compensation.md`
- `.llm-wiki/artifacts/index.md`

### Review

Mechanical checks verified:

- required `.llm-wiki` pages exist
- Change Brief contains routing record and scope split
- working-context contains scope lock
- artifact registry contains brief, verification, and dashboard rows
- dashboard contains evidence links
- fixture Node test passes

## Check Command

```powershell
powershell.exe -ExecutionPolicy Bypass -File C:\tmp\project-develop-copilot-case10-fixture\case10-check.ps1
```

Output:

```text
payment callback fixture tests passed
CASE10_FIXTURE_CHECK=PASS
FIXTURE_ROOT=C:\tmp\project-develop-copilot-case10-fixture
```

## Result

Case 10 fixture dry run: PASS.

## What This Proves

- The minimal lifecycle artifact set can be represented consistently.
- Change Brief, working-context, verification, artifact registry, and dashboard can form a traceable evidence chain.
- Dashboard status can point back to evidence instead of becoming an independent fact source.
- Scope lock can represent active/read-only/excluded services.
- A mechanical checker can catch missing evidence links or missing lifecycle files.

## What This Does Not Prove

- A live agent will always route correctly from natural language.
- External skills such as `systematic-debugging`, `writing-plans`, or `verification-before-completion` will always return proper handoff.
- Review will catch subtle code bugs in a real repository.
- Dashboard design is sufficient for a production project.
- Resume behavior avoids duplicate lifecycle sessions in a messy real `.llm-wiki`.

## Follow-Up

Next validation should use a real repository or a richer fixture with:

- at least one actual git diff
- a deliberate scope drift case
- a stale dashboard case
- an external bridge output sample
- a Dolores or evaluator trigger after an intentionally skipped gate