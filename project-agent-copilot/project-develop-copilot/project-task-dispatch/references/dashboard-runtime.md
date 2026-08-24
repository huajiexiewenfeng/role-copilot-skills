# PDC HTML Dashboard Runtime 2.0

## Purpose and shape

The dashboard is a read-only human projection for one PDC Dispatch. It does not
replace Codex tasks, Git evidence, Manager Review, or the long-lived Project
progress dashboard. Its fixed visual grammar is:

```text
Manager 1 → Project Sessions N → Manager final Review 1
```

Retries remain attempt history inside the original Project Session card. At
more than five Sessions the responsive grid wraps by repository while preserving
the outer 1 → N → 1 structure.

## Native Codex capability mapping

| Manager action | Native capability | Dashboard result |
|---|---|---|
| resolve destination | `list_projects` | verified Project/repository route |
| create peer task | `create_thread` | BOUND or CREATE_PENDING Session card |
| observe progress | `wait_threads` | native state and cursor observation |
| verify delivery | `read_thread` | SUBMITTED candidate enters Review |
| request rework/next batch | `send_message_to_thread` | same Session, next attempt |
| explicit pin/unpin | `set_thread_pinned` | called only when the user asks |
| explicit archive/unarchive | `set_thread_archived` | never inferred from CLOSED |
| optional in-window view | `open_in_codex` | queued/opened state is reported truthfully |

Native final is a turn observation, not PDC approval. The dashboard always shows
native and PDC state as separate badges.

## Projection and runtime

`scripts/dashboard_view.py` atomically writes:

```text
views/live/index.html
views/live/snapshot.json
views/live/assets/dashboard.js
views/live/assets/dashboard.css
```

The generated HTML includes the latest escaped server-side snapshot, so it is
still readable when no runtime exists. `scripts/dashboard_runtime.py` serves the
same files from a random loopback port, broadcasts revision changes over
WebSocket, accepts `revision-applied` acknowledgements, and falls back to JSON
polling on reconnect.

Start after the first non-empty revision:

```text
python scripts/dashboard_runtime.py start --dispatch-root <dispatch-directory>
```

Default behavior opens the operating system's external browser. Use
`--no-open-browser` for a deliberate headless run. Reopen an active runtime with:

```text
python scripts/dashboard_runtime.py reopen --dispatch-root <dispatch-directory>
```

The service exits after its configured no-client idle timeout. A CLOSED snapshot
becomes a terminal static view and the browser stops reconnecting.

## Security and authority

- Bind only `127.0.0.1`; never expose a LAN listener.
- Exchange a one-time bootstrap query token for an HttpOnly SameSite cookie.
- Do not write bootstrap/session tokens into JSON, Markdown, logs, or responses.
- Validate Host, Origin, cookie, WebSocket identity, and a private local control
  token for reopen.
- Apply a local-only Content Security Policy and use DOM `textContent`; never
  inject Project Session output through raw HTML.
- Keep `manifest.json` Manager-single-writer. The server may write only
  replaceable `server-state.json` and `client-state.json` presentation facts.

`server-state.json` records process/port/open state without secrets.
`client-state.json` records connection and the latest visible acknowledged
revision. A successful process launch or HTTP 200 is not proof that the user saw
the board; the acknowledgement is.

## Failure semantics

HTML generation, browser launch, WebSocket, and acknowledgement failures never
change Dispatch business state or block Worker coordination. Preserve the last
static snapshot and report the display limitation. Markdown is the universal
fallback; SVG/PNG are generated only on explicit request or deliberate fallback.
