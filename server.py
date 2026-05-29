import http.server
import json
import ssl
import urllib.request
import urllib.error
import os

PORT = 8080
WORKFLOW_BASE = "https://8bgbqk64vy.coze.site"
WORKFLOW_TOKEN = "pat_rXffEzsFW6w9wTJbgIGNVyi1qHJaj4qPBQDs1ZALLP4iAlRMSfniNpze3yWF6Dck"

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/workflow/stream_run":
            target_url = WORKFLOW_BASE + "/stream_run"

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""

            req = urllib.request.Request(
                target_url,
                data=body,
                headers={
                    "Authorization": f"Bearer {WORKFLOW_TOKEN}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(req) as resp:
                    self.send_response(resp.status)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                    self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Connection", "keep-alive")
                    self.send_header("X-Accel-Buffering", "no")
                    self.end_headers()

                    chunk_size = 4096
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
            except urllib.error.HTTPError as e:
                error_body = e.read()
                self.send_response(e.code)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(error_body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.send_response(404)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format, *args):
        if "/api/workflow/" in str(args):
            print(f"[WF] {args[0]}")
        elif "200" in str(args[1]) or "304" in str(args[1]):
            pass
        else:
            super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
    print(f"""
╔══════════════════════════════════════════╗
║   FilmCraft Server                       ║
║   地址: http://localhost:{PORT}              ║
║   工作流: /api/workflow/stream_run        ║
║   按 Ctrl+C 停止                          ║
╚══════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()
