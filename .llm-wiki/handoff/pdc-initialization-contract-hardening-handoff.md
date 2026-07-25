# Handoff: pdc-initialization-contract-hardening

## Status

- flow_id: `pdc-initialization-contract-hardening`
- development: done
- testing: done (`agent-local`)
- archive: done
- next_gate: none for this upgrade

## Implementation Summary

Project Develop Copilot now treats initialization as an execution contract instead of assuming that Skill selection authorizes execution.

The root Router preserves `pending_intent` and `pending_primary_stage`, routes Wiki-backed work through `project-init` when `.llm-wiki/` is absent, and keeps read-only and mechanical exceptions explicit.

`llm-wiki-doctor` refuses to diagnose a missing Wiki and returns a bootstrap handoff. `project-session-extract` allows ephemeral preview without a Wiki, but requires initialization before saving a Session Digest or promoting content into lifecycle state.

All child Skills must be classified under an initialization policy. The new `project-graph-visualize` Skill is integrated as a `mechanical-artifact` route that may write only its declared HTML output and does not create lifecycle documents or commits by default.

The repository also contains a dedicated upgrade-notes archive under `project-agent-copilot/project-develop-copilot/references/upgrades/`.

## Verification

| Check | Result | Exit |
|---|---|---:|
| initialization contract | passed, 11/11 | 0 |
| non-Blackbox unit tests | passed, 77/77 | 0 |
| Blackbox Grader tests | passed, 81/81 | 0 |
| Graph Visualizer smoke | passed, 18/18 | 0 |
| Skill structure validation | passed | 0 |
| text quality | no findings | 0 |
| document integrity | no findings | 0 |
| Doctor scaffold sync check | passed | 0 |
| Git diff check | passed | 0 |
| source/install tree hash comparison | difference count 0 | 0 |
| GitHub core push | commit `3719ef2` present on `main` | 0 |
| GitHub upgrade-note push | commit `8174375` present on `main` | 0 |

Verification provenance:

- executor: agent-local
- authority: source, tests, Git evidence, generated reports, and user-approved publish actions
- trust level: agent-local with GitHub push verification
- CI authority: not claimed for this Flow
- LLM Wiki Doctor finish command: not applicable; this repository has no `.llm-wiki/tools/llm_wiki_doctor.py`

## Test Integrity

- production runtime changes: no application production code
- Skill contract changes: yes
- deterministic scripts added: yes, for Project Graph visualization
- tests and fixtures changed: yes
- assertion strength: initialization policies are enumerated and the visualizer package contract is exact
- over-mocking risk: low; contract tests read the real Skill package, while the visualizer smoke test runs the real builder and validator

## Artifacts

- Change Brief: `requirements/pdc-initialization-contract-hardening.md`
- Upgrade note: `project-agent-copilot/project-develop-copilot/references/upgrades/2026-07-25-project-develop-copilot-upgrade-retrospective.zh.md`
- Core implementation commit: [`3719ef2`](https://github.com/huajiexiewenfeng/role-copilot-skills/commit/3719ef2620fc231e19be95e5586c4069f7de37d5)
- Upgrade-note commit: [`8174375`](https://github.com/huajiexiewenfeng/role-copilot-skills/commit/81743751dfeb734f83ea80c5d2ea14a87dd37fcb)

## Residual Risk

The existing real Agent Blackbox Runs cover Eval 2 and Eval 32 on `codex-desktop / gpt-5.6-sol` at an earlier Skill commit. Eval 2 scored `PARTIAL` because the answer did not cite a configured Wiki path; Eval 32 scored `PASS`.

Those Runs do not certify the new Initialization Gate behavior in Eval 33–35, and they do not establish cross-model compatibility. This limitation is intentionally carried into the next independent certification Flow.

## Return Handoff

- stage_or_bridge_used: project-finish
- result_summary: initialization hardening and graph visualization upgrade archived
- changed_assumptions: framework-level top-model adaptation is complete, but multi-model behavior certification remains separate
- recommended_scope_changes: none for the completed upgrade
- artifacts: Change Brief, upgrade note, this handoff, GitHub commits
- verification_notes: local suites and repository checks passed; GitHub pushes verified; CI and cross-model certification not claimed
- lifecycle_updates_needed: none for this Flow
- next_gate: create a separate multi-model certification Flow when the target model matrix is confirmed
