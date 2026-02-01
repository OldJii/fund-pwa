# -*- coding: utf-8 -*-
"""
市场数据代理 API
获取全球指数、成交量等市场数据
"""

import json
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings()

# HTTP 请求头
MARKET_HEADERS = {
    "Accept": "application/vnd.finance-web.v1+json",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Origin": "https://gushitong.baidu.com",
    "Referer": "https://gushitong.baidu.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def fetch_global_indices():
    """获取全球市场指数"""
    indices = []
    
    try:
        session = requests.Session()
        session.headers.update(MARKET_HEADERS)
        
        # 初始化会话
        session.get("https://gushitong.baidu.com/index/ab-000001", timeout=10, verify=False)
        
        # 获取亚洲和美洲市场
        for market in ["asia", "america"]:
            url = f"https://finance.pae.baidu.com/api/getbanner?market={market}&finClientType=pc"
            response = session.get(url, timeout=15, verify=False)
            data = response.json()
            
            if data.get("ResultCode") == "0":
                for item in data["Result"]["list"]:
                    indices.append({
                        "name": item["name"],
                        "value": item["lastPrice"],
                        "change_percent": item["ratio"]
                    })
        
        # 获取创业板指
        response = session.get(
            "https://finance.pae.baidu.com/vapi/v1/getquotation",
            params={
                "srcid": "5353",
                "all": "1",
                "pointType": "string",
                "group": "quotation_index_minute",
                "query": "399006",
                "code": "399006",
                "market_type": "ab",
                "newFormat": "1",
                "name": "创业板指",
                "finClientType": "pc"
            },
            timeout=15,
            verify=False
        )
        
        data = response.json()
        if str(data.get("ResultCode")) == "0":
            cur = data["Result"]["cur"]
            chinext = {
                "name": "创业板指",
                "value": cur["price"],
                "change_percent": cur["ratio"]
            }
            # 插入到第三位
            if len(indices) >= 2:
                indices.insert(2, chinext)
            else:
                indices.append(chinext)
    
    except Exception as e:
        print(f"获取指数失败: {e}")
    
    return indices


def fetch_intraday_index(count=20):
    """获取上证指数分时数据"""
    points = []
    
    try:
        session = requests.Session()
        session.headers.update(MARKET_HEADERS)
        session.get("https://gushitong.baidu.com/index/ab-000001", timeout=10, verify=False)
        
        response = session.get(
            "https://finance.pae.baidu.com/vapi/v1/getquotation",
            params={
                "srcid": "5353",
                "all": "1",
                "pointType": "string",
                "group": "quotation_index_minute",
                "query": "000001",
                "code": "000001",
                "market_type": "ab",
                "newFormat": "1",
                "name": "上证指数",
                "finClientType": "pc"
            },
            timeout=15,
            verify=False
        )
        
        data = response.json()
        if str(data.get("ResultCode")) == "0":
            market_data = data["Result"]["newMarketData"]["marketData"][0]["p"]
            raw_points = market_data.split(";")[-count:]
            
            for raw in raw_points:
                parts = raw.split(",")[1:]
                if len(parts) >= 6:
                    volume = round(float(parts[4]) / 10000, 2)
                    turnover = round(float(parts[5]) / 100000000, 2)
                    
                    points.append({
                        "time": parts[0],
                        "price": parts[1],
                        "change_amount": parts[2],
                        "change_percent": f"{parts[3]}%",
                        "volume": f"{volume}万手",
                        "turnover": f"{turnover}亿"
                    })
    
    except Exception as e:
        print(f"获取分时数据失败: {e}")
    
    return points


def fetch_volume_trend(days=7):
    """获取成交量趋势"""
    volumes = []
    
    try:
        session = requests.Session()
        session.headers.update(MARKET_HEADERS)
        session.get("https://gushitong.baidu.com/index/ab-000001", timeout=10, verify=False)
        
        response = session.get(
            "https://finance.pae.baidu.com/sapi/v1/metrictrend",
            params={
                "financeType": "index",
                "market": "ab",
                "code": "000001",
                "targetType": "market",
                "metric": "amount",
                "finClientType": "pc"
            },
            timeout=15,
            verify=False
        )
        
        data = response.json()
        if str(data.get("ResultCode")) == "0":
            trend = data["Result"]["trend"]
            today = datetime.now()
            dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days + 1)]
            
            for date in dates:
                total_data = next((x for x in trend[0]["content"] if x["marketDate"] == date), None)
                sh_data = next((x for x in trend[1]["content"] if x["marketDate"] == date), None)
                sz_data = next((x for x in trend[2]["content"] if x["marketDate"] == date), None)
                bj_data = next((x for x in trend[3]["content"] if x["marketDate"] == date), None)
                
                if all([total_data, sh_data, sz_data, bj_data]):
                    volumes.append({
                        "date": date,
                        "total_volume": f"{total_data['data']['amount']}亿",
                        "shanghai_volume": f"{sh_data['data']['amount']}亿",
                        "shenzhen_volume": f"{sz_data['data']['amount']}亿",
                        "beijing_volume": f"{bj_data['data']['amount']}亿"
                    })
    
    except Exception as e:
        print(f"获取成交量失败: {e}")
    
    return volumes


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        action = params.get('action', [''])[0]
        
        result = {"success": False, "message": "未知操作"}
        
        try:
            if action == 'indices':
                indices = fetch_global_indices()
                result = {"success": True, "data": indices}
            
            elif action == 'intraday':
                count = int(params.get('count', ['20'])[0])
                points = fetch_intraday_index(count)
                result = {"success": True, "data": points}
            
            elif action == 'volume':
                days = int(params.get('days', ['7'])[0])
                volumes = fetch_volume_trend(days)
                result = {"success": True, "data": volumes}
            
            else:
                result = {"success": False, "message": f"未知操作: {action}"}
        
        except Exception as e:
            result = {"success": False, "message": str(e)}
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        self.do_GET()
