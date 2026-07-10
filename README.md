# MiningRightsDailyAgent - 矿权日报 Agent

基于 LangGraph + MCP 协议的「矿权日报 Agent」，输入一句自然语言即可生成结构化 Markdown 矿权日报。

## 功能

输入：
```text
给我生成一份关于 Pilbara 锂矿的今日简报
```

输出 Markdown 简报，包含：
1. 新闻摘要
2. NI 43-101 / 矿权报告中的 Indicated / Inferred 资源量数据
3. 锂 / 相关金属价格走势
4. 风险提示
5. 引用源链接

## 架构

```text
User Input
   ↓
LangGraph Agent Client
   ↓
┌───────────────┬────────────────┬───────────────┐
│ mining-news   │ mineral-pdf     │ lme-price     │
│ MCP Server    │ MCP Server      │ MCP Server    │
└───────────────┴────────────────┴───────────────┘
   ↓
LangGraph Report Renderer
   ↓
Markdown Briefing
```

- **MCP Server 工具层**：3 个 MCP Server 提供标准化工具（新闻采集、PDF 解析、价格查询）
- **LangGraph 编排层**：14 个节点的 StateGraph，含条件路由和质检循环
- **报告生成层**：基于模板渲染 Markdown 日报

## 技术栈

| 模块 | 技术 |
|------|------|
| Agent 编排 | LangGraph StateGraph |
| MCP Server | Python + FastMCP |
| LLM | 通义千问 Qwen（OpenAI 兼容接口） |
| PDF 解析 | PyMuPDF + pdfplumber |
| 新闻采集 | feedparser + httpx + trafilatura |
| 价格行情 | httpx + pandas |
| 容器化 | Docker Compose |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 Agent
python agent/main.py "给我生成一份关于 Pilbara 锂矿的今日简报"

# 查看报告
cat reports/pilbara_daily_briefing_2026-07-09.md
```

详细说明见 [RUN.md](RUN.md)。

## LangGraph 工作流

```text
START → parse_intent → resolve_asset → search_news → [条件路由]
  → fetch_articles → extract_resources → fetch_price
  → analyze_context → generate_risks → render_report
  → quality_check → [条件路由]
  → save_report / revise_report / save_report_with_warnings → END
```

特性：
- 新闻搜索降级：无结果时自动扩大搜索天数（1→7→30）
- PDF 抽取降级：多 PDF 备选 + Mock 兜底
- 质检循环：不合格报告最多修订 2 次

## 数据降级

采用"真实数据源 + Mock 兜底"策略，保证 demo 任何时候可运行：
- 新闻：RSS 源 → Mock 数据
- PDF：真实 PDF 下载解析 → Mock 资源量
- 价格：真实 API → Mock 价格

## 测试

```bash
pytest tests/ -v
```

## License

MIT
