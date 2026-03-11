#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.error
import hashlib
import random
import json

PORT = 20000  # 新端口
TARGET_HOST = "api.kimi.com"

def generate_device_id():
    return 'opencode-' + hashlib.md5(str(random.randint(10000000, 99999999)).encode()).hexdigest()[:8]

class KimiProxyHandler(http.server.BaseHTTPRequestHandler):
    device_id = generate_device_id()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")
    
    def _fix_request_messages(self, body):
        try:
            if not body:
                return body
            data = json.loads(body.decode('utf-8'))
            if 'messages' in data:
                for msg in data['messages']:
                    # 转换数组 content 为字符串
                    if isinstance(msg.get('content'), list):
                        texts = []
                        for item in msg['content']:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                texts.append(item.get('text', ''))
                        msg['content'] = ''.join(texts) if texts else ''
            return json.dumps(data).encode('utf-8')
        except Exception as e:
            print(f"⚠️  请求修复失败: {e}")
            return body
    
    def _fix_response_content(self, body):
        try:
            data = json.loads(body.decode('utf-8'))
            if 'choices' in data:
                for choice in data['choices']:
                    if 'message' in choice:
                        msg = choice['message']
                        if not msg.get('content') or msg.get('content') == '':
                            if msg.get('reasoning_content'):
                                msg['content'] = msg['reasoning_content'][:200]
                            else:
                                msg['content'] = '...'
                        if isinstance(msg.get('content'), list):
                            msg['content'] = ''.join([c.get('text', '') for c in msg['content'] if isinstance(c, dict)])
            return json.dumps(data).encode('utf-8')
        except Exception as e:
            print(f"⚠️  响应修复失败: {e}")
            return body
    
    def do_POST(self):
        try:
            target_url = f'https://{TARGET_HOST}/coding/v1{self.path}'
            headers = {
                'User-Agent': 'KimiCLI/1.12.0',
                'X-Msh-Platform': 'kimi_cli',
                'X-Msh-Version': '1.12.0',
                'X-Msh-Device-Id': self.device_id,
                'X-Msh-Device-Model': 'Windows_PC',
                'X-Msh-App-Name': 'KimiCLI',
                'X-Msh-App-Version': '1.12.0',
                'X-Msh-App-Channel': 'pypi',
                'X-Msh-Locale': 'zh-CN',
                'X-Msh-Timezone': 'Asia/Shanghai',
            }
            
            auth_header = self.headers.get('Authorization')
            if auth_header:
                headers['Authorization'] = auth_header
            
            content_type = self.headers.get('Content-Type')
            if content_type:
                headers['Content-Type'] = content_type
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            if body and '/chat/completions' in self.path:
                body = self._fix_request_messages(body)
            
            req = urllib.request.Request(url=target_url, data=body, headers=headers, method='POST')
            
            print(f"➡️  POST {target_url}")
            with urllib.request.urlopen(req, timeout=300) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                        self.send_header(key, value)
                self.end_headers()
                response_body = response.read()
                if '/chat/completions' in self.path:
                    response_body = self._fix_response_content(response_body)
                self.wfile.write(response_body)
                print(f"✅ {response.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def do_GET(self):
        try:
            target_url = f'https://{TARGET_HOST}/coding/v1{self.path}'
            headers = {
                'User-Agent': 'KimiCLI/1.12.0',
                'X-Msh-Platform': 'kimi_cli',
                'X-Msh-Version': '1.12.0',
                'X-Msh-Device-Id': self.device_id,
                'Authorization': self.headers.get('Authorization', '')
            }
            
            req = urllib.request.Request(url=target_url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

print(f"🚀 Kimi 代理 (端口 {PORT})")
print("=" * 50)
with socketserver.ThreadingTCPServer(("", PORT), KimiProxyHandler) as httpd:
    print(f"✅ 代理运行中: http://localhost:{PORT}")
    httpd.serve_forever()
