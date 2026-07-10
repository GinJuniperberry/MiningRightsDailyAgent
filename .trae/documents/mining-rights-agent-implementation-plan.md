# 矿权日报 Agent - 项目实施计划

> 基于 `初始技术方案.md`，使用 LangGraph + MCP 协议实现「矿权日报 Agent」
> 计划生成日期：2026-07-09

---

## 一、摘要

在现有空项目（仅含 README.md 和初始技术方案.md）基础上，从零实现一个基于 MCP 协议和 LangGraph 编排的「矿权日报 Agent」。系统接收自然语言输入（如"给我生成一份关于 Pilbara 锂矿的今日简报"），通过 3 个 MCP Server（新闻、PDF 资源量、价格）采集数据，经 LangGraph StateGraph 编排生成结构化 Markdown 日报，包含新闻摘要、资源量数据、价格走势、风险提示和引用源。

**关键技术决策（已与用户确认）：**
- LLM 提供商：通义千问 Qwen（阿里云 DashScope，OpenAI 兼容接口，国内访问稳定）
- 数据源策略：真实数据源 + Mock 兜底（保证 demo 可运行性）
- MCP SDK：FastMCP（装饰器风格，开发效率高）

---

## 二、现状分析

### 2.1 项目当前状态
- **已有文件**：`README.md`（仅一行标题）、`初始技术方案.md`（完整技术方案）、`mermaid-diagram.png`
- **代码状态**：零代码，需从零搭建全部模块
- **运行环境**：Windows 11，Python 3.11.7 已安装

### 2.2 技术方案要点
技术方案文档已提供完整设计，包括：
- 总体架构：MCP 工具层 + LangGraph 编排层 + Markdown 报告层
- 3 个 MCP Server 共 5 个工具（search、fetch_article、extract_resources、get_price、get_trend）
- LangGraph StateGraph 含 14 个节点 + 2 个条件路由
- BriefingState 状态定义（TypedDict）
- 完整节点函数骨架代码
- 目录结构、Docker Compose、mcp-config.json
- 24 小时开发排期

### 2.3 需要补充实现的技术细节
技术方案提供了骨架，但以下细节需要实现时补全：
1. **DeepSeek LLM 集成**：意图解析、摘要生成、风险判断、质检的 LLM 调用
2. **真实数据源适配器**：RSS 新闻抓取、PDF 下载解析、价格 API 查询
3. **Mock 兜底机制**：每个 MCP Server 在真实数据源失败时返回样例数据
4. **MCP Client 连接管理**：基于 stdio transport 的客户端封装
5. **报告模板渲染**：Markdown 生成逻辑
6. **质检规则**：6 项规则检查 + LLM 轻量判断

---

## 三、实施计划

### 3.1 任务分解与时间节点

| 阶段 | 时间节点 | 任务内容 | 交付物 |
|------|---------|---------|--------|
| P1 | 0-2h | 项目初始化与基础设施 | 目录结构、依赖、Docker、配置文件 |
| P2 | 2-6h | 3 个 MCP Server 实现 | servers/ 下 3 个完整 server |
| P3 | 6-9h | MCP Client 封装与 LLM 客户端 | mcp_clients.py、llm_client.py |
| P4 | 9-15h | LangGraph Agent 核心实现 | state、nodes、routers、graph |
| P5 | 15-18h | 报告生成与质检循环 | report_generator.py、quality.py |
| P6 | 18-21h | 测试编写与端到端验证 | tests/ 下 5 个测试文件 |
| P7 | 21-24h | 文档、Demo 与收尾 | RUN.md、README.md、样例数据 |

### 3.2 资源分配

| 模块 | 文件数 | 复杂度 | 依赖关系 |
|------|--------|--------|---------|
| MCP Servers | 12 文件 | 中 | 无（独立模块） |
| Agent 核心 | 10 文件 | 高 | 依赖 MCP Client |
| 配置文件 | 4 文件 | 低 | 无 |
| 测试 | 5 文件 | 中 | 依赖所有模块 |
| 部署/文档 | 4 文件 | 低 | 依赖全部完成 |

---

## 四、详细实施步骤

### 步骤 1：项目初始化（P1, 0-2h）

#### 1.1 创建完整目录结构

```text
mining-rights-daily-agent/
├── servers/
│   ├── mining_news_mcp/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── adapters.py
│   │   ├── mock_data.py
│   │   └── schemas.py
│   ├── mineral_pdf_mcp/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   ├── extractor.py
│   │   ├── table_parser.py
│   │   ├── mock_data.py
│   │   └── schemas.py
│   └── lme_price_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── price_client.py
│       ├── mock_data.py
│       └── schemas.py
├── agent/
│   ├── __init__.py
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── nodes.py
│   ├── routers.py
│   ├── mcp_clients.py
│   ├── asset_resolver.py
│   ├── report_generator.py
│   ├── quality.py
│   ├── llm_client.py
│   └── prompts.py
├── configs/
│   ├── assets.yaml
│   ├── sources.yaml
│   └── mcp-config.json
├── reports/
│   └── .gitkeep
├── data/
│   ├── cache/
│   │   └── .gitkeep
│   └── sample/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   ├── test_graph.py
│   ├── test_news_mcp.py
│   ├── test_pdf_mcp.py
│   ├── test_price_mcp.py
│   └── test_agent_e2e.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── RUN.md
└── README.md
```

#### 1.2 创建 `requirements.txt`

```text
# LangGraph 编排
langgraph>=0.2.0

# MCP 协议
mcp[cli]>=1.0.0

# LLM（DeepSeek 使用 OpenAI 兼容接口）
openai>=1.0.0

# HTTP / 新闻采集
httpx>=0.27.0
feedparser>=6.0.10
trafilatura>=1.12.0

# PDF 解析
PyMuPDF>=1.24.0
pdfplumber>=0.11.0

# 数据处理
pandas>=2.2.0

# 配置与校验
pyyaml>=6.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# 测试
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

#### 1.3 创建 `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "agent/main.py"]
```

#### 1.4 创建 `docker-compose.yml`

```yaml
services:
  mining-rights-agent:
    build: .
    container_name: mining-rights-agent
    volumes:
      - .:/app
      - reports-data:/app/reports
    working_dir: /app
    environment:
      - PYTHONPATH=/app
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY:-}
      - USE_LLM=${USE_LLM:-true}
    command: python agent/main.py "给我生成一份关于 Pilbara 锂矿的今日简报"

volumes:
  reports-data:
```

#### 1.5 创建配置文件

**`configs/assets.yaml`** - 矿权资产别名与 PDF 配置：

```yaml
assets:
  pilbara:
    aliases:
      - Pilbara
      - Pilbara Minerals
      - Pilgangoora
    company: Pilbara Minerals
    commodity: lithium
    pdf_urls:
      - https://corp.pilbaraminerals.com.au/wp-content/uploads/2024/08/Pilbara-Minerals-Mineral-Resources-and-Ore-Reserves-Statement-2024.pdf
    keywords:
      - lithium
      - Li2O
      - spodumene

  greenbushes:
    aliases:
      - Greenbushes
      - Talison Lithium
    company: Talison Lithium
    commodity: lithium
    pdf_urls: []
    keywords:
      - lithium
      - Li2O
```

**`configs/sources.yaml`** - 新闻源与价格 API 配置：

```yaml
news:
  rss_feeds:
    - https://www.mining.com/feed/
    - https://www.reuters.com/markets/commodities/rss
  search_engine: rss
  max_items: 10
  fetch_timeout: 15

price:
  api_base: "https://api.example.com/metals"
  commodities:
    lithium:
      unit: CNY/t
      currency: CNY
  cache_ttl: 3600
  fetch_timeout: 10

llm:
  provider: qwen
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  model: qwen-plus
  temperature: 0.3
  max_tokens: 2000
  timeout: 30
```

**`configs/mcp-config.json`** - MCP Server 配置：

```json
{
  "mcpServers": {
    "mining-news-mcp": {
      "command": "python",
      "args": ["servers/mining_news_mcp/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    "mineral-pdf-mcp": {
      "command": "python",
      "args": ["servers/mineral_pdf_mcp/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    "lme-price-mcp": {
      "command": "python",
      "args": ["servers/lme_price_mcp/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**`.env.example`** - 环境变量模板：

```text
# 通义千问 API（LLM 调用，不配置则走规则模式）
DASHSCOPE_API_KEY=sk-your-dashscope-api-key

# 是否启用 LLM（false 时纯规则运行，无需 API Key）
USE_LLM=true

# LLM 基础配置
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

---

### 步骤 2：实现 3 个 MCP Server（P2, 2-6h）

#### 2.1 mining-news-mcp（新闻采集）

**`servers/mining_news_mcp/schemas.py`** - Pydantic 数据模型：

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class NewsItem(BaseModel):
    title: str
    url: str
    source: str = ""
    published_at: str = ""
    summary: str = ""
    score: float = 0.0

class SearchResponse(BaseModel):
    items: List[NewsItem]

class Article(BaseModel):
    url: str
    title: str
    published_at: str = ""
    source: str = ""
    content: str
    citations: List[str] = Field(default_factory=list)
```

**`servers/mining_news_mcp/adapters.py`** - 真实数据源适配器：

```python
import feedparser
import httpx
import trafilatura
from typing import List, Dict, Any
from datetime import datetime, timedelta

class NewsAdapter:
    """真实新闻数据源适配器：RSS 抓取 + 正文抽取"""

    def __init__(self, rss_feeds: List[str], timeout: int = 15):
        self.rss_feeds = rss_feeds
        self.timeout = timeout

    async def search(self, query: str, days: int) -> List[Dict[str, Any]]:
        """从 RSS 源搜索新闻，按关键词和时间过滤"""
        # 解析 RSS，按 query 关键词匹配，按 days 过滤日期
        ...

    async def fetch_article(self, url: str) -> Dict[str, Any]:
        """使用 trafilatura 抽取正文"""
        # httpx 下载页面 → trafilatura 提取正文
        ...
```

**`servers/mining_news_mcp/mock_data.py`** - Mock 兜底数据：

```python
"""当真实 RSS 抓取失败时的 Mock 数据，保证 demo 可运行"""

MOCK_NEWS_ITEMS = [
    {
        "title": "Pilbara Minerals announces record lithium production in Q2 2026",
        "url": "https://www.mining.com/pilbara-minerals-q2-2026",
        "source": "mining.com",
        "published_at": "2026-07-09",
        "summary": "Pilbara Minerals reported record spodumene concentrate production...",
        "score": 0.92
    },
    # ... 更多 mock 数据
]

MOCK_ARTICLE = {
    "url": "https://www.mining.com/pilbara-minerals-q2-2026",
    "title": "Pilbara Minerals announces record lithium production in Q2 2026",
    "published_at": "2026-07-09",
    "source": "mining.com",
    "content": "Pilbara Minerals Limited (ASX: PLS) today announced...",
    "citations": ["https://www.pilbaraminerals.com.au"]
}
```

**`servers/mining_news_mcp/server.py`** - FastMCP Server：

```python
"""mining-news-mcp: 矿权新闻采集 MCP Server"""
from mcp.server.fastmcp import FastMCP
from servers.mining_news_mcp.adapters import NewsAdapter
from servers.mining_news_mcp.mock_data import MOCK_NEWS_ITEMS, MOCK_ARTICLE
import yaml
import os

mcp = FastMCP("mining-news-mcp")

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()
_adapter = NewsAdapter(
    rss_feeds=_config["news"]["rss_feeds"],
    timeout=_config["news"]["fetch_timeout"]
)

@mcp.tool()
async def search(query: str, days: int = 7) -> dict:
    """搜索指定矿权/公司/矿种相关的新闻

    Args:
        query: 搜索关键词（项目名、公司名或矿种）
        days: 搜索最近多少天的新闻，默认 7 天

    Returns:
        包含新闻列表的字典，每条新闻含 title, url, source, published_at, summary, score
    """
    try:
        items = await _adapter.search(query, days)
        if items:
            return {"items": items}
        # 真实数据为空时降级到 Mock
        return {"items": MOCK_NEWS_ITEMS}
    except Exception as e:
        # 异常时降级到 Mock
        return {"items": MOCK_NEWS_ITEMS, "warning": f"RSS 抓取失败，使用样例数据: {e}"}

@mcp.tool()
async def fetch_article(url: str) -> dict:
    """根据 URL 抽取新闻正文

    Args:
        url: 新闻文章的 URL

    Returns:
        文章详情字典，含 url, title, published_at, source, content, citations
    """
    try:
        article = await _adapter.fetch_article(url)
        if article and article.get("content"):
            return article
        return MOCK_ARTICLE
    except Exception as e:
        return {**MOCK_ARTICLE, "warning": f"正文抓取失败，使用样例数据: {e}"}

if __name__ == "__main__":
    mcp.run()
```

#### 2.2 mineral-pdf-mcp（PDF 资源量抽取）

**`servers/mineral_pdf_mcp/schemas.py`**：

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Quantity(BaseModel):
    value: float
    unit: str

class ResourceEntry(BaseModel):
    category: str  # Indicated / Inferred / Measured
    ore_tonnage: Quantity
    grade: Quantity
    contained_metal: Quantity
    page: int = 0
    confidence: float = 0.0

class ExtractResponse(BaseModel):
    project: str
    report_url: str
    resources: List[ResourceEntry]
    warnings: List[str] = Field(default_factory=list)
```

**`servers/mineral_pdf_mcp/extractor.py`** - PDF 下载与解析：

```python
"""PDF 资源量抽取器：PyMuPDF + pdfplumber，失败降级到 Mock"""
import httpx
import fitz  # PyMuPDF
import pdfplumber
import re
import io
import os
from typing import Dict, Any, List

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache")

class PDFExtractor:
    """从 NI 43-101 报告 PDF 中抽取资源量表"""

    async def download_pdf(self, url: str) -> bytes:
        """下载 PDF 到内存，缓存到 data/cache"""
        ...

    def extract_resources(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """解析 PDF，提取 Indicated/Inferred 资源量数据

        策略：
        1. 用 pdfplumber 扫描所有页面的表格
        2. 匹配含 "Indicated" / "Inferred" / "Measured" 的表格
        3. 提取矿石量、品位、金属量字段
        4. 用正则清洗数值和单位
        """
        ...

    def _parse_table_row(self, row: List[str]) -> Dict[str, Any]:
        """解析单行表格数据"""
        ...
```

**`servers/mineral_pdf_mcp/table_parser.py`** - 表格解析辅助：

```python
"""PDF 表格解析辅助函数"""
import re
from typing import Dict, Any, Optional

def parse_quantity(text: str) -> Optional[Dict[str, Any]]:
    """解析 '120.5 Mt' -> {'value': 120.5, 'unit': 'Mt'}"""
    ...

def parse_grade(text: str) -> Optional[Dict[str, Any]]:
    """解析 '1.2% Li2O' -> {'value': 1.2, 'unit': '% Li2O'}"""
    ...

def is_resource_table_row(row: List[str]) -> bool:
    """判断表格行是否为资源量数据行"""
    ...
```

**`servers/mineral_pdf_mcp/mock_data.py`**：

```python
"""PDF 抽取失败的 Mock 数据"""

MOCK_RESOURCES = {
    "project": "Pilbara",
    "report_url": "https://example.com/pilbara-resource-report.pdf",
    "resources": [
        {
            "category": "Indicated",
            "ore_tonnage": {"value": 120.5, "unit": "Mt"},
            "grade": {"value": 1.2, "unit": "% Li2O"},
            "contained_metal": {"value": 1.45, "unit": "Mt Li2O"},
            "page": 128,
            "confidence": 0.86
        },
        {
            "category": "Inferred",
            "ore_tonnage": {"value": 45.2, "unit": "Mt"},
            "grade": {"value": 1.0, "unit": "% Li2O"},
            "contained_metal": {"value": 0.45, "unit": "Mt Li2O"},
            "page": 129,
            "confidence": 0.81
        }
    ],
    "warnings": ["使用 Mock 数据，真实 PDF 抽取失败"]
}
```

**`servers/mineral_pdf_mcp/server.py`**：

```python
"""mineral-pdf-mcp: 矿权 PDF 资源量抽取 MCP Server"""
from mcp.server.fastmcp import FastMCP
from servers.mineral_pdf_mcp.extractor import PDFExtractor
from servers.mineral_pdf_mcp.mock_data import MOCK_RESOURCES

mcp = FastMCP("mineral-pdf-mcp")
_extractor = PDFExtractor()

@mcp.tool()
async def extract_resources(pdf_url: str) -> dict:
    """从 NI 43-101 / 矿权 PDF 报告中抽取资源量数据

    Args:
        pdf_url: PDF 报告的 URL 地址

    Returns:
        资源量字典，含 project, report_url, resources 列表, warnings
        每条 resource 含 category, ore_tonnage, grade, contained_metal, page, confidence
    """
    try:
        pdf_bytes = await _extractor.download_pdf(pdf_url)
        result = _extractor.extract_resources(pdf_bytes)
        if result.get("resources"):
            return result
        return {**MOCK_RESOURCES, "report_url": pdf_url}
    except Exception as e:
        return {
            **MOCK_RESOURCES,
            "report_url": pdf_url,
            "warnings": [f"PDF 抽取失败，使用 Mock 数据: {e}"]
        }

if __name__ == "__main__":
    mcp.run()
```

#### 2.3 lme-price-mcp（价格行情）

**`servers/lme_price_mcp/schemas.py`**：

```python
from pydantic import BaseModel, Field
from typing import List

class PriceResponse(BaseModel):
    commodity: str
    date: str
    price: float
    unit: str
    currency: str
    source: str

class TrendResponse(BaseModel):
    commodity: str
    days: int
    latest_price: float
    start_price: float
    change_abs: float
    change_pct: float
    ma_7: float
    ma_30: float
    trend: str
    observations: List[str]
```

**`servers/lme_price_mcp/price_client.py`** - 真实价格客户端：

```python
"""价格数据客户端：真实 API + Mock 兜底"""
import httpx
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

class PriceClient:
    """价格查询客户端"""

    def __init__(self, api_base: str, timeout: int = 10):
        self.api_base = api_base
        self.timeout = timeout

    async def get_price(self, commodity: str, date: str) -> Dict[str, Any]:
        """查询指定日期的商品价格"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.api_base}/{commodity}/{date}")
                resp.raise_for_status()
                return resp.json()
        except Exception:
            raise

    async def get_trend(self, commodity: str, days: int) -> Dict[str, Any]:
        """计算价格趋势：涨跌幅、均线、趋势判断"""
        # 获取 days 天的历史价格
        # 用 pandas 计算 MA7, MA30, change_pct
        ...

    def _generate_mock_history(self, commodity: str, days: int) -> List[Dict]:
        """生成 Mock 历史价格序列（用于兜底）"""
        ...
```

**`servers/lme_price_mcp/mock_data.py`**：

```python
"""价格 Mock 数据"""

MOCK_PRICE = {
    "commodity": "lithium",
    "date": "2026-07-09",
    "price": 105000,
    "unit": "CNY/t",
    "currency": "CNY",
    "source": "mock-data"
}

MOCK_TREND = {
    "commodity": "lithium",
    "days": 30,
    "latest_price": 105000,
    "start_price": 98000,
    "change_abs": 7000,
    "change_pct": 7.14,
    "ma_7": 103200,
    "ma_30": 99700,
    "trend": "up",
    "observations": [
        "近 30 天价格上涨 7.14%",
        "当前价格高于 7 日均线和 30 日均线"
    ]
}
```

**`servers/lme_price_mcp/server.py`**：

```python
"""lme-price-mcp: 金属价格行情 MCP Server"""
from mcp.server.fastmcp import FastMCP
from servers.lme_price_mcp.price_client import PriceClient
from servers.lme_price_mcp.mock_data import MOCK_PRICE, MOCK_TREND
import yaml
import os

mcp = FastMCP("lme-price-mcp")

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "configs", "sources.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

_config = load_config()
_client = PriceClient(
    api_base=_config["price"]["api_base"],
    timeout=_config["price"]["fetch_timeout"]
)

@mcp.tool()
async def get_price(commodity: str, date: str) -> dict:
    """查询指定商品的当日价格

    Args:
        commodity: 商品名称（如 lithium）
        date: 日期，格式 YYYY-MM-DD

    Returns:
        价格字典，含 commodity, date, price, unit, currency, source
    """
    try:
        return await _client.get_price(commodity, date)
    except Exception:
        return {**MOCK_PRICE, "commodity": commodity, "date": date, "source": "mock-data"}

@mcp.tool()
async def get_trend(commodity: str, days: int = 30) -> dict:
    """查询商品价格走势

    Args:
        commodity: 商品名称
        days: 统计天数，默认 30

    Returns:
        趋势字典，含 latest_price, start_price, change_pct, ma_7, ma_30, trend, observations
    """
    try:
        return await _client.get_trend(commodity, days)
    except Exception:
        return {**MOCK_TREND, "commodity": commodity, "days": days}

if __name__ == "__main__":
    mcp.run()
```

---

### 步骤 3：MCP Client 封装与 LLM 客户端（P3, 6-9h）

#### 3.1 `agent/mcp_clients.py` - MCP 客户端封装

```python
"""MCP 客户端封装：在 LangGraph node 内调用 MCP tools"""
import json
import asyncio
from typing import Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPToolClient:
    """单个 MCP Server 的客户端连接"""

    def __init__(self, server_name: str, config: Dict[str, Any]):
        self.server_name = server_name
        self.config = config
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None

    async def connect(self):
        """建立与 MCP Server 的 stdio 连接"""
        self._exit_stack = AsyncExitStack()
        server_params = StdioServerParameters(
            command=self.config["command"],
            args=self.config["args"],
            env={**self.config.get("env", {})}
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read, write = stdio_transport
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self.session.initialize()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用 MCP tool 并返回结果"""
        if not self.session:
            await self.connect()
        result = await self.session.call_tool(tool_name, arguments)
        # MCP 返回的是 content 列表，取第一个 text 内容
        if result.content:
            text_content = result.content[0]
            if hasattr(text_content, 'text'):
                return json.loads(text_content.text)
        return {}

    async def close(self):
        """关闭连接"""
        if self._exit_stack:
            await self._exit_stack.aclose()

_clients: Dict[str, MCPToolClient] = {}

async def get_client(server_name: str) -> MCPToolClient:
    """获取或创建 MCP 客户端（单例缓存）"""
    if server_name not in _clients:
        config = _load_mcp_config(server_name)
        client = MCPToolClient(server_name, config)
        await client.connect()
        _clients[server_name] = client
    return _clients[server_name]

def _load_mcp_config(server_name: str) -> Dict[str, Any]:
    """从 mcp-config.json 加载 server 配置"""
    import os
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "mcp-config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["mcpServers"][server_name]

async def call_mining_news_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    client = await get_client("mining-news-mcp")
    return await client.call_tool(tool_name, arguments)

async def call_mineral_pdf_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    client = await get_client("mineral-pdf-mcp")
    return await client.call_tool(tool_name, arguments)

async def call_price_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    client = await get_client("lme-price-mcp")
    return await client.call_tool(tool_name, arguments)

async def close_all_clients():
    """关闭所有客户端连接"""
    for client in _clients.values():
        await client.close()
    _clients.clear()
```

#### 3.2 `agent/llm_client.py` - 通义千问 LLM 客户端

```python
"""通义千问 LLM 客户端：OpenAI 兼容接口（DashScope）"""
import os
import json
from typing import Optional, Dict, Any
from openai import AsyncOpenAI

class LLMClient:
    """通义千问 LLM 客户端封装

    不配置 DASHSCOPE_API_KEY 或 USE_LLM=false 时，
    所有方法返回 None，调用方需走规则兜底。
    """

    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.use_llm = os.getenv("USE_LLM", "true").lower() == "true"
        self.base_url = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = os.getenv("LLM_MODEL", "qwen-plus")

        self.client = None
        if self.api_key and self.use_llm:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

    @property
    def available(self) -> bool:
        return self.client is not None

    async def chat(self, system_prompt: str, user_prompt: str,
                   temperature: float = 0.3) -> Optional[str]:
        """通用 LLM 对话接口"""
        if not self.available:
            return None
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM] 调用失败: {e}")
            return None

    async def parse_intent(self, query: str) -> Optional[Dict[str, Any]]:
        """LLM 意图解析，返回 None 时调用方走规则"""
        ...

    async def summarize(self, content: str, context: str = "") -> Optional[str]:
        """LLM 摘要生成"""
        ...

    async def generate_risks(self, context: str) -> Optional[list]:
        """LLM 风险生成"""
        ...

    async def check_quality(self, markdown: str, state: Dict) -> Optional[Dict]:
        """LLM 质检"""
        ...

# 全局单例
llm_client = LLMClient()
```

#### 3.3 `agent/prompts.py` - LLM Prompt 模板

```python
"""LLM Prompt 模板"""

PARSE_INTENT_SYSTEM = """你是一个矿权领域的意图解析助手。
从用户输入中提取以下信息：
- project: 矿权项目名称
- company: 公司名
- commodity: 矿种（lithium/copper/gold/iron 等）
- report_type: 报告类型（daily_briefing/weekly_summary）
- days: 时间范围（天数，默认 1）

只返回 JSON，不要其他文字。"""

PARSE_INTENT_USER = "用户输入: {query}"

SUMMARIZE_NEWS_SYSTEM = """你是一个矿业新闻摘要专家。
将给定的新闻内容总结为 2-3 句话，突出关键事实和对矿权项目的影响。"""

# ... 更多 prompt 模板
```

---

### 步骤 4：LangGraph Agent 核心实现（P4, 9-15h）

#### 4.1 `agent/state.py` - 状态定义

直接采用技术方案中的 BriefingState 定义，使用 TypedDict。

#### 4.2 `agent/asset_resolver.py` - 资产解析器

```python
"""矿权资产配置解析器：根据项目名/公司名/矿种匹配 assets.yaml"""
import os
import yaml
from typing import Dict, Any, List

def load_assets_config() -> Dict[str, Any]:
    """加载 assets.yaml 配置"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "assets.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def resolve_asset_by_query(project: str = "", company: str = "",
                           commodity: str = "") -> Dict[str, Any]:
    """根据项目名/公司名匹配 assets.yaml 中的资产配置

    匹配策略：
    1. 精确匹配 project 或 company
    2. 模糊匹配 aliases
    3. 匹配失败返回默认值
    """
    ...
```

#### 4.3 `agent/nodes.py` - 全部 14 个节点函数

基于技术方案 7.3 节的骨架代码实现，关键增强：
1. **parse_intent**：规则优先（关键词匹配），LLM 兜底
2. **search_news / fetch_articles / extract_resources / fetch_price**：调用 MCP client，异常降级
3. **analyze_context**：LLM 生成摘要，失败走模板
4. **generate_risks**：基于规则 + LLM 增强
5. **render_report**：调用 report_generator
6. **quality_check**：调用 quality.check_report_quality
7. **revise_report**：基于 quality_issues 重写
8. **save_report / save_report_with_warnings**：写入 reports/ 目录

所有节点函数签名遵循 LangGraph 约定：`(state: BriefingState) -> dict`（返回部分状态更新）。

#### 4.4 `agent/routers.py` - 条件路由

直接采用技术方案 7.2 节的代码，实现：
- `route_news_result`：新闻搜索结果路由
- `route_quality_result`：质检结果路由

#### 4.5 `agent/graph.py` - StateGraph 构建

直接采用技术方案 7.1 节的代码，实现完整图结构：
- 14 个节点
- 线性边 + 2 个条件边
- 质检循环（最多 2 次修订）

#### 4.6 `agent/main.py` - 入口

直接采用技术方案 9.1 节代码，增加：
- .env 加载
- MCP 客户端清理
- 错误处理

---

### 步骤 5：报告生成与质检循环（P5, 15-18h）

#### 5.1 `agent/report_generator.py` - Markdown 报告生成

```python
"""Markdown 报告生成器：基于模板 + 状态数据渲染"""
from datetime import date
from typing import Dict, Any, Optional, List

def generate_markdown_report(state: Dict[str, Any],
                             previous_markdown: Optional[str] = None,
                             quality_issues: Optional[List[str]] = None) -> str:
    """生成完整的 Markdown 日报

    结构：
    1. 标题与生成时间
    2. 今日结论（3-5 条要点）
    3. 新闻摘要（每条新闻含标题、摘要、来源）
    4. 资源量/储量数据（Markdown 表格）
    5. 价格走势（当前价、涨跌幅、均线、趋势）
    6. 风险提示（编号列表）
    7. 引用源（新闻、PDF、价格来源）

    如果有 quality_issues，在对应章节补充缺失内容。
    """
    ...
```

#### 5.2 `agent/quality.py` - 质检模块

```python
"""报告质检：6 项规则检查 + LLM 轻量判断"""
from typing import Dict, Any, List

def check_report_quality(markdown: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """检查 Markdown 报告质量

    规则检查：
    1. 有标题（# 开头）
    2. 有新闻摘要（至少 1 条）
    3. 有资源量表格（| ... | 表格）
    4. 有价格走势
    5. 有风险提示（至少 3 条）
    6. 有引用链接（http）

    LLM 判断（可选）：
    - 报告是否完整
    - 是否有明显缺项

    返回: {"score": float, "issues": List[str]}
    score >= 8 通过，否则需要修订
    """
    ...
```

---

### 步骤 6：测试编写与端到端验证（P6, 18-21h）

#### 6.1 MCP Server 单元测试

**`tests/test_news_mcp.py`**：
- 测试 `search` 返回新闻列表
- 测试 `fetch_article` 返回正文
- 测试 Mock 兜底

**`tests/test_pdf_mcp.py`**：
- 测试 `extract_resources` 返回资源量
- 测试 Mock 兜底

**`tests/test_price_mcp.py`**：
- 测试 `get_price` 返回价格
- 测试 `get_trend` 返回趋势
- 测试 Mock 兜底

#### 6.2 LangGraph 编排测试

**`tests/test_graph.py`**：
- 测试 `parse_intent` 识别 Pilbara
- 测试 `resolve_asset` 补全 PDF URL
- 测试 `route_news_result` 路由逻辑
- 测试 `route_quality_result` 路由逻辑
- 测试 `quality_check` 识别缺项

#### 6.3 端到端测试

**`tests/test_agent_e2e.py`**：
- 测试完整流程：输入 → MCP 调用 → 报告生成 → 保存
- 验证报告包含所有必需章节
- 验证报告保存到 `reports/` 目录

---

### 步骤 7：文档、Demo 与收尾（P7, 21-24h）

#### 7.1 `RUN.md`

包含环境要求、启动方式、单独启动 MCP Server、接入 Claude Desktop、查看报告等。

#### 7.2 更新 `README.md`

包含项目简介、架构图、快速开始、目录结构说明。

#### 7.3 样例数据

在 `data/sample/` 放置样例 PDF 和新闻数据，用于离线测试。

#### 7.4 最终验收

按照技术方案第 18 节的 10 项验收标准逐项检查。

---

## 五、假设与决策

### 5.1 技术决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| LLM 提供商 | 通义千问 Qwen | 用户指定，DashScope OpenAI 兼容接口，国内访问稳定 |
| MCP SDK | FastMCP | 用户指定，装饰器风格，开发效率高 |
| 数据源策略 | 真实 + Mock 兜底 | 用户指定，保证 demo 可运行性 |
| MCP 传输协议 | stdio | 技术方案指定，适合本地 demo |
| LangGraph 流程 | 显式 StateGraph | 技术方案指定，非 LLM 自由 ReAct |
| 质检方式 | 规则 + LLM 轻量 | 技术方案指定，24h 版本不做复杂评估 |
| PDF 解析 | PyMuPDF + pdfplumber | 技术方案指定 |

### 5.2 假设

1. **通义千问 API Key 可选**：未配置 DASHSCOPE_API_KEY 时系统走纯规则模式，仍可生成日报
2. **真实数据源可能不稳定**：RSS/API 可能超时或返回空，Mock 兜底保证 demo 不中断
3. **PDF URL 可访问性**：配置的 PDF URL 可能无法访问，Mock 兜底保证资源量数据存在
4. **Docker 环境**：用户已安装 Docker 和 Docker Compose（本地运行不依赖 Docker）

### 5.3 编码规范

1. **类型标注**：所有函数使用 Python type hints
2. **错误处理**：MCP 调用全部 try/except，异常降级到 Mock 或 warnings
3. **注释**：模块级 docstring + 关键函数 docstring，复杂逻辑加行内注释
4. **配置外置**：所有可配置项放 configs/ 目录，不硬编码
5. **异步**：MCP 调用和 LLM 调用使用 async/await，LangGraph 使用 ainvoke

---

## 六、验证步骤

### 6.1 本地运行验证

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选，不配置走纯规则模式）
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY

# 3. 运行 Agent
python agent/main.py "给我生成一份关于 Pilbara 锂矿的今日简报"

# 4. 查看报告
cat reports/pilbara_daily_briefing_2026-07-09.md
```

### 6.2 Docker 运行验证

```bash
docker compose up --build
```

### 6.3 单独验证 MCP Server

```bash
python servers/mining_news_mcp/server.py
python servers/mineral_pdf_mcp/server.py
python servers/lme_price_mcp/server.py
```

### 6.4 运行测试

```bash
pytest tests/ -v
```

### 6.5 验收标准检查

对照技术方案第 18 节的 10 项必须满足标准 + 6 项加分项，逐项确认：

1. ✅ 有 3 个 MCP server
2. ✅ 每个 server 暴露题目要求的 tools
3. ✅ Agent client 基于 LangGraph
4. ✅ LangGraph 中有明确 nodes / edges / conditional edges
5. ✅ 输入自然语言，输出 Markdown 简报
6. ✅ Markdown 包含新闻、资源量、价格走势、风险提示和引用
7. ✅ 有 mcp-config.json
8. ✅ 有 RUN.md
9. ✅ 有 docker-compose.yml
10. ✅ 5 分钟内可以跑起来

加分项：
1. ✅ graph 流程图输出
2. ✅ quality_check → revise_report 真实循环
3. ✅ 失败降级信息写入 warnings
4. ✅ 报告保存到 reports/
5. ✅ 每个 MCP 工具独立测试
6. ✅ LangGraph 状态可打印

---

## 七、技术路线图

```text
P1 项目初始化
  ├── 目录结构 + requirements.txt
  ├── Dockerfile + docker-compose.yml
  └── 配置文件 (assets.yaml, sources.yaml, mcp-config.json)
        ↓
P2 MCP Server 实现
  ├── mining-news-mcp (search, fetch_article)
  ├── mineral-pdf-mcp (extract_resources)
  └── lme-price-mcp (get_price, get_trend)
        ↓
P3 Client 封装
  ├── mcp_clients.py (MCP stdio 客户端)
  ├── llm_client.py (DeepSeek 客户端)
  └── prompts.py (Prompt 模板)
        ↓
P4 LangGraph 核心
  ├── state.py (BriefingState)
  ├── asset_resolver.py
  ├── nodes.py (14 个节点)
  ├── routers.py (2 个路由)
  ├── graph.py (StateGraph)
  └── main.py (入口)
        ↓
P5 报告与质检
  ├── report_generator.py (Markdown 渲染)
  └── quality.py (规则 + LLM 质检)
        ↓
P6 测试验证
  ├── test_news_mcp.py
  ├── test_pdf_mcp.py
  ├── test_price_mcp.py
  ├── test_graph.py
  └── test_agent_e2e.py
        ↓
P7 文档收尾
  ├── RUN.md
  ├── README.md
  ├── 样例数据
  └── 最终验收
```
