"""mining-news-mcp: 矿权新闻采集 MCP Server

提供两个工具：
- search(query, days): 搜索指定矿权/公司/矿种相关的新闻
- fetch_article(url): 根据 URL 抽取新闻正文

真实数据源失败时自动降级到 Mock 数据，保证 demo 可运行。
"""
import os
import sys
import yaml

# 确保项目根目录在 PYTHONPATH 中
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from servers.mining_news_mcp.adapters import NewsAdapter
from servers.mining_news_mcp.mock_data import MOCK_NEWS_ITEMS, MOCK_ARTICLE


def _load_config() -> dict:
    """加载 sources.yaml 配置"""
    config_path = os.path.join(_PROJECT_ROOT, "configs", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_config = _load_config()
_adapter = NewsAdapter(
    rss_feeds=_config["news"]["rss_feeds"],
    timeout=_config["news"]["fetch_timeout"],
    max_items=_config["news"]["max_items"],
)

mcp = FastMCP("mining-news-mcp")


@mcp.tool()
async def search(query: str, days: int = 7) -> dict:
    """搜索指定矿权/公司/矿种相关的新闻

    Args:
        query: 搜索关键词（项目名、公司名或矿种，如 "Pilbara lithium"）
        days: 搜索最近多少天的新闻，默认 7 天

    Returns:
        包含新闻列表的字典，每条新闻含 title, url, source, published_at, summary, score。
        真实 RSS 源失败时返回 Mock 数据。
    """
    try:
        items = await _adapter.search(query, days)
        if items:
            return {"items": items}
        # 真实数据为空时降级到 Mock
        print(f"[mining-news-mcp] RSS 无结果，降级到 Mock 数据 (query={query})")
        return {"items": MOCK_NEWS_ITEMS}
    except Exception as e:
        # 异常时降级到 Mock
        print(f"[mining-news-mcp] 搜索失败，降级到 Mock 数据: {e}")
        return {"items": MOCK_NEWS_ITEMS, "warning": f"RSS 抓取失败，使用样例数据: {e}"}


@mcp.tool()
async def fetch_article(url: str) -> dict:
    """根据 URL 抽取新闻正文

    Args:
        url: 新闻文章的 URL

    Returns:
        文章详情字典，含 url, title, published_at, source, content, citations。
        正文抓取失败时返回 Mock 文章。
    """
    try:
        article = await _adapter.fetch_article(url)
        if article and article.get("content"):
            return article
        # content 为空时降级到 Mock
        print(f"[mining-news-mcp] 正文抽取为空，降级到 Mock 数据 (url={url})")
        return {**MOCK_ARTICLE, "url": url}
    except Exception as e:
        # 异常时降级到 Mock
        print(f"[mining-news-mcp] 正文抓取失败，降级到 Mock 数据: {e}")
        return {**MOCK_ARTICLE, "url": url, "warning": f"正文抓取失败，使用样例数据: {e}"}


if __name__ == "__main__":
    mcp.run()
