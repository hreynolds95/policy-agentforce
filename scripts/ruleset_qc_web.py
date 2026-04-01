#!/usr/bin/env python3
"""
Simple local web UI for ruleset-driven Google Doc QC.

Run:
  python3 scripts/ruleset_qc_web.py

Then open:
  http://127.0.0.1:8090
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from run_ruleset_qc import build_markdown_report, run_ruleset_qc


HOST = "127.0.0.1"
PORT = 8090
ROOT_DIR = Path(__file__).resolve().parents[1]
UI_PATH = ROOT_DIR / "ui" / "ruleset_qc.html"
THEME_PATH = ROOT_DIR / "assets" / "styles" / "block-theme-static.css"
DEFAULT_RULESET_PATH = ROOT_DIR / "rulesets" / "policy_on_policies_qc_ruleset.md"


class RulesetQcHandler(BaseHTTPRequestHandler):
    server_version = "RulesetQcWeb/0.1"

    def do_GET(self):  # noqa: N802
        if self.path == "/" or self.path == "/index.html":
            self._serve_file(UI_PATH, "text/html; charset=utf-8")
            return

        if self.path == "/assets/styles/block-theme-static.css":
            self._serve_file(THEME_PATH, "text/css; charset=utf-8")
            return

        if self.path == "/api/default-ruleset":
            payload = {
                "name": DEFAULT_RULESET_PATH.name,
                "content": DEFAULT_RULESET_PATH.read_text(encoding="utf-8"),
            }
            self._send_json(payload)
            return

        if self.path == "/health":
            self._send_json({"ok": True})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self):  # noqa: N802
        if self.path != "/api/run":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            body = json.loads(raw_body.decode("utf-8"))

            google_doc_url = (body.get("google_doc_url") or "").strip()
            ruleset_text = body.get("ruleset_text") or ""
            if not google_doc_url:
                self._send_json({"error": "Google Doc URL is required."}, status=HTTPStatus.BAD_REQUEST)
                return
            if not ruleset_text.strip():
                self._send_json({"error": "Ruleset markdown is required."}, status=HTTPStatus.BAD_REQUEST)
                return

            payload = run_ruleset_qc(
                google_doc_url=google_doc_url,
                ruleset_text=ruleset_text,
                provider=body.get("provider") or "auto",
                model=body.get("model") or "claude-3-5-sonnet-latest",
                dry_run=bool(body.get("dry_run")),
            )

            report = None
            if not body.get("dry_run"):
                report = build_markdown_report(payload)

            self._send_json(
                {
                    "payload": payload,
                    "report_markdown": report,
                }
            )
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
    httpd = ThreadingHTTPServer((HOST, PORT), RulesetQcHandler)
    print(f"ruleset QC web running at http://{HOST}:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
