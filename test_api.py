#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 接口测试脚本
测试所有后端代理 API 功能
"""

import sys
import json
sys.path.insert(0, 'api')

print("=" * 60)
print("基金盯盘 PWA - API 测试")
print("=" * 60)

# 测试 1: 基金搜索
print("\n[测试 1] 基金搜索 API")
print("-" * 40)
try:
    from fund import search_fund
    result = search_fund("000217")
    print(f"搜索结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    if result.get("success"):
        print("✅ 基金搜索 API 测试通过")
        fund_key = result.get("fund_key")
    else:
        print("❌ 基金搜索 API 测试失败")
        fund_key = None
except Exception as e:
    print(f"❌ 错误: {e}")
    fund_key = None

# 测试 2: 基金估值
print("\n[测试 2] 基金估值 API")
print("-" * 40)
try:
    from fund import fetch_fund_valuation
    if fund_key:
        result = fetch_fund_valuation("000217", fund_key)
        print(f"估值结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("✅ 基金估值 API 测试通过")
    else:
        print("⚠️ 跳过（缺少 fund_key）")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 3: 全球指数
print("\n[测试 3] 全球指数 API")
print("-" * 40)
try:
    from market import fetch_global_indices
    result = fetch_global_indices()
    print(f"获取到 {len(result)} 个指数:")
    for idx in result[:5]:
        print(f"  - {idx['name']}: {idx['value']} ({idx['change_percent']})")
    if len(result) > 0:
        print("✅ 全球指数 API 测试通过")
    else:
        print("❌ 全球指数 API 测试失败（无数据）")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 4: 成交量趋势
print("\n[测试 4] 成交量趋势 API")
print("-" * 40)
try:
    from market import fetch_volume_trend
    result = fetch_volume_trend(5)
    print(f"获取到 {len(result)} 天数据:")
    for vol in result[:3]:
        print(f"  - {vol['date']}: 总成交 {vol['total_volume']}")
    if len(result) > 0:
        print("✅ 成交量趋势 API 测试通过")
    else:
        print("❌ 成交量趋势 API 测试失败（无数据）")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 5: 板块行情
print("\n[测试 5] 板块行情 API")
print("-" * 40)
try:
    from sector import fetch_sector_performance
    result = fetch_sector_performance()
    print(f"获取到 {len(result)} 个板块:")
    for sector in result[:5]:
        print(f"  - {sector['name']}: {sector['change_percent']} (主力: {sector['main_flow']})")
    if len(result) > 0:
        print("✅ 板块行情 API 测试通过")
    else:
        print("❌ 板块行情 API 测试失败（无数据）")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试 6: 板块基金
print("\n[测试 6] 板块基金 API")
print("-" * 40)
try:
    from sector import fetch_sector_funds
    # 使用人工智能板块代码
    result = fetch_sector_funds("BK000217")
    print(f"获取到 {len(result)} 只基金:")
    for fund in result[:3]:
        print(f"  - {fund['code']} {fund['name']}: 今年来 {fund['year_ytd']}")
    if len(result) > 0:
        print("✅ 板块基金 API 测试通过")
    else:
        print("❌ 板块基金 API 测试失败（无数据）")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
