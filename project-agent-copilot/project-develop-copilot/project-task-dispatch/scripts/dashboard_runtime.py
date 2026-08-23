from __future__ import annotations

import argparse
import base64
import hashlib
import http.client
import json
import os
import secrets
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    from dashboard_view import render_dashboard
    from manifest_v2 import load_manifest
except ImportError:  # pragma: no cover
    from .dashboard_view import render_dashboard
    from .manifest_v2 import load_manifest


COOKIE_NAME = "pdc_dashboard"
WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self' ws:; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"


def _atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with temporary.open("wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    for attempt in range(12):
        try:
            os.replace(temporary, path)
            break
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(min(0.01 * (2 ** attempt), 0.2))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def websocket_accept(key: str) -> str:
    digest = hashlib.sha1((key + WS_GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def websocket_text_frame(value: str) -> bytes:
    payload = value.encode("utf-8")
    if len(payload) < 126:
        return bytes((0x81, len(payload))) + payload
    if len(payload) <= 0xFFFF:
        return bytes((0x81, 126)) + struct.pack("!H", len(payload)) + payload
    return bytes((0x81, 127)) + struct.pack("!Q", len(payload)) + payload


def read_websocket_frame(stream: Any) -> tuple[int, bytes] | None:
    header = stream.read(2)
    if len(header) != 2:
        return None
    first, second = header
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", stream.read(2))[0]
    elif length == 127:
        length = struct.unpack("!Q", stream.read(8))[0]
    if length > 1_048_576:
        raise ValueError("websocket frame is too large")
    mask = stream.read(4) if masked else b""
    payload = stream.read(length)
    if len(payload) != length:
        return None
    if masked:
        payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
    return opcode, payload


class DashboardState:
    def __init__(self, dispatch_root: Path, port: int, idle_timeout: int) -> None:
        self.dispatch_root = dispatch_root
        self.live_root = dispatch_root / "views" / "live"
        self.snapshot_path = self.live_root / "snapshot.json"
        self.state_path = self.live_root / "server-state.json"
        self.client_state_path = self.live_root / "client-state.json"
        self.control_path = self.live_root / ".control-token"
        self.port = port
        self.idle_timeout = idle_timeout
        self.bootstrap_token: str | None = secrets.token_urlsafe(32)
        self.session_token = secrets.token_urlsafe(32)
        self.control_token = secrets.token_urlsafe(32)
        self.started_at = _utc_now()
        self.last_activity = time.monotonic()
        self.clients: set[socket.socket] = set()
        self.lock = threading.RLock()
        self.last_snapshot = self.snapshot()
        self.control_path.write_text(self.control_token, encoding="ascii")
        try:
            self.control_path.chmod(0o600)
        except OSError:
            pass

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def snapshot(self) -> dict[str, Any]:
        return _read_json(self.snapshot_path)

    def write_server_state(self, state: str = "running", open_state: str = "not-requested") -> None:
        with self.lock:
            snapshot = self.snapshot()
            _atomic_json(self.state_path, {
                "schemaVersion": "pdc-dashboard-server-2.0",
                "dispatchId": snapshot["dispatchId"],
                "pid": os.getpid(),
                "host": "127.0.0.1",
                "port": self.port,
                "serverState": state,
                "openState": open_state,
                "connectedClients": len(self.clients),
                "lastRenderedRevision": snapshot["revision"],
                "startedAt": self.started_at,
                "updatedAt": _utc_now(),
            })

    def acknowledge(self, payload: dict[str, Any]) -> None:
        with self.lock:
            self.last_activity = time.monotonic()
            _atomic_json(self.client_state_path, {
                "schemaVersion": "pdc-dashboard-client-2.0",
                "dispatchId": self.last_snapshot["dispatchId"],
                "connectedClients": len(self.clients),
                "lastAcknowledgedRevision": payload.get("revision"),
                "visible": bool(payload.get("visible")),
                "lastAcknowledgedAt": _utc_now(),
            })
            self.write_server_state(open_state="acknowledged")

    def add_client(self, connection: socket.socket) -> None:
        with self.lock:
            self.clients.add(connection)
            self.last_activity = time.monotonic()
            self.write_server_state(open_state="connected")

    def remove_client(self, connection: socket.socket) -> None:
        with self.lock:
            self.clients.discard(connection)
            self.write_server_state(open_state="disconnected")

    def broadcast_revision(self, current: dict[str, Any]) -> None:
        previous_sessions = {item["projectSessionKey"]: item for item in self.last_snapshot.get("sessions", [])}
        changed = []
        for item in current.get("sessions", []):
            before = previous_sessions.get(item["projectSessionKey"])
            keys = ("pdcState", "nativeStatus", "attempt", "openFindings", "acceptancePassed", "nextAction")
            if before is None or any(before.get(key) != item.get(key) for key in keys):
                changed.append(item["projectSessionKey"])
        message = json.dumps({
            "type": "revision-available",
            "dispatchId": current["dispatchId"],
            "revision": current["revision"],
            "changedProjectSessionKeys": changed,
            "reason": "snapshot-updated",
        }, ensure_ascii=False)
        frame = websocket_text_frame(message)
        stale = []
        with self.lock:
            for connection in self.clients:
                try:
                    connection.sendall(frame)
                except OSError:
                    stale.append(connection)
            for connection in stale:
                self.clients.discard(connection)
            self.last_snapshot = current
            self.last_activity = time.monotonic()
            self.write_server_state(open_state="connected" if self.clients else "disconnected")


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, address: tuple[str, int], state: DashboardState) -> None:
        super().__init__(address, DashboardHandler)
        self.dashboard = state


class DashboardHandler(BaseHTTPRequestHandler):
    server: DashboardServer

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _host_valid(self) -> bool:
        host = self.headers.get("Host", "")
        return host in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def _origin_valid(self) -> bool:
        return self.headers.get("Origin") in {None, self.server.dashboard.origin, f"http://localhost:{self.server.server_port}"}

    def _authenticated(self) -> bool:
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        value = cookie.get(COOKIE_NAME)
        return value is not None and secrets.compare_digest(value.value, self.server.dashboard.session_token)

    def _headers(self, status: int, content_type: str, length: int = 0) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.end_headers()

    def _reject(self, status: int = HTTPStatus.FORBIDDEN) -> None:
        self._headers(status, "text/plain; charset=utf-8", 0)

    def do_GET(self) -> None:  # noqa: N802
        if not self._host_valid():
            self._reject()
            return
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/bootstrap":
            supplied = urllib.parse.parse_qs(parsed.query).get("token", [""])[0]
            expected = self.server.dashboard.bootstrap_token
            if expected is None or not secrets.compare_digest(supplied, expected):
                self._reject()
                return
            self.server.dashboard.bootstrap_token = None
            self.server.dashboard.last_activity = time.monotonic()
            self.send_response(HTTPStatus.FOUND)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"{COOKIE_NAME}={self.server.dashboard.session_token}; HttpOnly; SameSite=Strict; Path=/")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if not self._authenticated():
            self._reject(HTTPStatus.UNAUTHORIZED)
            return
        if parsed.path == "/ws":
            self._websocket()
            return
        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/index.html": ("index.html", "text/html; charset=utf-8"),
            "/api/snapshot": ("snapshot.json", "application/json; charset=utf-8"),
            "/assets/dashboard.js": ("assets/dashboard.js", "text/javascript; charset=utf-8"),
            "/assets/dashboard.css": ("assets/dashboard.css", "text/css; charset=utf-8"),
        }
        selected = files.get(parsed.path)
        if selected is None:
            self._reject(HTTPStatus.NOT_FOUND)
            return
        path = self.server.dashboard.live_root / selected[0]
        try:
            payload = path.read_bytes()
        except FileNotFoundError:
            self._reject(HTTPStatus.NOT_FOUND)
            return
        self.server.dashboard.last_activity = time.monotonic()
        self._headers(HTTPStatus.OK, selected[1], len(payload))
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        if not self._host_valid():
            self._reject()
            return
        parsed_path = urllib.parse.urlsplit(self.path).path
        if parsed_path == "/api/control/reopen":
            supplied = self.headers.get("X-PDC-Control", "")
            if not secrets.compare_digest(supplied, self.server.dashboard.control_token):
                self._reject()
                return
            self.server.dashboard.bootstrap_token = secrets.token_urlsafe(32)
            token = self.server.dashboard.bootstrap_token
            opened = webbrowser.open(
                f"{self.server.dashboard.origin}/bootstrap?token={urllib.parse.quote(token)}", new=2
            )
            self.server.dashboard.write_server_state(open_state="opened" if opened else "open-failed")
            self._headers(HTTPStatus.NO_CONTENT if opened else HTTPStatus.SERVICE_UNAVAILABLE, "text/plain", 0)
            return
        if not self._origin_valid() or not self._authenticated():
            self._reject()
            return
        if parsed_path != "/api/ack":
            self._reject(HTTPStatus.NOT_FOUND)
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 8192)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict) or type(payload.get("revision")) is not int:
                raise ValueError
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._reject(HTTPStatus.BAD_REQUEST)
            return
        self.server.dashboard.acknowledge(payload)
        self._headers(HTTPStatus.NO_CONTENT, "text/plain", 0)

    def _websocket(self) -> None:
        if not self._origin_valid() or self.headers.get("Upgrade", "").lower() != "websocket":
            self._reject()
            return
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self._reject(HTTPStatus.BAD_REQUEST)
            return
        self.send_response(HTTPStatus.SWITCHING_PROTOCOLS)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", websocket_accept(key))
        self.end_headers()
        connection = self.connection
        self.server.dashboard.add_client(connection)
        current = self.server.dashboard.snapshot()
        connection.sendall(websocket_text_frame(json.dumps({
            "type": "revision-available", "dispatchId": current["dispatchId"],
            "revision": current["revision"], "changedProjectSessionKeys": [], "reason": "connected",
        })))
        try:
            while True:
                frame = read_websocket_frame(self.rfile)
                if frame is None or frame[0] == 0x8:
                    break
                if frame[0] == 0x9:
                    connection.sendall(bytes((0x8A, len(frame[1]))) + frame[1])
                elif frame[0] == 0x1:
                    payload = json.loads(frame[1].decode("utf-8"))
                    if payload.get("type") == "revision-applied":
                        self.server.dashboard.acknowledge(payload)
        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            pass
        finally:
            self.server.dashboard.remove_client(connection)
            self.close_connection = True


def _watch(server: DashboardServer) -> None:
    state = server.dashboard
    while True:
        time.sleep(0.5)
        try:
            current = state.snapshot()
            if current.get("revision") != state.last_snapshot.get("revision") or current != state.last_snapshot:
                state.broadcast_revision(current)
            if not state.clients and time.monotonic() - state.last_activity >= state.idle_timeout:
                state.write_server_state(state="stopped", open_state="idle-timeout")
                server.shutdown()
                return
        except (FileNotFoundError, json.JSONDecodeError):
            continue


def serve(dispatch_root: Path, *, port: int = 0, idle_timeout: int = 1800, open_browser: bool = False) -> None:
    manifest_path = dispatch_root / "manifest.json"
    cache_path = dispatch_root / "runtime-cache.json"
    manifest = load_manifest(manifest_path)
    cache = _read_json(cache_path) if cache_path.exists() else None
    render_dashboard(dispatch_root, manifest, cache)
    provisional = DashboardState(dispatch_root, 0, idle_timeout)
    server = DashboardServer(("127.0.0.1", port), provisional)
    provisional.port = server.server_port
    provisional.write_server_state(open_state="opening" if open_browser else "not-requested")
    watcher = threading.Thread(target=_watch, args=(server,), name="pdc-dashboard-watcher", daemon=True)
    watcher.start()
    if open_browser:
        token = provisional.bootstrap_token
        opened = bool(token) and webbrowser.open(f"{provisional.origin}/bootstrap?token={urllib.parse.quote(token)}", new=2)
        provisional.write_server_state(open_state="opened" if opened else "open-failed")
    try:
        server.serve_forever(poll_interval=0.25)
    finally:
        provisional.write_server_state(state="stopped", open_state="closed")
        server.server_close()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start(dispatch_root: Path, *, idle_timeout: int = 1800, open_browser: bool = True) -> dict[str, Any]:
    state_path = dispatch_root / "views" / "live" / "server-state.json"
    if state_path.exists():
        previous = _read_json(state_path)
        if previous.get("serverState") == "running" and _pid_alive(int(previous.get("pid", 0))):
            if open_browser:
                reopen(dispatch_root)
                previous = _read_json(state_path)
            return previous
    command = [sys.executable, str(Path(__file__).resolve()), "serve", "--dispatch-root", str(dispatch_root), "--idle-timeout", str(idle_timeout)]
    if open_browser:
        command.append("--open-browser")
    kwargs: dict[str, Any] = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True
    before = state_path.stat().st_mtime_ns if state_path.exists() else 0
    subprocess.Popen(command, **kwargs)
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if state_path.exists() and state_path.stat().st_mtime_ns != before:
            state = _read_json(state_path)
            if state.get("serverState") == "running":
                return state
        time.sleep(0.1)
    raise RuntimeError("dashboard server did not become ready")


def reopen(dispatch_root: Path) -> dict[str, Any]:
    live = dispatch_root / "views" / "live"
    state = _read_json(live / "server-state.json")
    control_token = (live / ".control-token").read_text(encoding="ascii")
    connection = http.client.HTTPConnection("127.0.0.1", int(state["port"]), timeout=5)
    connection.request(
        "POST", "/api/control/reopen", body=b"",
        headers={"Host": f"127.0.0.1:{state['port']}", "X-PDC-Control": control_token},
    )
    response = connection.getresponse()
    response.read()
    connection.close()
    if response.status != HTTPStatus.NO_CONTENT:
        raise RuntimeError(f"dashboard browser reopen failed with HTTP {response.status}")
    return _read_json(live / "server-state.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PDC localhost HTML dashboard runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    serve_parser = subparsers.add_parser("serve")
    start_parser = subparsers.add_parser("start")
    reopen_parser = subparsers.add_parser("reopen")
    for item in (render, serve_parser, start_parser, reopen_parser):
        item.add_argument("--dispatch-root", required=True, type=Path)
    for item in (serve_parser, start_parser):
        item.add_argument("--idle-timeout", type=int, default=1800)
    serve_parser.add_argument("--port", type=int, default=0)
    serve_parser.add_argument("--open-browser", action="store_true")
    start_parser.add_argument("--no-open-browser", action="store_true")
    arguments = parser.parse_args(argv)
    if arguments.command == "render":
        manifest = load_manifest(arguments.dispatch_root / "manifest.json")
        cache_path = arguments.dispatch_root / "runtime-cache.json"
        result = render_dashboard(arguments.dispatch_root, manifest, _read_json(cache_path) if cache_path.exists() else None)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if arguments.command == "serve":
        serve(arguments.dispatch_root, port=arguments.port, idle_timeout=arguments.idle_timeout, open_browser=arguments.open_browser)
        return 0
    if arguments.command == "reopen":
        print(json.dumps(reopen(arguments.dispatch_root), ensure_ascii=False))
        return 0
    result = start(arguments.dispatch_root, idle_timeout=arguments.idle_timeout, open_browser=not arguments.no_open_browser)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
