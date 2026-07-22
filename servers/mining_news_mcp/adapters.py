"""mining-news-mcp 真实数据源适配器

从 RSS 源抓取新闻，按关键词和时间过滤，并用 trafilatura 抽取正文。
失败时由 server.py 降级到 Mock 数据。
"""
import feedparser
import httpx
import trafilatura
import sys
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any


class NewsAdapter:
    """真实新闻数据源适配器：RSS 抓取 + 正文抽取"""

    def __init__(self, rss_feeds: List[str], timeout: int = 15, max_items: int = 10):
        self.rss_feeds = rss_feeds
        self.timeout = timeout
        self.max_items = max_items

    async def search(self, query: str, days: int) -> List[Dict[str, Any]]:
        """从 RSS 源搜索新闻，按 query 关键词和时间过滤

        Args:
            query: 搜索关键词（项目名、公司名或矿种）
            days: 搜索最近多少天的新闻

        Returns:
            新闻条目列表，每条含 title, url, source, published_at, summary, score
        """
        keywords = [k.strip().lower() for k in query.split() if k.strip()]
        if not keywords:
            return []

        cutoff = datetime.now() - timedelta(days=days)
        all_items: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            results = await asyncio.gather(
                *(
                    self._fetch_feed(client, feed_url, keywords, cutoff)
                    for feed_url in self.rss_feeds
                ),
                return_exceptions=True,
            )

        for feed_url, result in zip(self.rss_feeds, results):
            if isinstance(result, Exception):
                print(
                    f"[NewsAdapter] RSS 抓取失败 {feed_url}: {result}",
                    file=sys.stderr,
                )
                continue
            all_items.extend(result)

        # 按相关度评分排序，取 top N
        all_items.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_items[: self.max_items]

    async def _fetch_feed(self, client: httpx.AsyncClient, feed_url: str,
                          keywords: List[str],
                          cutoff: datetime) -> List[Dict[str, Any]]:
        """抓取单个 RSS 源并过滤"""
        response = await client.get(feed_url)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        items = []

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))

            # 解析发布时间
            published_at = ""
            if entry.get("published_parsed"):
                try:
                    dt = datetime(*entry.published_parsed[:6])
                    if dt < cutoff:
                        continue
                    published_at = dt.strftime("%Y-%m-%d")
                except Exception:
                    published_at = entry.get("published", "")

            # 关键词匹配评分
            text = f"{title} {summary}".lower()
            matched = sum(1 for kw in keywords if kw in text)
            if matched == 0:
                continue

            score = matched / len(keywords)
            source = feed.feed.get("title", feed_url)

            items.append({
                "title": title,
                "url": link,
                "source": source,
                "published_at": published_at,
                "summary": summary[:300] if summary else "",
                "score": round(score, 2),
            })

        return items

    async def fetch_article(self, url: str) -> Dict[str, Any]:
        """使用 trafilatura 抽取新闻正文

        Args:
            url: 新闻文章 URL

        Returns:
            文章详情，含 url, title, published_at, source, content, citations
        """
        async with httpx.AsyncClient(timeout=self.timeout,
                                     follow_redirects=True,
                                     headers={"User-Agent": "Mozilla/5.0"}) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        extracted = trafilatura.extract(
            html,
            output_format="json",
            with_metadata=True,
            include_links=True
        )

        if not extracted:
            # trafilatura 失败，返回原始 HTML 的简单提取
            return {
                "url": url,
                "title": "",
                "published_at": "",
                "source": "",
                "content": html[:5000],
                "citations": [url],
            }

        import json
        data = json.loads(extracted)

        return {
            "url": url,
            "title": data.get("title", ""),
            "published_at": data.get("date", ""),
            "source": data.get("sitename", ""),
            "content": data.get("text", ""),
            "citations": [url] + (data.get("comments", []) or []),
        }
