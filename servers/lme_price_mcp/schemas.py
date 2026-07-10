"""lme-price-mcp 数据模型定义"""
from pydantic import BaseModel, Field
from typing import List


class PriceResponse(BaseModel):
    """价格查询响应"""
    commodity: str
    date: str
    price: float
    unit: str
    currency: str
    source: str


class TrendResponse(BaseModel):
    """价格趋势响应"""
    commodity: str
    days: int
    latest_price: float
    start_price: float
    change_abs: float
    change_pct: float
    ma_7: float
    ma_30: float
    trend: str
    observations: List[str] = Field(default_factory=list)
