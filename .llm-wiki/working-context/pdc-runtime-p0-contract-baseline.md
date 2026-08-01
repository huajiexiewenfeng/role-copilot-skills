# Project Lifecycle Runtime P0 Contract And Skill-only Baseline Implementation Plan

> **SUPERSEDED — DO NOT EXECUTE:** 项目 Owner 已否决统一 Lifecycle Runtime 作为当前路线。本计划没有执行，也没有产生 Runtime、CLI、MCP 或 CI 代码。当前权威设计是 `../requirements/pdc-llm-first-deterministic-guardrails-v3.md`；只有新的真实失败满足 V3 的全部 Guardrail 晋升门槛时，才允许创建独立实施计划。

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to execute this plan task by task. This repository owner currently prefers one Codex task with sequential execution; do not delegate to other Agents unless the user later asks. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Project Develop Copilot 建立版本化、可机读、可测试的 Runtime P0 契约和 Skill-only 基线，使 P1 只读 Runtime 可以直接复用同一 authority、invariant、operation、error 与 context-ref 定义，而不提前引入 CLI、写入事务或 MCP。

**Architecture:** 在 PDC 源码包内新增无 `SKILL.md` 的内部 `project-lifecycle-runtime/` 组件。JSON catalog 是版本化机器契约，Python 标准库 loader 只负责加载和闭合校验，Markdown 解释设计意图，fixture manifest 保存后续阶段可重放场景。P0 不读取或写入消费项目 `.llm-wiki`，不提供 Agent tool，不改变 Router；CI 只运行离线契约测试。

**Tech Stack:** Python 3.11+ 标准库、`unittest`、JSON、Markdown、GitHub Actions。

## Global Constraints

- `flow_id`: `pdc-runtime-p0-contract-baseline`；父 Flow 为 `pdc-runtime-first-architecture-v2`。
- Runtime 组件根固定为 `project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/`。
- Python import package 固定为 `project_lifecycle_runtime`；P0 不承诺最终 CLI 的安装或模块发现方式。
- P0 只实现 catalog loader、contract validators 和测试辅助函数，不实现 `resolve/query/diagnose/preview/commit` 的业务逻辑。
- JSON catalog 是 P0 机器契约权威；Markdown 只能解释，不能定义另一套冲突的 ID、状态或错误码。
- 所有 catalog 都使用 `schema_version: 1` 和稳定、snake_case ID；数组顺序不得成为语义。
- 所有文件路径保存为 repo-relative POSIX 形式；不得持久化盘符路径、用户 home、临时目录或已安装 Skill 的本机路径。
- 所有实现只使用 Python 标准库；不得新增 `jsonschema`、Pydantic、MCP SDK、网络依赖或后台服务。
- P0 不创建 `SKILL.md`，不修改根 Router/子 Skill 触发，不调用 Agent/LLM，不增加普通用户步骤、prompt、token 或 latency。
- 不修改现有 Doctor/Task Control 业务代码；只读取它们作为模式和基线证据。
- 不修改既有未提交的 `references/session-digest-implementation-plan.zh.md` 与 `internal-trial-guides/`。
- 每项实现先保留可复现 RED，再加入最小 GREEN；没有证据不得把 Flow Record 的 development/testing 标为 done。
- 实现开始前必须确认隔离策略。若使用 worktree，先验证 `.worktrees/` 被 Git 忽略，并只带入本 Flow 已确认的文件。
- 未经用户单独授权，不执行 commit、push、PR、merge、tag 或 release。

## Context Handoff

- lifecycle_session: `.llm-wiki/requirements/pdc-runtime-p0-contract-baseline.md`
- parent_design: `project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md`
- active_scope: P0 internal runtime package、versioned catalogs、contract loader/tests、fixtures、Skill-only baseline、CI discovery 和生命周期文档。
- read_only_scope: Doctor、Task Control、Black-box Eval、Flow Record/Change Brief/Dashboard/Graph/Session Digest contracts、v0.1.0 release evidence。
- excluded_scope: P1 read-only operations、JSON CLI、P2 Preview、P3 Commit、P4 MCP、Agent automation、Router/Skill 行为改动。
- current_gate: 候选实施计划已生成，等待用户确认和 worktree 决定。
- execution_mode: 当前推荐同一 Codex 任务顺序执行；不使用其他 Agent。

## Target File Map

| Responsibility | Files |
|---|---|
| Internal component boundary | Create `project-lifecycle-runtime/README.md`; assert no `SKILL.md` |
| Python contract loader | Create `project-lifecycle-runtime/project_lifecycle_runtime/__init__.py`; create `project_lifecycle_runtime/contracts.py` |
| Versioned authority | Create `project-lifecycle-runtime/contracts/authority-model.v1.json` |
| Runtime invariants | Create `project-lifecycle-runtime/contracts/invariants.v1.json` |
| Operations/envelope | Create `project-lifecycle-runtime/contracts/operations.v1.json` |
| Error taxonomy | Create `project-lifecycle-runtime/contracts/errors.v1.json` |
| Context refs/compatibility | Create `project-lifecycle-runtime/contracts/context-refs.v1.json`; create `compatibility-policy.v1.json` |
| Representative fixtures | Create `project-lifecycle-runtime/fixtures/manifest.v1.json`; create six case JSON files under `fixtures/cases/` |
| Skill-only baseline | Create `project-lifecycle-runtime/baselines/project-develop-copilot-v0.1.0.json` |
| Runtime tests | Create `project-lifecycle-runtime/tests/__init__.py`; create `tests/test_contract_catalog.py`; create `tests/test_fixture_manifest.py`; create `tests/test_skill_only_baseline.py` |
| Parent CI contract | Modify `scripts/tests/test_ci_release_contract.py`; modify `.github/workflows/project-develop-copilot-ci.yml` |
| Architecture/lifecycle state | Modify V2 architecture status, this Change Brief/plan, `.llm-wiki/index.md`, `.llm-wiki/log.md`; create final handoff only after implementation verification |

## Contract Shape Decisions

### Catalog loader

`project_lifecycle_runtime/contracts.py` exposes only deterministic P0 helpers:

```python
SCHEMA_VERSION = 1
CATALOG_FILES = {
    "authority": "authority-model.v1.json",
    "invariants": "invariants.v1.json",
    "operations": "operations.v1.json",
    "errors": "errors.v1.json",
    "context_refs": "context-refs.v1.json",
    "compatibility": "compatibility-policy.v1.json",
}

def load_catalog(name: str) -> dict[str, object]: ...
def validate_catalogs() -> tuple[str, ...]: ...
def validate_context_ref(value: object) -> tuple[str, ...]: ...
```

Validation returns stable finding strings sorted by catalog/id/path. It does not read a project, infer user intent, perform lifecycle transitions or format an Agent answer.

### Stable operations

The only operation IDs are:

```text
project_context.resolve
project_context.query
project_context.diagnose
project_lifecycle.preview
project_lifecycle.commit
```

Each registry entry declares `introduced_phase`, `read_only`, request fields, response data fields and allowed error codes. P0 validates the catalog; P1-P3 implement the operations in phase order.

### Response envelope

Every operation uses the same top-level fields:

```text
schema_version
operation
status
request_id
runtime_version
data
context_refs
diagnostics
error
```

Allowed status values are `ok`, `degraded`, `rejected`, `partial` and `error`.
`partial` is reserved for P3 recovery semantics and cannot be emitted by a P0/P1 operation.

### Exit classifications

Only the following process classifications are reserved in P0:

```text
0 success, including read-only warnings/degraded data
2 invalid request/schema/unsupported operation
3 precondition/conflict/stale state
4 permission/root containment rejection
5 partial commit/recovery required
6 internal runtime error
```

JSON error code remains the stable detailed contract; exit code is a coarse adapter classification.

### Context refs

A context ref uses:

```json
{
  "kind": "wiki",
  "path": ".llm-wiki/requirements/example.md",
  "anchor": "flow-record",
  "revision": "git:0123456789abcdef0123456789abcdef01234567",
  "digest": "sha256:<64 lowercase hex characters>",
  "trust": "source_verified"
}
```

`path` is required and repo/wiki relative. `anchor`, `revision` and `digest` are nullable but, when present, must use the registered format. `trust` is one of `candidate`, `wiki_checked`, `source_verified`, `agent_local`, `ci_backed`, `user_accepted` or `unknown`.

## Task 1: Establish The Internal Runtime Boundary And CI RED

**Files:**

- Create: `project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/README.md`
- Create: `project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/tests/__init__.py`
- Create: `project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/tests/test_contract_catalog.py`
- Modify: `project-agent-copilot/project-develop-copilot/scripts/tests/test_ci_release_contract.py`
- Modify later in this task: `.github/workflows/project-develop-copilot-ci.yml`

- [ ] **Step 1: Write boundary and CI contract tests**

Add tests that require:

```python
runtime_root.is_dir()
not (runtime_root / "SKILL.md").exists()
(runtime_root / "project_lifecycle_runtime").is_dir()
(runtime_root / "contracts").is_dir()
```

Extend the existing CI contract test to require this exact command in both OS jobs:

```text
python -m unittest discover -s project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/tests -t project-agent-copilot/project-develop-copilot/project-lifecycle-runtime
```

- [ ] **Step 2: Run RED**

Run:

```powershell
python -m unittest project-agent-copilot/project-develop-copilot/scripts/tests/test_ci_release_contract.py
python -m unittest discover -s project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/tests -t project-agent-copilot/project-develop-copilot/project-lifecycle-runtime
```

Expected: CI contract fails because the Runtime test command is absent; Runtime contract discovery fails because the package/catalog does not exist.

- [ ] **Step 3: Add the minimal internal boundary**

Create the README with these explicit statements:

- developer-only internal component;
- no user-invoked Skill and no `SKILL.md`;
- no MCP in P0;
- JSON catalogs are canonical P0 machine contracts;
- ordinary PDC users have no new setup or workflow.

Add the exact Runtime test command to both GitHub Actions jobs. Do not rename either existing job or remove existing tests/checkers.

- [ ] **Step 4: Re-run the focused tests**

Expected: CI static contract passes; Runtime test still fails only for missing catalog implementation, preserving the next task's RED.

## Task 2: Implement The Versioned Catalog Loader

**Files:**

- Create: `project-lifecycle-runtime/project_lifecycle_runtime/__init__.py`
- Create: `project-lifecycle-runtime/project_lifecycle_runtime/contracts.py`
- Create: all six empty-shape versioned catalog files under `project-lifecycle-runtime/contracts/`
- Modify: `project-lifecycle-runtime/tests/test_contract_catalog.py`

- [ ] **Step 1: Add loader and meta-contract tests**

Tests must prove:

- exactly six registered catalogs exist;
- every catalog is UTF-8 JSON object with `schema_version == 1`;
- filename version and payload version agree;
- unknown catalog names are rejected without accepting a path;
- duplicate IDs, unknown top-level fields and absolute paths produce sorted findings;
- loading does not inspect cwd, environment variables, Git, network or a consumer project.

- [ ] **Step 2: Run RED**

Expected: import or catalog presence assertions fail.

- [ ] **Step 3: Implement the minimal loader**

Use `Path(__file__).resolve().parents[1] / "contracts"` as the package-owned catalog root. Resolve only values from the constant allowlist; never concatenate caller input into a path. Decode with `encoding="utf-8"`, reject a leading BOM, and return JSON data without mutation.

- [ ] **Step 4: Add minimal valid catalog skeletons and run GREEN**

Each skeleton contains its final top-level keys and an empty `entries` array. Expected: focused Runtime suite passes loader/meta-contract tests.

## Task 3: Freeze Authority Order And Write-point Inventory

**Files:**

- Modify: `project-lifecycle-runtime/contracts/authority-model.v1.json`
- Modify: `project-lifecycle-runtime/tests/test_contract_catalog.py`
- Modify: `project-lifecycle-runtime/README.md`

- [ ] **Step 1: Add failing authority closure tests**

Require the ordered authority tiers:

```text
current_user_decision
current_source_test_verification
flow_record
artifact_registry
append_only_log
dashboard_handoff_projection
unpromoted_session_digest
```

Require write families for project index, source proxies/ingest index, requirement/bug/working context, Flow Record, artifact registry, dashboard, handoff, log, session digest, project graph edge/candidate/cross-ref, Base tracked files and derived cache/lock/journal.

For every write family assert non-empty `authority`, `allowed_writer`, `preconditions`, `projection_targets`, `introduced_phase` and `path_patterns`. Projection entries must reference a stronger authority tier and cannot point back into Flow Record.

- [ ] **Step 2: Run RED**

Expected: empty authority catalog fails required tier/write-family coverage.

- [ ] **Step 3: Populate authority-model.v1.json**

Encode current contracts without inventing state:

- Flow Record is lifecycle status authority;
- Artifact Registry is artifact discoverability authority but cannot claim artifact existence without filesystem evidence;
- Dashboard/Handoff are projections;
- Log is append-only audit;
- Session Digest is recall context until explicit promotion;
- remote project is read-only by default;
- business project sessions cannot write Base tracked files;
- derived cache/lock/journal are local, rebuildable and not Markdown/Git truth.

- [ ] **Step 4: Run GREEN and manually compare every entry to source references**

The review evidence must name the source reference used for each write family. Do not call the catalog complete merely because JSON validation passes.

## Task 4: Register The Fifteen Runtime Invariants

**Files:**

- Modify: `project-lifecycle-runtime/contracts/invariants.v1.json`
- Modify: `project-lifecycle-runtime/tests/test_contract_catalog.py`

- [ ] **Step 1: Add failing invariant coverage tests**

Use stable IDs `PDC-INV-001` through `PDC-INV-015`. Tests require exact set equality, unique IDs, a non-empty rule, `introduced_phase`, applicable operations, enforcement type and evidence requirements.

Cross-catalog assertions must prove every referenced operation, authority write family and error code exists.

- [ ] **Step 2: Run RED**

Expected: empty registry fails exact 15-ID coverage.

- [ ] **Step 3: Encode V2 section 9 without strengthening claims**

Map each invariant to its earliest enforceable phase:

- P0 catalog-only rules are statically enforceable now;
- root/read-only/context rules become runtime-enforced in P1;
- projection/verification/confirmation rules become preview-enforced in P2;
- idempotency/stale preview/partial success rules become commit-enforced in P3;
- Skill truthfulness remains a cross-layer contract and is not falsely described as fully Runtime-enforceable.

- [ ] **Step 4: Run GREEN**

Expected: all registry and cross-reference tests pass; no test invokes a lifecycle operation.

## Task 5: Freeze Operations, Envelope And Error Taxonomy

**Files:**

- Modify: `project-lifecycle-runtime/contracts/operations.v1.json`
- Modify: `project-lifecycle-runtime/contracts/errors.v1.json`
- Modify: `project-lifecycle-runtime/project_lifecycle_runtime/contracts.py`
- Modify: `project-lifecycle-runtime/tests/test_contract_catalog.py`

- [ ] **Step 1: Add failing operation/envelope tests**

Assert exact operation IDs, phase order, read-only flags, required request fields and required response data fields. Reject an operation containing `mcp`, `server`, `transport` or Host product names.

Assert the exact envelope field set and status set. P0/P1 operations must not allow `partial`.

- [ ] **Step 2: Add failing error tests**

Require unique snake_case error codes with `exit_code`, `retryable`, `introduced_phase`, `operations` and `meaning`. Reserve exit codes exactly `{0, 2, 3, 4, 5, 6}` and reject success code 0 on an error entry.

The initial taxonomy must distinguish at least:

```text
invalid_request
unsupported_schema_version
unsupported_operation
project_root_not_found
wiki_not_initialized
root_not_allowed
path_escape
ambiguous_flow
duplicate_flow_id
invalid_transition
missing_verification_evidence
artifact_missing
projection_conflict
confirmation_required
unverified_evidence
remote_write_forbidden
base_write_forbidden
conflict
stale_preview
idempotency_conflict
partial_commit
recovery_required
internal_error
```

- [ ] **Step 3: Run RED**

Expected: exact operation/envelope set and minimum error taxonomy assertions fail.

- [ ] **Step 4: Populate both catalogs and add cross-catalog validation**

Every operation error reference must exist; each error operation reference must point back to an operation available in the same or earlier phase. Error meaning is stable; changing meaning requires a new code or breaking schema version.

- [ ] **Step 5: Run GREEN**

Expected: operation/envelope/error tests pass without adding CLI argument parsing or stdout output.

## Task 6: Define Context Refs And Compatibility Policy

**Files:**

- Modify: `project-lifecycle-runtime/contracts/context-refs.v1.json`
- Modify: `project-lifecycle-runtime/contracts/compatibility-policy.v1.json`
- Modify: `project-lifecycle-runtime/project_lifecycle_runtime/contracts.py`
- Modify: `project-lifecycle-runtime/tests/test_contract_catalog.py`

- [ ] **Step 1: Add failing positive/negative context-ref tests**

Positive cases cover Wiki Markdown, source/test evidence, Git revision and Runtime diagnostic refs. Negative cases cover drive-letter paths, UNC paths, POSIX absolute paths, `..` escape, invalid digest, unknown trust, empty path and secret-like inline content.

- [ ] **Step 2: Add failing compatibility tests**

Require explicit rules for:

- additive field change;
- breaking field removal/rename/semantic change;
- reader ignores registered optional additions but rejects unsupported major schema;
- writer emits exactly one supported schema version;
- Markdown/Git remains shared authority;
- cache/index/lock/journal remains derived and rebuildable;
- adapters cannot advertise a schema newer than Runtime Core.

- [ ] **Step 3: Run RED, implement validation, then run GREEN**

`validate_context_ref` must be a pure function. It returns deterministic findings and never resolves the path on the local filesystem; containment against an allowed root belongs to P1.

## Task 7: Add Replayable Fixtures And The v0.1.0 Skill-only Baseline

**Files:**

- Create: `project-lifecycle-runtime/fixtures/manifest.v1.json`
- Create: six JSON case files under `project-lifecycle-runtime/fixtures/cases/`
- Create: `project-lifecycle-runtime/baselines/project-develop-copilot-v0.1.0.json`
- Create: `project-lifecycle-runtime/tests/test_fixture_manifest.py`
- Create: `project-lifecycle-runtime/tests/test_skill_only_baseline.py`

- [ ] **Step 1: Write failing fixture manifest tests**

Create cases with these stable IDs and expected contracts:

| Case | Operation | Expected contract |
|---|---|---|
| `resolve-uninitialized-project` | `project_context.resolve` | success/degraded, no write |
| `preview-testing-without-evidence` | `project_lifecycle.preview` | `missing_verification_evidence` |
| `diagnose-dashboard-ahead-of-flow` | `project_context.diagnose` | `projection_conflict` finding |
| `preview-candidate-promotion` | `project_lifecycle.preview` | `unverified_evidence` |
| `commit-remote-write` | `project_lifecycle.commit` | `remote_write_forbidden` |
| `commit-path-escape` | `project_lifecycle.commit` | `path_escape` |

Each fixture declares phase, operation, input facts, expected status/error, invariant IDs and authority refs. P0 validates fixture closure only; P1-P3 later add replay executors.

- [ ] **Step 2: Run RED and add fixture files**

Expected GREEN condition: every referenced ID exists, phase availability is coherent, no fixture claims execution evidence, and all fixture paths are relative.

- [ ] **Step 3: Write failing baseline provenance tests**

Require:

```text
baseline_type = skill_only
release_tag = project-develop-copilot-v0.1.0
source_commit = 49e7599ba9350adef9eb12533d6895406f377fe1
runtime_operations_available = 0
state_enforcement_mode = skill_contract_and_human_agent
```

Require GitHub Release/Actions evidence refs and explicit `not_measured` values for token usage, tool-call count and lifecycle drift rate. The test must reject numeric zero for an unmeasured metric.

- [ ] **Step 4: Add the baseline and run GREEN**

Record the verified release facts only: release/tag/commit, Linux and Windows CI, parent script tests 179/179, Task Dispatch tests 30/30, Runtime absent, and current Codex-only behavior certification boundary. Do not convert canned answers, static tests or file-only evidence into cross-Agent claims.

## Task 8: Complete Cross-platform Verification And Lifecycle Sync

**Files:**

- Modify: `project-agent-copilot/project-develop-copilot/references/2026-08-01-project-develop-copilot-runtime-first-architecture-v2.zh.md`
- Modify: `.llm-wiki/requirements/pdc-runtime-p0-contract-baseline.md`
- Modify: `.llm-wiki/working-context/pdc-runtime-p0-contract-baseline.md`
- Modify: `.llm-wiki/index.md`
- Modify: `.llm-wiki/log.md`
- Create after verification: `.llm-wiki/handoff/pdc-runtime-p0-contract-baseline-handoff.md`

- [ ] **Step 1: Run focused P0 tests**

```powershell
python -m unittest discover -s project-agent-copilot/project-develop-copilot/project-lifecycle-runtime/tests -t project-agent-copilot/project-develop-copilot/project-lifecycle-runtime
```

Expected: all P0 catalog, fixture and baseline tests pass.

- [ ] **Step 2: Run parent regression tests**

```powershell
python -m unittest discover project-agent-copilot/project-develop-copilot/scripts/tests
python -m unittest discover project-agent-copilot/project-develop-copilot/project-task-dispatch/tests
```

Expected: all current parent and Task Dispatch tests pass with no regression.

- [ ] **Step 3: Run repository gates**

```powershell
python project-agent-copilot/project-develop-copilot/scripts/check_text_quality.py --root project-agent-copilot/project-develop-copilot
python project-agent-copilot/project-develop-copilot/scripts/check_doc_integrity.py --root project-agent-copilot/project-develop-copilot
python project-agent-copilot/project-develop-copilot/scripts/sync-doctor.py --check
git diff --check
```

Expected: no findings, scaffold drift or whitespace errors.

- [ ] **Step 4: Run P0 boundary audit**

Verify the exact P0 Git union:

- contains no `project-lifecycle-runtime/SKILL.md`;
- contains no imports named `mcp`, `requests`, `httpx`, `pydantic` or `jsonschema`;
- contains no socket/network/process startup code;
- contains no working-station absolute path, UTF-8 BOM or U+FFFD;
- does not include the pre-existing session-digest/internal-trial changes;
- changes no Router or child `SKILL.md`.

- [ ] **Step 5: Review diff against all Acceptance items**

Check every Acceptance item with file/test evidence. Pay special attention to catalog semantic duplication, operation phase leakage, authority cycles and baseline overclaiming.

- [ ] **Step 6: Sync lifecycle state only from evidence**

After all checks pass:

1. mark development/testing done with exact commands and counts;
2. update V2 status to approved architecture baseline with P0 implemented;
3. create handoff with residual risks and P1 entry criteria;
4. project the Flow into `.llm-wiki/index.md` and append one log event;
5. leave archive pending until the user accepts P0 or authorizes integration.

## Verification Matrix

| Risk | Deterministic evidence |
|---|---|
| Contract files drift or duplicate IDs | `test_contract_catalog.py` exact-set and cross-reference tests |
| Runtime becomes an accidental Skill | no-`SKILL.md` boundary test |
| MCP/Host coupling enters P0 | forbidden identifier/dependency audit plus operation ID tests |
| Authority/projection cycle | authority graph closure tests |
| Error code silently changes meaning | exact code set, exit mapping and version policy tests |
| Workstation path leaks into refs | context-ref negative tests plus final text/path audit |
| Fixture claims behavior not implemented | manifest phase and evidence-status tests |
| Baseline fabricates improvement | provenance requirements and `not_measured` tests |
| Linux/Windows diverge | identical P0 unittest command in both CI jobs |
| Existing PDC behavior regresses | parent script/Task Dispatch suites and repository gates |

## Self-review Checklist

- [ ] Every task has exact files, RED command, minimal implementation and GREEN evidence.
- [ ] No task implements P1 read-only filesystem behavior, P2 Preview execution, P3 Commit or P4 MCP.
- [ ] All five operation names remain protocol-neutral.
- [ ] The 15 invariant IDs map one-to-one to V2 section 9.
- [ ] Authority and error catalogs are canonical; Markdown does not fork their semantics.
- [ ] Baseline binds the released commit and labels missing telemetry honestly.
- [ ] Ordinary user cost remains zero and is covered by a boundary assertion.
- [ ] Existing unrelated dirty files are excluded from all Git and verification claims.

## Execution Handoff

Plan complete and saved to `.llm-wiki/working-context/pdc-runtime-p0-contract-baseline.md`.

Recommended execution mode for this repository owner: continue in the current Codex task with `executing-plans`, one task at a time, without other Agents. Before Task 1, ask once for consent to create an isolated worktree; if the owner declines, execute in the current checkout with an exact scope guard and preserve all unrelated changes.
