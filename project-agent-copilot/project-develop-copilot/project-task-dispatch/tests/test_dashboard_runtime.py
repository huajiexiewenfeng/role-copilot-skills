from __future__ import annotations

import http.client
import json
import struct
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import dashboard_runtime
import dashboard_view
from v2_fixture import make_manifest


class DashboardRuntimeTest(unittest.TestCase):
    def test_websocket_helpers_follow_rfc_example(self) -> None:
        self.assertEqual(
            dashboard_runtime.websocket_accept("dGhlIHNhbXBsZSBub25jZQ=="),
            "s3pPLMBiTxaQ9kYGzzhZRbK+xOo=",
        )
        short = dashboard_runtime.websocket_text_frame("ok")
        self.assertEqual(short, b"\x81\x02ok")
        medium = dashboard_runtime.websocket_text_frame("x" * 126)
        self.assertEqual(medium[:4], b"\x81\x7e" + struct.pack("!H", 126))

    def test_loopback_server_exchanges_one_time_token_and_records_ack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dashboard_view.render_dashboard(root, make_manifest())
            state = dashboard_runtime.DashboardState(root, 0, 60)
            server = dashboard_runtime.DashboardServer(("127.0.0.1", 0), state)
            state.port = server.server_port
            state.write_server_state()
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                connection.request("GET", f"/bootstrap?token={state.bootstrap_token}", headers={"Host": f"127.0.0.1:{server.server_port}"})
                response = connection.getresponse()
                self.assertEqual(response.status, 302)
                cookie = response.getheader("Set-Cookie").split(";", 1)[0]
                response.read()

                connection.request("GET", "/", headers={"Host": f"127.0.0.1:{server.server_port}", "Cookie": cookie})
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn("default-src 'self'", response.getheader("Content-Security-Policy"))
                self.assertIn("PDC 任务分发实时看板", response.read().decode("utf-8"))

                body = json.dumps({"revision": 0, "visible": True}).encode("utf-8")
                connection.request("POST", "/api/ack", body=body, headers={
                    "Host": f"127.0.0.1:{server.server_port}", "Cookie": cookie,
                    "Origin": state.origin, "Content-Type": "application/json",
                })
                response = connection.getresponse()
                self.assertEqual(response.status, 204)
                response.read()
                recorded = json.loads(state.client_state_path.read_text(encoding="utf-8"))
                self.assertEqual(recorded["lastAcknowledgedRevision"], 0)
                self.assertTrue(recorded["visible"])
                public_state = state.state_path.read_text(encoding="utf-8")
                self.assertNotIn(state.session_token, public_state)
                self.assertNotIn(state.control_token, public_state)

                with patch.object(dashboard_runtime.webbrowser, "open", return_value=True):
                    connection.request("POST", "/api/control/reopen", body=b"", headers={
                        "Host": f"127.0.0.1:{server.server_port}", "X-PDC-Control": state.control_token,
                    })
                    response = connection.getresponse()
                    self.assertEqual(response.status, 204)
                    response.read()
                    self.assertIsNotNone(state.bootstrap_token)

                connection.request("GET", "/bootstrap?token=wrong", headers={"Host": f"127.0.0.1:{server.server_port}"})
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
