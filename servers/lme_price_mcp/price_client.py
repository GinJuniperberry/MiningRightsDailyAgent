"""价格数据客户端

尝试从真实价格 API 获取数据，失败时生成基于配置基准价的模拟价格序列。

趋势计算使用 pandas：
- change_pct: 涨跌幅
- ma_7 / ma_30: 7 日 / 30 日均线
- trend: 趋势判断（up/down/flat）
"""
import httpx
import pandas as pd
import random
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List


class PriceClient:
    """价格查询客户端"""

    def __init__(self, api_base: str, timeout: int = 10,
                 commodities_config: Dict[str, Any] = None):
        self.api_base = api_base
        self.timeout = timeout
        self.commodities_config = commodities_config or {}

    async def get_price(self, commodity: str, date: str) -> Dict[str, Any]:
        """查询指定日期的商品价格

        Args:
            commodity: 商品名称（如 lithium）
            date: 日期，格式 YYYY-MM-DD

        Returns:
            价格字典，含 commodity, date, price, unit, currency, source

        Raises:
            Exception: API 不可用时抛出，由 server.py 降级到 Mock
        """
        url = f"{self.api_base}/{commodity}/{date}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        # 标准化返回格式
        return {
            "commodity": commodity,
            "date": date,
            "price": float(data.get("price", 0)),
            "unit": data.get("unit", self._get_unit(commodity)),
            "currency": data.get("currency", "CNY"),
            "source": data.get("source", "price-api"),
        }

    async def get_trend(self, commodity: str, days: int) -> Dict[str, Any]:
        """计算价格趋势：涨跌幅、均线、趋势判断

        Args:
            commodity: 商品名称
            days: 统计天数

        Returns:
            趋势字典，含 latest_price, start_price, change_pct, ma_7, ma_30, trend, observations

        Raises:
            Exception: API 不可用时抛出，由 server.py 降级到 Mock
        """
        # 尝试从 API 获取历史价格
        history = await self._fetch_history(commodity, days)

        if not history:
            raise Exception("无法获取历史价格数据")

        # 用 pandas 计算趋势指标
        df = pd.DataFrame(history)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        prices = df["price"]
        latest_price = float(prices.iloc[-1])
        start_price = float(prices.iloc[0])
        change_abs = round(latest_price - start_price, 2)
        change_pct = round((change_abs / start_price) * 100, 2) if start_price else 0

        # 均线计算
        ma_7 = float(prices.rolling(window=min(7, len(prices))).mean().iloc[-1])
        ma_30 = float(prices.rolling(window=min(30, len(prices))).mean().iloc[-1])

        # 趋势判断
        if change_pct > 2:
            trend = "up"
        elif change_pct < -2:
            trend = "down"
        else:
            trend = "flat"

        # 生成观察
        observations = self._generate_observations(
            change_pct, latest_price, ma_7, ma_30, trend
        )

        return {
            "commodity": commodity,
            "days": days,
            "latest_price": latest_price,
            "start_price": start_price,
            "change_abs": change_abs,
            "change_pct": change_pct,
            "ma_7": round(ma_7, 2),
            "ma_30": round(ma_30, 2),
            "trend": trend,
            "observations": observations,
        }

    async def _fetch_history(self, commodity: str, days: int) -> List[Dict[str, Any]]:
        """从 API 获取历史价格序列"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        url = f"{self.api_base}/{commodity}/history"
        params = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json().get("data", [])

    def _get_unit(self, commodity: str) -> str:
        """从配置获取商品单位"""
        config = self.commodities_config.get(commodity, {})
        return config.get("unit", "CNY/t")

    def _generate_observations(self, change_pct: float, latest: float,
                               ma_7: float, ma_30: float, trend: str) -> List[str]:
        """生成趋势观察文本"""
        obs = []

        if change_pct > 0:
            obs.append(f"近 30 天价格上涨 {change_pct}%")
        elif change_pct < 0:
            obs.append(f"近 30 天价格下跌 {abs(change_pct)}%")
        else:
            obs.append("近 30 天价格基本持平")

        if latest > ma_7 and latest > ma_30:
            obs.append("当前价格高于 7 日均线和 30 日均线")
        elif latest > ma_7:
            obs.append("当前价格高于 7 日均线")
        elif latest > ma_30:
            obs.append("当前价格高于 30 日均线")
        else:
            obs.append("当前价格低于 7 日均线和 30 日均线")

        if trend == "up":
            obs.append("短期趋势偏强，需关注下游需求持续性")
        elif trend == "down":
            obs.append("短期趋势偏弱，需关注供应端变化")
        else:
            obs.append("短期趋势震荡，建议观望")

        return obs
