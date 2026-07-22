"""LangGraph 节点函数

所有节点围绕 BriefingState 读写数据。
节点签名遵循 LangGraph 约定：(state: dict) -> dict（返回部分状态更新）。
"""
import os
from datetime import date
from typing import Dict, Any, List

from agent.mcp_clients import (
    call_mining_news_tool,
    call_mineral_pdf_tool,
    call_price_tool,
)
from agent.asset_resolver import resolve_asset_by_query
from agent.report_generator import generate_markdown_report
from agent.quality import check_report_quality_with_llm
from agent.llm_client import llm_client


# ============ 1. parse_intent ============

async def parse_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """从用户输入中解析矿权、公司、矿种和日报类型

    策略：规则优先（关键词匹配），LLM 兜底
    """
    query = state.get("user_query", "")

    # 已知项目统一从 assets.yaml 的别名配置识别，避免规则与配置漂移。
    asset = resolve_asset_by_query(query=query)
    if asset.get("project") != "unknown":
        return {
            "project": asset["project"],
            "company": asset.get("company", "Unknown"),
            "commodity": asset.get("commodity", "unknown"),
            "report_type": "daily_briefing",
            "days": 1,
            "revise_count": 0,
            "errors": [],
            "warnings": [],
        }

    # 规则匹配：矿种
    commodity = "unknown"
    if "锂" in query or "lithium" in query.lower():
        commodity = "lithium"
    elif "铜" in query or "copper" in query.lower():
        commodity = "copper"
    elif "铁" in query or "iron" in query.lower():
        commodity = "iron"
    elif "金" in query or "gold" in query.lower():
        commodity = "gold"

    # LLM 兜底（如果可用且配置、规则均未完整匹配）
    if llm_client.available:
        llm_result = await llm_client.parse_intent(query)
        if llm_result and llm_result.get("project"):
            llm_result.setdefault("report_type", "daily_briefing")
            llm_result.setdefault("days", 1)
            llm_result.setdefault("revise_count", 0)
            llm_result.setdefault("errors", [])
            llm_result.setdefault("warnings", [])
            return llm_result

    return {
        "project": "unknown",
        "commodity": commodity,
        "report_type": "daily_briefing",
        "days": 1,
        "revise_count": 0,
        "errors": [],
        "warnings": ["未能明确识别矿权项目，后续会尝试模糊匹配。"],
    }


# ============ 2. resolve_asset ============

def resolve_asset(state: Dict[str, Any]) -> Dict[str, Any]:
    """根据项目别名配置补全矿权信息"""
    asset = resolve_asset_by_query(
        project=state.get("project", ""),
        company=state.get("company", ""),
        commodity=state.get("commodity", ""),
        query=state.get("user_query", ""),
    )

    return {
        "project": asset.get("project", state.get("project", "unknown")),
        "aliases": asset.get("aliases", []),
        "pdf_urls": asset.get("pdf_urls", []),
        "company": asset.get("company", state.get("company")),
        "commodity": asset.get("commodity", state.get("commodity")),
    }


# ============ 3. search_news ============

async def search_news(state: Dict[str, Any]) -> Dict[str, Any]:
    """调用 mining-news-mcp.search 搜索新闻"""
    query = " ".join(filter(None, [
        state.get("project", ""),
        state.get("company", ""),
        state.get("commodity", "")
    ])).strip()

    if not query:
        query = state.get("user_query", "")

    days = state.get("days", 1)

    try:
        result = await call_mining_news_tool(
            tool_name="search",
            arguments={"query": query, "days": days}
        )
        news_items = result.get("items", [])
        warnings = state.get("warnings", [])
        if result.get("warning"):
            warnings.append(result["warning"])
        return {"news_items": news_items, "warnings": warnings}
    except Exception as e:
        return {
            "news_items": [],
            "errors": state.get("errors", []) + [{
                "node": "search_news",
                "error": str(e)
            }]
        }


# ============ 4. expand_news_days ============

def expand_news_days(state: Dict[str, Any]) -> Dict[str, Any]:
    """扩大新闻搜索天数（降级策略）

    days 扩展策略：1 → 7 → 30
    """
    current_days = state.get("days", 1)

    if current_days <= 1:
        next_days = 7
    elif current_days <= 7:
        next_days = 30
    else:
        next_days = 30

    return {"days": next_days}


# ============ 5. fetch_articles ============

async def fetch_articles(state: Dict[str, Any]) -> Dict[str, Any]:
    """对新闻搜索结果 top 3 调用 fetch_article 抓取正文"""
    articles: List[Dict[str, Any]] = []
    news_items = state.get("news_items", [])

    for item in news_items[:3]:
        url = item.get("url")
        if not url:
            continue

        try:
            article = await call_mining_news_tool(
                tool_name="fetch_article",
                arguments={"url": url}
            )
            articles.append(article)
        except Exception as e:
            # 正文抓取失败，使用摘要代替
            articles.append({
                "title": item.get("title"),
                "url": url,
                "published_at": item.get("published_at", ""),
                "source": item.get("source", ""),
                "content": item.get("summary", ""),
                "warning": f"正文抓取失败，使用摘要代替：{e}"
            })

    return {"articles": articles}


# ============ 6. extract_resources ============

async def extract_resources(state: Dict[str, Any]) -> Dict[str, Any]:
    """调用 mineral-pdf-mcp.extract_resources 抽取资源量

    如果有多个 PDF URL，优先使用最新报告，第一个失败后换下一个。
    """
    pdf_urls = state.get("pdf_urls", [])
    warnings = state.get("warnings", [])

    if not pdf_urls:
        return {
            "resources": {},
            "warnings": warnings + ["未配置资源量 PDF，储量数据部分待人工补充。"]
        }

    for pdf_url in pdf_urls:
        try:
            result = await call_mineral_pdf_tool(
                tool_name="extract_resources",
                arguments={"pdf_url": pdf_url}
            )

            if result.get("resources"):
                if result.get("warnings"):
                    warnings.extend(result["warnings"])
                return {"resources": result, "warnings": warnings}

        except Exception as e:
            warnings.append(f"PDF 抽取失败：{pdf_url}，错误：{e}")

    return {
        "resources": {},
        "warnings": warnings + ["所有 PDF 均抽取失败，资源量数据待人工复核。"]
    }


# ============ 7. fetch_price ============

async def fetch_price(state: Dict[str, Any]) -> Dict[str, Any]:
    """调用 lme-price-mcp 查询价格和趋势"""
    commodity = state.get("commodity", "lithium")
    today = date.today().isoformat()

    latest_price: Dict[str, Any] = {}
    price_trend: Dict[str, Any] = {}
    warnings = state.get("warnings", [])

    try:
        latest_price = await call_price_tool(
            tool_name="get_price",
            arguments={"commodity": commodity, "date": today}
        )
    except Exception as e:
        warnings.append(f"价格查询失败：{e}")

    try:
        price_trend = await call_price_tool(
            tool_name="get_trend",
            arguments={"commodity": commodity, "days": 30}
        )
    except Exception as e:
        warnings.append(f"价格趋势查询失败：{e}")

    return {
        "latest_price": latest_price,
        "price_trend": price_trend,
        "warnings": warnings,
    }


# ============ 8. analyze_context ============

async def analyze_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """将新闻、资源量、价格走势转成结构化摘要

    LLM 可用时用 LLM 生成摘要，否则走模板。
    """
    articles = state.get("articles", [])
    resources = state.get("resources", {})
    price_trend = state.get("price_trend", {})
    project = state.get("project", "")
    commodity = state.get("commodity", "")

    # 新闻摘要
    news_summary = "暂无相关新闻。"
    if articles:
        news_text = "\n".join(
            f"- {a.get('title', '')}: {a.get('content', a.get('summary', ''))[:200]}"
            for a in articles
        )

        # 尝试 LLM 摘要
        if llm_client.available:
            llm_summary = await llm_client.summarize_news(project, commodity, news_text)
            if llm_summary:
                news_summary = llm_summary
            else:
                news_summary = f"共检索到 {len(articles)} 条相关新闻，主要围绕项目进展、市场价格和运营风险。"
        else:
            news_summary = f"共检索到 {len(articles)} 条相关新闻，主要围绕项目进展、市场价格和运营风险。"

    # 资源量摘要
    resource_summary = "资源量数据待人工复核。"
    resource_list = resources.get("resources", [])
    if resource_list:
        categories = [r.get("category", "") for r in resource_list]
        resource_summary = f"已抽取到 {' / '.join(categories)} 资源量数据，可进入日报。"

    # 价格摘要
    price_summary = "价格趋势数据不可用。"
    if price_trend:
        change_pct = price_trend.get("change_pct", "N/A")
        trend = price_trend.get("trend", "unknown")
        trend_text = {"up": "上行", "down": "下行", "flat": "震荡"}.get(trend, trend)
        days = price_trend.get("days", 30)
        price_summary = f"近 {days} 天价格趋势为 {trend_text}，涨跌幅 {change_pct}%。"

    return {
        "news_summary": news_summary,
        "resource_summary": resource_summary,
        "price_summary": price_summary,
    }


# ============ 9. generate_risks ============

async def generate_risks(state: Dict[str, Any]) -> Dict[str, Any]:
    """基于新闻、资源量和价格生成风险提示

    LLM 可用时用 LLM 生成，否则走规则。
    """
    risks: List[str] = []
    price_trend = state.get("price_trend", {})
    resources = state.get("resources", {})
    articles = state.get("articles", [])
    project = state.get("project", "")
    commodity = state.get("commodity", "")

    # 尝试 LLM 生成风险
    if llm_client.available:
        news_summary = state.get("news_summary", "")
        resource_summary = state.get("resource_summary", "")
        price_summary = state.get("price_summary", "")

        llm_risks = await llm_client.generate_risks(
            project=project,
            commodity=commodity,
            news_summary=news_summary,
            resource_summary=resource_summary,
            price_summary=price_summary,
        )
        if llm_risks:
            risks = llm_risks

    # 规则兜底
    if not risks:
        if price_trend.get("change_pct") is not None:
            change_pct = price_trend.get("change_pct", 0)
            if abs(change_pct) > 5:
                risks.append(f"价格短期波动较大（{change_pct}%），可能影响项目收入预期。")
            else:
                risks.append("价格短期波动可能影响项目收入预期。")

        if not resources.get("resources"):
            risks.append("资源量数据未能稳定抽取，需人工复核后再用于正式投资判断。")

        if articles:
            risks.append("新闻事件可能影响项目投产节奏、审批进度或市场预期。")

        risks.append("矿权项目仍需关注政策、环保、运输和融资等外部变量。")

    return {"risks": risks}


# ============ 10. render_report ============

def render_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """生成 Markdown 日报"""
    markdown = generate_markdown_report(state)
    return {"markdown": markdown}


# ============ 11. quality_check ============

async def quality_check(state: Dict[str, Any]) -> Dict[str, Any]:
    """检查 Markdown 报告是否满足交付要求"""
    markdown = state.get("markdown", "")
    result = await check_report_quality_with_llm(markdown, state)
    return {
        "quality_score": result["score"],
        "quality_issues": result["issues"],
    }


# ============ 12. revise_report ============

async def revise_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """根据 quality_issues 修订报告，最多重写 2 次"""
    current = state.get("markdown", "")
    issues = state.get("quality_issues", [])
    revise_count = state.get("revise_count", 0)

    # 尝试 LLM 修订
    if llm_client.available:
        revised = await llm_client.revise_report(current, issues)
        if revised:
            return {
                "markdown": revised,
                "revise_count": revise_count + 1,
            }

    # 规则修订：重新生成报告（带 quality_issues 标记）
    revised = generate_markdown_report(
        state,
        previous_markdown=current,
        quality_issues=issues,
    )

    return {
        "markdown": revised,
        "revise_count": revise_count + 1,
    }


# ============ 13. save_report ============

def save_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """保存 Markdown 报告到 reports/ 目录"""
    return _save_report_to_file(state, with_warnings=False)


# ============ 14. save_report_with_warnings ============

def save_report_with_warnings(state: Dict[str, Any]) -> Dict[str, Any]:
    """保存报告（带警告标记），用于质检未通过且修订次数已达上限的情况"""
    return _save_report_to_file(state, with_warnings=True)


def _save_report_to_file(state: Dict[str, Any], with_warnings: bool) -> Dict[str, Any]:
    """保存报告到文件的通用逻辑"""
    markdown = state.get("markdown", "")
    project = state.get("project", "unknown")
    today = date.today().isoformat()

    # 生成文件名：{project}_daily_briefing_{date}.md
    safe_project = project.lower().replace(" ", "_")
    filename = f"{safe_project}_daily_briefing_{today}.md"

    # 确定报告目录
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    filepath = os.path.join(reports_dir, filename)

    # 如果是带警告保存，在报告末尾追加警告说明
    if with_warnings:
        quality_issues = state.get("quality_issues", [])
        warnings = state.get("warnings", [])
        markdown += "\n\n---\n\n> **注意**：本报告未通过全部质检项，请人工复核以下问题：\n"
        for issue in quality_issues:
            markdown += f"> - {issue}\n"
        if warnings:
            markdown += "\n> **数据警告**：\n"
            for w in warnings:
                markdown += f"> - {w}\n"

    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"[save_report] 报告已保存: {filepath}")

    return {"report_path": filepath}
