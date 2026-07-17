# Project Develop Copilot Black-box Eval Sidecar

## Scope

This is a **Developer-only** sidecar for Eval 2 and Eval 32. It is not part of
Skill routing or the ordinary team workflow, so ordinary users pay zero setup,
prompt, token, or latency cost. The sidecar never calls an Agent or LLM. A human
operator runs those tools separately and moves the resulting files across the
boundary described below.

The sidecar has three commands:

```text
python scripts/blackbox_eval.py prepare --case {2,32} [--skill-path PATH] [--workspace PATH]
python scripts/blackbox_eval.py grade --run PATH [--execution-kind {agent,canned} --agent-product LABEL --agent-model LABEL]
python scripts/blackbox_eval.py report --run PATH [--baseline PATH] [--regression-pair BEFORE AFTER]...
```

The workspace must be outside the source repository. Supplying `--skill-path`
records a verified Skill path and SHA-256 tree fingerprint; omitting it records
an unverified identity.

## Human-operated workflow

1. Run `prepare`. It prints the Run, `prompt.md`, `fixture/`, and `answer.md`
   paths.
2. `fixture/` is the Agent project root and current working directory (cwd).
   Do not run the Agent from the caller's real repository.
   A human starts the chosen Agent in that cwd, gives it `prompt.md`, and copies
   only its final answer into the Run. `answer.md` must contain the final answer produced from that Run's `fixture/`.
   Record the manual `execution_kind`, Agent product, and Agent model on the
   first `grade` call. The three values are one immutable group; later grade
   calls may omit all three.
3. Run `grade`. When semantic review is unresolved, a human runs the Judge
   outside this program using `judge-request.json`, copies the response into
   `judge.json`, and runs `grade` again. `grading.json` records the validated
   assertions and full provenance, including Agent, answer, Skill, prompt,
   fixture, and Judge identities.
4. For a behavior `PARTIAL` or `FAIL`, the sidecar may emit
   `diagnosis-request.json`. A human or offline diagnostic tool supplies
   `diagnosis.json`; a later grade freezes the diagnosis and evidence in the
   immutable `freeze-manifest.json`.
5. Stop at the **Human Patch Gate**. Only a human may provide the separate
   `patch-decision.json`. `approve` is the only decision that authorizes a Level
   B before/after comparison. `revise` and `reject` do not authorize it.
6. Run `report` for the candidate and only the explicitly declared baseline and
   repeatable `--regression-pair BEFORE AFTER` inputs. The command writes and
   prints `report.md`.

`execution_kind=agent` describes a human-operated real Agent run.
`execution_kind=canned` is only for testing the deterministic grader and
sidecar mechanics. A canned Run cannot support an Agent-quality or Level B
claim.

## File boundaries

- `answer.md` is a human copy boundary. `prepare` creates it empty; this program
  does not generate an answer.
- `judge-request.json` is local Judge input, and `judge.json` is the manual Judge
  response boundary. This program does not call a Judge.
- `grading.json` is deterministic output whose provenance must continue to match
  the locked Run metadata and answer bytes.
- `diagnosis.json` is validated before the diagnosis and evidence become
  immutable under `freeze-manifest.json`.
- `patch-decision.json` is a separate Human decision. It is not produced or
  inferred by the grader.

## Run Status and Behavior Score

Run Status tracks whether the sidecar completed safely:

- `READY_FOR_AGENT`: prepared but no locked answer exists.
- `READY_TO_GRADE`: an answer is locked while grading is in progress.
- `NEEDS_REVIEW`: deterministic work completed but required Judge assertions are
  unresolved.
- `GRADED`: grading completed and has a Behavior Score.
- `RUN_ERROR`: the Run or its provenance is invalid; this is not a behavior
  failure.

Behavior Score is only `PASS`, `PARTIAL`, or `FAIL`. `NEEDS_REVIEW` and
`RUN_ERROR` are excluded from behavior-score and PASS-rate denominators.

## Evidence limits and caveats

The canary pairs are legacy/source authority probes. They indicate which literal
the answer adopted; they are not a claim that every source file is wrong or that
literal matching proves the complete reasoning path. Eval 32 therefore retains
a `manual-only` read-order assertion: final files and answers cannot prove read
order without a runtime trace, so a human must assess that assertion.

For untracked content, the maximum captured file size is **65,536** bytes and
the maximum total is **1,048,576** bytes. Eligible content payloads are
**local-only** Judge inputs. `report.md` exposes paths, sizes, and hashes rather
than private payload content. Do not use private conversations, customer data,
credentials, or sensitive project material as fixtures.

## Claim boundary

- **Level A** reports one validated Run and its deterministic/Judge evidence. It
  can describe that Run, not a Skill improvement.
- **Level B** is a before/after claim. It requires compatible real Agent Runs,
  verified but changed Skill identity, matching Agent and Judge identities, an
  approved frozen baseline, and declared regression coverage from the other
  Eval. Only Human `approve` authorizes the comparison.

No live Agent or LLM runs in CI. CI runs the offline unit tests and repository
integrity checks only; it neither generates `answer.md` nor `judge.json`.
