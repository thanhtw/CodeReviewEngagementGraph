#!/usr/bin/env python3
"""
ProgEdu Review 專用本地服務器 - 修復JSON響應問題
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
    """自定義請求處理器，支援 CORS 和正確的 JSON 處理"""
    
    def __init__(self, *args, **kwargs):
        # 確保在正確的目錄下運行
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def do_GET(self):
        """處理 GET 請求"""
        # URL 解碼
        path = unquote(self.path)
        
        # 移除查詢參數
        if '?' in path:
            path = path.split('?')[0]
        
        print(f"🌐 收到請求: {path}")
        
        # 特殊處理 JSON 文件 - 在其他處理之前
        if (path.endswith('.json') or 'visualization_data.json' in path):
            print(f"📊 JSON請求: {path}")
            self._serve_json_only(path)
            return
        
        # 根目錄重定向到 static
        if path == '/':
            self.send_response(301)
            self.send_header('Location', '/static/')
            self._add_cors_headers()
            self.end_headers()
            return
            
        # 處理 static 目錄的索引
        if path == '/static/' or path == '/static':
            self._list_static_directory()
            return
        
        # 對於其他所有文件，調用父類方法
        print(f"📄 標準處理: {path}")
        try:
            super().do_GET()
        except Exception as e:
            print(f"❌ 標準處理失敗 {path}: {e}")
            self.send_error(404, f"File not found: {path}")

    def _serve_json_only(self, path):
        """專門處理JSON文件，返回純JSON數據"""
        try:
            print(f"🔧 處理JSON: {path}")
            
            # 構建完整的文件路徑
            if path.startswith('/'):
                file_path = path[1:]
            else:
                file_path = path
            
            full_path = os.path.join(BASE_DIR, file_path)
            print(f"📂 文件路徑: {full_path}")
            
            if not os.path.exists(full_path):
                print(f"❌ 文件不存在: {full_path}")
                self._send_json_error(404, "JSON file not found")
                return
            
            # 讀取JSON文件
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📊 JSON大小: {len(content)} 字符")
            
            # 驗證JSON格式
            try:
                json.loads(content)
                print("✅ JSON格式驗證通過")
            except json.JSONDecodeError as e:
                print(f"❌ JSON格式錯誤: {e}")
                self._send_json_error(500, f"Invalid JSON: {e}")
                return
            
            # 發送純JSON響應
            self._send_pure_json(content)
            print("✅ JSON響應發送成功")
            
        except Exception as e:
            print(f"❌ JSON處理失敗: {e}")
            import traceback
            traceback.print_exc()
            self._send_json_error(500, f"Server error: {e}")

    def _send_pure_json(self, json_content):
        """發送純JSON內容，不包含多餘的HTTP頭"""
        try:
            content_bytes = json_content.encode('utf-8')
            
            # 構建最簡潔的HTTP響應
            response_parts = [
                "HTTP/1.0 200 OK",
                "Content-Type: application/json; charset=utf-8",
                f"Content-Length: {len(content_bytes)}",
                "Access-Control-Allow-Origin: *",
                "Access-Control-Allow-Methods: GET, POST, OPTIONS",
                "Access-Control-Allow-Headers: Content-Type",
                "",  # 空行分隔頭和體
                ""   # 這裡會被JSON內容替換
            ]
            
            # 發送響應頭
            response_headers = "\r\n".join(response_parts[:-1]) + "\r\n"
            self.wfile.write(response_headers.encode('utf-8'))
            
            # 發送JSON內容
            self.wfile.write(content_bytes)
            self.wfile.flush()
            
        except Exception as e:
            print(f"❌ 發送JSON響應失敗: {e}")

    def _send_json_error(self, status_code, message):
        """發送JSON格式的錯誤響應"""
        try:
            error_json = json.dumps({"error": message, "status": status_code})
            content_bytes = error_json.encode('utf-8')
            
            response_parts = [
                f"HTTP/1.0 {status_code} Error",
                "Content-Type: application/json; charset=utf-8",
                f"Content-Length: {len(content_bytes)}",
                "Access-Control-Allow-Origin: *",
                "",
                ""
            ]
            
            response_headers = "\r\n".join(response_parts[:-1]) + "\r\n"
            self.wfile.write(response_headers.encode('utf-8'))
            self.wfile.write(content_bytes)
            self.wfile.flush()
            
        except Exception as e:
            print(f"❌ 發送錯誤響應失敗: {e}")

    def _add_cors_headers(self):
        """添加CORS頭"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def end_headers(self):
        """覆寫 end_headers 添加 CORS 支持"""
        self._add_cors_headers()
        super().end_headers()

    def _list_static_directory(self):
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
                <div class="alert alert-success">
                    <strong>✅ JSON修復完成!</strong> 現在可以正常載入視覺化數據
                </div>
                <h2>📁 主要頁面</h2>
                <ul class="file-list">
            """
            
            # 分類文件
            html_files = [f for f in files if f.endswith('.html')]
            js_files = [f for f in files if f.endswith('.js')]
            json_files = [f for f in files if f.endswith('.json')]
            
            # 重要頁面優先顯示
            important_pages = [
                ('visualizationAnalysis.html', '📊 視覺化分析 (主要功能)'),
                ('test_json_load.html', '🔍 JSON載入測試'),
                ('academicTables.html', '📋 學術表格'),
                ('multipleRegressionReport.html', '📈 多元回歸報告')
            ]
            
            for page, description in important_pages:
                if page in html_files:
                    html_content += f'<li><a href="/static/{page}" class="html-file">{description}</a></li>\n'
                    html_files.remove(page)
            
            # 其他HTML文件
            for file in sorted(html_files):
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
                <footer style="margin-top: 40px; color: #666;">
                    <p>🚀 服務器運行成功，JSON問題已修復</p>
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
            print(f"🎓 ProgEdu Review 服務器啟動成功! (JSON修復版)")
            print(f"📡 地址: http://127.0.0.1:{port}")
            print(f"📁 根目錄: {os.getcwd()}")
            print(f"🌐 主頁面: http://127.0.0.1:{port}/static/")
            print(f"📊 視覺化分析: http://127.0.0.1:{port}/static/visualizationAnalysis.html")
            print(f"🔍 JSON測試: http://127.0.0.1:{port}/static/test_json_load.html")
            print(f"🔗 網路圖: http://127.0.0.1:{port}/static/3label.html")
            print(f"\n✅ JSON載入問題已修復!")
            print("按 Ctrl+C 停止服務器")
            
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
