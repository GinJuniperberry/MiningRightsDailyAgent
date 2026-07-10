"""mining-news-mcp 数据模型定义"""
from pydantic import BaseModel, Field
from typing import List


class NewsItem(BaseModel):
    """新闻条目"""
    title: str
    url: str
    source: str = ""
    published_at: str = ""
    summary: str = ""
    score: float = 0.0


class SearchResponse(BaseModel):
    """搜索响应"""
    items: List[NewsItem] = Field(default_factory=list)


class Article(BaseModel):
    """新闻正文"""
    url: str
    title: str
    published_at: str = ""
    source: str = ""
    content: str
    citations: List[str] = Field(default_factory=list)
