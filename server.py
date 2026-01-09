#!/usr/bin/env python3
"""
ProgEdu Review 專用本地服務器
解決靜態文件服務和 CORS 問題
"""

import http.server
import socketserver
import os
import sys
import mimetypes
from urllib.parse import unquote
import json

# 使用當前腳本所在目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ProgEduHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定義請求處理器，支援 CORS 和正確的 MIME 類型"""
    
    def __init__(self, *args, **kwargs):
        # 確保在正確的目錄下運行
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def end_headers(self):
        """添加 CORS 標頭"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def guess_type(self, path):
        """確保 JSON 文件有正確的 MIME 類型"""
        base, ext = os.path.splitext(path.lower())
        if ext == '.json':
            return 'application/json'
        return super().guess_type(path)

    def do_GET(self):
        """處理 GET 請求"""
        # URL 解碼
        path = unquote(self.path)
        
        # 移除查詢參數
        if '?' in path:
            path = path.split('?')[0]
        
        print(f"🌐 收到請求: {path}")
        
        # 根目錄重定向到 static
        if path == '/':
            self.send_response(301)
            self.send_header('Location', '/static/')
            self.end_headers()
            return
            
        # 處理 static 目錄的索引
        if path == '/static/' or path == '/static':
            self.list_static_directory()
            return
        
        # 特殊處理 JSON 文件 - 精確匹配
        if (path.endswith('.json') or 
            '/visualization_data.json' in path or
            path == '/static/visualization_data.json'):
            print(f"📊 檢測到JSON請求: {path}")
            self.serve_json_file(path)
            return
        
        # 對於其他所有文件，調用父類方法
        print(f"📄 使用標準處理: {path}")
        try:
            super().do_GET()
        except Exception as e:
            print(f"❌ 標準處理失敗 {path}: {e}")
            self.send_error(404, f"File not found: {path}")

    def serve_json_file(self, path):
        """專門處理 JSON 文件的方法 - 使用標準方法但確保純JSON輸出"""
        try:
            print(f"🔧 處理JSON請求: {path}")
            
            # 構建完整的文件路徑
            if path.startswith('/'):
                file_path = path[1:]  # 移除開頭的 /
            else:
                file_path = path
            
            full_path = os.path.join(BASE_DIR, file_path)
            print(f"📂 完整路徑: {full_path}")
            
            if not os.path.exists(full_path):
                print(f"❌ 文件不存在: {full_path}")
                self.send_error(404, f"JSON file not found: {path}")
                return
            
            # 讀取 JSON 文件
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📊 JSON文件大小: {len(content)} 字符")
            
            # 驗證JSON格式
            try:
                import json
                json.loads(content)  # 驗證JSON格式
                print(f"✅ JSON格式驗證通過")
            except json.JSONDecodeError as e:
                print(f"❌ JSON格式錯誤: {e}")
                self.send_error(500, f"Invalid JSON format: {e}")
                return
            
            # 使用標準方法發送響應
            content_bytes = content.encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(content_bytes)))
            # 手動添加CORS頭，避免使用 end_headers() 中的自動添加
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # 結束頭部
            self.wfile.write(b'\r\n')
            
            # 發送JSON內容
            self.wfile.write(content_bytes)
            self.wfile.flush()
            
            print(f"✅ JSON 文件服務成功: {path}")
            
        except Exception as e:
            print(f"❌ JSON 文件服務失敗: {path}, 錯誤: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Error serving JSON file: {e}")

    def end_headers(self):
        """重寫 end_headers 以避免重複的頭部"""
        # 對於JSON請求，不調用此方法
        if hasattr(self, '_json_request'):
            return
        
        # 對於其他請求，添加 CORS 標頭
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def list_static_directory(self):
        """列出 static 目錄內容"""
        try:
            static_path = os.path.join(BASE_DIR, "static")
            files = os.listdir(static_path)
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>ProgEdu Review - 文件目錄</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    h1 { color: #333; }
                    .file-list { list-style: none; padding: 0; }
                    .file-list li { margin: 10px 0; }
                    .file-list a { 
                        text-decoration: none; 
                        color: #0066cc; 
                        padding: 8px 12px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        display: inline-block;
                        min-width: 200px;
                    }
                    .file-list a:hover { background: #f0f8ff; }
                    .html-file { background: #e8f5e8; }
                    .js-file { background: #fff8e1; }
                    .json-file { background: #f3e5f5; }
                </style>
            </head>
            <body>
                <h1>🎓 ProgEdu Review - 文件目錄</h1>
                <h2>📁 主要頁面</h2>
                <ul class="file-list">
            """
            
            # 分類文件
            html_files = [f for f in files if f.endswith('.html')]
            js_files = [f for f in files if f.endswith('.js')]
            json_files = [f for f in files if f.endswith('.json')]
            
            # HTML 文件
            for file in sorted(html_files):
                if file != 'index.html':  # index.html 放最前面
                    html_content += f'<li><a href="/static/{file}" class="html-file">📄 {file}</a></li>\n'
            
            html_content += """
                </ul>
                <h2>📁 數據文件</h2>
                <ul class="file-list">
            """
            
            # JSON 文件
            for file in sorted(json_files):
                html_content += f'<li><a href="/static/{file}" class="json-file">📊 {file}</a></li>\n'
            
            html_content += """
                </ul>
                <h2>📁 腳本文件</h2>
                <ul class="file-list">
            """
            
            # JS 文件
            for file in sorted(js_files):
                html_content += f'<li><a href="/static/{file}" class="js-file">⚙️ {file}</a></li>\n'
            
            html_content += """
                </ul>
                <footer style="margin-top: 40px; color: #666;">
                    <p>🚀 服務器運行於: http://127.0.0.1:8000</p>
                </footer>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error listing directory: {e}")

    def log_message(self, format, *args):
        """自定義日誌格式"""
        print(f"[{self.date_time_string()}] {format % args}")

def start_server(port=8000):
    """啟動服務器"""
    try:
        # 切換到正確的工作目錄
        os.chdir(BASE_DIR)
        
        with socketserver.TCPServer(("", port), ProgEduHTTPRequestHandler) as httpd:
            print(f"🎓 ProgEdu Review 服務器啟動成功!")
            print(f"📡 地址: http://127.0.0.1:{port}")
            print(f"📁 根目錄: {os.getcwd()}")
            print(f"🌐 主頁面: http://127.0.0.1:{port}/static/")
            print(f"📊 視覺化分析: http://127.0.0.1:{port}/static/visualizationAnalysis.html")
            print(f"🔗 網路圖: http://127.0.0.1:{port}/static/3label.html")
            print("\n按 Ctrl+C 停止服務器")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 服務器已停止")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ 端口 {port} 已被占用，嘗試使用端口 {port + 1}")
            start_server(port + 1)
        else:
            print(f"❌ 服務器啟動失敗: {e}")
    except Exception as e:
        print(f"❌ 意外錯誤: {e}")

if __name__ == "__main__":
    # 檢查是否指定了端口
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ 端口號必須是數字")
            sys.exit(1)
    
    start_server(port)
