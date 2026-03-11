import http.server
import socketserver
import urllib.request
import json

PORT = 20000
TARGET = "api.kimi.com"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[PROXY] {fmt % args}")

    def do_GET(self):
        try:
            print(f"\n{'=' * 60}")
            print(f"GET: {self.path}")
            req = urllib.request.Request(
                f"https://{TARGET}/coding/v1{self.path}",
                headers={
                    "Authorization": self.headers.get("Authorization", ""),
                    "User-Agent": "KimiCLI/1.12.0",
                },
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in [
                        "transfer-encoding",
                        "content-encoding",
                        "content-length",
                    ]:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
        except Exception as e:
            print(f"GET ERROR: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length > 0 else b""

            print(f"\n{'=' * 60}")
            print(f"POST: {self.path}")
            print(f"BODY: {body.decode('utf-8', errors='replace')[:500]}")

            # 修复请求中的数组 content
            try:
                data = json.loads(body.decode("utf-8"))
                if "messages" in data:
                    for msg in data["messages"]:
                        if isinstance(msg.get("content"), list):
                            texts = [
                                item.get("text", "")
                                for item in msg["content"]
                                if isinstance(item, dict)
                            ]
                            msg["content"] = "".join(texts) if texts else ""
                            print(f"Fixed array content to: {msg['content'][:50]}")

                        # 修复 developer 角色为 system
                        if msg.get("role") == "developer":
                            msg["role"] = "system"
                            print(f"Fixed role: developer -> system")
                body = json.dumps(data).encode("utf-8")
            except Exception as e:
                print(f"Fix error: {e}")

            req = urllib.request.Request(
                f"https://{TARGET}/coding/v1{self.path}",
                data=body,
                headers={
                    "Authorization": self.headers.get("Authorization", ""),
                    "Content-Type": "application/json",
                    "User-Agent": "KimiCLI/1.12.0",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                response_body = resp.read()
                print(
                    f"RESPONSE: {response_body.decode('utf-8', errors='replace')[:200]}"
                )

                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in [
                        "transfer-encoding",
                        "content-encoding",
                        "content-length",
                    ]:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(response_body)
        except Exception as e:
            print(f"POST ERROR: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


print(f"Proxy on port {PORT}")
with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
