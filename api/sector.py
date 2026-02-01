# -*- coding: utf-8 -*-
"""
板块数据代理 API
获取行业板块行情和板块基金
"""

import json
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests

# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings()

# HTTP 请求头
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# 板块代码映射
SECTOR_IDENTIFIERS = {
    "optical_modules": "BK000651",
    "artificial_intelligence": "BK000217",
    "semiconductors": "BK000054",
    "cloud_computing": "BK000266",
    "fifth_generation": "BK000291",
    "new_energy_vehicles": "BK000225",
    "photovoltaic": "BK000146",
    "lithium_batteries": "BK000295",
    "pharmaceutical": "BK000090",
    "medical_devices": "BK000095",
    "banking": "BK000121",
    "securities": "BK000128",
    "real_estate": "BK000105",
    "food_beverage": "BK000074",
    "spirits": "BK000076",
    "defense_military": "BK000156",
    "robotics": "BK000234",
    "humanoid_robots": "BK000581",
    "computing_power": "BK000601",
    "energy_storage": "BK000230",
    "hydrogen_energy": "BK000227",
    "wind_power": "BK000147",
    "coal": "BK000177",
    "steel": "BK000043",
    "non_ferrous_metals": "BK000047",
    "precious_metals": "BK000050",
    "generative_ai": "BK000369",
    "autonomous_driving": "BK000279",
    "smart_driving": "BK000461",
    "low_altitude_economy": "BK000521"
}

# 板块中文名映射
SECTOR_CN_NAMES = {
    "optical_modules": "光模块",
    "artificial_intelligence": "人工智能",
    "semiconductors": "半导体",
    "cloud_computing": "云计算",
    "fifth_generation": "5G概念",
    "new_energy_vehicles": "新能源汽车",
    "photovoltaic": "光伏",
    "lithium_batteries": "锂电池",
    "pharmaceutical": "医药",
    "medical_devices": "医疗器械",
    "banking": "银行",
    "securities": "证券",
    "real_estate": "房地产",
    "food_beverage": "食品饮料",
    "spirits": "白酒",
    "defense_military": "国防军工",
    "robotics": "机器人",
    "humanoid_robots": "人形机器人",
    "computing_power": "算力",
    "energy_storage": "储能",
    "hydrogen_energy": "氢能源",
    "wind_power": "风电",
    "coal": "煤炭",
    "steel": "钢铁",
    "non_ferrous_metals": "有色金属",
    "precious_metals": "贵金属",
    "generative_ai": "生成式AI",
    "autonomous_driving": "自动驾驶",
    "smart_driving": "智能驾驶",
    "low_altitude_economy": "低空经济"
}

# 板块分类
SECTOR_CATEGORIES = {
    "科技": ["artificial_intelligence", "semiconductors", "cloud_computing", "fifth_generation", "optical_modules", "computing_power", "generative_ai"],
    "新能源": ["new_energy_vehicles", "photovoltaic", "lithium_batteries", "energy_storage", "hydrogen_energy", "wind_power"],
    "医药健康": ["pharmaceutical", "medical_devices"],
    "金融": ["banking", "securities"],
    "消费": ["food_beverage", "spirits"],
    "工业制造": ["robotics", "humanoid_robots", "autonomous_driving", "smart_driving", "defense_military", "low_altitude_economy"],
    "周期资源": ["coal", "steel", "non_ferrous_metals", "precious_metals", "real_estate"]
}


def fetch_sector_performance():
    """获取行业板块资金流向"""
    sectors = []
    
    try:
        response = requests.get(
            "https://push2.eastmoney.com/api/qt/clist/get",
            headers=DEFAULT_HEADERS,
            params={
                "cb": "",
                "fid": "f62",
                "po": "1",
                "pz": "100",
                "pn": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
                "fs": "m:90 t:2",
                "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
            },
            timeout=15,
            verify=False
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
            
            # 按涨跌幅排序
            sectors.sort(
                key=lambda x: float(x["change_percent"].replace("%", "")),
                reverse=True
            )
    
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
                "dt": "4",
                "sd": "",
                "ed": "",
                "tp": sector_code,
                "sc": "1n",
                "st": "desc",
                "pi": "1",
                "pn": "500",
                "zf": "diy",
                "sh": "list",
                "rnd": str(random.random())
            },
            timeout=30,
            verify=False
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
        category_sectors = []
        for key in sectors:
            if key in SECTOR_IDENTIFIERS:
                category_sectors.append({
                    "key": key,
                    "name": SECTOR_CN_NAMES.get(key, key),
                    "code": SECTOR_IDENTIFIERS[key]
                })
        if category_sectors:
            result.append({
                "category": category,
                "sectors": category_sectors
            })
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
            if action == 'performance':
                sectors = fetch_sector_performance()
                result = {"success": True, "data": sectors}
            
            elif action == 'funds':
                sector_code = params.get('code', [''])[0]
                if sector_code:
                    funds = fetch_sector_funds(sector_code)
                    result = {"success": True, "data": funds}
                else:
                    result = {"success": False, "message": "缺少板块代码"}
            
            elif action == 'list':
                sectors = get_sector_list()
                result = {"success": True, "data": sectors}
            
            else:
                result = {"success": False, "message": f"未知操作: {action}"}
        
        except Exception as e:
            result = {"success": False, "message": str(e)}
        
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        self.do_GET()
