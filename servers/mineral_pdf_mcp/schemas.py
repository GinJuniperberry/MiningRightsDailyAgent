"""mineral-pdf-mcp 数据模型定义"""
from pydantic import BaseModel, Field
from typing import List


class Quantity(BaseModel):
    """带单位的量值"""
    value: float
    unit: str


class ResourceEntry(BaseModel):
    """单条资源量数据"""
    category: str  # Indicated / Inferred / Measured
    ore_tonnage: Quantity
    grade: Quantity
    contained_metal: Quantity
    page: int = 0
    confidence: float = 0.0


class ExtractResponse(BaseModel):
    """资源量抽取响应"""
    project: str
    report_url: str
    resources: List[ResourceEntry] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
