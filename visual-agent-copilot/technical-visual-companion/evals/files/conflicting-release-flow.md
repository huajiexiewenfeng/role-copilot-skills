# Unresolved Release Startup Order

Status: unresolved. The team has documented two mutually exclusive alternatives and has not selected one.

## Alternative A — pending selection

1. Start infrastructure and wait for health.
2. Run database init jobs and wait for successful completion.
3. Start business services.

## Alternative B — pending selection

1. Start infrastructure and wait for health.
2. Start business services.
3. Run database init jobs after business services are running.

Both alternatives are labelled `pending selection`. Do not combine them, choose one, or generate a compromise sequence.
