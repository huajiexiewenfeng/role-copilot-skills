# Development Delivery and Review

The filename is retained for compatibility, but new Project Worker Sessions do
not use a receipt-first progress protocol. Commentary and final are normal,
human-readable Codex messages.

## Worker final checklist

Final must state:

- completed work and acceptance IDs;
- changed files;
- actual project-local test commands and results;
- current repository root, branch, HEAD, and local commit;
- unresolved risks, blockers, and incomplete work;
- `NO_CHANGE_REQUIRED` plus direct evidence when no change is needed.

Final creates a delivery candidate. Manager classification moves `ASSIGNED` to
`SUBMITTED`; it never directly approves work.

## Manager Review

Manager transitions `SUBMITTED→REVIEWING`, then independently verifies Git,
diff, test evidence, acceptance, current contract revision, dependencies, and
side effects. Normal code changes require project-local passing tests and at
least one local commit. Never push. Do not run system-wide cross-project tests by
default.

If valid, apply `REVIEW_APPROVED`. If not, create structured OPEN findings,
apply `REVIEW_CHANGES_REQUESTED`, and send them to the original Worker Session.
The Worker resubmits in the same Session; review round increments. OPEN findings,
failed/not-run required tests, branch/HEAD mismatch, stale contracts, or missing
dependency approval block approval.

`NO_CHANGE_REQUIRED` creates no empty commit but still needs acceptance evidence
and explicit Manager approval. A blocker becomes structured PDC blocker state,
not a fake completion.

## Legacy 1.x

Only an already-active 1.x run may use `scripts/legacy_receipt.py`. Its
`COMPLETED` receipt maps to a v2 delivery candidate/`SUBMITTED`, retaining an
unverified-risk marker. It cannot bypass Review.
