"""mining-news-mcp 测试

测试 search 和 fetch_article 工具是否正常返回数据。
由于真实 RSS 源可能不稳定，主要验证 Mock 兜底逻辑。
"""
import pytest
import sys
import os

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from servers.mining_news_mcp.mock_data import MOCK_NEWS_ITEMS, MOCK_ARTICLE
from servers.mining_news_mcp.schemas import NewsItem, SearchResponse, Article


def test_mock_news_items_structure():
    """测试 Mock 新闻数据结构完整性"""
    assert len(MOCK_NEWS_ITEMS) > 0

    for item in MOCK_NEWS_ITEMS:
        assert "title" in item
        assert "url" in item
        assert "source" in item
        assert "published_at" in item
        assert "summary" in item
        assert "score" in item
        assert isinstance(item["score"], float)
        assert 0 <= item["score"] <= 1


def test_mock_article_structure():
    """测试 Mock 文章数据结构完整性"""
    assert "url" in MOCK_ARTICLE
    assert "title" in MOCK_ARTICLE
    assert "content" in MOCK_ARTICLE
    assert "citations" in MOCK_ARTICLE
    assert len(MOCK_ARTICLE["content"]) > 0


def test_news_item_schema():
    """测试 NewsItem Pydantic 模型"""
    item = NewsItem(
        title="Test News",
        url="https://example.com/test",
        source="test.com",
        published_at="2026-07-09",
        summary="Test summary",
        score=0.9,
    )
    assert item.title == "Test News"
    assert item.score == 0.9


def test_article_schema():
    """测试 Article Pydantic 模型"""
    article = Article(
        url="https://example.com/test",
        title="Test Article",
        content="Test content",
        citations=["https://example.com"],
    )
    assert article.title == "Test Article"
    assert len(article.citations) == 1


def test_search_response_schema():
    """测试 SearchResponse Pydantic 模型"""
    response = SearchResponse(items=[
        NewsItem(title="Test", url="https://example.com", score=0.5)
    ])
    assert len(response.items) == 1


@pytest.mark.asyncio
async def test_search_with_mock_fallback():
    """测试 search 工具在真实数据源失败时返回 Mock 数据

    直接调用 server 的 search 函数，验证 Mock 兜底逻辑。
    """
    from servers.mining_news_mcp.server import search

    # 调用 search（真实 RSS 可能失败，应返回 Mock 数据）
    result = await search(query="Pilbara lithium", days=7)

    assert "items" in result
    assert len(result["items"]) > 0
    assert "title" in result["items"][0]


@pytest.mark.asyncio
async def test_fetch_article_with_mock_fallback():
    """测试 fetch_article 工具在真实抓取失败时返回 Mock 数据"""
    from servers.mining_news_mcp.server import fetch_article

    result = await fetch_article(url="https://example.com/nonexistent")

    assert "content" in result
    assert len(result["content"]) > 0
