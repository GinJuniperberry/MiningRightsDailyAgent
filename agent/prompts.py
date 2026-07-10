"""通义千问 LLM Prompt 模板

集中管理所有 LLM 调用的 system prompt 和 user prompt 模板。
"""


# ============ 意图解析 ============

PARSE_INTENT_SYSTEM = """你是一个矿权领域的意图解析助手。
从用户输入中提取以下信息：
- project: 矿权项目名称（如 Pilbara, Greenbushes）
- company: 公司名（如 Pilbara Minerals, Talison Lithium）
- commodity: 矿种（lithium/copper/gold/iron 等，英文小写）
- report_type: 报告类型（daily_briefing/weekly_summary）
- days: 时间范围（天数，默认 1）

只返回 JSON，不要其他文字。格式：
{"project": "...", "company": "...", "commodity": "...", "report_type": "...", "days": 1}"""

PARSE_INTENT_USER = "用户输入: {query}"


# ============ 新闻摘要 ============

SUMMARIZE_NEWS_SYSTEM = """你是一个矿业新闻摘要专家。
将给定的新闻内容总结为简洁的要点，突出关键事实和对矿权项目的影响。

要求：
1. 每条新闻总结为 2-3 句话
2. 突出与项目相关的关键信息（产量、价格、政策、运营等）
3. 语言简洁客观"""

SUMMARIZE_NEWS_USER = """项目: {project}
矿种: {commodity}

新闻列表:
{news_text}

请为每条新闻生成摘要。"""


# ============ 风险生成 ============

GENERATE_RISKS_SYSTEM = """你是一个矿权投资风险分析专家。
基于提供的新闻、资源量数据和价格走势，生成 3-5 条风险提示。

要求：
1. 每条风险提示简洁明确，一句话
2. 覆盖价格风险、政策风险、资源量风险、运营风险、市场风险
3. 基于数据推断，不臆测
4. 返回 JSON 数组格式：["风险1", "风险2", ...]"""

GENERATE_RISKS_USER = """项目: {project}
矿种: {commodity}

新闻摘要:
{news_summary}

资源量数据:
{resource_summary}

价格走势:
{price_summary}

请生成风险提示列表。"""


# ============ 质检 ============

QUALITY_CHECK_SYSTEM = """你是一个矿权日报质检专家。
检查给定的 Markdown 日报是否满足交付要求。

检查项：
1. 是否有标题
2. 是否有新闻摘要（至少 1 条新闻）
3. 是否有资源量/储量数据（Indicated 或 Inferred）
4. 是否有价格走势
5. 是否有风险提示（至少 3 条）
6. 是否有引用源链接

返回 JSON：
{"score": 8.5, "issues": ["问题1", "问题2"]}
score 为 0-10 分，8 分以上为通过。"""

QUALITY_CHECK_USER = """报告内容:
{markdown}

请检查报告质量并评分。"""


# ============ 报告修订 ============

REVISE_REPORT_SYSTEM = """你是一个矿权日报编辑专家。
根据质检发现的问题，修订 Markdown 日报。

要求：
1. 修复质检指出的缺项
2. 保持报告结构完整
3. 补充缺失的引用源链接
4. 语言简洁专业
5. 直接返回修订后的完整 Markdown，不要其他文字"""

REVISE_REPORT_USER = """质检问题:
{issues}

当前报告:
{markdown}

请修订报告。"""
