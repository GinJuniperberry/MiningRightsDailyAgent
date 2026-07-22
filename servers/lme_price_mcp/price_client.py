"""价格数据客户端

基于配置的 base_price 生成模拟价格序列（随机游走模型），
计算涨跌幅、均线和趋势判断。

无需外部 API 依赖，保证任何环境下都能返回数据。
"""
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import pandas as pd


class PriceClient:
    """价格查询客户端（本地生成）

    使用随机游走模型基于配置的 base_price 生成价格序列，
    然后用 pandas 计算趋势指标。
    """

    def __init__(self, api_base: str = "", timeout: int = 10,
                 commodities_config: Dict[str, Any] = None):
        # api_base 保留参数兼容性，实际不使用外部 API
        self.api_base = api_base
        self.timeout = timeout
        self.commodities_config = commodities_config or {}

    async def get_price(self, commodity: str, date: str) -> Dict[str, Any]:
        """查询指定日期的商品价格

        基于 base_price 生成当日价格。

        Args:
            commodity: 商品名称（如 lithium）
            date: 日期，格式 YYYY-MM-DD

        Returns:
            价格字典，含 commodity, date, price, unit, currency, source
        """
        config = self.commodities_config.get(commodity, {})
        base_price = config.get("base_price", 100000)
        unit = config.get("unit", "CNY/t")
        currency = config.get("currency", "CNY")

        # 在基准价上下浮动 ±3% 生成当日价格
        fluctuation = random.uniform(-0.03, 0.03)
        price = round(base_price * (1 + fluctuation), 2)

        return {
            "commodity": commodity,
            "date": date,
            "price": price,
            "unit": unit,
            "currency": currency,
            "source": "local-simulation",
        }

    async def get_trend(self, commodity: str, days: int) -> Dict[str, Any]:
        """计算价格趋势：涨跌幅、均线、趋势判断

        生成 days 天的价格序列，用 pandas 计算趋势指标。

        Args:
            commodity: 商品名称
            days: 统计天数

        Returns:
            趋势字典，含 latest_price, start_price, change_pct, ma_7, ma_30, trend, observations
        """
        history = self._generate_price_series(commodity, days)

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

    def _generate_price_series(self, commodity: str, days: int) -> List[Dict[str, Any]]:
        """生成价格序列（随机游走模型）

        基于配置的 base_price，每天在前一天基础上随机波动 ±2%，
        生成具有真实感的连续价格序列。

        Args:
            commodity: 商品名称
            days: 天数

        Returns:
            [{"date": "YYYY-MM-DD", "price": float}, ...]
        """
        config = self.commodities_config.get(commodity, {})
        base_price = config.get("base_price", 100000)

        end_date = datetime.now()
        history: List[Dict[str, Any]] = []

        # 随机游走：从 base_price 开始，每天波动 ±2%
        price = base_price
        for i in range(days):
            d = end_date - timedelta(days=days - i - 1)
            daily_change = random.uniform(-0.02, 0.02)
            price = price * (1 + daily_change)
            # 防止价格偏离基准太远（回归）
            if price > base_price * 1.15:
                daily_change = -abs(daily_change)
                price = price * (1 + daily_change)
            elif price < base_price * 0.85:
                daily_change = abs(daily_change)
                price = price * (1 + daily_change)

            history.append({
                "date": d.strftime("%Y-%m-%d"),
                "price": round(price, 2),
            })

        return history

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
