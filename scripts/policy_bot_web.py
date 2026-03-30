#!/usr/bin/env python3
"""
Simple local web UI for the policy bot.

Run:
  python3 scripts/policy_bot_web.py

Then open:
  http://127.0.0.1:8080
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from query_policy_bot import get_snowflake_connection, run_query


HOST = "127.0.0.1"
PORT = 8080
ROOT_DIR = Path(__file__).resolve().parents[1]
UI_PATH = ROOT_DIR / "ui" / "policy_bot_chat.html"
THEME_PATH = ROOT_DIR / "assets" / "styles" / "block-theme-static.css"


class PolicyBotHandler(BaseHTTPRequestHandler):
    server_version = "PolicyBotWeb/0.1"

    def do_GET(self):  # noqa: N802
        if self.path == "/" or self.path == "/index.html":
            self._serve_file(UI_PATH, "text/html; charset=utf-8")
            return

        if self.path == "/assets/styles/block-theme-static.css":
            self._serve_file(THEME_PATH, "text/css; charset=utf-8")
            return

        if self.path == "/health":
            self._send_json({"ok": True})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self):  # noqa: N802
        if self.path != "/api/query":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            body = json.loads(raw_body.decode("utf-8"))

            question = (body.get("question") or "").strip()
            if not question:
                self._send_json({"error": "Question is required."}, status=HTTPStatus.BAD_REQUEST)
                return

            with get_snowflake_connection() as conn:
                payload = run_query(
                    conn=conn,
                    question=question,
                    document_type=body.get("document_type") or None,
                    domain=body.get("domain") or None,
                    top_k=int(body.get("top_k") or 5),
                    use_llm=bool(body.get("use_llm")),
                    model=body.get("model") or "gpt-5-mini",
                    user_id=body.get("user_id") or "web-user",
                    no_log=bool(body.get("no_log")),
                )

            self._send_json(payload)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format, *args):  # noqa: A003
        return

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), PolicyBotHandler)
    print(f"policy bot web running at http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
