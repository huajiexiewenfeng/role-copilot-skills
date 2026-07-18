# Confirmed Runtime Orchestration Design

Status: approved. Every statement below is a confirmed fact for visualization.

## Boundary

The dock host runs one Docker Compose project. `dock-gateway` owns runtime configuration rendering and the synchronous deployment API. The caller prepares a complete configuration object before invoking that API.

## Persistent Services

Exactly nine services are already running and must not be recreated by the runtime action:

1. `dbgate`
2. `emqx`
3. `mysql`
4. `nginx`
5. `redis`
6. `zlmediakit-edge`
7. `cloud-smart-go`
8. `cloud-dim-client`
9. `dock-gateway`

Database init jobs have already completed. They are outside this runtime action.

## Dynamic Services

Exactly three services are generated and converged by the runtime action:

1. `file`
2. `device-mapping`
3. `smarthub-mediakit-client`

## Synchronous Sequence

1. The caller invokes the `dock-gateway` deployment endpoint with the complete configuration object.
2. `dock-gateway` validates required values and renders the version-specific Compose template to a candidate file.
3. `dock-gateway` runs `docker compose config` against the candidate.
4. After validation passes, it backs up the active generated Compose file and promotes the candidate.
5. It runs Docker Compose only for the three dynamic services.
6. It polls each dynamic service through its HTTP/Actuator health endpoint.
7. The endpoint returns only after all three services are healthy or rollback finishes.

## Two-Phase Activation

- Phase 1, prepare: validate input, render candidate, validate Compose, and preserve the previous active file.
- Phase 2, converge: promote the candidate, start or recreate the three dynamic services, and verify health.

## States

- `VALIDATING`
- `RENDERED`
- `PROMOTED`
- `STARTING`
- `HEALTHY`
- `ROLLING_BACK`
- `ROLLED_BACK`
- `FAILED`

Success means all three dynamic services report healthy and the promoted Compose remains active.

If Compose startup or health verification fails and a previous active file exists, `dock-gateway` restores that file, reconverges the same three services, verifies their health, and returns a failed deployment result with state `ROLLED_BACK`. If no previous active file exists, it keeps the failed candidate as an audit artifact, reports `FAILED`, and does not modify the nine persistent services.

## Exclusions

- Do not start, stop, or recreate the nine persistent services.
- Do not rerun database init jobs.
- Do not add asynchronous queues or background deployment workers.
- Do not invent additional dynamic services.
