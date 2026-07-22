# MiningRightsDailyAgent - 矿权日报 Agent

基于 LangGraph + MCP 协议的矿权信息查询与日报生成系统。用户输入矿权项目、公司、矿种或关注主题后，系统会组合新闻、公开资源量报告、价格趋势和风险信息，生成可追溯的结构化日报。

## 系统能查询什么

| 信息类型 | 查询内容 | 返回结果 |
| --- | --- | --- |
| 矿权与公司 | 根据项目名、公司名和中英文别名识别矿权 | 标准项目名、所属公司、矿种、项目别名、已配置报告 |
| 矿业新闻 | 按项目、公司和矿种搜索最近 1 / 7 / 30 天的 RSS 新闻 | 标题、链接、来源、发布日期、摘要、相关度评分 |
| 新闻正文 | 抓取搜索结果中排名靠前的新闻页面 | 正文、标题、发布日期、来源和引用链接 |
| 资源量与储量 | 从 JORC / NI 43-101 等公开 PDF 报告抽取结构化数据 | Measured、Indicated、Inferred、Stockpiles、矿石量、品位、金属量、页码和置信度 |
| 价格行情 | 查询指定矿种的当日模拟价格和近 30 天趋势 | 最新价、起始价、涨跌额、涨跌幅、MA7、MA30、趋势和观察结论 |
| 风险提示 | 综合新闻、资源量和价格变化 | 价格、运营、资源量可信度、政策、环保、运输和融资风险 |
| 日报与历史 | 生成、检查、保存和下载日报 | Markdown 报告、引用源、数据警告、质检分数、历史任务和 SSE 实时进度 |

当前内置资产配置支持：

- **Pilbara / Pilgangoora / Pilbara Minerals / 皮尔巴拉**：锂矿，已配置公开资源量 PDF。
- **Greenbushes / Talison Lithium / 格林布什**：锂矿，当前未配置资源量 PDF，相关章节会提示人工补充。
- **Mount Cattlin / Mt Cattlin / Allkem**：锂矿，已配置 ASX 官方资源量 PDF，可抽取 12.8 Mt 的 Measured、Indicated、Stockpiles 和 Inferred 明细。
- 其他查询可识别锂、铜、铁、金等矿种关键词；未配置资产别名或 PDF 时，项目和资源量信息可能进入降级流程。

价格模块当前为**本地模拟行情**，不是交易所或商业行情 API。`configs/sources.yaml` 已配置 lithium 和 copper 的基准价、单位与币种；其余矿种会使用通用默认参数。

## 核心能力

输入示例：

```text
给我生成一份关于 Pilbara 锂矿的今日简报
Greenbushes 锂矿最新动态和资源量分析
Mount Cattlin 今日行情与风险提示
分析最近 7 天锂矿新闻和价格风险
```

系统会完成：

1. 解析项目、公司、矿种和报告类型，优先匹配 `configs/assets.yaml`，识别不到时可由通义千问辅助解析。
2. 搜索新闻；无结果时将时间范围从 1 天扩展到 7 天、30 天。
3. 抓取排名靠前的新闻正文，并保留原始链接作为引用。
4. 下载项目公开 PDF，抽取资源分类、矿石量、品位和金属量。
5. 生成当日模拟价格与 30 日趋势，计算 MA7、MA30 和涨跌幅。
6. 综合数据生成摘要和风险提示；未配置 LLM 时自动使用规则模板。
7. 渲染 Markdown 日报，执行质量检查，必要时最多修订两次。
8. 通过 Web 页面展示执行进度、结构化结果、历史记录和报告下载入口。

## MCP 服务能力

系统包含三个可独立调用的 MCP Server：

| MCP Server | 工具 | 能力 |
| --- | --- | --- |
| `mining-news-mcp` | `search(query, days)` | 按关键词并发查询 Mining.com、Mining Journal、Reuters Commodities RSS，按时间和相关度筛选，最多返回 10 条新闻 |
| `mining-news-mcp` | `fetch_article(url)` | 下载新闻网页，使用 trafilatura 提取正文与元数据；失败时返回摘要或内置示例文章 |
| `mineral-pdf-mcp` | `extract_resources(pdf_url)` | 下载并缓存 PDF，从表格或页面文本中抽取 Measured / Indicated / Inferred 等资源量数据 |
| `lme-price-mcp` | `get_price(commodity, date)` | 根据已配置基准价生成指定日期的本地模拟价格 |
| `lme-price-mcp` | `get_trend(commodity, days)` | 生成连续价格序列并计算涨跌幅、MA7、MA30、趋势和观察结论 |

### mining-news-mcp 能做什么

`mining-news-mcp` 是系统的新闻检索和正文采集服务，适合被 Agent、Codex、Claude Code、Cursor 或其他 MCP 客户端独立调用。

- 支持按“项目 + 公司 + 矿种”组合关键词搜索。
- 支持指定最近天数，Agent 默认按 1 → 7 → 30 天逐级扩大范围。
- 三个 RSS 数据源并发请求，单个来源失败不会阻塞其他来源。
- 返回统一新闻结构：`title`、`url`、`source`、`published_at`、`summary`、`score`。
- 可进一步调用 `fetch_article` 获取 `content` 和 `citations`。
- Agent 内部通过 stdio 启动；直接运行脚本时提供 Streamable HTTP 端点 `http://127.0.0.1:8001/mcp`。
- RSS 无结果或正文抓取失败时会使用内置示例数据，保证演示流程继续运行；内置新闻目前主要是 Pilbara 锂矿样例，不应视为实时新闻。

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
| 新闻采集 | httpx + feedparser + trafilatura |
| 价格行情 | 本地随机游走模拟 + pandas |
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
- PDF 抽取：多 PDF 备选 + 表格/页面文本解析 + Mock 兜底
- 质检循环：不合格报告最多修订 2 次

## 数据降级

采用"真实数据源 + Mock 兜底"策略，保证 demo 任何时候可运行：

- 新闻：真实 RSS / 新闻正文 → 内置 Pilbara 示例新闻与文章。
- PDF：真实公开 PDF 下载解析 → 内置示例资源量；没有配置 PDF 时明确提示人工补充。
- 价格：始终使用本地随机游走模拟，不代表真实市场报价，不应用于交易或投资决策。
- 风险和摘要：通义千问不可用时使用规则模板，报告仍可生成。

## 测试

```bash
pytest tests/ -v
```

## License

MIT
