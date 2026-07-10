"""lme-price-mcp: 金属价格行情 MCP Server

提供两个工具：
- get_price(commodity, date): 查询指定商品的当日价格
- get_trend(commodity, days): 查询商品价格走势

真实价格 API 不可用时自动降级到 Mock 数据，保证 demo 可运行。
"""
import os
import sys
import yaml
from datetime import date

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from servers.lme_price_mcp.price_client import PriceClient
from servers.lme_price_mcp.mock_data import MOCK_PRICE, MOCK_TREND


def _load_config() -> dict:
    """加载 sources.yaml 配置"""
    config_path = os.path.join(_PROJECT_ROOT, "configs", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_config = _load_config()
_client = PriceClient(
    api_base=_config["price"]["api_base"],
    timeout=_config["price"]["fetch_timeout"],
    commodities_config=_config["price"]["commodities"],
)

mcp = FastMCP("lme-price-mcp")


@mcp.tool()
async def get_price(commodity: str, date: str) -> dict:
    """查询指定商品的当日价格

    Args:
        commodity: 商品名称（如 lithium, copper）
        date: 日期，格式 YYYY-MM-DD

    Returns:
        价格字典，含 commodity, date, price, unit, currency, source。
        真实 API 不可用时返回 Mock 数据。
    """
    try:
        return await _client.get_price(commodity, date)
    except Exception as e:
        print(f"[lme-price-mcp] 价格查询失败，降级到 Mock 数据: {e}")
        return {
            **MOCK_PRICE,
            "commodity": commodity,
            "date": date,
            "source": "mock-data",
        }


@mcp.tool()
async def get_trend(commodity: str, days: int = 30) -> dict:
    """查询商品价格走势

    Args:
        commodity: 商品名称
        days: 统计天数，默认 30

    Returns:
        趋势字典，含 latest_price, start_price, change_pct, ma_7, ma_30, trend, observations。
        真实 API 不可用时返回 Mock 数据。
    """
    try:
        return await _client.get_trend(commodity, days)
    except Exception as e:
        print(f"[lme-price-mcp] 趋势查询失败，降级到 Mock 数据: {e}")
        return {
            **MOCK_TREND,
            "commodity": commodity,
            "days": days,
        }


if __name__ == "__main__":
    mcp.run()
