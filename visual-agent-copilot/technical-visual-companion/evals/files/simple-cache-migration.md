# Confirmed Cache Migration

Status: approved. This is intentionally a small flow.

Exactly two components participate:

1. `Legacy Cache`
2. `New Cache`

The migration has exactly three ordered steps:

1. Export the confirmed key set from `Legacy Cache`.
2. Import the exported key set into `New Cache`.
3. Compare key counts and sampled values, then record the migration result.

There is no state machine, retry loop, rollback branch, third component, or deployment topology in this design.
