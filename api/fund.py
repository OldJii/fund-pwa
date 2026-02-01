# -*- coding: utf-8 -*-
"""
基金数据代理 API
解决浏览器 CORS 跨域问题
"""

import json
import re
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings()

# HTTP 请求头
FUND_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://www.fund123.cn",
    "Referer": "https://www.fund123.cn/fund",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# 全局会话和 CSRF Token 缓存
_session = None
_csrf_token = ""
_token_time = 0

def get_session():
    """获取或创建 HTTP 会话"""
    global _session, _csrf_token, _token_time
    
    # Token 有效期 5 分钟
    if _session and _csrf_token and (time.time() - _token_time) < 300:
        return _session, _csrf_token
    
    _session = requests.Session()
    
    try:
        response = _session.get(
            "https://www.fund123.cn/fund",
            headers=FUND_HEADERS,
            timeout=15,
            verify=False
        )
        token_match = re.findall(r'"csrf":"([^"]+)"', response.text)
        if token_match:
            _csrf_token = token_match[0]
            _token_time = time.time()
    except Exception as e:
        print(f"初始化会话失败: {e}")
    
    return _session, _csrf_token


def search_fund(code):
    """搜索基金"""
    session, csrf = get_session()
    
    try:
        response = session.post(
            "https://www.fund123.cn/api/fund/searchFund",
            headers=FUND_HEADERS,
            params={"_csrf": csrf},
            json={"fundCode": code},
            timeout=15,
            verify=False
        )
        data = response.json()
        if data.get("success"):
            return {
                "success": True,
                "fund_key": data["fundInfo"]["key"],
                "fund_name": data["fundInfo"]["fundName"]
            }
    except Exception as e:
        print(f"搜索基金失败: {e}")
    
    return {"success": False, "message": "未找到基金"}


def fetch_fund_detail(code):
    """获取基金日涨幅"""
    session, _ = get_session()
    
    try:
        url = f"https://www.fund123.cn/matiaria?fundCode={code}"
        response = session.get(url, headers=FUND_HEADERS, timeout=15, verify=False)
        
        growth_match = re.findall(r'"dayOfGrowth":"([^"]+)"', response.text)
        date_match = re.findall(r'"netValueDate":"([^"]+)"', response.text)
        
        if growth_match:
            growth_val = round(float(growth_match[0]), 2)
            daily_change = f"{growth_val}%"
            if date_match:
                daily_change = f"{growth_val}%({date_match[0]})"
            return {"daily_change": daily_change}
    except Exception as e:
        print(f"获取基金详情失败: {e}")
    
    return {"daily_change": "N/A"}


def fetch_fund_trend(fund_key):
    """获取基金 30 天趋势"""
    session, csrf = get_session()
    
    try:
        response = session.post(
            "https://www.fund123.cn/api/fund/queryFundQuotationCurves",
            headers=FUND_HEADERS,
            params={"_csrf": csrf},
            json={
                "productId": fund_key,
                "dateInterval": "ONE_MONTH"
            },
            timeout=15,
            verify=False
        )
        
        data = response.json()
        if not data.get("success"):
            return {}
        
        points = [p for p in data["points"] if p["type"] == "fund"]
        if not points:
            return {}
        
        # 分析趋势
        movements = []
        prev_rate = None
        for point in points:
            curr_rate = point["rate"]
            if prev_rate is not None:
                direction = "up" if curr_rate >= prev_rate else "down"
                movements.append((direction, curr_rate))
            prev_rate = curr_rate
        
        movements = movements[::-1]  # 反转为最新在前
        
        if not movements:
            return {}
        
        up_days = sum(1 for m in movements if m[0] == "up")
        total_days = len(movements)
        start_rate = movements[0][1]
        monthly_change = f"{round(start_rate * 100, 2)}%"
        
        # 计算连涨/跌
        streak_count = 1
        streak_direction = movements[0][0]
        end_rate = 0
        
        for i, (direction, rate) in enumerate(movements[1:], 1):
            if direction == streak_direction:
                streak_count += 1
            else:
                end_rate = rate
                break
        
        streak_change = round((start_rate - end_rate) * 100, 2)
        streak_days = -streak_count if streak_direction == "down" else streak_count
        
        return {
            "monthly_up_days": up_days,
            "monthly_total_days": total_days,
            "monthly_change": monthly_change,
            "streak_days": streak_days,
            "streak_change": f"{streak_change}%"
        }
        
    except Exception as e:
        print(f"获取趋势失败: {e}")
    
    return {}


def fetch_fund_estimate(fund_key):
    """获取基金实时估值"""
    session, csrf = get_session()
    
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = session.post(
            "https://www.fund123.cn/api/fund/queryFundEstimateIntraday",
            headers=FUND_HEADERS,
            params={"_csrf": csrf},
            json={
                "startTime": today,
                "endTime": tomorrow,
                "limit": 200,
                "productId": fund_key,
                "format": True,
                "source": "WEALTHBFFWEB"
            },
            timeout=15,
            verify=False
        )
        
        data = response.json()
        if data.get("success") and data.get("list"):
            latest = data["list"][-1]
            estimate_time = datetime.fromtimestamp(latest["time"] / 1000).strftime("%H:%M:%S")
            estimate_val = round(float(latest["forecastGrowth"]) * 100, 2)
            return {
                "estimate_time": estimate_time,
                "estimate_change": f"{estimate_val}%"
            }
    except Exception as e:
        print(f"获取估值失败: {e}")
    
    return {"estimate_time": "N/A", "estimate_change": "N/A"}


def fetch_fund_valuation(code, fund_key):
    """获取基金完整估值数据"""
    result = {
        "code": code,
        "fund_key": fund_key,
        "daily_change": "N/A",
        "estimate_time": "N/A",
        "estimate_change": "N/A",
        "streak_days": 0,
        "streak_change": "0%",
        "monthly_up_days": 0,
        "monthly_total_days": 0,
        "monthly_change": "0%"
    }
    
    # 获取日涨幅
    detail = fetch_fund_detail(code)
    result.update(detail)
    
    # 获取趋势数据
    trend = fetch_fund_trend(fund_key)
    result.update(trend)
    
    # 获取实时估值
    estimate = fetch_fund_estimate(fund_key)
    result.update(estimate)
    
    return result


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
            if action == 'search':
                code = params.get('code', [''])[0]
                if code:
                    result = search_fund(code)
                else:
                    result = {"success": False, "message": "缺少基金代码"}
            
            elif action == 'valuation':
                code = params.get('code', [''])[0]
                fund_key = params.get('fund_key', [''])[0]
                if code and fund_key:
                    result = {"success": True, "data": fetch_fund_valuation(code, fund_key)}
                else:
                    result = {"success": False, "message": "缺少参数"}
            
            elif action == 'batch_valuation':
                # 批量获取估值，参数格式: funds=code1:key1,code2:key2
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
            
            else:
                result = {"success": False, "message": f"未知操作: {action}"}
        
        except Exception as e:
            result = {"success": False, "message": str(e)}
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        self.do_GET()
