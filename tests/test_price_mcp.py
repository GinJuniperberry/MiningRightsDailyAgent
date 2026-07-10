"""lme-price-mcp 测试

测试 get_price 和 get_trend 工具，以及价格趋势计算逻辑。
"""
import pytest
import sys
import os

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from servers.lme_price_mcp.mock_data import MOCK_PRICE, MOCK_TREND
from servers.lme_price_mcp.schemas import PriceResponse, TrendResponse


def test_mock_price_structure():
    """测试 Mock 价格数据结构"""
    assert "commodity" in MOCK_PRICE
    assert "date" in MOCK_PRICE
    assert "price" in MOCK_PRICE
    assert "unit" in MOCK_PRICE
    assert "currency" in MOCK_PRICE
    assert "source" in MOCK_PRICE
    assert MOCK_PRICE["price"] > 0


def test_mock_trend_structure():
    """测试 Mock 趋势数据结构"""
    assert "commodity" in MOCK_TREND
    assert "days" in MOCK_TREND
    assert "latest_price" in MOCK_TREND
    assert "start_price" in MOCK_TREND
    assert "change_abs" in MOCK_TREND
    assert "change_pct" in MOCK_TREND
    assert "ma_7" in MOCK_TREND
    assert "ma_30" in MOCK_TREND
    assert "trend" in MOCK_TREND
    assert "observations" in MOCK_TREND

    # 验证趋势计算一致性
    expected_change = MOCK_TREND["latest_price"] - MOCK_TREND["start_price"]
    assert abs(MOCK_TREND["change_abs"] - expected_change) < 0.01

    assert MOCK_TREND["trend"] in ("up", "down", "flat")


def test_price_response_schema():
    """测试 PriceResponse Pydantic 模型"""
    resp = PriceResponse(
        commodity="lithium",
        date="2026-07-09",
        price=105000,
        unit="CNY/t",
        currency="CNY",
        source="test",
    )
    assert resp.price == 105000


def test_trend_response_schema():
    """测试 TrendResponse Pydantic 模型"""
    resp = TrendResponse(
        commodity="lithium",
        days=30,
        latest_price=105000,
        start_price=98000,
        change_abs=7000,
        change_pct=7.14,
        ma_7=103200,
        ma_30=99700,
        trend="up",
        observations=["test"],
    )
    assert resp.trend == "up"
    assert resp.change_pct == 7.14


@pytest.mark.asyncio
async def test_get_price_with_mock_fallback():
    """测试 get_price 在 API 不可用时返回 Mock 数据"""
    from servers.lme_price_mcp.server import get_price

    result = await get_price(commodity="lithium", date="2026-07-09")

    assert "price" in result
    assert result["price"] > 0
    assert result["commodity"] == "lithium"


@pytest.mark.asyncio
async def test_get_trend_with_mock_fallback():
    """测试 get_trend 在 API 不可用时返回 Mock 数据"""
    from servers.lme_price_mcp.server import get_trend

    result = await get_trend(commodity="lithium", days=30)

    assert "trend" in result
    assert result["trend"] in ("up", "down", "flat")
    assert "change_pct" in result
    assert "observations" in result
    assert len(result["observations"]) > 0
