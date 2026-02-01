#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地开发服务器
模拟 Vercel 运行环境，用于本地测试
"""

import json
import sys
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 添加 api 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# 导入 API 模块
from fund import search_fund, fetch_fund_valuation
from market import fetch_global_indices, fetch_intraday_index, fetch_volume_trend
from sector import fetch_sector_performance, fetch_sector_funds, get_sector_list

class DevHandler(SimpleHTTPRequestHandler):
    """开发服务器请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 设置静态文件目录
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), 'public'), **kwargs)
    
    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)
        
        # API 路由
        if parsed.path.startswith('/api/'):
            self.handle_api(parsed)
            return
        
        # 静态文件
        super().do_GET()
    
    def handle_api(self, parsed):
        """处理 API 请求"""
        params = parse_qs(parsed.query)
        action = params.get('action', [''])[0]
        
        result = {"success": False, "message": "未知操作"}
        
        try:
            # 基金 API
            if parsed.path == '/api/fund':
                if action == 'search':
                    code = params.get('code', [''])[0]
                    result = search_fund(code) if code else {"success": False, "message": "缺少基金代码"}
                
                elif action == 'valuation':
                    code = params.get('code', [''])[0]
                    fund_key = params.get('fund_key', [''])[0]
                    if code and fund_key:
                        result = {"success": True, "data": fetch_fund_valuation(code, fund_key)}
                    else:
                        result = {"success": False, "message": "缺少参数"}
                
                elif action == 'batch_valuation':
                    funds_str = params.get('funds', [''])[0]
                    if funds_str:
                        valuations = []
                        for item in funds_str.split(','):
                            parts = item.split(':')
                            if len(parts) == 2:
                                code, fund_key = parts
                                val = fetch_fund_valuation(code, fund_key)
                                valuations.append(val)
                        result = {"success": True, "data": valuations}
                    else:
                        result = {"success": False, "message": "缺少基金列表"}
            
            # 市场 API
            elif parsed.path == '/api/market':
                if action == 'indices':
                    result = {"success": True, "data": fetch_global_indices()}
                elif action == 'intraday':
                    count = int(params.get('count', ['20'])[0])
                    result = {"success": True, "data": fetch_intraday_index(count)}
                elif action == 'volume':
                    days = int(params.get('days', ['7'])[0])
                    result = {"success": True, "data": fetch_volume_trend(days)}
            
            # 板块 API
            elif parsed.path == '/api/sector':
                if action == 'performance':
                    result = {"success": True, "data": fetch_sector_performance()}
                elif action == 'funds':
                    code = params.get('code', [''])[0]
                    if code:
                        result = {"success": True, "data": fetch_sector_funds(code)}
                    else:
                        result = {"success": False, "message": "缺少板块代码"}
                elif action == 'list':
                    result = {"success": True, "data": get_sector_list()}
        
        except Exception as e:
            result = {"success": False, "message": str(e)}
        
        # 发送响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    port = 3000
    server = HTTPServer(('0.0.0.0', port), DevHandler)
    
    print("=" * 60)
    print("基金盯盘 PWA - 本地开发服务器")
    print("=" * 60)
    print(f"\n🚀 服务已启动: http://localhost:{port}")
    print(f"📱 移动端访问: http://<你的IP>:{port}")
    print("\n按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
