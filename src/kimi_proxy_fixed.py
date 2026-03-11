#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.error
import hashlib
import random
import json
import sys

PORT = 8080
TARGET_HOST = "api.kimi.com"

def generate_device_id():
    return 'opencode-' + hashlib.md5(str(random.randint(10000000, 99999999)).encode()).hexdigest()[:8]

class KimiProxyHandler(http.server.BaseHTTPRequestHandler):
    device_id = generate_device_id()
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")
    
    def do_GET(self):
        self._proxy_request('GET')
    
    def do_POST(self):
        self._proxy_request('POST')
    
    def _proxy_request(self, method):
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
            
            req = urllib.request.Request(
                url=target_url,
                data=body,
                headers=headers,
                method=method
            )
            
            print(f"➡️  {method} {target_url}")
            with urllib.request.urlopen(req, timeout=300) as response:
                self.send_response(response.status)
                
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding', 'content-length']:
                        self.send_header(key, value)
                
                self.end_headers()
                
                # 读取完整响应
                response_body = response.read()
                
                # 修复 chat completions 响应中的空 content
                if '/chat/completions' in self.path and b'choices' in response_body:
                    try:
                        data = json.loads(response_body.decode('utf-8'))
                        if 'choices' in data:
                            for choice in data['choices']:
                                if 'message' in choice:
                                    msg = choice['message']
                                    # 关键修复：确保 content 不为空
                                    if not msg.get('content') or msg.get('content') == '':
                                        if msg.get('reasoning_content'):
                                            msg['content'] = '[思考中...] ' + msg['reasoning_content'][:100]
                                        else:
                                            msg['content'] = '...'
                                        print(f"🔧 修复空 content")
                        response_body = json.dumps(data).encode('utf-8')
                    except Exception as e:
                        print(f"⚠️  修复失败: {e}")
                
                self.wfile.write(response_body)
                print(f"✅ {response.status}")
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error: {e.code}")
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Proxy Error: {str(e)}".encode())

def main():
    print("🚀 OpenClaw Kimi 代理（已修复空 content）")
    print("=" * 50)
    print(f"📝 设备ID: {KimiProxyHandler.device_id}")
    print(f"🌐 端口: {PORT}")
    print()
    
    with socketserver.ThreadingTCPServer(("", PORT), KimiProxyHandler) as httpd:
        print(f"✅ 代理运行中: http://localhost:{PORT}")
        print("⚠️  按 Ctrl+C 停止")
        print()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 已停止")

if __name__ == '__main__':
    main()
