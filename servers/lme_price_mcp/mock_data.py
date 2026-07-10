"""lme-price-mcp Mock 兜底数据

当真实价格 API 不可用时，使用这些样例数据保证 demo 可运行。
价格数据基于 2026 年锂矿市场的模拟值。
"""

MOCK_PRICE = {
    "commodity": "lithium",
    "date": "2026-07-09",
    "price": 105000,
    "unit": "CNY/t",
    "currency": "CNY",
    "source": "mock-data"
}

MOCK_TREND = {
    "commodity": "lithium",
    "days": 30,
    "latest_price": 105000,
    "start_price": 98000,
    "change_abs": 7000,
    "change_pct": 7.14,
    "ma_7": 103200,
    "ma_30": 99700,
    "trend": "up",
    "observations": [
        "近 30 天价格上涨 7.14%",
        "当前价格高于 7 日均线和 30 日均线",
        "短期趋势偏强，需关注下游需求持续性"
    ]
}
