# -*- coding: utf-8 -*-
"""
板块数据代理 API - Vercel Serverless Function
"""

from http.server import BaseHTTPRequestHandler
import json
import random
from urllib.parse import parse_qs, urlparse

import requests
import urllib3
urllib3.disable_warnings()

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SECTOR_CATEGORIES = {
    "科技": [
        ("artificial_intelligence", "人工智能", "BK000217"),
        ("semiconductors", "半导体", "BK000054"),
        ("cloud_computing", "云计算", "BK000266"),
        ("fifth_generation", "5G概念", "BK000291"),
        ("optical_modules", "光模块", "BK000651"),
        ("computing_power", "算力", "BK000601"),
        ("generative_ai", "生成式AI", "BK000369"),
    ],
    "新能源": [
        ("new_energy_vehicles", "新能源汽车", "BK000225"),
        ("photovoltaic", "光伏", "BK000146"),
        ("lithium_batteries", "锂电池", "BK000295"),
        ("energy_storage", "储能", "BK000230"),
        ("hydrogen_energy", "氢能源", "BK000227"),
        ("wind_power", "风电", "BK000147"),
    ],
    "医药健康": [
        ("pharmaceutical", "医药", "BK000090"),
        ("medical_devices", "医疗器械", "BK000095"),
    ],
    "金融": [
        ("banking", "银行", "BK000121"),
        ("securities", "证券", "BK000128"),
    ],
    "消费": [
        ("food_beverage", "食品饮料", "BK000074"),
        ("spirits", "白酒", "BK000076"),
    ],
    "工业制造": [
        ("robotics", "机器人", "BK000234"),
        ("humanoid_robots", "人形机器人", "BK000581"),
        ("autonomous_driving", "自动驾驶", "BK000279"),
        ("smart_driving", "智能驾驶", "BK000461"),
        ("defense_military", "国防军工", "BK000156"),
        ("low_altitude_economy", "低空经济", "BK000521"),
    ],
    "周期资源": [
        ("coal", "煤炭", "BK000177"),
        ("steel", "钢铁", "BK000043"),
        ("non_ferrous_metals", "有色金属", "BK000047"),
        ("precious_metals", "贵金属", "BK000050"),
        ("real_estate", "房地产", "BK000105"),
    ]
}


def fetch_sector_performance():
    """获取行业板块资金流向"""
    sectors = []
    
    try:
        response = requests.get(
            "https://push2.eastmoney.com/api/qt/clist/get",
            headers=DEFAULT_HEADERS,
            params={
                "cb": "", "fid": "f62", "po": "1", "pz": "100", "pn": "1",
                "np": "1", "fltt": "2", "invt": "2",
                "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
                "fs": "m:90 t:2",
                "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
            },
            timeout=15, verify=False
        )
        
        data = response.json()
        if data.get("data"):
            for item in data["data"]["diff"]:
                main_flow = round(item["f62"] / 100000000, 2)
                retail_flow = round(item["f84"] / 100000000, 2)
                
                sectors.append({
                    "name": item["f14"],
                    "change_percent": f"{item['f3']}%",
                    "main_flow": f"{main_flow}亿",
                    "main_flow_ratio": f"{round(item['f184'], 2)}%",
                    "retail_flow": f"{retail_flow}亿",
                    "retail_flow_ratio": f"{round(item['f87'], 2)}%"
                })
            
            sectors.sort(key=lambda x: float(x["change_percent"].replace("%", "")), reverse=True)
    
    except Exception as e:
        print(f"获取板块行情失败: {e}")
    
    return sectors


def fetch_sector_funds(sector_code):
    """获取板块基金列表"""
    funds = []
    
    try:
        response = requests.get(
            "https://fund.eastmoney.com/data/FundGuideapi.aspx",
            headers=DEFAULT_HEADERS,
            params={
                "dt": "4", "sd": "", "ed": "", "tp": sector_code,
                "sc": "1n", "st": "desc", "pi": "1", "pn": "500",
                "zf": "diy", "sh": "list", "rnd": str(random.random())
            },
            timeout=30, verify=False
        )
        
        text = response.text.replace("var rankData =", "").strip()
        data = json.loads(text)
        
        for item in data.get("datas", []):
            parts = item.split(",")
            funds.append({
                "code": parts[0] or "---",
                "name": parts[1] or "---",
                "type": parts[3] or "---",
                "date": parts[15] or "---",
                "nav_change": f"{parts[16] or '---'}（{parts[17] or '---'}%）",
                "week_1": f"{parts[5] or '---'}%",
                "month_1": f"{parts[6] or '---'}%",
                "month_3": f"{parts[7] or '---'}%",
                "month_6": f"{parts[8] or '---'}%",
                "year_ytd": f"{parts[4] or '---'}%",
                "year_1": f"{parts[9] or '---'}%",
                "year_2": f"{parts[10] or '---'}%",
                "year_3": f"{parts[11] or '---'}%",
                "since_inception": f"{parts[24] or '---'}%"
            })
    
    except Exception as e:
        print(f"获取板块基金失败: {e}")
    
    return funds


def get_sector_list():
    """获取板块列表"""
    result = []
    for category, sectors in SECTOR_CATEGORIES.items():
        category_sectors = [{"key": s[0], "name": s[1], "code": s[2]} for s in sectors]
        result.append({"category": category, "sectors": category_sectors})
    return result


class handler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self._send_json({})
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        action = params.get('action', [''])[0]
        
        result = {"success": False, "message": "未知操作"}
        
        try:
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
            else:
                result = {"success": False, "message": f"未知操作: {action}"}
        except Exception as e:
            result = {"success": False, "message": str(e)}
        
        self._send_json(result)
    
    def do_POST(self):
        self.do_GET()
