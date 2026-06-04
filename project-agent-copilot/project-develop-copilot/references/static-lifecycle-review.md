# Static Lifecycle Review

This review checks whether the current Project Develop Copilot skill documents can support the key Level 3.5 acceptance cases before real dry-run testing.

It is a static documentation review, not a proof that runtime behavior works.

## Result

Static readiness is acceptable for the first dry run.

The root router, child skills, and references now cover the core lifecycle contracts needed for Cases 1, 2, 3, 5, 6, and evaluator/Dolores trigger paths. The next validation step should be pressure testing with real or simulated project prompts.

## Case Coverage

| Case | Static status | Evidence |
|---|---|---|
| Case 1: Lightweight Design Discussion | Covered | Root `SKILL.md` has Lightweight Answer Boundary; `lifecycle-router.md` defines lightweight-answer and no lifecycle state by default. |
| Case 2: Natural Bug Request With External Debugging Bridge | Covered | `project-fix/SKILL.md` requires Bug Brief, Bug Evidence Gate, Context Lock Gate, scoped systematic-debugging bridge, and Return Handoff. |
| Case 3: Feature Request With Change Brief And Scope Lock | Covered | `project-develop/SKILL.md` requires Change Brief creation/resume, Clarification Gate, Context Lock Gate, and external bridge handoff. |
| Case 4: Temporary Source Ingest Attached To Lifecycle | Covered | `project-ingest/SKILL.md` attaches sources to Change Brief, Bug Brief, module, or working-context; it preserves sensitivity boundaries. |
| Case 5: Finish Sync With Dashboard Evidence | Covered | `project-finish/SKILL.md` owns Verification, Knowledge Sync, Artifact Sync, and Progress Dashboard Sync gates; `progress-dashboard.md` defines evidence rules. |
| Case 6: Review Finds Scope, Wiki, Artifact, And Dashboard Drift | Covered | `project-review/SKILL.md` checks scope, wiki, artifact, dashboard, bridge, and lifecycle quality drift. |
| Case 7: Resume Previous Lifecycle Session | Covered by router reference | `lifecycle-router.md` defines resume lookup order for Change Brief, Bug Brief, working-context, log, and artifacts. |
| Case 8: Conversation Review / Dolores Trigger | Covered | `continuous-evolution.md` and `project-review/SKILL.md` define Dolores trace review and non-blocking trigger behavior. |
| Case 9: Skill Evaluator Trigger From Review Finding | Covered | `continuous-evolution.md` defines evaluator diagnosis, eval gap, and minimal patch plan; `project-review/SKILL.md` exposes Lifecycle Quality output. |
| Case 10: End-To-End Full Lifecycle Dry Run | Not proven | Static docs cover the path, but a real dry run is still required before claiming broad testing readiness. |

## Fix Applied During Review

README installation examples were corrected to install the top-level `project-develop-copilot` router by default instead of the `project-develop` child skill. Child skills remain available for narrow testing.

## Remaining Runtime Risks

- The router may still be too heavy in live conversation if agents overuse full lifecycle for lightweight discussion.
- Resume behavior needs a real project `.llm-wiki` to prove duplicate session avoidance.
- Dashboard sync needs a real static HTML file to prove evidence links remain maintainable.
- External bridge handoff needs pressure testing with `systematic-debugging`, `writing-plans`, and `verification-before-completion`.
- Evaluator and Dolores should be tested carefully so they do not block normal delivery.

## Next Validation

Run these first:

1. Case 1 lightweight design discussion.
2. Case 2 bug request with systematic-debugging bridge.
3. Case 3 feature request with Change Brief and scope lock.
4. Case 5 finish sync with partial verification and dashboard evidence.
5. Case 6 lifecycle review with drift.
6. Case 8 or Case 9 for non-blocking evolution trigger.

Do not claim complete lifecycle readiness until these pass in a real or simulated project.